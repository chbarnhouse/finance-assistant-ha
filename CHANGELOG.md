# Changelog

All notable changes to the Finance Assistant Home Assistant Integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.17] - 2025-08-07

### Fixed

- Fix UI caching issue where API key field still showed as "Optional"
- Ensure API key validation is properly enforced in coordinator
- Add debug logging for API key configuration

## [1.0.16] - 2025-08-07

### Changed

- **BREAKING**: API key is now required for all connections
- Enhanced security by enforcing authentication for all API requests
- Updated configuration flow to require API key field

### Fixed

- Fix configuration schema mismatch by making API key required in CONFIG_SCHEMA
- Resolve "Invalid config" errors caused by schema validation conflicts

## [1.0.6] - 2025-08-07

### Fixed

- Fix configuration schema mismatch by making API key optional in CONFIG_SCHEMA
- Resolve "Invalid config" errors caused by schema validation conflicts

## [1.0.5] - 2025-08-07

### Fixed

- Force Home Assistant to detect new version by incrementing to 1.0.5
- Resolve persistent caching issue with integration version display

## [1.0.4] - 2025-08-07

### Fixed

- Force HACS version detection with proper GitHub release
- Integration now properly displays semantic versioning

## [1.0.3] - 2025-08-07

### Fixed

- Enhanced version detection with version.py and hacs.json configuration

## [1.0.2] - 2025-08-07

### Fixed

- Force HACS to recognize semantic versioning by creating fresh commit

## [1.0.1] - 2025-08-07

### Fixed

- Version detection issue in Home Assistant - now properly shows semantic versioning

## [1.0.0] - 2025-08-07

### Added

- Initial stable release with proper semantic versioning
- Support for custom financial sensors and calendars
- Real-time data updates with configurable intervals
- Query-based entity creation from Finance Assistant

### Changed

- Switched from development versioning (0.14.x) to semantic versioning (1.0.0)
- Fixed field mapping from `output_type` to `query_type` in API responses
- Updated configuration flow to require API key for security

### Fixed

- Authentication issues that prevented connection to Finance Assistant service
- Field mapping errors in coordinator that caused connection failures
- Configuration validation errors in Home Assistant

## [0.14.64] - 2025-08-07

### Fixed

- Authentication and query_type field mapping issues
- Connection validation in coordinator

## [0.14.63] - 2025-08-07

### Added

- Initial release with sensor and calendar support
- Basic integration framework
- API endpoint integration with Finance Assistant service

---

## Versioning

This project now follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Migration from Development Versions

- **0.14.x** → **1.0.0**: Major version bump to indicate stable release
- All previous development versions are considered pre-release
- Version 1.0.0 represents the first stable, production-ready release
