#!/bin/bash

# Onion Site Checker Startup Script
# This script checks if Tor is running, starts it if needed, and runs the onion checker

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/onion_site_checker.py"
VENV_PYTHON="$SCRIPT_DIR/../.venv/bin/python"

echo -e "${BLUE}=================================================="
echo -e "        Onion Site Checker Startup Script"
echo -e "==================================================${NC}"

# Function to check if Tor is running
check_tor_running() {
    if pgrep -x "tor" > /dev/null; then
        return 0  # Tor is running
    else
        return 1  # Tor is not running
    fi
}

# Function to check if Tor port 9050 is listening
check_tor_port() {
    if netstat -tulpn 2>/dev/null | grep -q ":9050 "; then
        return 0  # Port 9050 is listening
    else
        return 1  # Port 9050 is not listening
    fi
}

# Function to start Tor
start_tor() {
    echo -e "${YELLOW}Starting Tor service...${NC}"
    
    # Try different methods to start Tor
    if command -v systemctl >/dev/null 2>&1; then
        # systemd system
        echo -e "${BLUE}Using systemctl to start Tor...${NC}"
        if sudo systemctl start tor; then
            echo -e "${GREEN}✓ Tor started successfully with systemctl${NC}"
            return 0
        else
            echo -e "${RED}✗ Failed to start Tor with systemctl${NC}"
        fi
    fi
    
    if command -v service >/dev/null 2>&1; then
        # init.d system
        echo -e "${BLUE}Using service command to start Tor...${NC}"
        if sudo service tor start; then
            echo -e "${GREEN}✓ Tor started successfully with service command${NC}"
            return 0
        else
            echo -e "${RED}✗ Failed to start Tor with service command${NC}"
        fi
    fi
    
    # Try starting Tor directly
    echo -e "${BLUE}Attempting to start Tor directly...${NC}"
    if command -v tor >/dev/null 2>&1; then
        echo -e "${YELLOW}Starting Tor in background...${NC}"
        sudo tor --RunAsDaemon 1 &
        sleep 3
        if check_tor_running; then
            echo -e "${GREEN}✓ Tor started successfully in daemon mode${NC}"
            return 0
        else
            echo -e "${RED}✗ Failed to start Tor in daemon mode${NC}"
        fi
    fi
    
    return 1  # All methods failed
}

# Function to wait for Tor to be ready
wait_for_tor() {
    echo -e "${YELLOW}Waiting for Tor to be ready...${NC}"
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_tor_port; then
            echo -e "${GREEN}✓ Tor is ready and listening on port 9050${NC}"
            return 0
        fi
        
        echo -e "${BLUE}Attempt $attempt/$max_attempts: Waiting for Tor port 9050...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}✗ Tor port 9050 is not responding after $max_attempts attempts${NC}"
    return 1
}

# Function to check if Python script exists
check_python_script() {
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        echo -e "${RED}✗ Python script not found: $PYTHON_SCRIPT${NC}"
        return 1
    fi
    
    if [ ! -f "$VENV_PYTHON" ]; then
        echo -e "${RED}✗ Python virtual environment not found: $VENV_PYTHON${NC}"
        echo -e "${YELLOW}Please run the setup first or check the path${NC}"
        return 1
    fi
    
    return 0
}

# Function to install Tor if not present
install_tor() {
    echo -e "${YELLOW}Tor is not installed. Attempting to install...${NC}"
    
    if command -v apt-get >/dev/null 2>&1; then
        echo -e "${BLUE}Installing Tor using apt-get...${NC}"
        sudo apt-get update && sudo apt-get install -y tor
    elif command -v yum >/dev/null 2>&1; then
        echo -e "${BLUE}Installing Tor using yum...${NC}"
        sudo yum install -y tor
    elif command -v dnf >/dev/null 2>&1; then
        echo -e "${BLUE}Installing Tor using dnf...${NC}"
        sudo dnf install -y tor
    elif command -v pacman >/dev/null 2>&1; then
        echo -e "${BLUE}Installing Tor using pacman...${NC}"
        sudo pacman -S --noconfirm tor
    else
        echo -e "${RED}✗ Cannot install Tor automatically. Please install Tor manually.${NC}"
        echo -e "${YELLOW}On Debian/Ubuntu: sudo apt-get install tor${NC}"
        echo -e "${YELLOW}On RHEL/CentOS: sudo yum install tor${NC}"
        echo -e "${YELLOW}On Arch: sudo pacman -S tor${NC}"
        return 1
    fi
}

# Main execution starts here
echo -e "${BLUE}Step 1: Checking if Python script exists...${NC}"
if ! check_python_script; then
    echo -e "${RED}Cannot proceed without the Python script. Exiting.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python script found${NC}"

echo -e "\n${BLUE}Step 2: Checking if Tor is installed...${NC}"
if ! command -v tor >/dev/null 2>&1; then
    echo -e "${YELLOW}Tor is not installed${NC}"
    if ! install_tor; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Tor is installed${NC}"
fi

echo -e "\n${BLUE}Step 3: Checking if Tor is running...${NC}"
if check_tor_running; then
    echo -e "${GREEN}✓ Tor is already running${NC}"
    
    # Check if port 9050 is listening
    if check_tor_port; then
        echo -e "${GREEN}✓ Tor is listening on port 9050${NC}"
    else
        echo -e "${YELLOW}⚠ Tor is running but not listening on port 9050${NC}"
        echo -e "${YELLOW}Attempting to restart Tor...${NC}"
        sudo pkill tor 2>/dev/null || true
        sleep 2
        if ! start_tor; then
            echo -e "${RED}✗ Failed to restart Tor. Exiting.${NC}"
            exit 1
        fi
        if ! wait_for_tor; then
            echo -e "${RED}✗ Tor is not ready. Exiting.${NC}"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}Tor is not running${NC}"
    if ! start_tor; then
        echo -e "${RED}✗ Failed to start Tor. Exiting.${NC}"
        exit 1
    fi
    
    if ! wait_for_tor; then
        echo -e "${RED}✗ Tor failed to become ready. Exiting.${NC}"
        exit 1
    fi
fi

echo -e "\n${BLUE}Step 4: Testing Tor connection...${NC}"
# Quick test using curl if available
if command -v curl >/dev/null 2>&1; then
    if curl --socks5 127.0.0.1:9050 --connect-timeout 10 -s http://httpbin.org/ip >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Tor connection test successful${NC}"
    else
        echo -e "${YELLOW}⚠ Tor connection test failed, but continuing anyway${NC}"
    fi
else
    echo -e "${YELLOW}⚠ curl not available for connection test, but continuing anyway${NC}"
fi

echo -e "\n${GREEN}=================================================="
echo -e "          Starting Onion Site Checker"
echo -e "==================================================${NC}"

# Parse command line arguments to pass to the Python script
PYTHON_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --start-page)
            PYTHON_ARGS+=("--start-page" "$2")
            shift 2
            ;;
        --max-pages)
            PYTHON_ARGS+=("--max-pages" "$2")
            shift 2
            ;;
        --output)
            PYTHON_ARGS+=("--output" "$2")
            shift 2
            ;;
        --min-delay)
            PYTHON_ARGS+=("--min-delay" "$2")
            shift 2
            ;;
        --max-delay)
            PYTHON_ARGS+=("--max-delay" "$2")
            shift 2
            ;;
        -h|--help)
            echo -e "${BLUE}Usage: $0 [Python script options]${NC}"
            echo -e "${YELLOW}This script will start Tor if needed and run the onion checker${NC}"
            echo -e "${YELLOW}All additional arguments are passed to the Python script${NC}"
            echo ""
            "$VENV_PYTHON" "$PYTHON_SCRIPT" --help
            exit 0
            ;;
        *)
            PYTHON_ARGS+=("$1")
            shift
            ;;
    esac
done

# Run the Python script with the virtual environment Python
echo -e "${BLUE}Running: $VENV_PYTHON $PYTHON_SCRIPT ${PYTHON_ARGS[*]}${NC}"
echo ""

# Change to the script directory to ensure relative paths work correctly
cd "$SCRIPT_DIR"

# Execute the Python script
exec "$VENV_PYTHON" "$PYTHON_SCRIPT" "${PYTHON_ARGS[@]}"