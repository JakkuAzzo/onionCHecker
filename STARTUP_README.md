# Onion Checker Startup Script

This folder contains scripts to automatically manage Tor and run the onion site checker.

## Files

- `start_onion_checker.sh` - Main startup script that handles Tor management
- `run.sh` - Simple wrapper for easy execution
- `onion_site_checker.py` - The main Python script
- `requirements.txt` - Python dependencies (if moved here)

## Quick Start

```bash
# Simple run with default settings
./run.sh

# Run with custom options
./run.sh --max-pages 20 --min-delay 3 --max-delay 10

# See all available options
./run.sh --help
```

## What the Startup Script Does

1. **Checks Prerequisites**: Verifies Python script and virtual environment exist
2. **Tor Installation**: Automatically installs Tor if not present (on supported systems)
3. **Tor Status Check**: Checks if Tor is running and listening on port 9050
4. **Tor Management**: Starts Tor service if not running
5. **Connection Test**: Verifies Tor connectivity before starting the checker
6. **Script Execution**: Runs the onion checker with all passed arguments

## Supported Systems

The script automatically detects and uses the appropriate package manager:
- **Debian/Ubuntu/Kali**: `apt-get`
- **RHEL/CentOS**: `yum`
- **Fedora**: `dnf`
- **Arch Linux**: `pacman`

## Service Management

The script tries multiple methods to start Tor:
1. `systemctl start tor` (systemd)
2. `service tor start` (init.d)
3. `tor --RunAsDaemon 1` (direct execution)

## Manual Tor Management

If you prefer to manage Tor manually:

```bash
# Start Tor
sudo systemctl start tor

# Check Tor status
sudo systemctl status tor

# Enable Tor to start on boot
sudo systemctl enable tor

# Check if Tor is listening on port 9050
netstat -tulpn | grep 9050
```

## Troubleshooting

### Permission Issues
If you get permission errors:
```bash
# Make scripts executable
chmod +x start_onion_checker.sh run.sh

# Check sudo access for Tor management
sudo -l
```

### Tor Installation Issues
If automatic installation fails:
```bash
# Manual installation on Debian/Ubuntu/Kali
sudo apt update
sudo apt install tor

# Manual installation on RHEL/CentOS
sudo yum install epel-release
sudo yum install tor

# Manual installation on Arch
sudo pacman -S tor
```

### Port 9050 Already in Use
If port 9050 is occupied by another process:
```bash
# Find what's using port 9050
sudo netstat -tulpn | grep 9050
sudo lsof -i :9050

# Kill the process if needed (replace PID)
sudo kill <PID>
```

### Python Virtual Environment Issues
If the virtual environment is not found:
```bash
# Recreate the virtual environment
cd /home/kali/SecLists/Passwords
python3 -m venv .venv
source .venv/bin/activate
pip install -r onionCHecker/requirements.txt  # or wherever requirements.txt is located
```

## Output Files

- `accessible_onion_sites.json` - Results (created in the onionCHecker directory)
- `onion_checker.log` - Detailed logs (created in the onionCHecker directory)

## Examples

```bash
# Basic run - check 10 pages starting from default page
./run.sh

# Check more pages with faster delays
./run.sh --max-pages 50 --min-delay 2 --max-delay 8

# Save to custom file
./run.sh --output my_accessible_sites.json

# Start from specific page
./run.sh --start-page 1072722848287667155968 --max-pages 5
```

## Security Notes

- The script requires sudo access to manage Tor service
- All traffic is routed through Tor for anonymity
- Random delays are used to avoid detection
- The script respects rate limiting to be courteous to target sites