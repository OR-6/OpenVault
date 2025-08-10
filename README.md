# OpenVault

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/OR-6/OpenVault/releases)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/OR-6/OpenVault/graphs/commit-activity)

A secure, open-source password manager, 2FA generator, secure notes app, and file locker built with Python.  
OpenVault combines strong encryption with an intuitive command-line interface to protect your sensitive data locally.

## Features

- **Password Management**: Store and organize passwords with custom categories
- **Two-Factor Authentication**: Generate TOTP codes with QR code import (image or webcam)
- **Secure File Storage**: Encrypt and store sensitive files locally
- **Encrypted Notes**: Create and manage secure text notes
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Zero-Knowledge Architecture**: All encryption and decryption happens locally

## Security

OpenVault uses modern, proven cryptographic methods:

- **AES-128 (via Fernet)**: All vault data and files are encrypted using Fernet (AES in CBC mode with HMAC authentication)
- **PBKDF2 Key Derivation**: Protects the master password using a salt and many iterations
- **Zero-Knowledge**: No data leaves your device; no remote storage
- **Clipboard Auto-Clear**: Copies expire automatically after a configurable timeout
- **Local Storage Only**: Your data stays in your local filesystem

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### From Source

```bash
git clone https://github.com/OR-6/OpenVault.git
cd OpenVault
pip install -r requirements.txt
python main.py
```

### Dependencies

Required packages:

* `cryptography` — encryption and key handling
* `pyotp` — time-based one-time password generation
* `qrcode` — QR code creation for 2FA backups
* `rich` — styled command-line interface
* `pillow` — image handling for QR decoding

Optional (for advanced QR scanning features):

* `opencv-python` — webcam QR scanning
* `pyzbar` — QR code decoding

## Quick Start

1. **First Run**: Launch OpenVault and set your master password:

   ```bash
   python main.py
   ```
2. **Add a Password**: Password Manager → Add Password
3. **Set Up 2FA**: 2FA Authenticator → Add 2FA → Scan QR or enter secret
4. **Store Files**: Secure File Locker → Upload File
5. **Create Notes**: Secure Notes → Add Note

## Usage

### Password Manager

* Add, view, edit, and delete entries
* Category-based organization
* Optional password generator
* Clipboard auto-clear for sensitive fields

### 2FA Authenticator

* Import from QR (webcam or image file)
* Manual secret key entry
* Automatic detection of algorithm, digits, and period from otpauth URIs
* Real-time code generation with expiry countdown
* Export 2FA secrets as QR for backup

### Secure File Locker

* Encrypt and store any file type
* Organized by category
* Decrypt to a chosen location
* Option to open decrypted files immediately

### Secure Notes

* Create encrypted text notes
* Category organization
* View, edit, and delete notes

## Configuration

Vault data is stored locally:

* **Linux/macOS**: `~/.config/openvault/`
* **Windows**: `%APPDATA%\openvault\`

Key files:

* `vault.enc` — Encrypted vault database
* `config.json` — App settings
* `locker/` — Encrypted file storage

## Contributing

Pull requests are welcome. To contribute:

1. Fork the repository
2. Create a feature branch:
   `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests:
   `python -m pytest`
5. Open a pull request

## Reporting Issues

Please use GitHub Issues. Include:

* Python version
* OS
* Steps to reproduce
* Expected vs. actual results

## Security Tips

* Use a strong, unique master password
* Backup your vault file securely
* Keep your OpenVault installation up-to-date
* Consider full-disk encryption for added protection

## License

MIT License — see [LICENSE](LICENSE) for details.

## Disclaimer

While OpenVault uses strong encryption, no software can guarantee absolute security.
Use at your own risk and maintain secure backups.

## Author

**OR-6**

* GitHub: [@OR-6](https://github.com/OR-6)
* Repository: [OpenVault](https://github.com/OR-6/OpenVault)

## Support

1. Read the [documentation](https://github.com/OR-6/OpenVault/wiki)
2. Search [issues](https://github.com/OR-6/OpenVault/issues)
3. Open a new issue if needed

---

**⭐ Star this repo if you find it useful!**