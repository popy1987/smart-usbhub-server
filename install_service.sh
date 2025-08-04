#!/bin/bash

# SmartUSBHub Service Installation Script

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo)${NC}"
  exit 1
fi

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
  echo -e "${YELLOW}Warning: This script is designed for Ubuntu. You may need to modify it for other distributions.${NC}"
fi

# Create directory for the service
echo -e "${GREEN}Creating directory for SmartUSBHub service...${NC}"
mkdir -p /opt/smartusbhub

# Copy service files
echo -e "${GREEN}Copying service files...${NC}"
cp smartusbhub_service.py /opt/smartusbhub/
cp smartusbhub.py /opt/smartusbhub/
cp requirements.txt /opt/smartusbhub/ 2>/dev/null || echo -e "${YELLOW}Note: requirements.txt not found${NC}"

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
apt update
apt install -y python3 python3-pip
pip3 install pyserial

# Create systemd service file
echo -e "${GREEN}Creating systemd service file...${NC}"
cp smartusbhub.service /etc/systemd/system/

# Reload systemd
echo -e "${GREEN}Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Enable the service
echo -e "${GREEN}Enabling SmartUSBHub service...${NC}"
systemctl enable smartusbhub.service

# Start the service
echo -e "${GREEN}Starting SmartUSBHub service...${NC}"
systemctl start smartusbhub.service

# Check service status
echo -e "${GREEN}Checking service status...${NC}"
systemctl status smartusbhub.service --no-pager || echo -e "${YELLOW}Service may still be starting. Check status again in a few seconds with: systemctl status smartusbhub.service${NC}"

# Display usage information
echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "The SmartUSBHub service is now running and will start automatically on boot."
echo -e "\n${YELLOW}Usage:${NC}"
echo -e "  Check service status: sudo systemctl status smartusbhub.service"
echo -e "  Start service:        sudo systemctl start smartusbhub.service"
echo -e "  Stop service:         sudo systemctl stop smartusbhub.service"
echo -e "  Restart service:      sudo systemctl restart smartusbhub.service"
echo -e "  View logs:            sudo journalctl -u smartusbhub.service -f"
echo -e "\n${YELLOW}API Endpoints:${NC}"
echo -e "  Get device info:      GET http://localhost:18089/device/info"
echo -e "  Get channel power:    GET http://localhost:18089/channel/power/{channel}"
echo -e "  Set channel power:    POST http://localhost:18089/channel/power?channels={channels}&state={state}"
echo -e "  Get channel dataline: GET http://localhost:18089/channel/dataline/{channel}"
echo -e "  Set channel dataline: POST http://localhost:18089/channel/dataline?channels={channels}&state={state}"
echo -e "\nExample API calls:"
echo -e "  curl http://localhost:18089/device/info"
echo -e "  curl http://localhost:18089/channel/power/1"
echo -e "  curl -X POST http://localhost:18089/channel/power?channels=1,2&state=1"
echo -e "  curl -X POST http://localhost:18089/channel/dataline?channels=1&state=0"