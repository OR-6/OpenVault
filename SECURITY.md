# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

Only the latest stable and beta releases of **OpenVault** receive security updates. Older versions should be upgraded immediately.

---

## Reporting a Vulnerability

If you believe you have found a security vulnerability in **OpenVault**:

1. **Do not** open a public issue.
2. Contact the project maintainer directly via:
   - **GitHub Security Advisories**: [Create private report](https://github.com/OR-6/OpenVault/security/advisories/new)
3. Provide:
   - A detailed description of the issue
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
4. Please allow up to **7 days** for acknowledgement.

---

## Disclosure Policy

- We follow a **coordinated disclosure** approach.
- Vulnerabilities will be addressed in private until a fix is ready.
- A public advisory will be published once the fix is released.
- Credit will be given to the reporter if desired.

---

## Security Principles

OpenVault is designed with the following principles:

- **Local-first**: No cloud storage, no remote servers — all data stays on the user’s machine.
- **Strong encryption**: All vault data is encrypted with a key derived from your master password using industry-standard algorithms.
- **Minimal attack surface**: No background services or open network ports.
- **No master password recovery**: To ensure data confidentiality, there is no password reset feature.

---

## Additional Security Recommendations

- Keep your system and Python environment up to date.
- Use a **strong, unique master password**.
- Regularly back up your encrypted vault file to a secure offline location.
- Avoid running OpenVault on untrusted machines.
- Ensure your temporary files directory is secure and cleared after use.

---

_Last updated: 2025-08-14_
