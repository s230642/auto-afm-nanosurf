import cv2 as cv
import numpy as np
import pyautogui


# --- inputs ---
top_view_x = -708
top_view_y = 264
top_view_width = 630
top_view_height = 470

screenshot = pyautogui.screenshot(region=(top_view_x, top_view_y, top_view_width, top_view_height))
screenshot.save("screenshot.png")

frame =  cv.imread(r"C:\Users\spill\Downloads\sample_screenshot.png")          # your grab function
flat = cv.imread(r"C:\Users\spill\Downloads\closeup empty sample.png")          # empty-dish reference, same exposure

def preprocess(img, flat):
    g = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    flat_gray = cv.cvtColor(flat, cv.COLOR_BGR2GRAY)
    ff = cv.divide(g, flat_gray, scale=128)  
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(ff)

def detect_cantilever(g):
    """Improved cantilever detection with multiple methods"""
    h, w = g.shape
    
    # Method 1: Original Hough line detection
    edges = cv.Canny(g, 30, 100)  # Lowered thresholds for better edge detection
    lines = cv.HoughLinesP(edges, 1, np.pi/180, threshold=50,  # Lowered threshold
                           minLineLength=int(0.2*h), maxLineGap=15)  # More lenient parameters
    
    best = None
    if lines is not None:
        for (x1,y1,x2,y2) in lines[:,0]:
            dx, dy = x2-x1, y2-y1
            # Look for near-vertical lines (allow more angle variation)
            if abs(dx) < 8 and abs(dy) > 20:  # More lenient vertical detection
                x = (x1+x2)//2
                # Prefer lines in upper portion of image (cantilevers are usually there)
                y_avg = (y1+y2)//2
                if y_avg < h * 0.7:  # Upper 70% of image
                    if best is None or abs(x-w//2) < abs(best-w//2):
                        best = x
    
    if best is not None:
        return best
    
    # Method 2: Look for dark vertical features using morphology
    # Create vertical structuring element
    vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, max(10, h//20)))
    
    # Enhance vertical features
    vertical_enhanced = cv.morphologyEx(g, cv.MORPH_BLACKHAT, vertical_kernel)
    
    # Threshold to find dark vertical features
    _, vertical_thresh = cv.threshold(vertical_enhanced, 30, 255, cv.THRESH_BINARY)
    
    # Find contours of vertical features
    contours, _ = cv.findContours(vertical_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    best_x, best_score = None, 0
    for contour in contours:
        x, y, bw, bh = cv.boundingRect(contour)
        
        # Check if it's a good cantilever candidate
        aspect_ratio = bh / max(bw, 1)
        area = cv.contourArea(contour)
        
        # Should be tall, thin, and in upper portion
        if (aspect_ratio > 5 and  # Tall and thin
            bh > h * 0.15 and     # At least 15% of image height
            y < h * 0.6 and       # Starts in upper 60% of image
            area > 50):           # Reasonable size
            
            score = aspect_ratio * bh  # Prefer taller, thinner features
            if score > best_score:
                best_score = score
                best_x = x + bw // 2
    
    if best_x is not None:
        return best_x
    
    # Method 3: Column-wise analysis for consistent dark vertical features
    # Look in upper portion of image
    upper_region = g[0:h//2, :]
    
    # Calculate column-wise statistics
    col_means = np.mean(upper_region, axis=0)
    col_stds = np.std(upper_region, axis=0)
    overall_mean = np.mean(col_means)
    
    # Find columns that are consistently darker
    dark_threshold = overall_mean - 0.5 * np.std(col_means)
    dark_columns = np.where(col_means < dark_threshold)[0]
    
    if len(dark_columns) > 0:
        # Find the longest continuous sequence of dark columns
        sequences = []
        current_seq = [dark_columns[0]]
        
        for i in range(1, len(dark_columns)):
            if dark_columns[i] - dark_columns[i-1] <= 2:  # Allow small gaps
                current_seq.append(dark_columns[i])
            else:
                if len(current_seq) >= 3:  # At least 3 pixels wide
                    sequences.append(current_seq)
                current_seq = [dark_columns[i]]
        
        if len(current_seq) >= 3:
            sequences.append(current_seq)
        
        if sequences:
            # Choose the sequence closest to center
            best_seq = min(sequences, key=lambda seq: abs(np.mean(seq) - w//2))
            return int(np.mean(best_seq))
    
    return None  # No cantilever found

def sample_mask(g, exclude_cantilever_region=True, x_cant=None):
    """Create mask for sample detection, optionally excluding cantilever area"""
    
    # Method 1: Simple threshold to find dark features (samples are dark!)
    # First, find a good threshold value
    mean_val = np.mean(g)
    std_val = np.std(g)
    threshold_val = max(50, int(mean_val - 0.5 * std_val))  # Below average intensity
    
    _, th = cv.threshold(g, threshold_val, 255, cv.THRESH_BINARY_INV)
    
    # Alternative: Try Otsu if simple threshold doesn't work well
    # _, th = cv.threshold(g, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    
    # Exclude cantilever region to avoid interference
    if exclude_cantilever_region and x_cant is not None:
        h, w = th.shape
        # Mask out cantilever area (vertical strip around cantilever)
        cant_width = 20  # pixels on each side of cantilever to exclude
        x_start = max(0, x_cant - cant_width)
        x_end = min(w, x_cant + cant_width)
        th[:, x_start:x_end] = 0
    
    # More aggressive noise removal for small dark features
    # Remove very small noise
    th = cv.morphologyEx(th, cv.MORPH_OPEN, np.ones((2,2), np.uint8))  
    # Fill small holes in features
    th = cv.morphologyEx(th, cv.MORPH_CLOSE, np.ones((3,3), np.uint8))
    
    # Remove features that are too small to be real samples
    min_contour_area = 20  # Adjust based on your sample size
    contours, _ = cv.findContours(th, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    mask_cleaned = np.zeros_like(th)
    for contour in contours:
        if cv.contourArea(contour) >= min_contour_area:
            cv.drawContours(mask_cleaned, [contour], -1, 255, -1)
    
    return mask_cleaned

def detect_sample_features(g, mask, x_cant=None):
    """Detect sample features while considering cantilever position"""
    # Find connected components
    num_labels, labels, stats, cents = cv.connectedComponentsWithStats(mask, connectivity=8)
    
    if num_labels <= 1:  # Only background found
        return None, 0, 0
    
    # Filter components by size, shape, and intensity
    valid_components = []
    min_area = 20  # Minimum area for a valid sample feature
    max_area = 2000  # Reasonable max area for particles
    h, w = g.shape
    
    for i in range(1, num_labels):  # Skip background (label 0)
        area = stats[i, cv.CC_STAT_AREA]
        if min_area < area < max_area:
            cy, cx = cents[i][1], cents[i][0]
            x = stats[i, cv.CC_STAT_LEFT]
            y = stats[i, cv.CC_STAT_TOP]
            width = stats[i, cv.CC_STAT_WIDTH]
            height = stats[i, cv.CC_STAT_HEIGHT]
            
            # Check if component is reasonably compact (not a line artifact)
            aspect_ratio = max(width, height) / max(min(width, height), 1)
            if aspect_ratio < 4:  # Reject very elongated features
                
                # Check average intensity in original image at this location
                component_mask = (labels == i).astype(np.uint8) * 255
                masked_region = cv.bitwise_and(g, g, mask=component_mask)
                avg_intensity = np.mean(masked_region[masked_region > 0])
                
                # Only accept dark features (samples should be darker than background)
                if avg_intensity < np.mean(g) * 0.8:  # 20% darker than average
                    valid_components.append((i, area, cx, cy, avg_intensity))
    
    if not valid_components:
        return None, 0, 0
    
    # Choose the best component for targeting
    # Strategy: Prefer larger, darker features
    # Score = area_score + darkness_score
    scored_components = []
    max_area = max(comp[1] for comp in valid_components)
    min_intensity = min(comp[4] for comp in valid_components)
    
    for comp in valid_components:
        idx, area, cx, cy, intensity = comp
        area_score = area / max_area  # 0-1
        darkness_score = (np.mean(g) - intensity) / np.mean(g)  # Higher for darker
        total_score = area_score + darkness_score
        scored_components.append((total_score, idx, area, cx, cy))
    
    # Get the highest scoring component
    best_comp = max(scored_components, key=lambda x: x[0])
    score, idx, area, cx, cy = best_comp
    
    return idx, cx, cy

# Main processing
g = preprocess(frame, flat)

# Cantilever is always at fixed position (set these to your actual cantilever coordinates)
x_cant = 189  # Replace with your actual cantilever x-position in pixels
y_cant = 235  # Replace with your actual cantilever y-position in pixels

# Create sample mask (excluding cantilever region)
mask = sample_mask(g, exclude_cantilever_region=True, x_cant=x_cant)

# Check for sample under cantilever (improved method using x,y position)
over_sample = False
cantilever_sample_info = ""

if x_cant is not None and y_cant is not None:
    h, w = g.shape
    
    # Define region around cantilever tip/contact point
    cantilever_width = 15   # pixels on each side horizontally
    cantilever_height = 15  # pixels above and below vertically
    
    roi_x1 = max(0, x_cant - cantilever_width)
    roi_x2 = min(w, x_cant + cantilever_width)
    roi_y1 = max(0, y_cant - cantilever_height)
    roi_y2 = min(h, y_cant + cantilever_height)
    
    # Method 1: Check mask coverage in cantilever region
    roi_mask = mask[roi_y1:roi_y2, roi_x1:roi_x2]
    coverage_mask = roi_mask.mean() / 255.0 if roi_mask.size > 0 else 0
    
    # Method 2: Check original image for dark features under cantilever
    roi_original = g[roi_y1:roi_y2, roi_x1:roi_x2]
    avg_intensity_roi = np.mean(roi_original) if roi_original.size > 0 else np.mean(g)
    avg_intensity_image = np.mean(g)
    
    # Method 3: Look for actual sample features in cantilever region
    cantilever_region_mask = np.zeros_like(mask)
    cantilever_region_mask[roi_y1:roi_y2, roi_x1:roi_x2] = mask[roi_y1:roi_y2, roi_x1:roi_x2]
    
    num_labels_cant, labels_cant, stats_cant, cents_cant = cv.connectedComponentsWithStats(
        cantilever_region_mask, connectivity=8)
    
    sample_features_under_cant = 0
    for i in range(1, num_labels_cant):
        area = stats_cant[i, cv.CC_STAT_AREA]
        if area >= 20:  # Same minimum as main detection
            sample_features_under_cant += 1
    
    # Decision logic: multiple criteria
    over_sample = (coverage_mask > 0.25 or  # Significant mask coverage
                   avg_intensity_roi < avg_intensity_image * 0.85 or  # Darker than average
                   sample_features_under_cant > 0)  # Actual sample features detected
    
    # Debugging info
    cantilever_sample_info = (f"Coverage: {coverage_mask:.2f}, "
                            f"Intensity ratio: {avg_intensity_roi/avg_intensity_image:.2f}, "
                            f"Features: {sample_features_under_cant}, "
                            f"ROI: ({roi_x1},{roi_y1})-({roi_x2},{roi_y2})")
else:
    cantilever_sample_info = "Cantilever position not set"

# Detect sample features
sample_idx, cx, cy = detect_sample_features(g, mask, x_cant)

if sample_idx is not None:
    h, w = g.shape
    dx_pix, dy_pix = int(cx - w/2), int(cy - h/2)  # +x: right, +y: down
else:
    dx_pix = dy_pix = 0  # nothing found

# Convert pixels → microns: (calibrate once)
um_per_pix_x, um_per_pix_y = 0.25, 0.25
dx_um, dy_um = dx_pix * um_per_pix_x, dy_pix * um_per_pix_y

# Decide stage moves (clip for safety)
kx, ky = 0.6, 0.6  # proportional gains
move_x = float(np.clip(-kx*dx_um, -50, 50))  # stage coords may flip signs
move_y = float(np.clip(-ky*dy_um, -50, 50))

# Results and debugging
print(f"Cantilever position: {x_cant} pixels (fixed position)")
print(f"Sample under cantilever: {over_sample}")
print(f"Cantilever analysis: {cantilever_sample_info}")

if sample_idx is not None:
    print(f"Target sample at: ({cx:.1f}, {cy:.1f})")
    print(f"Centering move: ({move_x:.2f}, {move_y:.2f}) microns")
    
    # Additional debugging: show what we're targeting
    print(f"Image dimensions: {g.shape}")
    print(f"Image center: ({g.shape[1]//2}, {g.shape[0]//2})")
    print(f"Pixel offset: ({dx_pix}, {dy_pix})")
    
    # Check intensity at target location
    target_intensity = g[int(cy), int(cx)]
    avg_intensity = np.mean(g)
    print(f"Target intensity: {target_intensity} (avg: {avg_intensity:.1f})")
    print(f"Target is {'dark' if target_intensity < avg_intensity else 'bright'}")
    
    # If there's already a sample under cantilever, suggest different action
    if over_sample:
        print("RECOMMENDATION: Sample already under cantilever - consider scanning or fine positioning")
    else:
        print("RECOMMENDATION: Move to center on detected sample")
        
else:
    print("No sample target found")
    # Debug: Show why no samples were found
    unique_labels = np.unique(mask)
    print(f"Mask has {len(unique_labels)-1} potential features")
    print(f"Mask intensity range: {np.min(mask)} to {np.max(mask)}")
    print(f"Original image intensity range: {np.min(g)} to {np.max(g)}")
    print(f"Original image mean: {np.mean(g):.1f}, std: {np.std(g):.1f}")
    
    if over_sample:
        print("RECOMMENDATION: Sample under cantilever detected - consider scanning current position")
