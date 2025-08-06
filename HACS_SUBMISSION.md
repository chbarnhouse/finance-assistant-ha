# HACS Submission Documentation

## Repository Information

- **Repository**: `https://github.com/chbarnhouse/finance-assistant-ha`
- **Name**: Finance Assistant
- **Description**: Home Assistant integration for Finance Assistant - a comprehensive financial management system
- **Category**: Integration
- **Home Assistant Version**: 2023.8.0+
- **Python Version**: 3.9+

## Features

### Core Functionality
- **Custom Sensors**: Create sensors from Finance Assistant queries
- **Custom Calendars**: Create calendar entities from Finance Assistant queries
- **Real-time Updates**: Automatic data refresh with configurable intervals
- **API Authentication**: Secure API key-based authentication
- **Config Flow**: User-friendly setup and configuration

### Integration Capabilities
- **Query-based Entities**: Each Finance Assistant query becomes a Home Assistant entity
- **Sensor Platform**: Supports financial calculations and metrics
- **Calendar Platform**: Supports financial events and reminders
- **Data Coordinator**: Efficient real-time data management
- **Error Handling**: Comprehensive error handling and logging

## Technical Details

### Dependencies
- `aiohttp` - For async HTTP requests
- `voluptuous` - For configuration validation

### Platforms Supported
- `sensor` - For financial data sensors
- `calendar` - For financial event calendars

### Configuration Options
- `host` - Finance Assistant service hostname/IP
- `port` - Service port (default: 8080)
- `api_key` - API key for authentication
- `ssl` - Use HTTPS (default: false)
- `scan_interval` - Data refresh interval in seconds (default: 300)

### API Endpoints Used
- `GET /api/ha/queries/` - List available queries
- `GET /api/ha/sensor/{query_id}/` - Get sensor data
- `GET /api/ha/calendar/{query_id}/` - Get calendar data

## Installation

### HACS Installation (Recommended)
1. Install HACS in Home Assistant
2. Add custom repository: `https://github.com/chbarnhouse/finance-assistant-ha`
3. Install the integration
4. Configure via Home Assistant UI

### Manual Installation
1. Download the integration files
2. Copy to `config/custom_components/finance_assistant/`
3. Restart Home Assistant
4. Configure via Home Assistant UI

## Usage

### Prerequisites
1. Running Finance Assistant service (standalone deployment)
2. API key from Finance Assistant service
3. Network connectivity between Home Assistant and Finance Assistant

### Setup Process
1. Add integration via Home Assistant UI
2. Enter Finance Assistant service details
3. Provide API key for authentication
4. Configure scan interval
5. Save configuration

### Creating Entities
1. Create queries in Finance Assistant web interface
2. Set output type to "Sensor" or "Calendar"
3. Configure query parameters and filters
4. Save query
5. Entities automatically appear in Home Assistant

## Validation

### GitHub Actions
- Automated validation on push and pull requests
- HACS validation workflow
- Release workflow for versioned releases

### Testing
- API connection validation
- Configuration flow testing
- Entity creation and updates
- Error handling verification

## Compliance

### HACS Requirements
- ✅ Config flow implementation
- ✅ Translation support
- ✅ Proper manifest.json
- ✅ GitHub Actions validation
- ✅ Documentation
- ✅ License (MIT)

### Home Assistant Standards
- ✅ Async/await patterns
- ✅ Proper error handling
- ✅ Type hints
- ✅ Logging
- ✅ Entity attributes
- ✅ Device info

## Repository Structure

```
finance-assistant-ha/
├── custom_components/
│   └── finance_assistant/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── calendar.py
│       ├── const.py
│       └── translations/
│           └── en.json
├── .github/
│   └── workflows/
│       ├── validate.yml
│       └── release.yml
├── hacs.json
├── README.md
├── LICENSE
└── .gitignore
```

## Support

### Documentation
- Comprehensive README with installation and usage instructions
- Troubleshooting guide
- API endpoint documentation

### Issues
- GitHub Issues enabled for bug reports and feature requests
- Clear issue templates
- Responsive maintenance

### Community
- Active development and maintenance
- Regular updates and improvements
- Community feedback integration

## Version History

- **v0.14.63** - Initial release with sensor and calendar support

## License

MIT License - See LICENSE file for details.

## Author

Charlie Barnhouse - https://github.com/chbarnhouse

## Related Projects

- **Finance Assistant**: https://github.com/chbarnhouse/finance-assistant
- **Finance Assistant Addon**: https://github.com/chbarnhouse/ha-addons 