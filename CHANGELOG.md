# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [v1.0.0-beta.0] - 2025-08-09
### Added
- **Advanced UI** overhaul:
  - Rich-based banners, panels, colored menus, and formatted tables.
  - About section in main menu with project details.
- **2FA Enhancements**:
  - QR code import from image files.
  - QR code scanning via webcam (OpenCV + pyzbar).
  - `otpauth://` URI parsing with auto-detection of algorithm, digits, and period.
  - Live OTP display with color-coded countdown.
  - Export existing 2FA entries as QR codes.
- **Password Manager**:
  - View, edit, delete, and copy password entries.
  - Category filtering in views.
- **Secure File Locker**:
  - Fixed file dialog not opening on some platforms.
  - Fallback to manual path input if file dialog is unavailable.
  - Decrypt & open files directly from the app.
- **Secure Notes**:
  - View, edit, and delete encrypted notes.
  - Category support for better organization.
- Clipboard auto-clear feature after copying sensitive values.

### Changed
- Modularized application into separate scripts for better maintainability.
- Replaced dynamic `__import__` usage with explicit module imports.
- Simplified menu navigation for non-technical users while keeping advanced features.
- Improved file encryption/decryption progress reporting.

### Fixed
- File upload dialog failing to appear on some systems.
- AttributeError when passing `ui` incorrectly to feature modules.
- Minor display and formatting issues in older menus.

---

[v1.0.0-beta.0]: https://github.com/OR-6/OpenVault/releases/tag/v1.0.0-beta.0
