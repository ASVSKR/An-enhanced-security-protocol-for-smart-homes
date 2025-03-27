import skimage.feature as skfeat
import cv2
import numpy as np
import tensorflow as tf

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

def load_image_into_numpy_array(image_bytes):
   
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # Decode image

    if img is None:
        raise ValueError("❌ Invalid image data: Unable to decode bytes")

    # ✅ Convert BGR (OpenCV Default) to RGB and Return as NumPy Array
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# Preprocessing function
def identification_preprocess_image(image):
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    return input_tensor

# Detection function
def detect_objects(image, model):
    input_tensor = identification_preprocess_image(image)
    detections = model(input_tensor)
    return detections


def draw_best_box(image, boxes, scores, classes, min_score=0.5):
    h, w, _ = image.shape
    best_score = 0
    best_box = None

    for i in range(boxes.shape[0]):
        if scores[i] >= min_score and scores[i] > best_score:
            best_score = scores[i]
            best_box = boxes[i]

    if best_box is not None:
        ymin, xmin, ymax, xmax = best_box * np.array([h, w, h, w])
        ymin, xmin, ymax, xmax = int(ymin), int(xmin), int(ymax), int(xmax)
        cropped_image = image[ymin:ymax, xmin:xmax].copy()  # Copy cropped part of the image
        image_with_boxes = image.copy()  # Make a copy for drawing the box
        cv2.rectangle(image_with_boxes, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        return cropped_image, image_with_boxes
    return None, image