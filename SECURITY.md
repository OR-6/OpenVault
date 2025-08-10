# Security Policy

## Supported Versions

We take security seriously and provide security updates for the following versions of OpenVault:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

**Note**: As this is the initial release, only version 1.0.x is currently supported. Future versions will follow a rolling support window of the current major version plus one previous major version.

## Security Features

OpenVault implements multiple layers of security to protect your sensitive data:

### Encryption Standards
- **Fernet Encryption (AES-128-CBC + HMAC)**: All vault data encrypted using Fernet (AES in CBC mode with PKCS7 padding and HMAC-SHA256 authentication)
- **Key Derivation**: PBKDF2 with SHA-256, salt, and configurable iterations
- **Cryptographic Library**: Uses Python's `cryptography` library, which follows industry best practices

### Architecture Security
- **Zero-Knowledge Design**: No data transmitted to external servers
- **Local-Only Storage**: All vault data remains on your local filesystem
- **Memory Safety**: Automatic cleanup of sensitive data in memory
- **Secure Temporary Files**: Encrypted temporary files with automatic deletion

### Operational Security
- **Master Password Protection**: Strong password recommendations with entropy validation
- **Clipboard Security**: Automatic clipboard clearing after configurable timeout
- **Session Management**: Vault automatically locks after inactivity
- **Secure Deletion**: Overwriting of temporary files before deletion

## Reporting Security Vulnerabilities

If you discover a security vulnerability in OpenVault, please report it responsibly:

### Preferred Method
Create a private security advisory on GitHub:
1. Go to the [OpenVault repository](https://github.com/OR-6/OpenVault)
2. Navigate to Security → Advisories → New draft security advisory
3. Provide detailed information about the vulnerability

### Alternative Contact
If GitHub security advisories are not available, please contact:
- **Email**: [Create a GitHub issue marked as "Security" - we will provide direct contact]
- **Subject Line**: `[SECURITY] OpenVault Vulnerability Report`

### What to Include

Please provide the following information:
- **Vulnerability Type**: Buffer overflow, injection, cryptographic weakness, etc.
- **Affected Components**: Specific modules or functions affected
- **Attack Vector**: How the vulnerability can be exploited
- **Impact Assessment**: Potential damage or data exposure
- **Proof of Concept**: Steps to reproduce (if safe to share)
- **Suggested Fix**: If you have recommendations for remediation
- **Disclosure Timeline**: Your preferred timeline for public disclosure

### Response Process

1. **Acknowledgment**: We will acknowledge receipt within 48 hours
2. **Initial Assessment**: Vulnerability will be assessed within 5 business days
3. **Investigation**: Detailed analysis and impact assessment
4. **Fix Development**: Security patch development and testing
5. **Coordinated Disclosure**: Public disclosure after fix is available
6. **Credit**: Security researchers will be credited (unless anonymity is requested)

### Security Response Timeline

| Severity | Response Time | Fix Timeline |
|----------|---------------|--------------|
| Critical | 24 hours      | 7 days       |
| High     | 48 hours      | 14 days      |
| Medium   | 5 business days | 30 days    |
| Low      | 10 business days | Next release |

## Security Best Practices for Users

### Master Password Security
- Use a strong, unique master password (minimum 12 characters)
- Include uppercase, lowercase, numbers, and special characters
- Never reuse your master password for other services
- Consider using a passphrase with random words

### System Security
- Keep your operating system updated
- Use full-disk encryption on your device
- Regularly backup your vault file to a secure location
- Use reputable antivirus software

### OpenVault Usage
- Always verify file integrity after updates
- Lock your vault when not in use
- Regularly update to the latest version
- Monitor for unusual application behavior

### Environment Security
- Use OpenVault only on trusted devices
- Avoid using on public or shared computers
- Ensure physical security of devices containing vault data
- Be cautious of screen recording software or remote access tools

## Threat Model

OpenVault is designed to protect against:

### Protected Threats
- **Data Theft**: Encrypted vault prevents unauthorized data access
- **Password Exposure**: Clipboard clearing prevents credential harvesting
- **File Interception**: All files encrypted before storage
- **Brute Force Attacks**: Key derivation makes password cracking computationally expensive

### Limitations
- **Physical Access**: Cannot protect against authorized users with physical device access
- **Malware**: Advanced malware with keylogger capabilities may capture master password
- **Side Channel Attacks**: Not designed to resist advanced cryptographic attacks
- **Quantum Computing**: Current encryption may be vulnerable to future quantum computers

## Security Auditing

### Code Review
- All security-related code changes require multiple reviewer approval
- Regular security-focused code reviews by experienced developers
- Automated security scanning in CI/CD pipeline

### Dependency Management
- Regular updates of cryptographic dependencies
- Monitoring for known vulnerabilities in dependencies
- Use of minimal dependency set to reduce attack surface

### Testing
- Unit tests for all cryptographic operations
- Integration tests for security workflows
- Regular penetration testing (as resources allow)

## Cryptographic Details

### Algorithms Used
- **Symmetric Encryption**: AES-128 in CBC mode with PKCS7 padding (via Fernet)
- **Message Authentication**: HMAC-SHA256
- **Key Derivation**: PBKDF2 with SHA-256, 100,000 iterations minimum
- **Random Number Generation**: OS-provided cryptographically secure random numbers

### Key Management
- Master key derived from password using PBKDF2 with unique salt
- Individual data encryption keys derived from master key
- No keys stored in plaintext
- Automatic key rotation on password change

## Compliance and Standards

OpenVault aims to follow:
- **OWASP Secure Coding Practices**
- **NIST Cybersecurity Framework**
- **Industry standard cryptographic practices**
- **Responsible disclosure guidelines**

## Updates and Notifications

Security updates will be announced through:
- GitHub Security Advisories
- Repository releases with detailed changelog
- README updates for critical security information

## Disclaimer

While OpenVault implements strong security measures, no software is 100% secure. Users should:
- Understand the threat model and limitations
- Implement defense in depth with other security measures
- Keep regular backups of important data
- Stay informed about security best practices

---

**Last Updated**: August 10, 2025  
**Version**: 1.0.0
