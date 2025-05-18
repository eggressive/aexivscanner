# AEX DCF Scanner - Fair Value Configuration Guide

## Overview

The AEX DCF Scanner can use multiple sources of fair value estimates for stock valuation:

1. **DCF (Discounted Cash Flow)** - Values calculated by the built-in DCF model
2. **Manual** - Values manually entered by users
3. **Analyst** - Values derived from analyst target prices

The system determines which value to use for each stock based on a configurable priority order.

## Configuration File

Fair value settings are stored in `fair_values_config.json` in the project root directory. This file contains:

- **Sources** - Fair values from each source, organized by ticker
- **Priority** - The order in which sources should be considered
- **Last updated** - Timestamp and source of the last update

Example configuration:
```json
{
    "sources": {
        "dcf": { "ASML.AS": 772.89, "ADYEN.AS": 1450.25, ... },
        "manual": { "ASML.AS": 780.00, "ADYEN.AS": 1460.00, ... },
        "analyst": { "ASML.AS": 768.84, "ADYEN.AS": 1888.55, ... }
    },
    "priority": ["dcf", "manual", "analyst"],
    "last_updated": {
        "time": "2025-05-18 18:06:16",
        "source": "dcf"
    }
}
```

## Changing Priority

The system will use the first available value from the priority list. To change the priority:

```bash
# Set DCF as highest priority, followed by manual, then analyst
python config_manager.py --set-priority dcf manual analyst

# Set manual values as highest priority
python config_manager.py --set-priority manual dcf analyst
```

## Updating Fair Values

### DCF Values
To update DCF values:
```bash
python dcf_integration.py --update
```

To generate a DCF report without updating values:
```bash
python dcf_integration.py --report
```

### Analyst Target Prices
To update analyst target prices:
```bash
python fair_value_updater.py
```

### Manual Values
Manual values can be edited directly in the configuration file or using:
```bash
python config_manager.py --set-manual-value TICKER_SYMBOL FAIR_VALUE
```

Example:
```bash
python config_manager.py --set-manual-value ASML.AS 780.00
```

## Verifying Configuration

To verify which fair value sources are being used:
```bash
python test_fair_values.py
```

This will show:
1. Sample values from each source for common stocks
2. Statistics on which source is providing the values for each stock
3. Confirmation of the current priority order

## Best Practices

- **DCF First**: Using DCF as the primary source ensures valuation is based on company fundamentals
- **Manual Override**: Place manual values first in priority for specific stocks you want to override
- **Regular Updates**: Update your DCF values regularly to keep them current with market conditions
