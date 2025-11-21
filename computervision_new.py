import cv2 
from numpy import pi,uint8, sum as npsum
from skimage.morphology import erosion
from skimage.morphology import disk 

#######################################
######### Global variables ############
#######################################

erosion_disk_size = 3
threshhold_for_binary = 117
circularity_limit = 0.2
threshhold_for_binary_cantelever_on_skincell = 95  # adjust if needed
minimumArea = 200.0
maximumArea = 20000.0
blocksize_adaptive_thresh = 57
constant_adaptive_thresh = 20
top_crop = 75

#######################################
######### Functions in use ############
#######################################

def labelCurrentImage():
    image = cv2.imread("images/currentPosition.JPG")
    image = image[top_crop:, :]
    cv2.imshow("Original image", image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV , blocksize_adaptive_thresh,constant_adaptive_thresh)

    footprint_disk = disk(erosion_disk_size)

    eroded = erosion(binary, footprint_disk)

    cv2.imshow("Eroed", eroded)
    # Find contours
    contours, hierarchy = cv2.findContours(eroded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    

    # Convert to BGR so we can draw colored contours
    output = cv2.cvtColor(eroded, cv2.COLOR_GRAY2BGR)

    # Draw contours and print areas
    for i, contour in enumerate(contours):

        area = cv2.contourArea(contour)
        M = cv2.moments(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            continue  # avoid division by zero
        circularity = 4 * pi * (area / (perimeter * perimeter))

        if M["m00"] > 1e-5:  # avoid division by zero
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            # fallback: bounding box center
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = x + w // 2, y + h // 2
        if area>minimumArea and area<maximumArea and (hierarchy[0][i][3]==-1) and (hierarchy[0][i][2]==-1)and not(290 <= cx <= 315 and 175 - top_crop <= cy <= 330 - top_crop) and circularity > circularity_limit:
                # If First_Child == -1, no holes
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
            cv2.drawContours(output, [contour], -1, (0, 255, 0), 2)
            print(f"Contour no. {i} has area: {area}")
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue  # avoid division by zero
            
            circularity = 4 * pi * (area / (perimeter * perimeter))
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
    #cv2.imshow("Binary", binary)
    cv2.imshow("Selected area", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def onSkincell(image):
    image = image[top_crop:, :]

    cropped_image = image[310:335, 270:325]  # crops like (y1:y2, x1:x2)
    gray_cropped = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray_cropped, threshhold_for_binary_cantelever_on_skincell, 255, cv2.THRESH_BINARY_INV)
    binarysum = npsum(binary)
    print("Skincounter is: ", binarysum)
    return binarysum > 120000

def onSkincellFile(file):
    image = cv2.imread(file)
    return onSkincell(image)


def findBiggestSkincell(image):
    image = image[top_crop:, :]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV , blocksize_adaptive_thresh,constant_adaptive_thresh)
    footprint_disk = disk(erosion_disk_size)
    eroded = erosion(binary, footprint_disk)

    contours, hierarchy = cv2.findContours(eroded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    biggest_contour = None
    max_area = 0

    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            continue  # avoid division by zero
        
        circularity = 4 * pi * (area / (perimeter * perimeter))
        M = cv2.moments(contour)

        if M["m00"] > 1e-5:  # avoid division by zero
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            # fallback: bounding box center
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = x + w // 2, y + h // 2
        # Check both area range AND circularity
        if (minimumArea < area < maximumArea and circularity > circularity_limit)  and (hierarchy[0][i][3]==-1) and (hierarchy[0][i][2]==-1)and not(290 <= cx <= 315 and 175 - top_crop <= cy <= 330 - top_crop):
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
        return (cx, cy+top_crop)
    else:
        return None  # no valid contour found
    

def findBiggestSkincellFileName(file):
    image = cv2.imread(file)
    return findBiggestSkincell(image)


def findBiggestSkincellVisual(image):
    # Convert to grayscale and threshold
    image = image[top_crop:, :]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV , blocksize_adaptive_thresh,constant_adaptive_thresh)
    footprint_disk = disk(erosion_disk_size)
    eroded = erosion(binary, footprint_disk)
    # Find contours
    contours, hierarchy = cv2.findContours(eroded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    biggest_contour = None
    max_area = 0

    # Draw all contours within area limits
    for i, contour in enumerate(contours):
        contour_area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)


        if perimeter == 0:
            continue  # avoid division by zero
        M = cv2.moments(contour)
        if M["m00"] > 1e-5:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            # fallback: bounding box center
            x, y, w, h = cv2.boundingRect(biggest_contour)
            cx, cy = x + w // 2, y + h // 2


        circularity = 4 * pi * (contour_area / (perimeter * perimeter))
        
        # Check both area range AND circularity
        if contour_area>minimumArea and contour_area<maximumArea and (hierarchy[0][i][3]==-1) and (hierarchy[0][i][2]==-1) and not(290 <= cx <= 315 and 175 - top_crop <= cy <= 330 - top_crop) and circularity > circularity_limit:
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)  # green contour
            
            if contour_area > max_area:
                biggest_contour = contour
                max_area = contour_area

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
        return (cx, cy+top_crop), image  # return center + annotated image
    else:
        return None, image  # no valid contour found, just return original

def fullDebug():
    image = cv2.imread("images/currentPosition.jpg")

    coordinates, output = findBiggestSkincellVisual(image)
    print("---------------")
    print("Coordinates: " ,  coordinates)
    print("On skincell: ", onSkincell(image))
    print("---------------")
    
    labelCurrentImage()
    cv2.waitKey()
    cv2.destroyAllWindows()

import numpy as np


def centering():
    image = cv2.imread("images/currentPosition.jpg")
    cropped_image = image[280:360, 235:355]  # crops like (y1:y2, x1:x2)
    gray_cropped = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

    # Create binary mask where pixel values are between 60 and 100
    binary_image = cv2.inRange(gray_cropped, 60, 100)

    # Define kernel for morphological operations (e.g., 3x3 rectangle)
    kernel = np.ones((5, 5), np.uint8)
    
    # Apply opening (erode then dilate) to remove noise
    opened = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

    # Apply closing (dilate then erode) to fill small holes
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    #cv2.imshow("closed", closed)

    contours, _ = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    biggest_contour = None
    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        cv2.drawContours(cropped_image, [contour], -1, (255, 0, 0), 2)  # green contour
        if perimeter == 0:
            continue  # avoid division by zer
            
        if area > max_area and area > 300:
            biggest_contour = contour
            max_area = area
    if biggest_contour is not None:
        M = cv2.moments(biggest_contour)
        if M["m00"] > 1e-5:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            # fallback: bounding box center
            x, y, w, h = cv2.boundingRect(biggest_contour)
            cx, cy = x + w // 2, y + h // 2

        cv2.circle(image, (cx+235, cy+280), 2, (0, 0, 255), -1)  # red dot
        return (cx+235, cy+280), image  # return center + annotated image
    else:
        return None, image  # no valid contour found, just return original

#fullDebug()

"""
coordinates , image = centering()

print(coordinates)

def tupleSubtract(t1, t2):
    if t1 == None or t2 == None:
        return None
    return t1[0] - t2[0] , t1[1] - t2[1]

current_cantelever_position = (301,322) #This should be automated //TODO
move_distance = tupleSubtract(coordinates,current_cantelever_position)
print("Distance to move for centering", move_distance) 


cv2.imshow("image",image)
cv2.waitKey()
"""