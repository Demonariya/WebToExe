<div align="center">

# WebToExe

### Any website. Your own Windows desktop app.

**Turn any public HTTPS website into a standalone Windows EXE — with one request.**

[![Build](https://img.shields.io/github/actions/workflow/status/Demonariya/WebToExe/build-from-issue.yml?branch=main&label=Build%20pipeline)](https://github.com/Demonariya/WebToExe/actions/workflows/build-from-issue.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4.svg)](#)
[![Rust + Tauri](https://img.shields.io/badge/Powered%20by-Rust%20%2B%20Tauri-DEA584.svg)](https://v2.tauri.app/)

[**Request your EXE**](https://github.com/Demonariya/WebToExe/issues/new?template=build-request.yml) · [Build history](https://github.com/Demonariya/WebToExe/releases) · [Report a problem](https://github.com/Demonariya/WebToExe/issues)

</div>

---

## What is WebToExe?

WebToExe is a public, GitHub-powered website-to-desktop builder. Submit a website and a few app settings through the request form. GitHub Actions builds a dedicated Windows desktop wrapper and publishes the result as a downloadable GitHub Release.

No Rust setup, IDE, or local compilation is needed for people requesting an app.

> **One request = one independent app build.** WebToExe does not combine websites into a multi-site browser.

## The workflow

| Step | What happens |
|---|---|
| **01 — Submit** | Open the build request form and enter an HTTPS website address. |
| **02 — Configure** | Choose an app name, window dimensions, and optionally upload an icon. |
| **03 — Build** | A Windows runner validates the request and compiles a Tauri 2 application. |
| **04 — Download** | The request receives a link to its own GitHub Release containing the Windows installer. |

## Request a Windows app

<div align="center">

### Create your build request

[![Open build request](https://img.shields.io/badge/OPEN%20BUILD%20REQUEST-Submit%20a%20website-2563EB?style=for-the-badge)](https://github.com/Demonariya/WebToExe/issues/new?template=build-request.yml)

</div>

Fill in the form:

- **Website URL:** The full address, including HTTPS.
- **Application name:** The name shown in the app window and installer.
- **Window size:** Optional width and height; sensible defaults are provided.
- **Application icon:** Optional PNG, JPG, JPEG, WEBP, or GIF file. Click Browse or drag the image directly into the upload field.
- **Window and behavior options:** Choose right-click menu, maximize, resize, minimize, title bar, startup mode, always-on-top, page zoom, taskbar visibility, screen-capture protection, HTML5 drag-and-drop, and theme.

After submitting, follow the Actions run linked in the issue. When the build succeeds, the bot posts the download link in that issue.

## What gets built?

- A dedicated Windows x64 desktop application.
- An **EXE installer** (NSIS).
- An **MSI installer** (Windows Installer).
- Your app name, website address, window dimensions, and optional icon.
- A separate release for each request.

The generated app loads the submitted website in a native WebView powered by Tauri 2.

## App options

Every build request can customize the generated Windows app:

| Option | What it controls |
|---|---|
| Right-click context menu | Enable or suppress the website's context menu. |
| Maximize button | Enable or disable the maximize/restore control in the native or custom title bar. |
| Resize window | Allow or prevent resizing the app window. Turning this off also disables maximizing. |
| Minimize button | Enable or disable the minimize control in the native or custom title bar. |
| Native title bar and borders | Keep the standard Windows frame, or replace it with a custom title bar showing the app icon, app name, and window controls. |
| Start maximized / fullscreen | Choose the app's initial window state. These modes are mutually exclusive. |
| Always on top | Keep the app above other windows. |
| Page zoom shortcuts | Enable or disable Ctrl+Plus, Ctrl+Minus, and Ctrl+0. |
| Show in Windows taskbar | Control whether the app appears in the taskbar. |
| Prevent screenshots and screen capture | Ask Windows to exclude the window from supported capture APIs. This is not a universal anti-recording guarantee. |
| Website file drag-and-drop | Preserve HTML5 drag-and-drop support inside the website, such as dropping files onto upload areas. |
| App and WebView theme | Follow Windows, or start with Light or Dark preference. The website can still override its own colors. |

**Custom title bar:** When the native frame is disabled, WebToExe adds a 40px title bar with the uploaded app icon, app name, minimize, maximize/restore, and close controls. The empty area can drag the window, and double-clicking it toggles maximize/restore. Its surface and text colors are sampled from the website's theme-color metadata, header, and page colors, then refreshed as the site's theme changes. The title bar remains available while the app navigates between HTTPS pages.

The remote website receives only the Tauri window permissions required by these controls (close, minimize, maximize/restore, and dragging). No filesystem, shell, process, or arbitrary native-command permission is granted. Disabling right-click is applied by a WebView document event listener; embedded third-party frames can still implement their own context menus.

## Important limitations

WebToExe creates a desktop wrapper; it does **not** convert a website into an offline application or copy its backend to your computer.

- An internet connection is required to use the website.
- Sign-in, subscriptions, and account permissions remain controlled by the original website.
- Some websites may block embedded browsers or require features that a desktop WebView does not support.
- DRM-protected media, browser extensions, device-bound authentication, and site-specific security restrictions are not guaranteed to work.
- Windows SmartScreen may show a warning because generated installers are not individually code-signed.

## Security and privacy

WebToExe treats every public request as untrusted input.

- Only HTTPS website URLs are accepted.
- Localhost names, reserved local hostnames, and IP-literal website addresses are rejected.
- App names and dimensions are validated before being written into the Tauri configuration.
- Form values are treated as data; they are never executed as shell commands or source code.
- The build workflow runs repository-controlled code. A request cannot upload or execute its own workflow or Rust source.
- Website credentials are never requested. Users sign in directly on the original website.
- The GitHub Actions token is used by the workflow to publish the release and comment on the request; it is not embedded in the generated app.

Do not submit websites that you do not have permission to package or distribute. You are responsible for complying with the website's terms and applicable laws.

## Technology

| Component | Technology |
|---|---|
| Desktop runtime | [Tauri 2](https://v2.tauri.app/) |
| Application core | [Rust](https://www.rust-lang.org/) |
| Website rendering | Microsoft Edge WebView2 |
| Windows packaging | NSIS + MSI |
| Build automation | GitHub Actions |
| Request intake | GitHub Issue Forms |

## Repository layout

- .github/ISSUE_TEMPLATE — public build request form.
- .github/workflows — automated Windows build pipeline.
- src-tauri — minimal Rust and Tauri desktop shell.
- scripts/prepare_build.py — input validation and per-request app configuration.
- web — local fallback page used by the Tauri project.

## Build locally

This repository is designed around GitHub Issue Forms and automated Windows builds. To develop the Tauri shell locally, install Rust, the Tauri CLI, and the Windows prerequisites described in the [Tauri documentation](https://v2.tauri.app/start/prerequisites/).

The request preparation script requires Python 3.11+ and Pillow. It validates the GitHub-hosted image attachment and creates the application icon, writes the request-specific Tauri window configuration, and generates the Rust build option used to suppress the context menu before compilation.

## Contributing

Bug reports, workflow improvements, and pull requests are welcome. Do not add workflows that execute issue text, uploaded scripts, or contributor-controlled source with repository write permissions.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE).

---

<div align="center">

**Built for turning the web into desktop apps.**

</div>
