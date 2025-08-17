# Changelog

All notable changes to the Finance Assistant Home Assistant Integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.13] - 2025-08-16

### Fixed

- **Calendar Platform Caching**: Resolved calendar platform caching issues to ensure latest files are loaded
- **Integration File Updates**: Ensured all platform files are properly updated and recognized by Home Assistant
- **Platform Registration**: Final fix for calendar platform registration and entity creation
- **File Synchronization**: Guaranteed latest calendar.py implementation is loaded by Home Assistant

## [1.1.12] - 2025-08-16

### Fixed

- **Calendar Platform Loading**: Resolved calendar platform import issues that were preventing platform registration
- **Integration Stability**: Improved overall integration setup reliability and error handling
- **Platform Setup**: Enhanced platform setup process to ensure all platforms load correctly
- **Code Consistency**: Ensured all platform files have proper structure and function definitions

## [1.1.11] - 2025-08-16

### Fixed

- **Calendar Platform Errors**: Fixed missing async_setup_entry function and removed references to old query structure
- **Calendar Setup**: Simplified calendar implementation to work without complex query dependencies
- **Platform Registration**: Resolved calendar platform registration errors that were preventing entities from loading
- **Code Cleanup**: Removed unused methods and simplified calendar entity implementation

## [1.1.10] - 2025-08-16

### Fixed

- **Entity Recognition**: Fixed sensor and calendar entities not being recognized after integration setup
- **Coordinator Access**: Corrected coordinator access path in sensor.py and calendar.py
- **API Endpoint Dependencies**: Removed dependency on non-existent API endpoints (queries, dashboard, calendars)
- **Platform Setup**: Simplified sensor and calendar setup to work with available data

## [1.1.9] - 2025-08-16

### Fixed

- **Missing Constants Error**: Fixed "cannot import name 'ATTR_QUERY_ID' from 'custom_components.finance_assistant.const'" error
- **Integration Setup**: Added missing query attributes and device info constants to const.py
- **Sensor Setup**: Resolved sensor and calendar import errors by providing required constants

## [1.1.8] - 2025-08-16

### Fixed

- **Platform Setup Error**: Fixed "'ConfigEntries' object has no attribute 'async_forward_entry_setup'" error
- **Integration Setup**: Corrected platform setup to use standard Home Assistant mechanism
- **Platform Registration**: Use async_forward_entry_setups with PLATFORMS constant for proper platform registration

## [1.1.7] - 2025-08-16

### Fixed

- **Coordinator Data Property Error**: Fixed "property 'data' of 'FinanceAssistantCoordinator' object has no setter" error
- **Property Conflict**: Removed custom data property that was conflicting with DataUpdateCoordinator base class
- **Integration Setup**: Resolved integration setup failure by using base class data handling mechanism

## [1.1.6] - 2025-08-16

### Fixed

- **Coordinator Method Error**: Fixed "async_config_entry_first_refresh" method call that doesn't exist on DataUpdateCoordinator
- **Integration Setup**: Corrected coordinator initialization to use proper async_refresh() method
- **Setup Flow**: Resolved integration setup failure by fixing coordinator method calls

## [1.1.5] - 2025-08-16

### Fixed

- **Coordinator Property Error**: Fixed "property 'data' of 'FinanceAssistantCoordinator' object has no setter" error
- **Backward Compatibility**: Added missing data structures (queries, dashboard, calendars) for old sensor/calendar compatibility
- **Integration Setup**: Resolved integration setup failure by providing proper coordinator data structure
- **API Client Methods**: Added missing methods for backward compatibility with existing components

## [1.1.4] - 2025-08-16

### Fixed

- **API Health Endpoint**: Added missing `/api/health/` endpoint to Django backend for connection validation
- **Config Flow Connection**: Resolved "Failed to connect" error by implementing proper health check endpoint
- **Backend Integration**: Added health check view and URL routing for Home Assistant integration

## [1.1.3] - 2025-08-16

### Fixed

- **Import Compatibility**: Fixed `homeassistant.data_flow` import error for older Home Assistant versions
- **Backward Compatibility**: Changed import to `homeassistant.data_entry_flow` for broader version support

## [1.1.2] - 2025-08-16

### Fixed

- **Config Flow Registration**: Added missing config flow registration in **init**.py
- **Integration Setup**: Added missing async_setup function for proper integration initialization
- **Handler Resolution**: Fixed "Invalid handler specified" error by properly importing config_flow module

## [1.1.1] - 2025-08-16

### Fixed

- **Config Flow Issue**: Resolved "Invalid handler specified" error
- **Integration Name**: Restored proper name "Finance Assistant" (removed "Enhanced" suffix)
- **Configuration Loading**: Fixed configuration flow loading issues

## [1.1.0] - 2025-08-16

### Added

- **8 New Analytics Sensors** for comprehensive financial monitoring:
  - `Transaction Status Analytics` - Transaction counts by status (real, uncleared, unapproved, scheduled)
  - `Spending Trends` - Overall financial health and trend analysis
  - `Obligation Ratio` - Recurring obligations analysis with status indicators
  - `Financial Insights` - Recommendations and alerts with insight status
  - `Cash Flow Trend` - Cash flow direction (Improving/Stable/Declining) with numeric automation values
  - `Expense Trend` - Expense pattern analysis with trend descriptions
  - `Savings Trend` - Savings pattern analysis with automation triggers
  - `High Risk Items` - Risk assessment and mitigation strategies
- **Enhanced Calendar Integration** - New calendar functionality for financial events
- **Improved API Client** - Better error handling and API integration
- **Enhanced Configuration Flow** - Better setup experience and validation
- **Quality Scale Platinum** - Improved code quality and reliability

### Changed

- **Enhanced Coordinator** - Major improvements to data handling and financial calculations
- **Better Error Handling** - More robust integration with comprehensive error reporting
- **Improved Logging** - Enhanced debugging capabilities with structured logging
- **Enhanced Manifest** - Added supported features and improved metadata

### Technical Improvements

- Added comprehensive financial health scoring algorithms
- Implemented risk assessment calculations
- Enhanced recurring transaction analysis
- Improved cash flow forecasting capabilities
- Better transaction status categorization
- Enhanced sensor attributes for automation triggers

## [1.0.21] - 2025-08-07

### Fixed

- Remove redundant "(Required)" text from API key field label
- Keep asterisk (\*) to indicate required field

## [1.0.20] - 2025-08-07

### Fixed

- Fix 500 Internal Server Error in config flow by reverting to simple schema
- Keep API key as required field but use standard Home Assistant schema format
- Remove complex schema structure that was causing server errors

## [1.0.19] - 2025-08-07

### Changed

- Completely reworked config flow schema to force API key as required
- Added translations to explicitly mark API key as required
- Added clear description that API key is required for authentication
- Force reload of config flow schema by clearing cache

## [1.0.18] - 2025-08-07

### Fixed

- Force config flow UI update by bumping VERSION to 2
- Add explicit API key validation in config flow
- Add description to API key field for clarity
- Ensure API key field is properly marked as required

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
