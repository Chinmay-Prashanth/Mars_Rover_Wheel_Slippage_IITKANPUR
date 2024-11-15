#!/usr/bin/env python3
"""
Mars Rover Single Wheel Test Bench - Data Collector
Collects data from Arduino serial port and saves to CSV files
"""

import serial
import csv
import time
import os
import sys
from datetime import datetime
import argparse

class DataCollector:
    def __init__(self, port='/dev/ttyUSB0', baudrate=57600, output_dir='data'):
        self.port = port
        self.baudrate = baudrate
        self.output_dir = output_dir
        self.serial_conn = None
        self.csv_file = None
        self.csv_writer = None
        self.start_time = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def connect(self):
        """Connect to Arduino serial port"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to Arduino on {self.port} at {self.baudrate} baud")
            time.sleep(2)  # Wait for Arduino to initialize
            return True
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")
            return False
            
    def start_logging(self, test_name=None):
        """Start logging data to CSV file"""
        if test_name is None:
            test_name = datetime.now().strftime("wheel_test_%Y%m%d_%H%M%S")
            
        filename = f"{test_name}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        self.csv_file = open(filepath, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.start_time = time.time()
        
        print(f"Starting data logging to: {filepath}")
        print("Press Ctrl+C to stop logging")
        
    def collect_data(self):
        """Main data collection loop"""
        if not self.serial_conn or not self.csv_writer:
            print("Error: Not connected or logging not started")
            return
            
        try:
            while True:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if line:
                        # Add timestamp
                        timestamp = time.time() - self.start_time
                        
                        # Handle different line types
                        if line.startswith('#'):
                            # Comment line - print to console and log
                            print(f"[{timestamp:.2f}s] {line}")
                            self.csv_writer.writerow([timestamp, 'COMMENT', line])
                        else:
                            # Data line - parse and log
                            try:
                                data = line.split(',')
                                if len(data) >= 9:  # Expected number of data fields
                                    # Add our timestamp as first column
                                    row = [timestamp] + data
                                    self.csv_writer.writerow(row)
                                    
                                    # Print summary to console
                                    if len(data) >= 5:
                                        encoder_count = data[2]
                                        slip_percentage = data[4]
                                        direction = "Forward" if data[5] == '1' else "Reverse"
                                        print(f"[{timestamp:.2f}s] Encoder: {encoder_count}, Slip: {slip_percentage}%, Dir: {direction}")
                                        
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing line: {line} - {e}")
                                
                        # Flush to ensure data is written
                        self.csv_file.flush()
                        
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\nData collection stopped by user")
        except Exception as e:
            print(f"Error during data collection: {e}")
        finally:
            self.stop_logging()
            
    def stop_logging(self):
        """Stop logging and close files"""
        if self.csv_file:
            self.csv_file.close()
            print("Data logging stopped")
            
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.serial_conn:
            self.serial_conn.close()
            print("Disconnected from Arduino")

def main():
    parser = argparse.ArgumentParser(description='Mars Rover Wheel Test Data Collector')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port (default: /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=57600, help='Baud rate (default: 57600)')
    parser.add_argument('--output', default='data', help='Output directory (default: data)')
    parser.add_argument('--test-name', help='Test name for output file')
    
    args = parser.parse_args()
    
    # For Linux, try common Arduino ports
    if sys.platform.startswith('linux'):
        possible_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
        for port in possible_ports:
            if os.path.exists(port):
                args.port = port
                break
    
    collector = DataCollector(args.port, args.baudrate, args.output)
    
    if collector.connect():
        try:
            collector.start_logging(args.test_name)
            collector.collect_data()
        finally:
            collector.disconnect()
    else:
        print("Failed to connect to Arduino")
        print("Make sure the Arduino is connected and the correct port is specified")
        sys.exit(1)

if __name__ == '__main__':
    main() 