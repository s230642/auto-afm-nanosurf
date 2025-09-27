import cv2 
from numpy import pi,uint8, sum as npsum
from skimage.morphology import erosion
from skimage.morphology import disk 

#######################################
######### Global variables ############
#######################################

erosion_disk_size = 3
threshhold_for_binary = 115
circularity_limit = 0.16
threshhold_for_binary_cantelever_on_skincell = 95  # adjust if needed


#######################################
######### Functions in use ############
#######################################

def labelCurrentImage():
    image = cv2.imread("images/currentPosition.JPG")
    cv2.imshow("Original image", image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, threshhold_for_binary, 255, cv2.THRESH_BINARY_INV)

    footprint_disk = disk(erosion_disk_size)

    eroded = erosion(binary, footprint_disk)

    # Find contours
    contours, hierarchy = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # Convert to BGR so we can draw colored contours
    output = cv2.cvtColor(eroded, cv2.COLOR_GRAY2BGR)

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
    cv2.imshow("Image with contours", image)
    cv2.imshow("Contours Highlighted", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def onSkincell(image):
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
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshhold_for_binary, 255, cv2.THRESH_BINARY_INV)
    footprint_disk = disk(erosion_disk_size)
    eroded = erosion(binary, footprint_disk)

    contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    biggest_contour = None
    max_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            continue  # avoid division by zero
        
        circularity = 4 * pi * (area / (perimeter * perimeter))
        
        # Check both area range AND circularity
        if 500.0 < area < 5000.0 and circularity > circularity_limit:
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
    _, binary = cv2.threshold(gray, threshhold_for_binary, 255, cv2.THRESH_BINARY_INV)
    footprint_disk = disk(erosion_disk_size)
    eroded = erosion(binary, footprint_disk)
    # Find contours
    contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
        if 500.0 < area < 5000.0 and circularity > circularity_limit:
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

def fullDebug():
    image = cv2.imread("images/currentPosition.jpg")
    coordinates, output = findBiggestSkincellVisual(image)
    print("---------------")
    print("Coordinates: " ,  coordinates)
    print("On skincell: ", onSkincell(image))
    print("---------------")
    cv2.imshow("Selected area", output)
    labelCurrentImage()
    cv2.waitKey()
    cv2.destroyAllWindows()

#print("Currently on skincell is: ", onSkincellFile("images/currentPosition_after_one_move.jpg"))