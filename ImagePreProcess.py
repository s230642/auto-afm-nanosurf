import cv2 
import numpy as np

image = cv2.imread("images\BloblTargit.JPG")

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
cv2.imshow("Binary", binary)

cv2.imshow("Contours Highlighted", output)

cv2.waitKey(0)
cv2.destroyAllWindows()