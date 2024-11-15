#!/usr/bin/env python3
"""
Mars Rover Single Wheel Test Bench - Data Analyzer
Analyzes collected wheel slippage data and generates insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import argparse
import os
import glob
from datetime import datetime
import json

class SlipAnalyzer:
    def __init__(self, data_file=None, output_dir='analysis'):
        self.data_file = data_file
        self.output_dir = output_dir
        self.data = None
        self.analysis_results = {}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
    def load_data(self, file_path):
        """Load CSV data from file"""
        try:
            # Read CSV, handling comments and mixed data types
            self.data = pd.read_csv(file_path, comment='#', 
                                  names=['PC_Timestamp', 'Arduino_Timestamp', 'ElapsedTime', 
                                        'EncoderCount', 'ExpectedRotation', 'SlipPercentage', 
                                        'Direction', 'LoadCellReading', 'CurrentSensor', 
                                        'MotorCurrent', 'Comments'])
            
            # Filter out comment rows
            self.data = self.data[self.data['PC_Timestamp'] != 'COMMENT']
            
            # Convert numeric columns
            numeric_cols = ['PC_Timestamp', 'Arduino_Timestamp', 'ElapsedTime', 
                          'EncoderCount', 'ExpectedRotation', 'SlipPercentage', 
                          'LoadCellReading', 'CurrentSensor', 'MotorCurrent']
            
            for col in numeric_cols:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
            # Convert direction to boolean
            self.data['Direction'] = self.data['Direction'].astype(int).astype(bool)
            
            print(f"Loaded {len(self.data)} data points from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def basic_statistics(self):
        """Calculate basic statistics"""
        if self.data is None:
            return None
            
        stats = {
            'total_samples': len(self.data),
            'test_duration': self.data['ElapsedTime'].max() / 1000.0,  # Convert to seconds
            'encoder_range': {
                'min': self.data['EncoderCount'].min(),
                'max': self.data['EncoderCount'].max(),
                'total_rotation': self.data['EncoderCount'].max() - self.data['EncoderCount'].min()
            },
            'slip_statistics': {
                'mean': self.data['SlipPercentage'].mean(),
                'std': self.data['SlipPercentage'].std(),
                'min': self.data['SlipPercentage'].min(),
                'max': self.data['SlipPercentage'].max(),
                'median': self.data['SlipPercentage'].median()
            },
            'direction_changes': len(self.data[self.data['Comments'] == 'DIRECTION_CHANGE']),
            'slip_events': len(self.data[self.data['Comments'] == 'SLIP_DETECTED'])
        }
        
        self.analysis_results['basic_stats'] = stats
        return stats
    
    def slip_analysis(self):
        """Detailed slip analysis"""
        if self.data is None:
            return None
            
        # Identify slip events
        slip_threshold = 5.0  # Default threshold
        high_slip_events = self.data[abs(self.data['SlipPercentage']) > slip_threshold]
        
        # Analyze slip correlation with other sensors
        correlations = {}
        correlations['slip_vs_load'] = self.data['SlipPercentage'].corr(self.data['LoadCellReading'])
        correlations['slip_vs_current'] = self.data['SlipPercentage'].corr(self.data['MotorCurrent'])
        correlations['load_vs_current'] = self.data['LoadCellReading'].corr(self.data['MotorCurrent'])
        
        # Direction-based analysis
        forward_data = self.data[self.data['Direction'] == True]
        reverse_data = self.data[self.data['Direction'] == False]
        
        direction_analysis = {
            'forward_mean_slip': forward_data['SlipPercentage'].mean(),
            'reverse_mean_slip': reverse_data['SlipPercentage'].mean(),
            'forward_slip_events': len(forward_data[abs(forward_data['SlipPercentage']) > slip_threshold]),
            'reverse_slip_events': len(reverse_data[abs(reverse_data['SlipPercentage']) > slip_threshold])
        }
        
        slip_analysis = {
            'slip_events_count': len(high_slip_events),
            'slip_percentage': (len(high_slip_events) / len(self.data)) * 100,
            'correlations': correlations,
            'direction_analysis': direction_analysis,
            'slip_threshold': slip_threshold
        }
        
        self.analysis_results['slip_analysis'] = slip_analysis
        return slip_analysis
    
    def detect_slip_patterns(self):
        """Detect patterns in slip behavior"""
        if self.data is None:
            return None
            
        # Rolling window analysis
        window_size = 50  # Adjust based on data frequency
        self.data['slip_rolling_mean'] = self.data['SlipPercentage'].rolling(window=window_size).mean()
        self.data['slip_rolling_std'] = self.data['SlipPercentage'].rolling(window=window_size).std()
        
        # Detect sudden changes in slip
        slip_threshold = 2.0  # Standard deviations
        self.data['slip_anomaly'] = abs(self.data['SlipPercentage'] - self.data['slip_rolling_mean']) > \
                                   (slip_threshold * self.data['slip_rolling_std'])
        
        # Pattern detection
        patterns = {
            'total_anomalies': self.data['slip_anomaly'].sum(),
            'anomaly_percentage': (self.data['slip_anomaly'].sum() / len(self.data)) * 100,
            'max_consecutive_slip': self._find_max_consecutive_slip(),
            'slip_frequency': self._calculate_slip_frequency()
        }
        
        self.analysis_results['patterns'] = patterns
        return patterns
    
    def _find_max_consecutive_slip(self):
        """Find maximum consecutive slip events"""
        slip_events = abs(self.data['SlipPercentage']) > 5.0
        max_consecutive = 0
        current_consecutive = 0
        
        for event in slip_events:
            if event:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
                
        return max_consecutive
    
    def _calculate_slip_frequency(self):
        """Calculate slip event frequency"""
        slip_events = abs(self.data['SlipPercentage']) > 5.0
        total_time = self.data['ElapsedTime'].max() / 1000.0  # Convert to seconds
        slip_count = slip_events.sum()
        
        return slip_count / total_time if total_time > 0 else 0
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        if self.data is None:
            print("No data loaded")
            return
            
        # Run all analyses
        basic_stats = self.basic_statistics()
        slip_analysis = self.slip_analysis()
        patterns = self.detect_slip_patterns()
        
        # Create report
        report = {
            'analysis_date': datetime.now().isoformat(),
            'data_file': self.data_file,
            'basic_statistics': basic_stats,
            'slip_analysis': slip_analysis,
            'patterns': patterns
        }
        
        # Save report as JSON
        report_file = os.path.join(self.output_dir, 'analysis_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self._print_report_summary(report)
        
        return report
    
    def _print_report_summary(self, report):
        """Print analysis summary to console"""
        print("\n" + "="*60)
        print("MARS ROVER WHEEL SLIP ANALYSIS REPORT")
        print("="*60)
        
        stats = report['basic_statistics']
        slip = report['slip_analysis']
        patterns = report['patterns']
        
        print(f"Test Duration: {stats['test_duration']:.1f} seconds")
        print(f"Total Samples: {stats['total_samples']}")
        print(f"Total Rotation: {stats['encoder_range']['total_rotation']} encoder counts")
        print(f"Direction Changes: {stats['direction_changes']}")
        
        print(f"\nSLIP STATISTICS:")
        print(f"  Mean Slip: {slip['slip_analysis']['mean']:.2f}%")
        print(f"  Std Dev: {slip['slip_analysis']['std']:.2f}%")
        print(f"  Max Slip: {slip['slip_analysis']['max']:.2f}%")
        print(f"  Slip Events: {slip['slip_events_count']} ({slip['slip_percentage']:.1f}% of time)")
        
        print(f"\nCORRELATIONS:")
        print(f"  Slip vs Load Cell: {slip['correlations']['slip_vs_load']:.3f}")
        print(f"  Slip vs Current: {slip['correlations']['slip_vs_current']:.3f}")
        print(f"  Load vs Current: {slip['correlations']['load_vs_current']:.3f}")
        
        print(f"\nPATTERNS:")
        print(f"  Slip Anomalies: {patterns['total_anomalies']} ({patterns['anomaly_percentage']:.1f}%)")
        print(f"  Max Consecutive Slip: {patterns['max_consecutive_slip']} samples")
        print(f"  Slip Frequency: {patterns['slip_frequency']:.3f} events/second")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Mars Rover Wheel Test Data Analyzer')
    parser.add_argument('--file', help='CSV data file to analyze')
    parser.add_argument('--dir', default='data', help='Directory containing CSV files')
    parser.add_argument('--output', default='analysis', help='Output directory for analysis')
    parser.add_argument('--latest', action='store_true', help='Analyze the most recent file')
    
    args = parser.parse_args()
    
    # Determine which file to analyze
    if args.file:
        data_file = args.file
    elif args.latest:
        # Find most recent CSV file
        csv_files = glob.glob(os.path.join(args.dir, '*.csv'))
        if not csv_files:
            print("No CSV files found in data directory")
            return
        data_file = max(csv_files, key=os.path.getctime)
        print(f"Analyzing most recent file: {data_file}")
    else:
        # List available files
        csv_files = glob.glob(os.path.join(args.dir, '*.csv'))
        if not csv_files:
            print("No CSV files found in data directory")
            return
        
        print("Available CSV files:")
        for i, file in enumerate(csv_files):
            print(f"  {i+1}. {os.path.basename(file)}")
        
        try:
            choice = int(input("Select file number: ")) - 1
            data_file = csv_files[choice]
        except (ValueError, IndexError):
            print("Invalid selection")
            return
    
    # Run analysis
    analyzer = SlipAnalyzer(data_file, args.output)
    
    if analyzer.load_data(data_file):
        analyzer.generate_report()
    else:
        print("Failed to load data file")

if __name__ == '__main__':
    main() 