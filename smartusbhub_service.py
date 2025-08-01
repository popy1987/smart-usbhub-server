#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SmartUSBHub System Service

This service encapsulates the SmartUSBHub functionality, allowing different processes
to interact with the SmartUSBHub device through a standardized interface.

The service provides:
1. Automatic device discovery and connection
2. RESTful API for controlling the SmartUSBHub
3. Multi-process access through HTTP requests
4. Persistent configuration management
"""

import os
import sys
import json
import logging
import argparse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add the parent directory to the path to import smartusbhub
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from smartusbhub import SmartUSBHub


class SmartUSBHubService:
    """
    A service that encapsulates the SmartUSBHub functionality and provides
    a RESTful API for controlling the device.
    """

    def __init__(self, port=None, host='localhost', http_port=80891):
        """
        Initialize the SmartUSBHub service.
        
        Args:
            port (str): Serial port name. If None, will auto-discover.
            host (str): Host address for the HTTP server.
            http_port (int): Port for the HTTP server.
        """
        self.host = host
        self.http_port = http_port
        self.hub = None
        self.server = None
        self.server_thread = None
        
        # Connect to the SmartUSBHub
        if port:
            self.hub = SmartUSBHub(port)
        else:
            self.hub = SmartUSBHub.scan_and_connect()
            
        if self.hub is None:
            raise RuntimeError("Failed to connect to SmartUSBHub")
            
        logging.info(f"Connected to SmartUSBHub on {self.hub.port}")
        
    def start(self):
        """
        Start the HTTP server to provide RESTful API access.
        """
        self.server = HTTPServer((self.host, self.http_port), SmartUSBHubRequestHandler)
        self.server.hub_service = self  # Pass service reference to handler
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        logging.info(f"SmartUSBHub service started on http://{self.host}:{self.http_port}")
        
    def stop(self):
        """
        Stop the HTTP server and disconnect from the hub.
        """
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.hub:
            self.hub.disconnect()
        logging.info("SmartUSBHub service stopped")
        
    def get_device_info(self):
        """
        Get device information.
        
        Returns:
            dict: Device information.
        """
        return self.hub.get_device_info()
        
    def set_channel_power(self, channels, state):
        """
        Set power state for one or more channels.
        
        Args:
            channels (list): List of channel numbers (1-4).
            state (int): Power state (0=off, 1=on).
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.hub.set_channel_power(*channels, state=state)
        
    def get_channel_power_status(self, channels):
        """
        Get power status for one or more channels.
        
        Args:
            channels (list): List of channel numbers (1-4).
            
        Returns:
            dict or int or None: Power status for the channels.
        """
        if len(channels) == 1:
            return self.hub.get_channel_power_status(channels[0])
        else:
            return self.hub.get_channel_power_status(*channels)
            
    def set_channel_dataline(self, channels, state):
        """
        Set dataline state for one or more channels.
        
        Args:
            channels (list): List of channel numbers (1-4).
            state (int): Dataline state (0=disconnect, 1=connect).
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.hub.set_channel_dataline(*channels, state=state)
        
    def get_channel_dataline_status(self, channels):
        """
        Get dataline status for one or more channels.
        
        Args:
            channels (list): List of channel numbers (1-4).
            
        Returns:
            dict or None: Dataline status for the channels.
        """
        return self.hub.get_channel_dataline_status(*channels)


class SmartUSBHubRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the SmartUSBHub service.
    """
    
    def _send_response(self, data, status_code=200):
        """
        Send JSON response to client.
        
        Args:
            data (dict): Response data.
            status_code (int): HTTP status code.
        """
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
        
    def _send_error(self, message, status_code=400):
        """
        Send error response to client.
        
        Args:
            message (str): Error message.
            status_code (int): HTTP status code.
        """
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
        
    def do_GET(self):
        """
        Handle GET requests.
        """
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Get service reference
        service = self.server.hub_service
        
        if path == '/device/info':
            # Get device information
            try:
                info = service.get_device_info()
                self._send_response(info)
            except Exception as e:
                self._send_error(f"Failed to get device info: {str(e)}", 500)
                
        elif path.startswith('/channel/power/'):
            # Get power status for a channel
            try:
                channel = int(path.split('/')[-1])
                if channel < 1 or channel > 4:
                    self._send_error("Channel must be between 1 and 4")
                    return
                    
                status = service.get_channel_power_status([channel])
                self._send_response({'channel': channel, 'status': status})
            except ValueError:
                self._send_error("Invalid channel number")
            except Exception as e:
                self._send_error(f"Failed to get power status: {str(e)}", 500)
                
        elif path.startswith('/channel/dataline/'):
            # Get dataline status for a channel
            try:
                channel = int(path.split('/')[-1])
                if channel < 1 or channel > 4:
                    self._send_error("Channel must be between 1 and 4")
                    return
                    
                status = service.get_channel_dataline_status([channel])
                self._send_response({'channel': channel, 'status': status})
            except ValueError:
                self._send_error("Invalid channel number")
            except Exception as e:
                self._send_error(f"Failed to get dataline status: {str(e)}", 500)
                
        else:
            self._send_error("Endpoint not found", 404)
            
    def do_POST(self):
        """
        Handle POST requests.
        """
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Get service reference
        service = self.server.hub_service
        
        # Parse query parameters
        query_params = parse_qs(parsed_path.query)
        
        if path == '/channel/power':
            # Set power state for channels
            try:
                # Get channels from query parameters
                channels = [int(c) for c in query_params.get('channels', [])[0].split(',')]
                if not channels or any(c < 1 or c > 4 for c in channels):
                    self._send_error("Channels must be between 1 and 4")
                    return
                    
                # Get state from query parameters
                state = int(query_params.get('state', [None])[0])
                if state not in [0, 1]:
                    self._send_error("State must be 0 or 1")
                    return
                    
                success = service.set_channel_power(channels, state)
                self._send_response({'success': success})
            except (ValueError, TypeError):
                self._send_error("Invalid parameters")
            except Exception as e:
                self._send_error(f"Failed to set power state: {str(e)}", 500)
                
        elif path == '/channel/dataline':
            # Set dataline state for channels
            try:
                # Get channels from query parameters
                channels = [int(c) for c in query_params.get('channels', [])[0].split(',')]
                if not channels or any(c < 1 or c > 4 for c in channels):
                    self._send_error("Channels must be between 1 and 4")
                    return
                    
                # Get state from query parameters
                state = int(query_params.get('state', [None])[0])
                if state not in [0, 1]:
                    self._send_error("State must be 0 or 1")
                    return
                    
                success = service.set_channel_dataline(channels, state)
                self._send_response({'success': success})
            except (ValueError, TypeError):
                self._send_error("Invalid parameters")
            except Exception as e:
                self._send_error(f"Failed to set dataline state: {str(e)}", 500)
                
        else:
            self._send_error("Endpoint not found", 404)


def main():
    """
    Main function to run the SmartUSBHub service.
    """
    parser = argparse.ArgumentParser(description='SmartUSBHub System Service')
    parser.add_argument('--port', help='Serial port name (e.g., /dev/ttyUSB0)')
    parser.add_argument('--host', default='localhost', help='HTTP server host (default: localhost)')
    parser.add_argument('--http-port', type=int, default=80891, help='HTTP server port (default: 80891)')
    parser.add_argument('--log-level', default='INFO', help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create and start the service
        service = SmartUSBHubService(port=args.port, host=args.host, http_port=args.http_port)
        service.start()
        
        # Keep the service running
        print(f"SmartUSBHub service running on http://{args.host}:{args.http_port}")
        print("Press Ctrl+C to stop the service")
        
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\nStopping service...")
            service.stop()
            
    except Exception as e:
        logging.error(f"Failed to start service: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()