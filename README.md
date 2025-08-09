# OpenVault

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/OR-6/OpenVault/releases)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/OR-6/OpenVault/graphs/commit-activity)

A secure, open-source password manager, 2FA generator, and secure file locker built with Python. OpenVault provides enterprise-grade security for personal use with an intuitive command-line interface.

## Features

- **Password Management**: Organize and secure passwords with custom categories
- **Two-Factor Authentication**: Generate TOTP codes with QR code import and webcam scanning support
- **Secure File Storage**: Encrypt and store sensitive files using Fernet/AES encryption
- **Encrypted Notes**: Create and manage secure notes with category organization
- **Cross-Platform**: Compatible with Windows, macOS, and Linux
- **Zero-Knowledge Architecture**: All encryption happens locally on your device

## Security

OpenVault implements industry-standard security practices:

- **AES-256 Encryption**: All data encrypted using Fernet (AES-256 in CBC mode)
- **PBKDF2 Key Derivation**: Master password protection with salt and iterations
- **Zero-Knowledge Design**: No data transmitted to external servers
- **Secure Memory Handling**: Automatic clipboard clearing after specified timeout
- **Local Storage Only**: All vault data remains on your local filesystem

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### From Source

```bash
git clone https://github.com/OR-6/OpenVault.git
cd OpenVault
pip install -r requirements.txt
python main.py
```

### Dependencies

The following Python packages are required:

- `cryptography` - Encryption and key derivation
- `pyotp` - Time-based one-time password generation
- `qrcode` - QR code generation and processing
- `rich` - Enhanced terminal UI
- `pillow` - Image processing for QR codes

## Quick Start

1. **First Run**: Launch OpenVault and create your master password
   ```bash
   python main.py
   ```

2. **Add a Password**: Navigate to Password Manager → Add Password

3. **Setup 2FA**: Go to 2FA Authenticator → Add 2FA and scan a QR code

4. **Store Files**: Use Secure File Locker → Upload File to encrypt sensitive documents

5. **Create Notes**: Access Secure Notes → Add Note for encrypted text storage

## Usage

### Password Manager
Store and organize passwords with custom categories. Features include:
- Secure password generation
- Category-based organization
- Quick search and filtering
- Automatic clipboard management

### 2FA Authenticator
Generate time-based authentication codes:
- Import from QR codes via webcam or image files
- Manual secret key entry
- Real-time code generation with countdown timer
- Export backup codes

### Secure File Locker
Encrypt and store sensitive files:
- Drag-and-drop file encryption
- Support for any file type
- Organized storage with metadata
- Secure deletion of temporary files

### Secure Notes
Create encrypted text notes:
- Rich text support
- Category organization
- Full-text search capabilities
- Export to encrypted files

## Configuration

OpenVault stores data in the following locations:

- **Linux/macOS**: `~/.config/openvault/`
- **Windows**: `%APPDATA%\openvault\`

Configuration files:
- `vault.enc` - Encrypted vault database
- `config.json` - Application settings
- `locker/` - Encrypted file storage directory

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `python -m pytest`
5. Submit a pull request

### Reporting Issues

Please use the GitHub issue tracker to report bugs or request features. Include:
- Python version
- Operating system
- Steps to reproduce the issue
- Expected vs actual behavior

## Security Considerations

- Always use a strong, unique master password
- Regularly backup your vault file to a secure location
- Keep the application updated to receive security patches
- Consider using full-disk encryption on your system

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

While OpenVault implements strong encryption and security practices, no software is 100% secure. Use at your own risk and always maintain backups of important data.

## Author

**OR-6**
- GitHub: [@OR-6](https://github.com/OR-6)
- Repository: [OpenVault](https://github.com/OR-6/OpenVault)

## Support

For support, please:
1. Check the [documentation](https://github.com/OR-6/OpenVault/wiki)
2. Search [existing issues](https://github.com/OR-6/OpenVault/issues)
3. Create a new issue if needed

---

**Star this repository if you find it useful!**