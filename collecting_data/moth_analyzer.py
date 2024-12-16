import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime
import argparse
from get_bounding_boxes import process_images_for_consistency, get_bounding_boxes

def classify_moth(length_mm):
    """
    Placeholder for future ML classification.
    Currently only returns 'unknown' for moths > 35mm
    """
    if length_mm > 35:
        return 'unknown'
    return None

class MothAnalyzerTest:
    def __init__(self, sample_dir, date_str, mm_per_pixel=0.0703):
        """
        Initialize the moth analyzer with sample directory.
        
        Parameters:
        - sample_dir: Directory containing the sample data
        - date_str: Date string in YYYY-MM-DD format for the sample data
        - mm_per_pixel: Calibration factor for converting pixels to millimeters
        """
        self.base_dir = os.path.abspath(sample_dir)
        self.date_str = date_str
        self.mm_per_pixel = mm_per_pixel
        
        # Set up directory paths
        self.attractive_dir = os.path.join(self.base_dir, self.date_str, "attractive_light")
        self.red_dir = os.path.join(self.base_dir, self.date_str, "red_light")
        self.analysis_dir = os.path.join(self.base_dir, self.date_str, "analysis")
        
        # Create analysis directory if it doesn't exist
        os.makedirs(self.analysis_dir, exist_ok=True)
        
        # Validate directories exist
        if not os.path.exists(self.attractive_dir):
            raise ValueError(f"Attractive light directory not found: {self.attractive_dir}")
        if not os.path.exists(self.red_dir):
            raise ValueError(f"Red light directory not found: {self.red_dir}")


    def measure_moth_dimensions(self, roi):
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        
        # Combine adaptive and global thresholding
        adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY_INV, 11, 2)
        _, global_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        thresh = cv2.addWeighted(adaptive_thresh, 0.7, global_thresh, 0.3, 0)
        
        # Clean up with morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0, 0, 0
        
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get all points from the contour
        points = largest_contour.reshape(-1, 2)
        
        # Calculate the convex hull to better handle potential concavities
        hull = cv2.convexHull(largest_contour)
        hull_points = hull.reshape(-1, 2)
        
        # Find the maximum distance between any two points on the hull
        max_length = 0
        max_width = 0
        angle = 0
        p1_max = None
        p2_max = None
        
        for i in range(len(hull_points)):
            for j in range(i + 1, len(hull_points)):
                pt1 = hull_points[i]
                pt2 = hull_points[j]
                
                # Calculate distance between points
                length = np.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)
                
                if length > max_length:
                    max_length = length
                    p1_max = pt1
                    p2_max = pt2
                    # Calculate angle with horizontal
                    angle = np.degrees(np.arctan2(pt2[1] - pt1[1], pt2[0] - pt1[0]))
                    
                    # Calculate width perpendicular to this length
                    # Convert points to numpy array for easier manipulation
                    points_arr = largest_contour.reshape(-1, 2)
                    
                    # Create vector in direction of length
                    length_vector = np.array([pt2 - pt1]) / np.linalg.norm(pt2 - pt1)
                    
                    # Create perpendicular vector
                    perp_vector = np.array([-length_vector[0][1], length_vector[0][0]])
                    
                    # Project all points onto perpendicular vector
                    projections = np.abs(np.dot(points_arr - pt1, perp_vector))
                    max_width = np.max(projections)
        
        return max_length, max_width, angle

    def create_measurement_visualization(self, roi, length_px, width_px, angle, moth_id):
        """
        Create and save visualization of moth measurements with rotated bounding box.
        """
        vis_img = roi.copy()
        height, width = vis_img.shape[:2]
        
        # Calculate center point
        center = (width // 2, height // 2)
        
        # Create rotated rectangle
        box = cv2.boxPoints(((center[0], center[1]), (length_px, width_px), angle))
        box = np.int0(box)
        
        # Draw the rotated rectangle
        cv2.drawContours(vis_img, [box], 0, (0, 255, 0), 2)
        
        # Convert measurements to mm
        length_mm = length_px * self.mm_per_pixel
        width_mm = width_px * self.mm_per_pixel
        
        # Add measurement text
        margin = 10
        cv2.putText(vis_img, f"Length: {length_mm:.1f}mm", (margin, height-margin),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(vis_img, f"Width: {width_mm:.1f}mm", (margin, height-margin-25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(vis_img, f"Angle: {angle:.1f}°", (margin, height-margin-50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save visualization
        output_path = os.path.join(self.analysis_dir, f"moth_{moth_id}_measurements.jpg")
        cv2.imwrite(output_path, vis_img)
        return vis_img

    def analyze_consistent_moths(self):
        """Analyze moths with measurement visualization"""
        # Get the last 3 images from attractive phase
        image_files = sorted([f for f in os.listdir(self.attractive_dir) if f.endswith('.jpg')])[-3:]
        image_paths = [os.path.join(self.attractive_dir, f) for f in image_files]
        
        print(f"Processing images: {image_files}")
        
        base_image = cv2.imread(image_paths[-1])
        if base_image is None:
            raise ValueError(f"Could not read image: {image_paths[-1]}")
        
        # Get consistent moth detections
        detection_vis_path = os.path.join(self.analysis_dir, "consistent_detections.jpg")
        consistent_boxes = process_images_for_consistency(image_paths, detection_vis_path)
        
        print(f"Found {len(consistent_boxes)} consistent moth detections")
        
        moth_data = []
        for i, box in enumerate(consistent_boxes):
            x, y, w, h = box
            roi = base_image[y:y+h, x:x+w]
            
            # Save ROI with timestamp
            timestamp = datetime.strptime(image_files[-1].replace('.jpg', ''), '%H-%M-%S')
            full_timestamp = datetime.combine(
                datetime.strptime(self.date_str, '%Y-%m-%d').date(),
                timestamp.time()
            )
            
            roi_filename = f"moth_{i+1}_at_{timestamp.strftime('%H-%M-%S')}.jpg"
            roi_path = os.path.join(self.analysis_dir, roi_filename)
            cv2.imwrite(roi_path, roi)
            print(f"Saved ROI: {roi_filename}")
            
            # Measure dimensions
            length_px, width_px, angle = self.measure_moth_dimensions(roi)
            
            # Create measurement visualization
            self.create_measurement_visualization(roi, length_px, width_px, angle, i+1)
            
            # Convert to mm and collect data
            length_mm = length_px * self.mm_per_pixel
            width_mm = width_px * self.mm_per_pixel
            area_mm2 = length_mm * width_mm
            
            species = classify_moth(length_mm)
            
            moth_data.append({
                'moth_id': i + 1,
                'date': self.date_str,
                'timestamp': full_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'position_x': x,
                'position_y': y,
                'length_mm': round(length_mm, 2),
                'width_mm': round(width_mm, 2),
                'area_mm2': round(area_mm2, 2),
                'species': species,
                'source_image': image_files[-1]
            })
        
        # Save measurements
        df = pd.DataFrame(moth_data)
        measurements_path = os.path.join(self.analysis_dir, "moth_measurements.csv")
        df.to_csv(measurements_path, index=False)
        print(f"Saved measurements to: {measurements_path}")
        return df

    def analyze_departures(self):
        """Analyze how quickly moths depart after red light is activated"""
        red_images = sorted([f for f in os.listdir(self.red_dir) if f.endswith('.jpg')])
        
        if not red_images:
            print("No red phase images found")
            return pd.DataFrame()
            
        departure_data = []
        
        # Get baseline image (last from attractive phase)
        last_attractive = sorted([f for f in os.listdir(self.attractive_dir) if f.endswith('.jpg')])[-1]
        baseline_path = os.path.join(self.attractive_dir, last_attractive)
        print(f"Using baseline image: {last_attractive}")
        
        # Get timestamp when red light was activated
        red_start_time = datetime.strptime(red_images[0].replace('.jpg', ''), '%H-%M-%S')
        print(f"Red light activated at: {red_start_time.strftime('%H:%M:%S')}")
        
        # Track departures through the sequence
        moths_present = None  # Will store initial moth count
        for i, img_name in enumerate(red_images):
            current_path = os.path.join(self.red_dir, img_name)
            
            # Get current moth positions
            current_boxes = get_bounding_boxes(current_path)
            
            # On first image, establish baseline count
            if i == 0:
                moths_present = len(current_boxes)
                print(f"Initial moth count: {moths_present}")
                continue
                
            # Calculate departures
            current_time = datetime.strptime(img_name.replace('.jpg', ''), '%H-%M-%S')
            time_since_red = (current_time - red_start_time).total_seconds() / 60  # Minutes
            
            moths_now = len(current_boxes)
            moths_departed = moths_present - moths_now if moths_now < moths_present else 0
            
            if moths_departed > 0:
                departure_data.append({
                    'date': self.date_str,
                    'time_since_red_minutes': round(time_since_red, 2),
                    'moths_departed': moths_departed,
                    'moths_remaining': moths_now,
                    'image_name': img_name
                })
                moths_present = moths_now  # Update baseline for next image
                
                print(f"At {time_since_red:.1f} minutes: {moths_departed} moth(s) departed")
        
        # Create DataFrame and save
        df = pd.DataFrame(departure_data)
        if not df.empty:
            departures_path = os.path.join(self.analysis_dir, "moth_departures.csv")
            df.to_csv(departures_path, index=False)
            print(f"\nSaved departure data to: {departures_path}")
        
        return df

    def validate_images(self):
        """Validate that all required images exist and are readable"""
        try:
            # Check attractive phase images
            attractive_images = sorted([f for f in os.listdir(self.attractive_dir) if f.endswith('.jpg')])
            if len(attractive_images) < 3:
                print(f"Error: Need at least 3 attractive phase images, found {len(attractive_images)}")
                return False

            # Check red phase images
            red_images = sorted([f for f in os.listdir(self.red_dir) if f.endswith('.jpg')])
            if not red_images:
                print("Warning: No red phase images found")
                return False

            # Test image reading
            test_image = cv2.imread(os.path.join(self.attractive_dir, attractive_images[-1]))
            if test_image is None:
                print("Error: Unable to read image files")
                return False

            print("Image validation passed")
            print(f"Found {len(attractive_images)} attractive phase images")
            print(f"Found {len(red_images)} red phase images")
            return True

        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def run_analysis(self):
        """Run complete analysis pipeline with validation and error handling"""
        try:
            print("\n=== Starting Moth Analysis ===")
            print(f"Sample directory: {self.base_dir}")
            print(f"Date: {self.date_str}")
            
            # Validate images before processing
            if not self.validate_images():
                print("Analysis aborted due to validation failure")
                return None
            
            print("\nAnalyzing consistent moths...")
            moth_measurements = self.analyze_consistent_moths()
            if not moth_measurements.empty:
                print(f"\nFound {len(moth_measurements)} consistent moths:")
                print(moth_measurements[['moth_id', 'length_mm', 'width_mm', 'species']].to_string())
            
            print("\nAnalyzing departures...")
            departure_data = self.analyze_departures()
            if not departure_data.empty:
                print("\nDeparture summary:")
                print(departure_data.to_string())
            
            print("\n=== Analysis Complete ===")
            print(f"Results saved in: {self.analysis_dir}")
            
            return {
                'measurements': moth_measurements,
                'departures': departure_data
            }
        except Exception as e:
            print(f"\nError in analysis pipeline: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

def main():
    """Test the analysis on sample data with user input"""
    print("\n=== Moth Analysis Test Tool ===")
    
    # Get sample directory path
    while True:
        sample_dir = input("\nEnter the path to your sample data directory: ").strip()
        sample_dir = os.path.expanduser(sample_dir)  # Expand ~ if used
        
        if os.path.exists(sample_dir):
            # List available dates
            dates = [d for d in os.listdir(sample_dir) 
                    if os.path.isdir(os.path.join(sample_dir, d)) 
                    and d.count('-') == 2]  # Basic date format validation
            
            if dates:
                print("\nAvailable dates:")
                for i, date in enumerate(sorted(dates), 1):
                    print(f"{i}. {date}")
                
                # Get date selection
                while True:
                    try:
                        selection = input("\nEnter the number of the date to analyze (or 'q' to quit): ").strip()
                        if selection.lower() == 'q':
                            return
                        
                        idx = int(selection) - 1
                        if 0 <= idx < len(dates):
                            date_str = dates[idx]
                            break
                        else:
                            print("Invalid selection. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                # Optional: Get calibration factor
                while True:
                    cal_input = input("\nEnter mm per pixel calibration factor (press Enter for default 0.203): ").strip()
                    if not cal_input:
                        mm_per_pixel = 0.0703
                        break
                    try:
                        mm_per_pixel = float(cal_input)
                        if mm_per_pixel > 0:
                            break
                        else:
                            print("Calibration factor must be positive.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                # Run analysis
                print(f"\nAnalyzing data from {date_str} with calibration factor {mm_per_pixel} mm/pixel...")
                try:
                    analyzer = MothAnalyzerTest(sample_dir, date_str, mm_per_pixel)
                    results = analyzer.run_analysis()
                    
                    if results:
                        print("\nAnalysis completed successfully!")
                        print("\nResults can be found in:")
                        print(f"1. {os.path.join(analyzer.analysis_dir, 'moth_measurements.csv')}")
                        print(f"2. {os.path.join(analyzer.analysis_dir, 'moth_departures.csv')}")
                        print(f"3. ROI and measurement images in: {analyzer.analysis_dir}")
                
                except Exception as e:
                    print(f"\nError running analysis: {e}")
                    import traceback
                    print(traceback.format_exc())
                
                # Ask if user wants to analyze another date
                if input("\nWould you like to analyze another date? (y/n): ").lower() != 'y':
                    break
            else:
                print("No valid date directories found.")
                if input("\nWould you like to try another directory? (y/n): ").lower() != 'y':
                    break
        else:
            print("Directory not found.")
            if input("\nWould you like to try again? (y/n): ").lower() != 'y':
                break
    
    print("\nAnalysis complete. Goodbye!")

if __name__ == "__main__":
    main()
