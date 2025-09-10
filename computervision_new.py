import cv2 


########## EXTRA CODE BELOW ###########
"""
image = cv2.imread("images\BloblTargit.JPG")
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
        print(f"Contour {i} area: {area}")
        
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
        if 500.0 < area < 5000.0 and area > max_area:
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

import cv2

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
        if 500.0 < area < 5000.0:
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



