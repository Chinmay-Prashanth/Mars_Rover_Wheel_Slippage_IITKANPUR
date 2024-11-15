#!/usr/bin/env python3
"""
Mars Rover Single Wheel Test Bench - Complete Testing Workflow
Main script to run data collection, analysis, and visualization
"""

import os
import sys
import subprocess
import argparse
import time
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy', 'serial']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'serial':
                import serial
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def run_data_collection(port, duration, test_name):
    """Run data collection from Arduino"""
    print(f"\n{'='*50}")
    print("STARTING DATA COLLECTION")
    print(f"{'='*50}")
    print(f"Port: {port}")
    print(f"Duration: {duration} seconds")
    print(f"Test name: {test_name}")
    print("\nMake sure your Arduino is connected and running the test bench code!")
    
    input("Press Enter to start data collection...")
    
    cmd = ['python3', 'data_collector.py', '--port', port, '--test-name', test_name]
    
    try:
        if duration > 0:
            # Run for specified duration
            process = subprocess.Popen(cmd)
            time.sleep(duration)
            process.terminate()
            process.wait()
        else:
            # Run until user stops
            subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nData collection stopped by user")
    except Exception as e:
        print(f"Error during data collection: {e}")
        return False
    
    return True

def run_analysis(data_file):
    """Run data analysis"""
    print(f"\n{'='*50}")
    print("RUNNING DATA ANALYSIS")
    print(f"{'='*50}")
    
    cmd = ['python3', 'data_analyzer.py', '--file', data_file]
    
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False
    
    return True

def run_visualization(data_file):
    """Run data visualization"""
    print(f"\n{'='*50}")
    print("GENERATING VISUALIZATIONS")
    print(f"{'='*50}")
    
    cmd = ['python3', 'data_visualizer.py', '--file', data_file, '--dashboard']
    
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"Error during visualization: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Mars Rover Single Wheel Test - Complete Workflow')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Arduino serial port')
    parser.add_argument('--duration', type=int, default=30, help='Test duration in seconds (0 for manual stop)')
    parser.add_argument('--test-name', help='Test name (auto-generated if not provided)')
    parser.add_argument('--collect-only', action='store_true', help='Only collect data, skip analysis')
    parser.add_argument('--analyze-only', help='Only analyze existing data file')
    parser.add_argument('--visualize-only', help='Only visualize existing data file')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency check')
    
    args = parser.parse_args()
    
    # Check dependencies
    if not args.skip_deps and not check_dependencies():
        sys.exit(1)
    
    # Generate test name if not provided
    if not args.test_name:
        args.test_name = f"wheel_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    data_file = f"data/{args.test_name}.csv"
    
    # Handle different modes
    if args.analyze_only:
        if not os.path.exists(args.analyze_only):
            print(f"Error: Data file {args.analyze_only} not found")
            sys.exit(1)
        run_analysis(args.analyze_only)
        return
    
    if args.visualize_only:
        if not os.path.exists(args.visualize_only):
            print(f"Error: Data file {args.visualize_only} not found")
            sys.exit(1)
        run_visualization(args.visualize_only)
        return
    
    # Full workflow or collect-only
    success = run_data_collection(args.port, args.duration, args.test_name)
    
    if not success:
        print("Data collection failed!")
        sys.exit(1)
    
    if args.collect_only:
        print(f"\nData collection complete! Data saved to: {data_file}")
        return
    
    # Check if data file exists
    if not os.path.exists(data_file):
        print(f"Error: Expected data file {data_file} not found")
        sys.exit(1)
    
    # Run analysis
    print("\nStarting analysis...")
    success = run_analysis(data_file)
    
    if not success:
        print("Analysis failed!")
        sys.exit(1)
    
    # Run visualization
    print("\nStarting visualization...")
    success = run_visualization(data_file)
    
    if not success:
        print("Visualization failed!")
        sys.exit(1)
    
    print(f"\n{'='*50}")
    print("COMPLETE WORKFLOW FINISHED!")
    print(f"{'='*50}")
    print(f"Data file: {data_file}")
    print(f"Analysis report: analysis/analysis_report.json")
    print(f"Plots directory: plots/")
    print(f"Dashboard: plots/dashboard.png")
    print(f"{'='*50}")

if __name__ == '__main__':
    main() 