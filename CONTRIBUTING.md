# Contributing

Thanks for helping improve WebToExe.

## Before opening a pull request

1. Keep the public request flow simple and accessible.
2. Validate all request data before using it in Tauri configuration.
3. Treat issue bodies, uploaded files, and URLs as untrusted input.
4. Never execute user-provided source code, scripts, shell commands, or workflow files.
5. Do not add repository secrets or credentials to generated apps.
6. Keep generated app builds isolated by issue number and release tag.

## Development

The desktop shell is a minimal Rust + Tauri 2 project. The build workflow runs on Windows and creates NSIS and MSI installers.

For workflow changes, verify the issue-form labels and the Markdown headings parsed by scripts/prepare_build.py remain in sync.

## Pull requests

Describe the problem, the change, and how it was tested. Include relevant workflow logs for build-pipeline changes.
