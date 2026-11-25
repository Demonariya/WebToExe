# Security Policy

## Reporting a vulnerability

Please do not publish exploit details, access tokens, credentials, or private user data in a public issue.

Use GitHub's private vulnerability reporting feature for this repository when available. Otherwise, contact the repository owner privately through GitHub.

## Scope

Security-sensitive areas include:

- Issue-form parsing and input validation.
- Icon upload and image processing.
- GitHub Actions permissions and release publication.
- Tauri external-URL and WebView configuration.

## Design rules

- Issue content is untrusted data.
- User input must never be interpolated into executable shell code.
- Build workflows must execute only code checked out from this repository.
- Do not expose repository secrets to untrusted code.
- Validate URL schemes, hosts, image types, and file sizes.
