import cv2
import numpy as np

def get_bounding_boxes(image_path, mm_per_pixel=0.2033, min_size_mm=10, max_size_mm=70):
    """
    Detects bounding boxes for moths in the image.

    Parameters:
    - image_path: Path to the image.
    - mm_per_pixel: Conversion ratio from mm to pixels.
    - min_size_mm: Minimum size of the moth in mm.
    - max_size_mm: Maximum size of the moth in mm.

    Returns:
    - List of bounding boxes [(x, y, w, h), ...]
    """
    # Convert size constraints from mm to pixels
    min_contour_area = (min_size_mm / mm_per_pixel) ** 2
    max_contour_area = (max_size_mm / mm_per_pixel) ** 2

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return []

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(enhanced_gray, (5, 5), 0)

    # Adaptive thresholding for smaller moths
    adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Global thresholding for larger moths
    _, global_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Combine both thresholds
    combined_thresh = cv2.addWeighted(adaptive_thresh, 0.7, global_thresh, 0.3, 0)

    # Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned_thresh = cv2.morphologyEx(combined_thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(cleaned_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bounding_boxes = []
    for contour in contours:
        # Filter by area
        area = cv2.contourArea(contour)
        if min_contour_area < area < max_contour_area:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Additional filter: Aspect ratio and extent
            aspect_ratio = w / h
            rect_area = w * h
            extent = area / rect_area

            if 0.5 < aspect_ratio < 2.0 and extent > 0.3:  # Reasonable filters
                bounding_boxes.append((x, y, w, h))

    return bounding_boxes

def compare_bounding_boxes(boxes1, boxes2, boxes3, threshold=20):
    """
    Compares bounding boxes across three images to classify detections based on consistency.
    Returns three lists of boxes based on how many images they appear in.

    Parameters:
    - boxes1, boxes2, boxes3: Lists of bounding boxes [(x, y, w, h), ...] from three images
    - threshold: Maximum distance between centers of bounding boxes to consider them as the same moth

    Returns:
    - Tuple of three lists: (boxes_in_one_image, boxes_in_two_images, boxes_in_three_images)
    """
    def box_center(box):
        x, y, w, h = box
        return (x + w / 2, y + h / 2)

    def is_close(center1, center2, threshold):
        return np.linalg.norm(np.array(center1) - np.array(center2)) < threshold

    boxes_in_one_image = []
    boxes_in_two_images = []
    boxes_in_three_images = []
    
    used_boxes2 = set()
    used_boxes3 = set()

    # For each box in the first image
    for i, box1 in enumerate(boxes1):
        center1 = box_center(box1)
        
        # Find matches in second image
        matches2 = [(j, box2) for j, box2 in enumerate(boxes2) 
                   if j not in used_boxes2 and is_close(center1, box_center(box2), threshold)]
        
        if matches2:
            # For each potential match in second image
            for j, box2 in matches2:
                center2 = box_center(box2)
                
                # Find matches in third image
                matches3 = [(k, box3) for k, box3 in enumerate(boxes3) 
                           if k not in used_boxes3 and is_close(center2, box_center(box3), threshold)]
                
                if matches3:
                    # Use the first matching box from image 3
                    k, box3 = matches3[0]
                    boxes_in_three_images.append(box3)  # Use coordinates from the last image
                    used_boxes2.add(j)
                    used_boxes3.add(k)
                    break  # Move to next box in image 1
                else:
                    boxes_in_two_images.append(box2)
                    used_boxes2.add(j)
        else:
            boxes_in_one_image.append(box1)

    # Add remaining unmatched boxes from image 2
    for j, box2 in enumerate(boxes2):
        if j not in used_boxes2:
            boxes_in_one_image.append(box2)

    # Add remaining unmatched boxes from image 3
    for k, box3 in enumerate(boxes3):
        if k not in used_boxes3:
            boxes_in_one_image.append(box3)

    return boxes_in_one_image, boxes_in_two_images, boxes_in_three_images

def process_images_for_consistency(image_paths, output_path):
    """
    Process three consecutive images to identify moths based on consistency.

    Parameters:
    - image_paths: List of three image paths
    - output_path: Path to save the final visualization

    Returns:
    - List of bounding boxes that appear in three images
    """
    if len(image_paths) != 3:
        print("Error: Exactly three images are required.")
        return []

    # Get bounding boxes for each image
    boxes1 = get_bounding_boxes(image_paths[0])
    boxes2 = get_bounding_boxes(image_paths[1])
    boxes3 = get_bounding_boxes(image_paths[2])

    # Classify detections based on consistency
    boxes_in_one_image, boxes_in_two_images, boxes_in_three_images = compare_bounding_boxes(boxes1, boxes2, boxes3)

    # Load the first image for visualization
    image = cv2.imread(image_paths[0])

    # Draw bounding boxes with different colors
    for box in boxes_in_one_image:
        x, y, w, h = box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red for one image
    for box in boxes_in_two_images:
        x, y, w, h = box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 165, 255), 2)  # Orange for two images
    for box in boxes_in_three_images:
        x, y, w, h = box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green for three images

    # Save the output visualization
    cv2.imwrite(output_path, image)
    print(f"Visualization saved to {output_path}.")
    
    # Return only the boxes that appear in three images
    return boxes_in_three_images
