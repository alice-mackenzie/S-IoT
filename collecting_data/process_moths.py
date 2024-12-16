import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import shutil
from moth_analyzer import MothAnalyzerTest

class ProcessMoths:
    def __init__(self):
        """Initialize paths for moth processing"""
        # Base paths
        self.base_dir = os.path.expanduser("~/Documents")
        self.collecting_data_dir = os.path.join(self.base_dir, "collecting_data")
        self.moths_dir = os.path.join(self.collecting_data_dir, "moths")
        self.images_dir = os.path.join(self.moths_dir, "images")
        self.data_dir = os.path.join(self.base_dir, "app/data")
        self.measurements_csv = os.path.join(self.data_dir, "moth_measurements.csv")

        # Ensure required directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def cleanup_old_directories(self):
        """Remove image directories older than 7 days"""
        current_date = datetime.now()
        
        for date_dir in os.listdir(self.images_dir):
            try:
                dir_path = os.path.join(self.images_dir, date_dir)
                if not os.path.isdir(dir_path):
                    continue
                    
                # Parse directory name as date
                dir_date = datetime.strptime(date_dir, '%Y-%m-%d')
                
                # Check if older than 7 days
                if (current_date - dir_date).days > 7:
                    shutil.rmtree(dir_path)
                    print(f"Removed old directory: {date_dir}")
            except ValueError:
                # Skip directories that don't match date format
                continue
            except Exception as e:
                print(f"Error cleaning up directory {date_dir}: {str(e)}")

    def process_latest_session(self):
        """Process the most recent image session"""
        try:
            # Get latest date directory
            date_dirs = [d for d in os.listdir(self.images_dir) 
                        if os.path.isdir(os.path.join(self.images_dir, d))]
            
            if not date_dirs:
                print("No image directories found.")
                return False
                
            latest_date = max(date_dirs)
            print(f"Processing session: {latest_date}")
            
            # Initialize analyzer with the moths directory (parent of images)
            analyzer = MothAnalyzerTest(
                sample_dir=self.moths_dir,
                date_str=latest_date,
                mm_per_pixel=0.0703  # Using your calibrated value
            )
            
            # Run analysis
            results = analyzer.run_analysis()
            
            if results and not results['measurements'].empty:
                # Update measurements CSV
                self.update_measurements(results['measurements'])
                print(f"Successfully processed {latest_date}")
                return True
            else:
                print(f"No valid measurements found for {latest_date}")
                return False
                
        except Exception as e:
            print(f"Error processing session: {str(e)}")
            return False

    def update_measurements(self, new_measurements):
        """Update the measurements CSV with new data"""
        try:
            if os.path.exists(self.measurements_csv):
                # Load existing data
                master_df = pd.read_csv(self.measurements_csv)
                
                # Check if this data is already in the master CSV
                existing_dates = master_df['date'].unique()
                new_dates = new_measurements['date'].unique()
                
                # Only append if we have new dates
                if not any(date in existing_dates for date in new_dates):
                    # Append new data
                    master_df = pd.concat([master_df, new_measurements], ignore_index=True)
                else:
                    print("This data appears to already be in the master CSV. Skipping update.")
                    return
            else:
                master_df = new_measurements
            
            # Sort by date and time
            master_df.sort_values(['date', 'timestamp'], inplace=True)
            
            # Save updated data
            master_df.to_csv(self.measurements_csv, index=False)
            print(f"Updated measurements CSV: {self.measurements_csv}")
            
        except Exception as e:
            print(f"Error updating measurements CSV: {str(e)}")
            raise

def process_moths():
    """Function to be called after data collection"""
    try:
        processor = ProcessMoths()
        
        # Clean up old directories
        processor.cleanup_old_directories()
        
        # Process latest session
        success = processor.process_latest_session()
        
        if success:
            print("Processing completed successfully")
        else:
            print("Processing completed with errors")
            
    except Exception as e:
        print(f"Error in moth processing: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    process_moths()
