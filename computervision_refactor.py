import cv2
import numpy as np
from numpy import pi, sum as npsum
from skimage.morphology import erosion, disk, opening, closing

def apply_mask(binary, mask):
    """Zero out binary pixels where mask is also 1 (white)."""
    return cv2.bitwise_and(binary, cv2.bitwise_not(mask))

#######################################
######### Global variables ############
#######################################

OPENING_DISK_SIZE = 2
THRESHOLD_TYPE = cv2.ADAPTIVE_THRESH_MEAN_C 
CIRCULARITY_LIMIT = 0.25
MINIMUM_AREA = 250.0
SKINCELL_BINARY_SUM_THRESHOLD = 120000
THRESH_BLOCKSIZE = 49
THRESH_MEAN_SUBTRACT = 40

#######################################
######### Helper functions ############
#######################################

def load_cantelever_mask():
    cantelever_mask = cv2.imread(r"Code\images\binary-mask-cantelever.JPG")
    cantelever_mask = cv2.cvtColor(cantelever_mask, cv2.COLOR_BGR2GRAY)
    cantelever_mask = cantelever_mask.astype(np.uint8)  # <-- ensure correct dtype
    return cantelever_mask

def _contour_centroid(contour):
    """Returns (cx, cy) for a given contour using moments, with bounding box fallback."""
    M = cv2.moments(contour)
    if M["m00"] > 1e-5:
        return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
    x, y, w, h = cv2.boundingRect(contour)
    return x + w // 2, y + h // 2

def _is_visited(candidate_patch, visited_patches, threshold=0.90):
    """
    For each stored patch, compare with incoming patch.
    If match we cannot consider it.
    """
    for stored_patch in visited_patches:
        ph, pw = stored_patch.shape[:2]
        if candidate_patch.shape[0] < ph or candidate_patch.shape[1] < pw:
            continue
        result = cv2.matchTemplate(candidate_patch, stored_patch, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            return True
    return False

def _extract_patch(image, cx, cy, size=48):
    """Crop a small square patch around a centroid."""
    half = size // 2
    x1, y1 = max(cx - half, 0), max(cy - half, 0)
    x2, y2 = min(cx + half, image.shape[1]), min(cy + half, image.shape[0])
    return image[y1:y2, x1:x2].copy()


def _is_valid_skincell_contour(contour, hierarchy_entry):
    """Returns True if the contour passes area, circularity, and hierarchy checks."""
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return False
    circularity = 4 * pi * (area / (perimeter ** 2))
    no_parent = hierarchy_entry[3] == -1
    no_child  = hierarchy_entry[2] == -1
    area_and_circularity = MINIMUM_AREA < area < 5000.0 and circularity > CIRCULARITY_LIMIT
    return area_and_circularity and no_parent and no_child

def _make_bin_image(image,visual = False):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(
        gray, 255, THRESHOLD_TYPE, cv2.THRESH_BINARY_INV, THRESH_BLOCKSIZE, THRESH_MEAN_SUBTRACT
    )

    if visual==True:
        cv2.imshow("Raw binary image", binary)

    opened = opening(binary, disk(OPENING_DISK_SIZE))
    cantelever_mask = load_cantelever_mask()
    opened = apply_mask(opened, cantelever_mask)          # <-- apply mask here

    return opened

#######################################
######### Public API ##################
#######################################

def onSkincell(image, threshold=75, min_count=450):
    """Returns True if the cantilever is positioned on a skin cell."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cropped = gray[230:260, 280:315]
    return np.sum(cropped <= threshold) > min_count

def findBiggestSkincell(image, already_visited_blobs, visual=False):
    """
    Finds the centroid of the biggest valid skin cell contour in the image.

    Args:
        image:  BGR image (will be annotated in-place when visual=True).
        visual: If True, draws all candidate contours in green and marks the
                biggest centroid with a red dot.

    Returns:
        (cx, cy)          when visual=False and a contour is found.
        None              when visual=False and no contour is found.
        ((cx, cy), image) when visual=True and a contour is found.
        (None,     image) when visual=True and no contour is found.
    """
    bin_image = _make_bin_image(image, visual)
    contours, hierarchy = cv2.findContours(bin_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    biggest_contour = None
    max_area = 0
    output_patch = None

    for i, contour in enumerate(contours):
        if not _is_valid_skincell_contour(contour, hierarchy[0][i]):
            continue
        cx, cy = _contour_centroid(contour)
        patch = _extract_patch(image, cx, cy)
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)  # green border

        if _is_visited(patch, already_visited_blobs):  # compare patches
            if visual:
                cv2.drawContours(image, [contour], -1, (0, 0, 255), 1)  # red = visited
            continue

        area = cv2.contourArea(contour)
        if area > max_area:
            biggest_contour = contour
            max_area = area
            output_patch = patch

    if biggest_contour is not None:
        cx, cy = _contour_centroid(biggest_contour)
        if visual:
            cv2.circle(image, (cx, cy), 4, (0, 0, 255), -1)
            return (cx, cy), image , output_patch
        return (cx, cy), output_patch

    return (None, image) if visual else None, None

#######################################
######### Debug functions #############
#######################################

def _labelAllContours(bin_image):
    """
    Debug helper: shows all candidate contours with their index, area,
    and circularity printed to stdout, and displays two annotated windows.
    Uses adaptive Gaussian thresholding (better for uneven lighting than the
    global threshold used in findBiggestSkincell).
    """
    
    contours, hierarchy = cv2.findContours(bin_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    output = cv2.cvtColor(bin_image, cv2.COLOR_GRAY2BGR)

    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if not _is_valid_skincell_contour(contour, hierarchy[0][i]):
            continue
        circularity = 4 * pi * (area / (perimeter ** 2))
        print(f"Contour {i}: area={area:.1f}, circularity={circularity:.3f}")
        print("---------------")
        cv2.drawContours(output, [contour], -1, (0, 255, 0), 2)
        cx, cy = _contour_centroid(contour)
        cv2.putText(output, str(i), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Contours Highlighted", output)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def fullDebug(image_path=r"Code\images\smaller_blobs.jpg"):
    """Runs all debug visualisations on the given image file."""
    image = cv2.imread(image_path)
    bin_image = _make_bin_image(image)
    cv2.imshow("Original image", image)

    coordinates, output, patch = findBiggestSkincell(image, [] , visual=True)
    print("---------------")
    print("Coordinates:", coordinates)
    print("On skincell:", onSkincell(image))
    print("---------------")
    cv2.imshow("Selected area", output)
    cv2.imwrite("Code\images\Image_with_contours.JPG",output)
    scaled = cv2.resize(patch, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)
    cv2.waitKey()
    cv2.destroyAllWindows()

def tuneThreshold(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.namedWindow("Binary")
    cv2.createTrackbar("Block size", "Binary", 35, 150, lambda x: None)
    cv2.createTrackbar("C subtract",  "Binary", 10,  50,  lambda x: None)
    cv2.createTrackbar("Open disk",   "Binary", 1, 5, lambda x: None)
    cv2.createTrackbar("Close disk",   "Binary", 1, 5, lambda x: None)

    cv2.imshow("original image" , image)
    while True:
        block = cv2.getTrackbarPos("Block size", "Binary")
        c     = cv2.getTrackbarPos("C subtract",  "Binary")
        o_d     = cv2.getTrackbarPos("Open disk",   "Binary")
        c_d     = cv2.getTrackbarPos("Close disk",   "Binary")

        block = max(3, block | 1)  # enforce odd number, minimum 3
        o_d     = max(1, o_d)          # disk size must be at least 1
        c_d     = max(1, c_d)          # disk size must be at least 1

        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV, block, c
        )
        opened = opening(binary, disk(o_d))
        closed = closing(opened, disk(c_d))

        cv2.imshow("Binary", closed)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    print(f"Final values \n — block_size={block}, C={c}, opening_disk_size={o_d},  closing_disk_size={c_d}")
    cv2.destroyAllWindows()

def adaptiveVsMeanThresholding(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    load_cantelever_mask()

    cv2.imshow("original image", image)

    # --- GAUSSIAN ---
    o_d = max(1, 4)
    c_d = max(1, 1)

    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 51, 17
    )
    opened = opening(binary, disk(o_d))
    closed = closing(opened, disk(c_d))
    cantelever_mask = load_cantelever_mask()
    closed = apply_mask(closed, cantelever_mask)          # <-- apply mask here

    
    # Convert binary mask to BGR and overlay on original
    binary_bgr = cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR)
    binary_colored = np.zeros_like(image)
    binary_colored[:, :] = (0, 0, 255)          # red tint for detected regions
    binary_colored[closed == 0] = (0, 0, 0)     # black where nothing detected

    overlay_gaussian = cv2.addWeighted(image, 0.7, binary_colored, 0.3, 0)

    cv2.imshow("GAUSSIAN overlay", overlay_gaussian)
    cv2.imwrite(r"Code\images\gassian_thresholding.JPG", overlay_gaussian)

    # --- MEAN ---
    o_d = max(1, 2)
    c_d = max(1, 2)

    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 49, 40
    )
    opened = opening(binary, disk(o_d))
    closed = closing(opened, disk(c_d))
    closed = apply_mask(closed, cantelever_mask)          # <-- apply mask here

    binary_colored = np.zeros_like(image)
    binary_colored[:, :] = (0, 255, 0)          # green tint for detected regions
    binary_colored[closed == 0] = (0, 0, 0)     # black where nothing detected

    overlay_mean = cv2.addWeighted(image, 0.7, binary_colored, 0.3, 0)
    cv2.imshow("MEAN overlay", overlay_mean)
    cv2.imwrite(r"Code\images\mean_thresholding.JPG", overlay_mean)

    cv2.waitKey()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    fullDebug()  # TODO: add cropping to exclude bottom and rightmost edges of image
    pass

