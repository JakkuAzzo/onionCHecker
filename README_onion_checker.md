# Onion Site Accessibility Checker

This Python script uses Tor to access a .onion site listing and tests the accessibility of listed .onion sites, saving accessible ones to a JSON file in real-time.

## Prerequisites

1. **Tor must be installed and running**
   ```bash
   # On Debian/Ubuntu/Kali
   sudo apt update
   sudo apt install tor
   sudo systemctl start tor
   sudo systemctl enable tor
   
   # On other systems, install Tor and make sure it's running on port 9050
   ```

2. **Python 3.7+ with required packages**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python onion_site_checker.py
```

### Advanced Usage with Options
```bash
python onion_site_checker.py --start-page 1072722848287667155967 --max-pages 20 --output my_sites.json --min-delay 3 --max-delay 10
```

### Command Line Options

- `--start-page`: Starting page number (default: 1072722848287667155967)
- `--max-pages`: Maximum number of pages to check (default: 10)
- `--output`: Output JSON file (default: accessible_onion_sites.json)
- `--min-delay`: Minimum delay between requests in seconds (default: 5)
- `--max-delay`: Maximum delay between requests in seconds (default: 15)

## Features

- **Tor Integration**: Routes all requests through Tor SOCKS proxy (port 9050)
- **Real-time JSON Updates**: Saves accessible sites immediately when found
- **Comprehensive Logging**: Logs to both file (`onion_checker.log`) and console
- **Error Handling**: Robust error handling with retries and timeouts
- **Rate Limiting**: Random delays between requests to avoid being blocked
- **Resume Capability**: Automatically skips already tested sites when restarting
- **Progress Tracking**: Shows progress with detailed statistics

## Output Format

The script creates a JSON file with the following structure:

```json
{
  "last_updated": "2025-11-05T...",
  "total_accessible_sites": 5,
  "accessible_sites": [
    {
      "domain": "example.onion",
      "url": "http://example.onion",
      "text": "Example Site",
      "status": "accessible",
      "tested_at": "2025-11-05T...",
      "response_time": 2.34
    }
  ]
}
```

## Important Notes

1. **Legal Disclaimer**: This tool is for educational and research purposes only. Ensure you comply with all applicable laws and regulations.

2. **Tor Connection**: The script will test your Tor connection before starting. If the test fails, check that Tor is running on port 9050.

3. **Rate Limiting**: The script includes delays between requests to be respectful to the target sites. Adjust the delay parameters as needed.

4. **Persistence**: The script saves progress after finding each accessible site, so you can safely interrupt and resume.

## Troubleshooting

### Tor Connection Issues
```bash
# Check if Tor is running
sudo systemctl status tor

# Restart Tor if needed
sudo systemctl restart tor

# Check if port 9050 is listening
netstat -tulpn | grep 9050
```

### Python Dependencies
```bash
# If you have permission issues, try:
pip install --user -r requirements.txt
```

## Example Run

```
2025-11-05 10:00:00 - INFO - ==================================================
2025-11-05 10:00:00 - INFO - Onion Site Accessibility Checker
2025-11-05 10:00:00 - INFO - ==================================================
2025-11-05 10:00:01 - INFO - Tor connection successful. Current IP: 185.220.101.32
2025-11-05 10:00:02 - INFO - Starting onion site checker from page 1072722848287667155967
2025-11-05 10:00:03 - INFO - Fetching listing page: 1072722848287667155967
2025-11-05 10:00:05 - INFO - Found 15 onion sites on page 1072722848287667155967
2025-11-05 10:00:06 - INFO - Testing accessibility: example.onion
2025-11-05 10:00:08 - INFO - ✓ example.onion is accessible
2025-11-05 10:00:08 - INFO - Saved 1 accessible sites to accessible_onion_sites.json
```