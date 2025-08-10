# Changelog

All notable changes to OpenVault will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-10

### Added

#### Core Features
- Password manager with category organization and secure storage
- Two-factor authentication (TOTP) generator with QR code import support
- Secure file locker with Fernet (AES-128-CBC + HMAC) encryption
- Encrypted notes system with category management
- Master password protection with PBKDF2 key derivation

#### Security Features
- Zero-knowledge architecture with local-only data storage
- Vault encryption using Fernet symmetric encryption (AES-128-CBC with HMAC)
- Secure key derivation using PBKDF2 with salt
- Automatic clipboard clearing with configurable timeout (default: 15 seconds)
- Secure temporary file handling and cleanup

#### User Interface
- Rich terminal-based user interface with color coding and formatting
- Interactive menu system with number-based selection
- Real-time feedback and status messages
- Progress indicators for encryption/decryption
- First-time setup wizard for vault initialization

#### Password Management
- Add, view, edit, and delete password entries
- Category-based organization system
- Secure password generation with customizable parameters
- Search and filter functionality
- Automatic clipboard integration with security timeout

#### Two-Factor Authentication
- TOTP code generation following RFC 6238 standard
- QR code import via webcam scanning
- QR code import from image files
- Manual secret key entry support
- Automatic detection of algorithm, digits, and period from otpauth URIs
- Real-time code generation with countdown timers
- Export 2FA secrets as QR codes for backup

#### File Security
- Encrypt and store files of any type and size
- Organized storage with metadata tracking
- Optional opening of decrypted files immediately after extraction
- Secure deletion of temporary files

#### Notes System
- Create and manage encrypted text notes
- Category-based organization
- Search functionality across all notes

#### Cross-Platform Support
- Windows compatibility with proper path handling
- macOS support with native directory conventions
- Linux compatibility with XDG base directory specification
- Automatic configuration directory creation

### Technical Implementation
- Modular architecture with separation of concerns
- Comprehensive error handling and user feedback
- Memory-safe operations with automatic cleanup
- Configuration management with sensible defaults
- Easily extensible for future enhancements

### Dependencies
- `cryptography` ^41.0.0 - Encryption and cryptographic operations
- `pyotp` ^2.9.0 - Time-based one-time password generation
- `qrcode[pil]` ^7.4.2 - QR code generation
- `rich` ^13.7.0 - Enhanced terminal user interface
- `pillow` ^10.0.0 - Image processing for QR code handling
- *(Optional)* `opencv-python` - Webcam QR scanning
- *(Optional)* `pyzbar` - QR code decoding

### Known Issues
- File upload dialog may not open on some systems without GUI libraries
- QR code scanning via webcam may fail on systems with camera access restrictions or missing codecs
- Some antivirus software may flag encrypted vault files as suspicious (false positive)

### Security Notes
- All cryptographic operations use industry-standard implementations
- No network communication — completely offline operation
- Vault data is encrypted at rest using strong encryption standards
- Master password is never stored in plaintext

---

## Release Information

### Versioning Strategy
This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible changes
- **MINOR** version for backwards-compatible feature additions
- **PATCH** version for backwards-compatible bug fixes

### Release Types
- **Major Release** (x.0.0): Breaking changes, major new features
- **Minor Release** (x.y.0): New features, backwards compatible
- **Patch Release** (x.y.z): Bug fixes, security updates

### Support Policy
- Latest major version receives full support
- Previous major version receives security updates for 6 months
- Critical security issues may be backported when feasible

### Upgrade Notes
Future releases will include upgrade instructions and note any breaking changes here.

---

[1.0.0]: https://github.com/OR-6/OpenVault/releases/tag/v1.0.0
