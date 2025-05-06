import skimage.feature as skfeat
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

# Function to extract LBP features
def extract_lbp_features(image):
    lbp = skfeat.local_binary_pattern(image, P=24, R=3, method='uniform')
    return lbp.flatten()


# Function to predict using the loaded model
def predict_fingerprint(image_bytes, img_size, classifier):    
    # ✅ Convert Bytes to Image
    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale image
    
    if img is None:
        raise ValueError("❌ Invalid image data: Unable to decode bytes")

    # ✅ Preprocess Image
    img = cv2.resize(img, img_size)

    # ✅ Extract LBP Features
    lbp_features = extract_lbp_features(img)
    lbp_features = lbp_features.reshape(1, -1)

    # ✅ Predict using the trained classifier
    prediction = classifier.predict(lbp_features)

    result = 'Real' if prediction[0] == 1 else 'Spoof'
    return result

def IsolateFingerImage(image_bytes):
    # Convert bytes to a NumPy array and decode the image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        print("Image could not be decoded. Please check the bytes input.")
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Otsu's thresholding
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Perform morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    thresh_closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh_clean = cv2.morphologyEx(thresh_closed, cv2.MORPH_OPEN, kernel)

    # Find contours from the cleaned binary image
    contours, hierarchy = cv2.findContours(thresh_clean.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour assuming it corresponds to the finger
        largest_contour = max(contours, key=cv2.contourArea)

        # Draw the contour on a copy of the original image for visualization (optional)
        img_contour = img.copy()
        cv2.drawContours(img_contour, [largest_contour], -1, (0, 255, 0), 2)

        # Get the bounding rectangle of the largest contour and crop the image
        x, y, w, h = cv2.boundingRect(largest_contour)
        cropped = img[y:y+h, x:x+w]

        # Visualize the results
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 3, 1)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title("Original Image")
        plt.axis('off')
        
        plt.subplot(1, 3, 2)
        plt.imshow(thresh_clean, cmap='gray')
        plt.title("Binary Mask")
        plt.axis('off')
        
        plt.subplot(1, 3, 3)
        plt.imshow(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        plt.title("Cropped Finger")
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        return cropped
    else:
        print("No contours found. Please check the image or adjust the threshold parameters.")
        return None


def feature_matching_SIFT_RANSAC(img1, img2, ratio_thresh=0.7, ransac_thresh=3.0):
    # Create SIFT detector
    sift = cv2.SIFT_create()

    # Detect keypoints and compute descriptors
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # Brute Force Matcher using knnMatch for k=2
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    matches = bf.knnMatch(des1, des2, k=2)

    # Filter matches using the ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)
    print(f"Total good matches (pre-RANSAC): {len(good_matches)}")

    # Proceed only if there are enough matches to compute homography
    if len(good_matches) >= 4:
        # Extract location of good matches
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Find homography using RANSAC to filter out outliers
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, ransac_thresh)
        # mask is a list of 0s and 1s indicating outliers and inliers respectively
        num_inliers = int(mask.sum())
        print(f"Number of inliers after RANSAC: {num_inliers}")

        # Optionally, visualize inlier matches
        inlier_matches = [good_matches[i] for i in range(len(good_matches)) if mask[i]]
        matched_img = cv2.drawMatches(img1, kp1, img2, kp2, inlier_matches, None,
                                      flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        cv2.imshow("Inlier Matches after RANSAC", matched_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return H, mask, good_matches, num_inliers
    else:
        print("Not enough matches to compute homography.")
        return None, None, good_matches, None
