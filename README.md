# ZenExport

A simple tool to export Zendesk access logs to CSV or JSON format, for tenants with the [ADPP add-on](https://support.zendesk.com/hc/en-us/articles/6561144266906-About-the-Advanced-Data-Privacy-and-Protection-add-on) enabled.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Macmod/zenexport.git
cd zenexport
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

ZenExport can be run in two modes:
- Single export: Exports logs for a specific date range
- Continuous mode: Continuously exports logs at regular intervals

### Required Parameters

- `--subdomain`: Your Zendesk subdomain (e.g., "company" in `company.zendesk.com`)
- `--email`: Your Zendesk user email
- `--token`: Your Zendesk API token

### Optional Parameters

- `--out-dir`: Output directory for exported files (default: ./exports)
- `--format`: Export format (csv or json, default: json)
- `--start-time`: Start time for logs in ISO format (default: 7 days ago)
- `--end-time`: End time for logs in ISO format (default: current time)
- `--interval`: Interval in seconds between exports for continuous mode (default: 7200)
- `--continuous`: Run in continuous mode, exporting logs at regular intervals

## Examples

### Export logs for a specific date range

```bash
python zenexport.py --subdomain mycompany --email admin@example.com --token abc123 --start-time 2023-01-01T00:00:00Z --end-time 2023-01-31T23:59:59Z
```

### Export logs for the last 7 days (default)

```bash
python zenexport.py --subdomain mycompany --email admin@example.com --token abc123
```

### Export logs in JSON format

```bash
python zenexport.py --subdomain mycompany --email admin@example.com --token abc123 --format json
```

### Run in continuous mode, exporting logs every hour

```bash
python zenexport.py --subdomain mycompany --email admin@example.com --token abc123 --continuous --interval 3600
```

## Output

The exported files will be saved in the specified output directory with filenames in the format:
- `access_logs_START_DATE-to-END_DATE.csv` (for CSV format)
- `access_logs_START_DATE-to-END_DATE.json` (for JSON format)

## Authentication

This tool requires a Zendesk API token. To generate an API token:
1. Log in to your Zendesk account
2. Go to Admin > Channels > API
3. Enable Token Access if it's not already enabled
4. Click the "Add API token" button
5. Give your token a description and copy the token value

## License

The MIT License (MIT)

Copyright (c) 2023 Artur Henrique Marzano Gonzaga

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

