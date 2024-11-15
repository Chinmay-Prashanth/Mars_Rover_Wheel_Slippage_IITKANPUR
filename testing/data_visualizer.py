#!/usr/bin/env python3
"""
Mars Rover Single Wheel Test Bench - Data Visualizer
Generates plots and visualizations from collected wheel slippage data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
import argparse
import os
import glob
from datetime import datetime, timedelta

class SlipVisualizer:
    def __init__(self, output_dir='plots'):
        self.output_dir = output_dir
        self.data = None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
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
            
            # Convert elapsed time to seconds
            self.data['ElapsedTime_s'] = self.data['ElapsedTime'] / 1000.0
            
            print(f"Loaded {len(self.data)} data points from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def plot_time_series(self):
        """Create time series plots of all sensors"""
        if self.data is None:
            return
            
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        fig.suptitle('Mars Rover Wheel Test - Time Series Data', fontsize=16)
        
        # Plot 1: Encoder Count vs Expected Rotation
        axes[0].plot(self.data['ElapsedTime_s'], self.data['EncoderCount'], 
                    label='Actual Encoder Count', linewidth=1)
        axes[0].plot(self.data['ElapsedTime_s'], self.data['ExpectedRotation'], 
                    label='Expected Rotation', linewidth=1, linestyle='--')
        axes[0].set_ylabel('Encoder Count')
        axes[0].set_title('Encoder Count vs Expected Rotation')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Slip Percentage
        axes[1].plot(self.data['ElapsedTime_s'], self.data['SlipPercentage'], 
                    color='red', linewidth=1)
        axes[1].axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='Slip Threshold')
        axes[1].axhline(y=-5, color='orange', linestyle='--', alpha=0.7)
        axes[1].set_ylabel('Slip Percentage (%)')
        axes[1].set_title('Wheel Slip Percentage Over Time')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Load Cell Reading
        axes[2].plot(self.data['ElapsedTime_s'], self.data['LoadCellReading'], 
                    color='green', linewidth=1)
        axes[2].set_ylabel('Load Cell Reading')
        axes[2].set_title('Load Cell Force/Torque Measurement')
        axes[2].grid(True, alpha=0.3)
        
        # Plot 4: Motor Current
        axes[3].plot(self.data['ElapsedTime_s'], self.data['MotorCurrent'], 
                    color='purple', linewidth=1)
        axes[3].set_ylabel('Motor Current (A)')
        axes[3].set_xlabel('Time (seconds)')
        axes[3].set_title('Motor Current Consumption')
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'time_series_plot.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_slip_analysis(self):
        """Create slip-specific analysis plots"""
        if self.data is None:
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Mars Rover Wheel Slip Analysis', fontsize=16)
        
        # Plot 1: Slip Distribution
        axes[0,0].hist(self.data['SlipPercentage'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0,0].axvline(x=self.data['SlipPercentage'].mean(), color='red', 
                         linestyle='--', label=f'Mean: {self.data["SlipPercentage"].mean():.2f}%')
        axes[0,0].set_xlabel('Slip Percentage (%)')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].set_title('Slip Percentage Distribution')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Slip vs Load Cell
        axes[0,1].scatter(self.data['LoadCellReading'], self.data['SlipPercentage'], 
                         alpha=0.5, s=10)
        axes[0,1].set_xlabel('Load Cell Reading')
        axes[0,1].set_ylabel('Slip Percentage (%)')
        axes[0,1].set_title('Slip vs Load Cell Reading')
        axes[0,1].grid(True, alpha=0.3)
        
        # Add correlation coefficient
        corr = self.data['SlipPercentage'].corr(self.data['LoadCellReading'])
        axes[0,1].text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                      transform=axes[0,1].transAxes, fontsize=10, 
                      verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Plot 3: Slip vs Motor Current
        axes[1,0].scatter(self.data['MotorCurrent'], self.data['SlipPercentage'], 
                         alpha=0.5, s=10, color='orange')
        axes[1,0].set_xlabel('Motor Current (A)')
        axes[1,0].set_ylabel('Slip Percentage (%)')
        axes[1,0].set_title('Slip vs Motor Current')
        axes[1,0].grid(True, alpha=0.3)
        
        # Add correlation coefficient
        corr = self.data['SlipPercentage'].corr(self.data['MotorCurrent'])
        axes[1,0].text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                      transform=axes[1,0].transAxes, fontsize=10, 
                      verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Plot 4: Direction Analysis
        forward_data = self.data[self.data['Direction'] == True]
        reverse_data = self.data[self.data['Direction'] == False]
        
        axes[1,1].hist(forward_data['SlipPercentage'], bins=30, alpha=0.7, 
                      label='Forward', color='green', edgecolor='black')
        axes[1,1].hist(reverse_data['SlipPercentage'], bins=30, alpha=0.7, 
                      label='Reverse', color='red', edgecolor='black')
        axes[1,1].set_xlabel('Slip Percentage (%)')
        axes[1,1].set_ylabel('Frequency')
        axes[1,1].set_title('Slip Distribution by Direction')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'slip_analysis_plot.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_sensor_correlations(self):
        """Create correlation matrix and scatter plots"""
        if self.data is None:
            return
            
        # Select numerical columns for correlation
        sensor_cols = ['EncoderCount', 'ExpectedRotation', 'SlipPercentage', 
                      'LoadCellReading', 'CurrentSensor', 'MotorCurrent']
        
        # Calculate correlation matrix
        corr_matrix = self.data[sensor_cols].corr()
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Sensor Correlation Analysis', fontsize=16)
        
        # Plot 1: Correlation Heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=axes[0])
        axes[0].set_title('Sensor Correlation Matrix')
        
        # Plot 2: Pairwise relationships
        # Create a subset of the most interesting relationships
        axes[1].scatter(self.data['LoadCellReading'], self.data['MotorCurrent'], 
                       c=self.data['SlipPercentage'], cmap='viridis', alpha=0.6, s=10)
        axes[1].set_xlabel('Load Cell Reading')
        axes[1].set_ylabel('Motor Current (A)')
        axes[1].set_title('Load Cell vs Motor Current\n(colored by Slip %)')
        
        # Add colorbar
        scatter = axes[1].scatter(self.data['LoadCellReading'], self.data['MotorCurrent'], 
                                 c=self.data['SlipPercentage'], cmap='viridis', alpha=0.6, s=10)
        plt.colorbar(scatter, ax=axes[1], label='Slip Percentage (%)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'sensor_correlations.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_moving_averages(self):
        """Plot moving averages to show trends"""
        if self.data is None:
            return
            
        # Calculate moving averages
        window_sizes = [10, 50, 100]
        
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle('Moving Average Analysis', fontsize=16)
        
        # Plot 1: Slip Percentage Moving Averages
        axes[0].plot(self.data['ElapsedTime_s'], self.data['SlipPercentage'], 
                    alpha=0.3, color='gray', linewidth=0.5, label='Raw Data')
        
        for window in window_sizes:
            ma = self.data['SlipPercentage'].rolling(window=window).mean()
            axes[0].plot(self.data['ElapsedTime_s'], ma, 
                        label=f'{window}-point Moving Average', linewidth=2)
        
        axes[0].set_ylabel('Slip Percentage (%)')
        axes[0].set_title('Slip Percentage Moving Averages')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Motor Current Moving Averages
        axes[1].plot(self.data['ElapsedTime_s'], self.data['MotorCurrent'], 
                    alpha=0.3, color='gray', linewidth=0.5, label='Raw Data')
        
        for window in window_sizes:
            ma = self.data['MotorCurrent'].rolling(window=window).mean()
            axes[1].plot(self.data['ElapsedTime_s'], ma, 
                        label=f'{window}-point Moving Average', linewidth=2)
        
        axes[1].set_ylabel('Motor Current (A)')
        axes[1].set_xlabel('Time (seconds)')
        axes[1].set_title('Motor Current Moving Averages')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'moving_averages.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_slip_events(self):
        """Highlight slip events in the data"""
        if self.data is None:
            return
            
        # Define slip threshold
        slip_threshold = 5.0
        slip_events = abs(self.data['SlipPercentage']) > slip_threshold
        
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        fig.suptitle('Slip Event Detection and Analysis', fontsize=16)
        
        # Plot 1: Slip events over time
        axes[0].plot(self.data['ElapsedTime_s'], self.data['SlipPercentage'], 
                    color='blue', linewidth=1, alpha=0.7, label='Slip Percentage')
        axes[0].scatter(self.data[slip_events]['ElapsedTime_s'], 
                       self.data[slip_events]['SlipPercentage'], 
                       color='red', s=20, alpha=0.8, label='Slip Events')
        axes[0].axhline(y=slip_threshold, color='orange', linestyle='--', alpha=0.7)
        axes[0].axhline(y=-slip_threshold, color='orange', linestyle='--', alpha=0.7)
        axes[0].set_ylabel('Slip Percentage (%)')
        axes[0].set_title('Slip Events Over Time')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Load cell during slip events
        axes[1].plot(self.data['ElapsedTime_s'], self.data['LoadCellReading'], 
                    color='green', linewidth=1, alpha=0.7, label='Load Cell')
        axes[1].scatter(self.data[slip_events]['ElapsedTime_s'], 
                       self.data[slip_events]['LoadCellReading'], 
                       color='red', s=20, alpha=0.8, label='During Slip')
        axes[1].set_ylabel('Load Cell Reading')
        axes[1].set_title('Load Cell Reading During Slip Events')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Motor current during slip events
        axes[2].plot(self.data['ElapsedTime_s'], self.data['MotorCurrent'], 
                    color='purple', linewidth=1, alpha=0.7, label='Motor Current')
        axes[2].scatter(self.data[slip_events]['ElapsedTime_s'], 
                       self.data[slip_events]['MotorCurrent'], 
                       color='red', s=20, alpha=0.8, label='During Slip')
        axes[2].set_ylabel('Motor Current (A)')
        axes[2].set_xlabel('Time (seconds)')
        axes[2].set_title('Motor Current During Slip Events')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'slip_events.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
    def generate_all_plots(self):
        """Generate all visualization plots"""
        if self.data is None:
            print("No data loaded")
            return
            
        print("Generating visualizations...")
        
        self.plot_time_series()
        print("✓ Time series plot generated")
        
        self.plot_slip_analysis()
        print("✓ Slip analysis plot generated")
        
        self.plot_sensor_correlations()
        print("✓ Sensor correlation plot generated")
        
        self.plot_moving_averages()
        print("✓ Moving averages plot generated")
        
        self.plot_slip_events()
        print("✓ Slip events plot generated")
        
        print(f"\nAll plots saved to: {self.output_dir}/")
        
    def create_summary_dashboard(self):
        """Create a comprehensive dashboard"""
        if self.data is None:
            return
            
        fig = plt.figure(figsize=(20, 15))
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # Main title
        fig.suptitle('Mars Rover Single Wheel Test - Comprehensive Dashboard', fontsize=20)
        
        # Time series plots
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(self.data['ElapsedTime_s'], self.data['SlipPercentage'], 'b-', linewidth=1)
        ax1.set_title('Slip Percentage Over Time')
        ax1.set_ylabel('Slip (%)')
        ax1.grid(True, alpha=0.3)
        
        ax2 = fig.add_subplot(gs[0, 2:])
        ax2.plot(self.data['ElapsedTime_s'], self.data['MotorCurrent'], 'r-', linewidth=1)
        ax2.set_title('Motor Current Over Time')
        ax2.set_ylabel('Current (A)')
        ax2.grid(True, alpha=0.3)
        
        # Scatter plots
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.scatter(self.data['LoadCellReading'], self.data['SlipPercentage'], alpha=0.5, s=5)
        ax3.set_xlabel('Load Cell')
        ax3.set_ylabel('Slip (%)')
        ax3.set_title('Slip vs Load')
        ax3.grid(True, alpha=0.3)
        
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.scatter(self.data['MotorCurrent'], self.data['SlipPercentage'], alpha=0.5, s=5)
        ax4.set_xlabel('Motor Current')
        ax4.set_ylabel('Slip (%)')
        ax4.set_title('Slip vs Current')
        ax4.grid(True, alpha=0.3)
        
        # Histograms
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.hist(self.data['SlipPercentage'], bins=30, alpha=0.7, color='skyblue')
        ax5.set_xlabel('Slip (%)')
        ax5.set_ylabel('Frequency')
        ax5.set_title('Slip Distribution')
        ax5.grid(True, alpha=0.3)
        
        ax6 = fig.add_subplot(gs[1, 3])
        ax6.hist(self.data['MotorCurrent'], bins=30, alpha=0.7, color='orange')
        ax6.set_xlabel('Current (A)')
        ax6.set_ylabel('Frequency')
        ax6.set_title('Current Distribution')
        ax6.grid(True, alpha=0.3)
        
        # Correlation heatmap
        ax7 = fig.add_subplot(gs[2, :2])
        sensor_cols = ['SlipPercentage', 'LoadCellReading', 'MotorCurrent', 'EncoderCount']
        corr_matrix = self.data[sensor_cols].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax7)
        ax7.set_title('Sensor Correlations')
        
        # Direction analysis
        ax8 = fig.add_subplot(gs[2, 2:])
        forward_data = self.data[self.data['Direction'] == True]
        reverse_data = self.data[self.data['Direction'] == False]
        ax8.hist(forward_data['SlipPercentage'], bins=20, alpha=0.7, label='Forward', color='green')
        ax8.hist(reverse_data['SlipPercentage'], bins=20, alpha=0.7, label='Reverse', color='red')
        ax8.set_xlabel('Slip (%)')
        ax8.set_ylabel('Frequency')
        ax8.set_title('Slip by Direction')
        ax8.legend()
        ax8.grid(True, alpha=0.3)
        
        # Statistics summary
        ax9 = fig.add_subplot(gs[3, :])
        ax9.axis('off')
        
        # Calculate statistics
        stats_text = f"""
        TEST STATISTICS:
        Duration: {self.data['ElapsedTime_s'].max():.1f} seconds
        Samples: {len(self.data)}
        
        SLIP ANALYSIS:
        Mean Slip: {self.data['SlipPercentage'].mean():.2f}%
        Std Dev: {self.data['SlipPercentage'].std():.2f}%
        Max Slip: {self.data['SlipPercentage'].max():.2f}%
        Min Slip: {self.data['SlipPercentage'].min():.2f}%
        
        CORRELATIONS:
        Slip vs Load: {self.data['SlipPercentage'].corr(self.data['LoadCellReading']):.3f}
        Slip vs Current: {self.data['SlipPercentage'].corr(self.data['MotorCurrent']):.3f}
        Load vs Current: {self.data['LoadCellReading'].corr(self.data['MotorCurrent']):.3f}
        """
        
        ax9.text(0.1, 0.5, stats_text, transform=ax9.transAxes, fontsize=12, 
                verticalalignment='center', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.savefig(os.path.join(self.output_dir, 'dashboard.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Comprehensive dashboard generated")

def main():
    parser = argparse.ArgumentParser(description='Mars Rover Wheel Test Data Visualizer')
    parser.add_argument('--file', help='CSV data file to visualize')
    parser.add_argument('--dir', default='data', help='Directory containing CSV files')
    parser.add_argument('--output', default='plots', help='Output directory for plots')
    parser.add_argument('--latest', action='store_true', help='Visualize the most recent file')
    parser.add_argument('--dashboard', action='store_true', help='Generate comprehensive dashboard')
    
    args = parser.parse_args()
    
    # Determine which file to visualize
    if args.file:
        data_file = args.file
    elif args.latest:
        # Find most recent CSV file
        csv_files = glob.glob(os.path.join(args.dir, '*.csv'))
        if not csv_files:
            print("No CSV files found in data directory")
            return
        data_file = max(csv_files, key=os.path.getctime)
        print(f"Visualizing most recent file: {data_file}")
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
    
    # Generate visualizations
    visualizer = SlipVisualizer(args.output)
    
    if visualizer.load_data(data_file):
        if args.dashboard:
            visualizer.create_summary_dashboard()
        else:
            visualizer.generate_all_plots()
    else:
        print("Failed to load data file")

if __name__ == '__main__':
    main() 