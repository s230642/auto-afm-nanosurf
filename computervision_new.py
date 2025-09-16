import cv2 
from numpy import pi

"""
########## EXTRA CODE BELOW ###########
import numpy as np

image = cv2.imread("images\currentPosition_1.JPG")
cv2.imshow("Original image", image)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

_, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

# Find contours
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


# Convert to BGR so we can draw colored contours
output = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

# Draw contours and print areas
for i, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    if area>500.0 and area<5000.0:
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
        cv2.drawContours(output, [contour], -1, (0, 255, 0), 2)
        print(f"Contour no. {i} has area: {area}")
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue  # avoid division by zero
        
        circularity = 4 * np.pi * (area / (perimeter * perimeter))
        circularity = np.round(circularity,3)
        print(f"Contour no. {i} has circularity: {circularity}")
        print("---------------")
        
        # Calculate contour centroid
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = 0, 0
        
        # Put index number at centroid
        cv2.putText(output, str(i), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

# Show results
cv2.imshow("Original image with contours", image)
cv2.imshow("Contours Highlighted", output)

cv2.waitKey(0)
cv2.destroyAllWindows()

"""


def findBiggestSkincell(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    biggest_contour = None
    max_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            continue  # avoid division by zero
        
        circularity = 4 * pi * (area / (perimeter * perimeter))
        
        # Check both area range AND circularity
        if 500.0 < area < 5000.0 and circularity > 0.2:
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)  # green contour
            
            if area > max_area:
                biggest_contour = contour
                max_area = area


    if biggest_contour is not None:
        M = cv2.moments(biggest_contour)
        if M["m00"] > 1e-5:  # avoid division by zero
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            # fallback: bounding box center
            x, y, w, h = cv2.boundingRect(biggest_contour)
            cx, cy = x + w // 2, y + h // 2
        return (cx, cy)
    else:
        return None  # no valid contour found
    

def findBiggestSkincellFileName(file):
    image = cv2.imread(file)
    return findBiggestSkincell(image)


def findBiggestSkincellVisual(image):
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    biggest_contour = None
    max_area = 0

    # Draw all contours within area limits
    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            continue  # avoid division by zero
        
        circularity = 4 * pi * (area / (perimeter * perimeter))
        
        # Check both area range AND circularity
        if 500.0 < area < 5000.0 and circularity > 0.2:
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)  # green contour
            
            if area > max_area:
                biggest_contour = contour
                max_area = area

    # Mark the biggest one with a red dot
    if biggest_contour is not None:
        M = cv2.moments(biggest_contour)
        if M["m00"] > 1e-5:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            # fallback: bounding box center
            x, y, w, h = cv2.boundingRect(biggest_contour)
            cx, cy = x + w // 2, y + h // 2

        cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)  # red dot
        return (cx, cy), image  # return center + annotated image
    else:
        return None, image  # no valid contour found, just return original


##### Experiments on finding cantelever tip ######
"""
import cv2
import numpy as np

# Load image
image = cv2.imread("images/currentPosition.JPG")   # use forward slashes or raw string
cv2.imshow("Original image", image)

# Grayscale + threshold
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY)
cv2.imshow("Binary", binary)

# Get central region
h, w = binary.shape
roi_size = (h // 2, w // 3)

y1 = h//2 - roi_size[0]//2
y2 = h//2 + roi_size[0]//2
x1 = w//2 - roi_size[1]//2
x2 = w//2 + roi_size[1]//2

center_thresh = binary[y1:y2, x1:x2]

# Find contours in cropped image
contours, _ = cv2.findContours(center_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"(H,W) center = {center_thresh.shape}")

if contours:
    contour = max(contours, key=cv2.contourArea)


    # Filter: remove points that touch the cropped border
    filtered = []
    for pt in contour:
        x, y = pt[0]  # unpack
        if x <= 1 or y <= 1 or x >= center_thresh.shape[1]-1 or y >= center_thresh.shape[0]-1:
            continue
        filtered.append([[x, y]])   # keep OpenCV format (nested list)

    filtered = np.array(filtered, dtype=np.int32).reshape(-1,1,2)

    # Shift contour back to original coordinates
    filtered[:,:,0] += x1
    filtered[:,:,1] += y1

    # Draw on original
    output = image.copy()
    cv2.drawContours(output, [filtered], -1, (0,255,0), 2)

    cv2.imshow("Filtered Contour", output)

    contour = np.array(contour, dtype=np.int32).reshape(-1,1,2)

    # Shift contour back to original coordinates
    contour[:,:,0] += x1
    contour[:,:,1] += y1

    cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
    cv2.imshow("Raw Contour", image)


# Reshape to (N,2) for convenience
pts = filtered.reshape(-1, 2)

# Get point with max y
idx = np.argmax(pts[:,1])
southernmost = tuple(pts[idx])

print("Southernmost point:", southernmost)

cv2.waitKey(0)
cv2.destroyAllWindows()


import cv2
import numpy as np

# Load image
image = cv2.imread("images/currentPosition.JPG")
cv2.imshow("Original image", image)

# Grayscale + threshold
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY)
cv2.imshow("Binary", binary)

# Get central region
h, w = binary.shape
roi_size = (h // 2, w // 3)

y1 = h//2 - roi_size[0]//2
y2 = h//2 + roi_size[0]//2
x1 = w//2 - roi_size[1]//2
x2 = w//2 + roi_size[1]//2

center_thresh = binary[y1:y2, x1:x2]

# Find contours in cropped image
contours, _ = cv2.findContours(center_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"(H,W) center = {center_thresh.shape}")

if contours:
    contour = max(contours, key=cv2.contourArea)
    
    # Shift contour back to original coordinates first
    contour_shifted = contour.copy()
    contour_shifted[:,:,0] += x1
    contour_shifted[:,:,1] += y1
    
    # Analyze convexity defects for U-shape detection
    hull = cv2.convexHull(contour, returnPoints=False)
    
    try:
        defects = cv2.convexityDefects(contour, hull)
        
        output = image.copy()
        
        # Draw original contour
        cv2.drawContours(output, [contour_shifted], -1, (0, 255, 0), 2)
        
        # Draw convex hull
        hull_points = cv2.convexHull(contour)
        hull_shifted = hull_points.copy()
        hull_shifted[:,:,0] += x1
        hull_shifted[:,:,1] += y1
        cv2.drawContours(output, [hull_shifted], -1, (255, 0, 0), 2)
        
        u_shape_detected = False
        top_defects = []
        
        if defects is not None:
            print(f"Found {len(defects)} convexity defects")
            
            for i, defect in enumerate(defects):
                start_idx, end_idx, far_idx, distance = defect[0]
                
                # Get the actual points
                start = tuple(contour[start_idx][0])
                end = tuple(contour[end_idx][0])
                far = tuple(contour[far_idx][0])
                
                # Shift points to original coordinates
                start_orig = (start[0] + x1, start[1] + y1)
                end_orig = (end[0] + x1, end[1] + y1)
                far_orig = (far[0] + x1, far[1] + y1)
                
                # Calculate defect depth in pixels
                defect_depth = distance / 256.0
                
                print(f"Defect {i}: depth={defect_depth:.1f}, far_point={far_orig}")
                
                # Check if this is a significant defect at the top
                # (defect point should be in upper portion of the contour)
                contour_height = np.max(contour[:,:,1]) - np.min(contour[:,:,1])
                upper_threshold = np.min(contour[:,:,1]) + contour_height * 0.3  # top 30%
                
                if (defect_depth > 20 and  # Significant depth
                    far[1] < upper_threshold):  # In upper portion
                    
                    top_defects.append((defect_depth, far_orig, start_orig, end_orig))
                    
                    # Draw the defect
                    cv2.circle(output, far_orig, 8, (0, 0, 255), -1)
                    cv2.line(output, start_orig, end_orig, (255, 255, 0), 2)
                    
            # U-shape criteria: significant defect(s) at the top
            if len(top_defects) > 0:
                u_shape_detected = True
                largest_defect = max(top_defects, key=lambda x: x[0])
                print(f"U-SHAPE DETECTED! Largest top defect depth: {largest_defect[0]:.1f}")
                
                # Draw text on image
                cv2.putText(output, "U-SHAPE DETECTED", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        if not len(top_defects) > 0:
            print("Simple shape detected")
            cv2.putText(output, "Simple Shape", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Find the BOTTOM of the coherent green shape
        # This is simply the southernmost point of the contour
        southernmost_idx = np.argmax(contour_shifted[:,:,1])
        southernmost = tuple(contour_shifted[southernmost_idx][0])
        
        # Draw a larger, more visible marker at the bottom
        cv2.circle(output, southernmost, 15, (255, 0, 255), -1)  # Larger magenta circle
        cv2.circle(output, southernmost, 20, (255, 255, 255), 3)  # White outline
        
        print(f"BOTTOM of shape: {southernmost}")
        
        # Also find and mark the geometric center bottom
        # Get all bottom points within 5 pixels of the absolute bottom
        max_y = np.max(contour_shifted[:,:,1])
        bottom_points = contour_shifted[contour_shifted[:,:,1] >= max_y - 5]
        
        if len(bottom_points) > 1:
            # Find center of bottom edge
            print(bottom_points)
            center_x = int(np.mean(bottom_points[:,0]))
            center_bottom = (center_x, max_y)
            cv2.circle(output, center_bottom, 10, (0, 255, 255), -1)  # Yellow center
            print(f"CENTER of bottom edge: {center_bottom}")
        
        cv2.imshow("Bottom Detection", output)
        
    except cv2.error as e:
        print(f"Error computing convexity defects: {e}")
        print("This usually happens with very simple contours")
        
        # Fallback: just draw the contour
        output = image.copy()
        cv2.drawContours(output, [contour_shifted], -1, (0, 255, 0), 2)
        cv2.imshow("Contour Only", output)

cv2.waitKey(0)
cv2.destroyAllWindows()

"""
