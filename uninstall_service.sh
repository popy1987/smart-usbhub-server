#!/bin/bash

# SmartUSBHub Service Uninstallation Script

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo)${NC}"
  exit 1
fi

# Stop the service if running
echo -e "${GREEN}Stopping SmartUSBHub service...${NC}"
systemctl stop smartusbhub.service || echo -e "${RED}Service was not running${NC}"

# Disable the service
echo -e "${GREEN}Disabling SmartUSBHub service...${NC}"
systemctl disable smartusbhub.service || echo -e "${RED}Failed to disable service${NC}"

# Remove systemd service file
echo -e "${GREEN}Removing systemd service file...${NC}"
rm -f /etc/systemd/system/smartusbhub.service

# Reload systemd
echo -e "${GREEN}Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Remove service directory
echo -e "${GREEN}Removing service directory...${NC}"
rm -rf /opt/smartusbhub

echo -e "${GREEN}Uninstallation complete!${NC}"
echo -e "The SmartUSBHub service has been removed from your system."