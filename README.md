# Finance Assistant Home Assistant Integration

This integration connects Home Assistant to the Finance Assistant standalone service, allowing you to create custom financial sensors and calendars based on your queries.

## Features

- **Custom Sensors**: Create sensors from your Finance Assistant queries
- **Custom Calendars**: Create calendar entities from your Finance Assistant queries
- **Real-time Updates**: Automatic data refresh based on configurable intervals
- **Query-based Entities**: Each query in Finance Assistant becomes a Home Assistant entity

## Installation

### Method 1: Manual Installation (Recommended)

1. Download this integration folder
2. Copy the `finance_assistant` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for "Finance Assistant" and add it

### Method 2: HACS Installation (Recommended)

1. **Install HACS**: If you haven't already, install [HACS](https://hacs.xyz/) in your Home Assistant instance
2. **Add Repository**: In HACS, go to **Integrations** → **+** → **Custom repositories**
3. **Repository**: Add `https://github.com/chbarnhouse/finance-assistant-ha`
4. **Category**: Select **Integration**
5. **Install**: Click **Download** and restart Home Assistant
6. **Configure**: Go to **Settings** → **Devices & Services** → **Add Integration** and search for "Finance Assistant"

## Configuration

### Prerequisites

1. **Finance Assistant Service**: You need a running Finance Assistant service (standalone deployment)
2. **Network Access**: Home Assistant must be able to reach your Finance Assistant service

### Setup Steps

1. **Add Integration**: In Home Assistant, go to **Settings** → **Devices & Services** → **Add Integration**
2. **Configure Connection**:
   - **Host**: IP address or hostname of your Finance Assistant service
   - **Port**: Port number (default: 8080)
   - **Use SSL**: Enable if using HTTPS
   - **Scan Interval**: How often to refresh data (default: 300 seconds)

### Example Configuration

```yaml
# configuration.yaml (optional - can be done via UI)
finance_assistant:
  host: 192.168.1.113
  port: 8080
  ssl: false
  scan_interval: 300
```

## Usage

### Creating Queries

1. **Access Finance Assistant**: Open your Finance Assistant web interface
2. **Create Queries**: Go to the Queries page and create custom queries
3. **Set Output Type**: Choose either "Sensor" or "Calendar" as the output type
4. **Configure Query**: Set up filters, calculations, and templates
5. **Save Query**: Save your query with a unique entity ID

### Home Assistant Entities

Once configured, the integration will automatically create:

- **Sensors**: For queries with "Sensor" output type
- **Calendars**: For queries with "Calendar" output type

### Entity Attributes

Each entity includes these attributes:

- `query_id`: The Finance Assistant query ID
- `query_name`: The name of the query
- `query_description`: Description of the query
- `data_source`: Data source (TRANSACTIONS, ACCOUNTS)
- `query_type`: Query type (TRANSACTION_QUERY, BALANCE_QUERY)
- `last_updated`: When the data was last refreshed

### Sensor Entities

Sensor entities show:

- **State**: The calculated value from your query
- **Unit**: USD for financial data
- **State Class**: TOTAL for transactions, MEASUREMENT for balances

### Calendar Entities

Calendar entities show:

- **Events**: Financial events based on your query
- **Event Count**: Number of events in the calendar
- **Date Range**: Events within the specified time period

## Analytics Sensors

The Finance Assistant integration now includes **8 comprehensive analytics sensors** that provide real-time financial insights and enable powerful Home Assistant automations.

### Available Analytics Sensors

#### 1. Transaction Status Analytics

- **Entity ID**: `sensor.transaction_status_analytics`
- **State**: Total transaction count
- **Attributes**: Breakdown by status (real, uncleared, unapproved, scheduled, cancelled)
- **Use Case**: Monitor transaction processing status and create alerts for pending items

#### 2. Spending Trends

- **Entity ID**: `sensor.spending_trends`
- **State**: Overall financial health score (0-100)
- **Attributes**: Cash flow, expense, and savings trends with recommendations and alerts
- **Use Case**: Track financial health and trigger notifications for declining scores

#### 3. Obligation Ratio

- **Entity ID**: `sensor.obligation_ratio`
- **State**: Monthly obligation ratio percentage
- **Attributes**: Total monthly obligations, essential vs. discretionary breakdown
- **Use Case**: Monitor debt-to-income ratios and create alerts for high obligations

#### 4. Financial Insights

- **Entity ID**: `sensor.financial_insights`
- **State**: Number of active recommendations
- **Attributes**: Detailed recommendations, alerts, and insight status
- **Use Case**: Get actionable financial advice and monitor financial alerts

#### 5. Cash Flow Trend

- **Entity ID**: `sensor.cash_flow_trend`
- **State**: Numeric trend value (1=Improving, 0=Stable, -1=Declining)
- **Attributes**: Trend description, cash flow score, and automation triggers
- **Use Case**: Create automations based on cash flow direction changes

#### 6. Expense Trend

- **Entity ID**: `sensor.expense_trend`
- **State**: Numeric trend value (1=Decreasing, 0=Stable, -1=Increasing)
- **Attributes**: Expense pattern analysis and trend descriptions
- **Use Case**: Monitor spending patterns and trigger alerts for increasing expenses

#### 7. Savings Trend

- **Entity ID**: `sensor.savings_trend`
- **State**: Numeric trend value (1=Improving, 0=Stable, -1=Declining)
- **Attributes**: Savings pattern analysis and trend descriptions
- **Use Case**: Track savings progress and create motivation triggers

#### 8. High Risk Items

- **Entity ID**: `sensor.high_risk_items`
- **State**: Count of high-risk financial items
- **Attributes**: Risk breakdown by severity, mitigation strategies, and risk level
- **Use Case**: Monitor financial risks and trigger urgent alerts

### Automation Examples

#### Example 1: High Risk Alert

```yaml
automation:
  - alias: "High Financial Risk Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.high_risk_items
      above: 0
    action:
      - service: notify.mobile_app
        data:
          title: "Financial Risk Alert"
          message: "{{ states('sensor.high_risk_items') }} high-risk items detected"
```

#### Example 2: Declining Cash Flow Alert

```yaml
automation:
  - alias: "Declining Cash Flow Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.cash_flow_trend
      below: 0
    action:
      - service: notify.mobile_app
        data:
          title: "Cash Flow Warning"
          message: "Cash flow is declining - review expenses"
```

#### Example 3: Financial Health Dashboard

```yaml
automation:
  - alias: "Financial Health Update"
    trigger:
      platform: time_pattern
      hours: "*/6"
    action:
      - service: persistent_notification.create
        data:
          title: "Financial Health Update"
          message: |
            Health Score: {{ states('sensor.spending_trends') }}/100
            Risk Level: {{ state_attr('sensor.spending_trends', 'risk_level') }}
            Obligation Ratio: {{ states('sensor.obligation_ratio') }}%
            High Risk Items: {{ states('sensor.high_risk_items') }}
```

### Sensor Configuration

All analytics sensors automatically update based on your configured scan interval. They provide:

- **Real-time Data**: Live financial insights updated every scan cycle
- **Rich Attributes**: Comprehensive data for advanced automations
- **Automation Triggers**: Numeric values and status changes for triggers
- **Historical Context**: Trend analysis and pattern recognition

### Quality and Reliability

- **Quality Scale**: Platinum (highest level)
- **Error Handling**: Comprehensive error reporting and recovery
- **Logging**: Detailed logging for debugging and monitoring
- **Performance**: Optimized data processing and efficient updates

## Troubleshooting

### Common Issues

1. **Cannot Connect**

   - Check that Finance Assistant service is running
   - Verify host and port are correct
   - Ensure network connectivity

2. **No Entities Created**
   - Ensure you have queries with "Sensor" or "Calendar" output types
   - Check that queries are active
   - Verify the integration is properly configured

### Logs

Check Home Assistant logs for detailed error messages:

```bash
# In Home Assistant
Developer Tools → Logs
```

Look for entries with `finance_assistant` in the component name.

## API Endpoints

The integration uses these Finance Assistant API endpoints:

- `GET /api/ha/queries/` - List available queries
- `GET /api/ha/sensor/{query_id}/` - Get sensor data
- `GET /api/ha/calendar/{query_id}/` - Get calendar data

## Support

For issues and questions:

1. Check the Finance Assistant documentation
2. Review Home Assistant logs
3. Create an issue on the GitHub repository

## Version History

- **1.0.6**: Fix configuration schema mismatch by making API key optional
- **1.0.5**: Force version update to resolve caching issues
- **1.0.0**: Initial stable release with authentication fixes and semantic versioning
- **0.14.64**: Fixed authentication and query_type field mapping
- **0.14.63**: Initial release with sensor and calendar support
