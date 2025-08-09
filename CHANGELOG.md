# Changelog

All notable changes to OpenVault will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-10

### Added

#### Core Features
- Password manager with category organization and secure storage
- Two-factor authentication (TOTP) generator with QR code import support
- Secure file locker with AES-256 Fernet encryption
- Encrypted notes system with category management
- Master password protection with PBKDF2 key derivation

#### Security Features
- Zero-knowledge architecture with local-only data storage
- AES-256 encryption for all vault data using Fernet symmetric encryption
- Secure key derivation using PBKDF2 with salt
- Automatic clipboard clearing with configurable timeout (default: 15 seconds)
- Secure temporary file handling and cleanup

#### User Interface
- Rich terminal-based user interface with color coding and formatting
- Interactive menu system with keyboard navigation
- Real-time feedback and status messages
- Progress indicators for long-running operations
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
- Real-time code generation with countdown timers
- Backup and recovery options

#### File Security
- Encrypt and store files of any type and size
- Organized storage with metadata tracking
- File integrity verification
- Secure deletion of temporary files
- Support for nested directory structures

#### Notes System
- Create and manage encrypted text notes
- Category-based organization
- Rich text editing capabilities
- Search functionality across all notes
- Export options for backup purposes

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
- Extensible plugin architecture for future enhancements

### Dependencies
- `cryptography` ^41.0.0 - Encryption and cryptographic operations
- `pyotp` ^2.9.0 - Time-based one-time password generation
- `qrcode[pil]` ^7.4.2 - QR code generation and processing
- `rich` ^13.7.0 - Enhanced terminal user interface
- `pillow` ^10.0.0 - Image processing for QR code handling

### Known Issues
- File upload functionality may not work on systems with strict filesystem permissions
- QR code scanning via webcam may fail on systems with camera access restrictions or missing video codecs
- Some antivirus software may flag encrypted vault files as suspicious (false positive)

### Security Notes
- All cryptographic operations use industry-standard implementations
- No network communication - completely offline operation
- Vault data is encrypted at rest using strong encryption standards
- Master password is never stored in plaintext

---

## Release Information

### Versioning Strategy
This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Release Types
- **Major Release** (x.0.0): Breaking changes, major new features
- **Minor Release** (x.y.0): New features, backwards compatible
- **Patch Release** (x.y.z): Bug fixes, security updates

### Support Policy
- Latest major version receives full support
- Previous major version receives security updates for 6 months
- Critical security issues will be backported when feasible

### Upgrade Notes
For future releases, upgrade instructions and breaking changes will be documented here.

---

[1.0.0]: https://github.com/OR-6/OpenVault/releases/tag/v1.0.0
