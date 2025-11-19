# Vine Monitor

This program checks your Amazon Vine queue and notifies you of new items.

## Features
- Monitors **Recommended for You (RFY)**, **Available for All (AFA)**, and **Additional Items**.
- **Discord Notifications**: Get alerts for new items in specific queues.
- **Priority Alerts**: Define keywords to get special notifications for items you really want.
- **Browser Integration**: Uses your existing browser session (no password required).

## Setup

### 1. Prerequisites
- Python 3.8+
- **Firefox** installed and logged into Amazon Vine. (Chrome is not recommended as it restricts access to session cookies).
- **Tab Reloader** extension for Firefox (highly recommended to prevent session timeouts).

### 2. Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` to configure your settings:
   - `DISCORD_WEBHOOK_RFY`: Webhook for "Recommended for You" items.
   - `DISCORD_WEBHOOK_AFA`: Webhook for "Available for All" items.
   - `DISCORD_WEBHOOK_AI`: Webhook for "Additional Items".
   - `DISCORD_WEBHOOK_PRIORITY`: Webhook for items matching your priority terms.
   - `BROWSER_TYPE`: Set to `firefox`.

### 4. Priority Terms
Create a `priority_terms.json` file to track specific items. See `priority_terms.json.example` for a template.
```json
{
    "terms": ["laptop", "coffee maker", "standing desk"]
}
```

## Usage
1. Log into Amazon Vine in Firefox.
2. **Important**: To keep your session active, use the **Tab Reloader** extension to automatically refresh the Amazon Vine page every few minutes.
   - *Tip*: Enable "Random variation" in Tab Reloader to avoid detection.
3. Close the browser window (or ensure cookies are saved to disk).
4. Run the script:
   ```bash
   python src/amazon-vine.py
   ```

## Credits
Original Python 2 version: [@timur-tabi](https://github.com/timur-tabi)
