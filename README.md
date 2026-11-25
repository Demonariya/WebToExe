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
- **Application icon:** Optional PNG, JPG, or ICO attachment. Drag the file into the icon field.

After submitting, follow the Actions run linked in the issue. When the build succeeds, the bot posts the download link in that issue.

## What gets built?

- A dedicated Windows x64 desktop application.
- An **EXE installer** (NSIS).
- An **MSI installer** (Windows Installer).
- Your app name, website address, window dimensions, and optional icon.
- A separate release for each request.

The generated app loads the submitted website in a native WebView powered by Tauri 2.

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

The request preparation script requires Python 3.11+ and Pillow. It creates the application icon and writes the request-specific Tauri configuration before compilation.

## Contributing

Bug reports, workflow improvements, and pull requests are welcome. Do not add workflows that execute issue text, uploaded scripts, or contributor-controlled source with repository write permissions.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE).

---

<div align="center">

**Built for turning the web into desktop apps.**

</div>
