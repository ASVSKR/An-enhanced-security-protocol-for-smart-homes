import hashlib
import h5py
import cv2
import matplotlib.pyplot as plt
import numpy as np
import secrets

# caliculating the hash of a file

def hash_file(file_path):
    # Open the file
    with open(file_path, "rb") as file:
        data = file.read()

    return hashlib.sha256(data).hexdigest()
    
def nonce_gen():
    nonce = secrets.randbelow(1001)
    return nonce

import json

def read_json_file(file_path):
    """Reads a JSON file and returns a dictionary."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Load JSON into a dictionary
    return data


import sympy
def primeNumbergenerator():
    return sympy.randprime(0, 100)

def xor_strings(s1, s2):
    # Convert each character to its ASCII value, perform XOR, and convert back to character
    return ''.join(chr(ord(c1) ^ ord(c2)) for c1, c2 in zip(s1, s2))

def display_image_from_bytes(image_bytes):
    # Convert bytes to a NumPy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    # Decode the image from the array
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        print("Failed to decode image.")
        return
    # Convert from BGR (OpenCV's default) to RGB for matplotlib
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Display the image using matplotlib
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.title("Image from Bytes (OpenCV)")
    plt.show()

    return img_rgb

def image_file_to_bytes(file_path: str) -> bytes:
    with open(file_path, 'rb') as file:
        return file.read()

