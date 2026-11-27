#!/usr/bin/env python3
"""Validate a GitHub Issue Form request and prepare a Tauri Windows build."""

from __future__ import annotations

import base64
import io
import ipaddress
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import warnings
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = 16_777_216

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "src-tauri" / "tauri.conf.json"
ICON_DIR = ROOT / "src-tauri" / "icons"
CAPABILITY_DIR = ROOT / "src-tauri" / "capabilities"
CAPABILITY_PATH = CAPABILITY_DIR / "main.json"
MAX_ICON_BYTES = 2 * 1024 * 1024
# Exact hosts used by GitHub's attachment redirect chain. GitHub's
# /user-attachments/assets endpoint redirects to its signed S3 asset bucket;
# /user-attachments/files can redirect to objects.githubusercontent.com.
ALLOWED_ICON_HOSTS = {
    "github.com",
    "user-images.githubusercontent.com",
    "secured-user-images.githubusercontent.com",
    "private-user-images.githubusercontent.com",
    "objects.githubusercontent.com",
    "github-production-user-asset-6210df.s3.amazonaws.com",
    "github-production-repository-file-5c1aeb.s3.amazonaws.com",
}


def fail(message: str) -> None:
    print(f"Request rejected: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_field(body: str, label: str) -> str:
    pattern = rf"(?ms)^###\s+{re.escape(label)}\s*\n(.*?)(?=^###\s|\Z)"
    match = re.search(pattern, body)
    if not match:
        return ""
    value = match.group(1).strip()
    if value in {"_No response_", "N/A", "None"}:
        return ""
    return value


def validate_site_url(value: str) -> tuple[str, str]:
    value = value.strip()
    if not value or len(value) > 2048:
        fail("Website URL is missing or too long.")

    try:
        parsed = urllib.parse.urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        fail("Website URL is malformed.")

    if parsed.scheme.lower() != "https":
        fail("Only HTTPS website addresses are accepted.")
    if not host or parsed.username or parsed.password:
        fail("Website URL must contain a public hostname and no embedded credentials.")
    if port not in (None, 443):
        fail("Only the standard HTTPS port (443) is supported.")

    try:
        host = host.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError:
        fail("Website hostname is invalid.")

    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        fail("IP-literal website addresses are not accepted.")

    blocked_suffixes = (
        ".localhost",
        ".local",
        ".internal",
        ".test",
        ".invalid",
        ".example",
    )
    if (
        host in {"localhost", "local", "internal"}
        or host.endswith(blocked_suffixes)
        or "." not in host
    ):
        fail("A public internet hostname is required.")

    if not re.fullmatch(r"[a-z0-9.-]+", host) or ".." in host:
        fail("Website hostname contains invalid characters.")

    netloc = host
    if parsed.port == 443:
        netloc = f"{host}:443"

    normalized = urllib.parse.urlunsplit(
        ("https", netloc, parsed.path or "/", parsed.query, parsed.fragment)
    )
    return normalized, host


def clean_app_name(value: str) -> str:
    value = unicodedata.normalize("NFC", value).strip()
    cleaned = "".join(
        char for char in value
        if char.isalnum() or char in " ._-"
    ).strip(" ._-")

    if len(cleaned) < 2 or len(cleaned) > 40:
        fail("Application name must contain 2–40 valid letters, numbers, spaces, dots, dashes, or underscores.")
    if not any(char.isalnum() for char in cleaned):
        fail("Application name must contain at least one letter or number.")
    return cleaned


def parse_dimension(raw: str, default: int, minimum: int, maximum: int, label: str) -> int:
    if not raw.strip():
        return default
    if not re.fullmatch(r"\d{2,4}", raw.strip()):
        fail(f"{label} must be a whole number.")
    value = int(raw.strip())
    if not minimum <= value <= maximum:
        fail(f"{label} must be between {minimum} and {maximum}.")
    return value


def parse_toggle(body: str, label: str, default: bool) -> bool:
    raw = read_field(body, label).strip().casefold()
    if not raw:
        return default
    if raw == "enabled":
        return True
    if raw == "disabled":
        return False
    fail(f"{label} must be Enabled or Disabled.")


def parse_theme(body: str) -> str:
    raw = read_field(body, "App and WebView theme").strip().casefold()
    choices = {
        "system": "System",
        "light": "Light",
        "dark": "Dark",
    }
    if not raw:
        return "System"
    if raw not in choices:
        fail("App and WebView theme must be System, Light, or Dark.")
    return choices[raw]


def is_allowed_icon_url(url: str) -> bool:
    """Allow only HTTPS URLs on GitHub's exact attachment/CDN hosts."""
    try:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        port = parsed.port
    except ValueError:
        return False

    return (
        parsed.scheme.lower() == "https"
        and host in ALLOWED_ICON_HOSTS
        and port in (None, 443)
        and not parsed.username
        and not parsed.password
    )


class SafeIconRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        if not is_allowed_icon_url(new_url):
            raise urllib.error.HTTPError(
                new_url, code, "Icon redirect URL is not allowed", headers, None
            )
        return super().redirect_request(
            request, response, code, message, headers, new_url
        )


def extract_icon_url(value: str) -> str | None:
    if not value:
        return None

    candidates = re.findall(r"https://[^\s)>\]]+", value)
    for candidate in candidates:
        candidate = candidate.rstrip(".,;")
        parsed = urllib.parse.urlsplit(candidate)
        if (
            parsed.scheme == "https"
            and parsed.hostname in ALLOWED_ICON_HOSTS
            and parsed.hostname == "github.com"
            and parsed.path.startswith(("/user-attachments/assets/", "/user-attachments/files/"))
        ):
            return candidate

    if value.strip():
        fail("Upload the icon using the Application icon file field. Supported formats: PNG, JPG, JPEG, WEBP, GIF.")
    return None


def download_icon(url: str) -> Image.Image:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "WebToExe-Builder/1.0", "Accept": "image/*"},
    )
    opener = urllib.request.build_opener(SafeIconRedirect())
    try:
        with opener.open(request, timeout=20) as response:
            if not is_allowed_icon_url(response.geturl()):
                fail("Icon download redirected to an untrusted URL.")
            content_type = response.headers.get_content_type()
            if not content_type.startswith("image/"):
                fail("The uploaded icon is not an image.")
            data = response.read(MAX_ICON_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        fail(f"Could not download the uploaded icon: {exc}")

    if not data or len(data) > MAX_ICON_BYTES:
        fail("Icon file must be smaller than 2 MB.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(io.BytesIO(data))
            if image.format not in {"PNG", "JPEG", "WEBP", "GIF"}:
                fail("Use a PNG, JPG, JPEG, WEBP, or GIF image for the app icon.")
            image.verify()
            image = Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:
        fail("Uploaded icon is not a supported image or exceeds safe image limits.")
    if image.width < 32 or image.height < 32 or image.width > 4096 or image.height > 4096:
        fail("Icon dimensions must be between 32x32 and 4096x4096 pixels.")
    return image


def make_default_icon() -> Image.Image:
    size = 512
    image = Image.new("RGBA", (size, size), (19, 27, 42, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((28, 28, 484, 484), radius=112, fill=(30, 64, 110, 255))
    draw.rounded_rectangle((54, 54, 458, 458), radius=90, outline=(91, 151, 222, 255), width=7)

    font = None
    for font_path in (
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ):
        try:
            font = ImageFont.truetype(font_path, 286)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    text = "W"
    bounds = draw.textbbox((0, 0), text, font=font, stroke_width=1)
    x = (size - (bounds[2] - bounds[0])) / 2 - bounds[0]
    y = (size - (bounds[3] - bounds[1])) / 2 - bounds[1] - 8
    draw.text((x, y), text, font=font, fill=(245, 248, 252, 255), stroke_width=1)
    return image


def write_icons(image: Image.Image) -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    image = image.convert("RGBA")
    image.thumbnail((512, 512), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (512, 512), (19, 27, 42, 255))
    x = (512 - image.width) // 2
    y = (512 - image.height) // 2
    canvas.alpha_composite(image, (x, y))
    canvas.save(ICON_DIR / "icon.png", format="PNG")
    canvas.resize((64, 64), Image.Resampling.LANCZOS).save(
        ICON_DIR / "titlebar.png", format="PNG"
    )
    canvas.save(
        ICON_DIR / "icon.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "")
    if not body:
        fail("GitHub issue body is empty.")

    website_url, website_host = validate_site_url(read_field(body, "Website URL"))
    app_name = clean_app_name(read_field(body, "Application name"))
    width = parse_dimension(read_field(body, "Window width"), 1280, 600, 2560, "Window width")
    height = parse_dimension(read_field(body, "Window height"), 800, 400, 1600, "Window height")

    disable_context_menu = not parse_toggle(body, "Right-click context menu", True)
    allow_maximize = parse_toggle(body, "Maximize button", True)
    allow_resize = parse_toggle(body, "Resize window", True)
    allow_minimize = parse_toggle(body, "Minimize button", True)
    show_titlebar = parse_toggle(body, "Native title bar and borders", True)
    start_maximized = parse_toggle(body, "Start maximized", False)
    start_fullscreen = parse_toggle(body, "Start in fullscreen", False)
    always_on_top = parse_toggle(body, "Always on top", False)
    zoom_shortcuts = parse_toggle(body, "Page zoom shortcuts", True)
    show_in_taskbar = parse_toggle(body, "Show in Windows taskbar", True)
    prevent_screenshots = parse_toggle(body, "Prevent screenshots and screen capture", False)
    website_drag_drop = parse_toggle(body, "Website file drag-and-drop", True)
    app_theme = parse_theme(body)
    custom_titlebar = not show_titlebar

    if start_maximized and start_fullscreen:
        fail("Start maximized and Start in fullscreen cannot both be enabled.")
    if start_maximized and (not allow_maximize or not allow_resize):
        fail("Start maximized requires both Maximize button and Resize window to be enabled.")
    if not allow_resize:
        allow_maximize = False

    icon_url = extract_icon_url(read_field(body, "Application icon (optional)"))
    image = download_icon(icon_url) if icon_url else make_default_icon()
    write_icons(image)

    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Could not read the Tauri configuration: {exc}")

    issue_number = os.environ.get("ISSUE_NUMBER", "0")
    if not issue_number.isdigit():
        fail("Invalid issue number.")

    config["productName"] = app_name
    config["identifier"] = f"com.demonariya.webtoexe.request{issue_number}"
    config.setdefault("app", {})
    windows = config["app"].setdefault("windows", [{}])
    if not windows:
        windows.append({})
    window = windows[0]
    window.update(
        {
            "title": app_name,
            "url": website_url,
            "width": width,
            "height": height,
            "minWidth": min(600, width),
            "minHeight": min(400, height),
            "center": True,
            "resizable": allow_resize,
            "maximizable": allow_maximize,
            "minimizable": allow_minimize,
            "decorations": show_titlebar,
            "maximized": start_maximized,
            "fullscreen": start_fullscreen,
            "alwaysOnTop": always_on_top,
            "zoomHotkeysEnabled": zoom_shortcuts,
            "skipTaskbar": not show_in_taskbar,
            "contentProtected": prevent_screenshots,
            # Tauri's internal drag/drop handler must be disabled on Windows
            # so the website can receive native HTML5 drag-and-drop events.
            "dragDropEnabled": not website_drag_drop,
        }
    )
    if app_theme == "System":
        window.pop("theme", None)
    else:
        window["theme"] = app_theme

    # Expose only window-control APIs for the requested website origin.
    config["app"]["withGlobalTauri"] = custom_titlebar

    app_name_base64 = base64.b64encode(app_name.encode("utf-8")).decode("ascii")
    icon_base64 = base64.b64encode((ICON_DIR / "titlebar.png").read_bytes()).decode("ascii")
    options_path = ROOT / "src-tauri" / "src" / "build_options.rs"
    options_path.write_text(
        "\n".join(
            [
                "// Generated per build by scripts/prepare_build.py.",
                f"pub const DISABLE_CONTEXT_MENU: bool = {str(disable_context_menu).lower()};",
                f"pub const CUSTOM_TITLEBAR_ENABLED: bool = {str(custom_titlebar).lower()};",
                f"pub const SHOW_MINIMIZE_BUTTON: bool = {str(allow_minimize).lower()};",
                f"pub const SHOW_MAXIMIZE_BUTTON: bool = {str(allow_maximize).lower()};",
                f'pub const APP_NAME_BASE64: &str = "{app_name_base64}";',
                f'pub const APP_ICON_BASE64: &str = "{icon_base64}";',
                "",
            ]
        ),
        encoding="utf-8",
    )

    if custom_titlebar:
        CAPABILITY_DIR.mkdir(parents=True, exist_ok=True)
        capability = {
            "$schema": "../gen/schemas/desktop-schema.json",
            "identifier": "main-capability",
            "description": "Window-control permissions for the requested website's custom title bar.",
            "windows": ["main"],
            "remote": {
                "urls": [
                    f"https://{website_host}",
                    f"https://*.{website_host}",
                ]
            },
            "permissions": [
                "core:window:default",
                "core:window:allow-close",
                "core:window:allow-start-dragging",
            ],
        }
        if allow_minimize:
            capability["permissions"].append("core:window:allow-minimize")
        if allow_maximize:
            capability["permissions"].append("core:window:allow-toggle-maximize")
        CAPABILITY_PATH.write_text(
            json.dumps(capability, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        CAPABILITY_PATH.unlink(missing_ok=True)


    config.setdefault("bundle", {})
    config["bundle"]["active"] = True
    config["bundle"]["targets"] = ["nsis", "msi"]
    config["bundle"]["icon"] = ["icons/icon.png", "icons/icon.ico"]

    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8", newline="\n") as output:
            output.write(f"app_name={app_name}\n")
            output.write(f"website_url={website_url}\n")
            output.write(f"website_host={website_host}\n")

    print(f"Prepared Windows app: {app_name}")
    print(f"Website: {website_url}")
    print(f"Window: {width}x{height}")
    print(f"Custom icon: {'yes' if icon_url else 'no (generated default)'}")
    print(f"Custom title bar: {'enabled' if custom_titlebar else 'disabled (native title bar)'}")
    if custom_titlebar:
        print(f"Custom title bar permissions restricted to: {website_host} and its subdomains")
    print(
        "Window options: "
        f"resizable={allow_resize}, maximizable={allow_maximize}, "
        f"minimizable={allow_minimize}, titlebar={show_titlebar}, "
        f"context_menu={'enabled' if not disable_context_menu else 'disabled'}, "
        f"fullscreen={start_fullscreen}, maximized={start_maximized}, "
        f"always_on_top={always_on_top}, theme={app_theme}"
    )


if __name__ == "__main__":
    main()
