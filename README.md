# WindmillFan Home Assistant Integration

This integration creates a **fan entity** to connect your Windmill Fan units into Home Assistant, allowing you to control fan speed and power settings directly from your Home Assistant dashboard.

> **Note**: This is not an official integration. It is not associated, maintained, supported, or endorsed by Windmill. Windmill is a young company, their tech might change, and this integration might break. Use at your own risk.

**Attribution**: This integration is forked from [@bzellman/WindmillAC](https://github.com/bzellman/WindmillAC) and has been refactored to support Windmill Fans (instead of ACs) with improved error handling, async HTTP client, and enhanced reliability through AI-assisted development. Huge thanks to @bzellman for the original work!

## Features

- **Fan Control**: Turn your Windmill fan on/off
- **Speed Control**: 5-speed fan control (Whisper, Low, Medium, High, Boost)
- **Percentage Control**: Supports Home Assistant's percentage-based fan control
- **Real-time Updates**: Polls device status every 60 seconds
- **Proper Error Handling**: Robust error handling and retry logic

## Prerequisites

- Home Assistant 2024.1.0 or newer
- A Windmill Fan unit with access to the [Windmill Air Dashboard](https://dashboard.windmillair.com)
- HACS (Home Assistant Community Store) installed

## Installation

### Step 1: Install HACS (if you haven't already)

HACS is the Home Assistant Community Store that allows you to easily install custom integrations like this one.

**If you already have HACS installed, skip to Step 2.**

1. **Install HACS** by following the official installation guide: [HACS Installation](https://hacs.xyz/docs/use/download/download/)
2. **Restart Home Assistant** after HACS installation
3. **Configure HACS** by going to Settings → Devices & Services → Add Integration → HACS
4. Follow the GitHub authentication process when prompted

### Step 2: Add This Repository to HACS

1. Open Home Assistant and navigate to **HACS** (usually in the sidebar)
2. Click on **Integrations**
3. Click the **three dots menu** (⋮) in the top right corner
4. Select **Custom repositories**
5. In the dialog that opens:
   - **Repository URL**: `https://github.com/markuswinkler/WindmillFan`
   - **Category**: Select "Integration"
6. Click **Add**

### Step 3: Install the WindmillFan Integration

1. In HACS → Integrations, search for "WindmillFan"
2. Click on the **WindmillFan** integration
3. Click **Download**
4. **Restart Home Assistant** (this is important!)

### Step 4: Add the Integration to Home Assistant

Installing the repository through HACS doesn't automatically add it to your Home Assistant configuration.

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** (+ button in bottom right)
3. Search for "WindmillFan" 
4. Click on **WindmillFan** when it appears
5. You'll be prompted to configure the integration

### Step 5: Configure Your Windmill Fan Device

To complete the setup, you'll need your device's Auth Token:

1. **Get your Auth Token**:
   - Go to the [Windmill Air Dashboard](https://dashboard.windmillair.com)
   - Navigate to the **"Devices"** tab
   - Your Auth Token should be visible there

2. **Complete the integration setup**:
   - Enter your Auth Token when prompted in the integration configuration
   - The integration will automatically validate your token
   - Click **Submit**

## Usage

After successful configuration:

1. Go to **Settings** → **Devices & Services**
2. You should see your Windmill Fan listed under the WindmillFan integration
3. Your fan will appear as a fan entity in Home Assistant
4. You can control it through:
   - The fan card on your dashboard
   - Automations and scripts
   - Voice assistants (if configured)

### Fan Speeds

The integration supports 5 fan speeds that map to percentages:

- **Whisper**: 20%
- **Low**: 40%
- **Medium**: 60%
- **High**: 80%
- **Boost**: 100%

## Troubleshooting

### Integration doesn't appear in Add Integration menu
- Make sure you restarted Home Assistant after downloading from HACS
- Check that the repository was properly added to HACS
- Clear your browser cache and try again

### Authentication Issues
**"Invalid Auth" error during setup:**
- Verify your Auth Token is correct
- Make sure you copied the complete token without extra spaces
- Try refreshing the Windmill dashboard and copying the token again

**Can't copy Auth Token from dashboard:**
If clicking on the Auth Token doesn't copy it, try:
- Opening developer tools and finding the token value using inspect element
- Go to the Windmill phone app, About > Send Logs. Email yourself the log file and search for 'deviceToken'
- Use an OCR tool like Windows PowerToys (watch for character mistakes like 0/O or 1/l)

### Connection Issues
**"Cannot Connect" error:**
- Check your internet connection
- Verify your Windmill fan is online and connected to Wi-Fi
- Make sure the Windmill service is operational

### Fan entity not responding
- Check the integration logs: Settings → System → Logs, search for "windmillfan"
- Try reloading the integration: Settings → Devices & Services → WindmillFan → three dots → Reload
- Verify your device is online in the Windmill dashboard

### "Failed to get pin value for V1" Error
This might occur if something wasn't configured correctly initially:
1. Remove the integration: Settings → Devices & Services → WindmillFan → three dots → Delete
2. Re-add the integration following steps 4-5 above
3. If problems persist, check the Home Assistant logs for more details

## Advanced Configuration

### Changing Update Interval
The integration polls your device every 60 seconds by default. To change this, you would need to modify the `UPDATE_INTERVAL` constant in the code.

### Multiple Devices
To add multiple Windmill fans, simply add the integration multiple times with different Auth Tokens.

## Support & Contributing

This is a community-maintained integration. For issues or feature requests, please use the [GitHub Issues](https://github.com/markuswinkler/WindmillFan/issues) page.

### Debugging
Enable debug logging by adding this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.windmillfan: debug
```

## Version History

- **v1.0.5**: Major refactor to support Fans instead of ACs, with improved error handling, async HTTP client, proper resource cleanup
- **v1.0.4**: Previous version

## Disclaimer

This integration is provided as-is. While I do my best to maintain it, I offer no guarantee or warranty for your hardware, software, or devices. The integration may break if Windmill changes their API or technology stack. MIT License applies.