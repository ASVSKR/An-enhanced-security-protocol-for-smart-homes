from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64
import json
from cryptography.hazmat.primitives import padding

def encryption(data, public_key_pem):
    """Encrypts any data (JSON, String, or Bytes) using ECC Public Key."""
    public_key = serialization.load_pem_public_key(public_key_pem)
    
    # ✅ Generate Ephemeral Key Pair (for Hybrid Encryption)
    ephemeral_private_key = ec.generate_private_key(ec.SECP256R1())
    shared_secret = ephemeral_private_key.exchange(ec.ECDH(), public_key)

    # ✅ Derive AES Key from Shared Secret
    aes_key = HKDF(algorithm=SHA256(), length=32, salt=None, info=b"ECC Enc Key").derive(shared_secret)

    # ✅ Convert Data to Bytes
    if isinstance(data, dict) or isinstance(data, list):  # JSON Data
        data_bytes = json.dumps(data).encode()
    elif isinstance(data, str):  # String Data
        data_bytes = data.encode()
    elif isinstance(data, bytes):  # Binary Data
        data_bytes = data
    else:
        raise TypeError("❌ Unsupported data type. Use JSON, String, or Bytes.")

    # ✅ Encrypt Data with AES-256
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # ✅ Apply PKCS7 Padding
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # ✅ Return IV + Ciphertext + Ephemeral Public Key (Base64)
    ephemeral_public_pem = ephemeral_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return base64.b64encode(iv + ciphertext + ephemeral_public_pem).decode()

# ✅ Universal Public-Key Decryption (Fixed)
def decryption(encrypted_data, private_key_pem):
    """Decrypts data (JSON, String, Bytes) using ECC Private Key."""
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    encrypted_data = base64.b64decode(encrypted_data)

    # ✅ Extract IV (First 16 Bytes)
    iv = encrypted_data[:16]

    # ✅ Locate the Start of Ephemeral Public Key
    try:
        pem_start = encrypted_data.index(b"-----BEGIN PUBLIC KEY-----")
    except ValueError:
        raise ValueError("❌ Ephemeral public key not found in encrypted data!")

    # ✅ Extract Ciphertext & Ephemeral Public Key
    ciphertext = encrypted_data[16:pem_start]  # Everything before key
    ephemeral_public_pem = encrypted_data[pem_start:]  # Extract full key

    # ✅ Load Ephemeral Public Key (Now Fixed)
    ephemeral_public_key = serialization.load_pem_public_key(ephemeral_public_pem)

    # ✅ Compute Shared Secret
    shared_secret = private_key.exchange(ec.ECDH(), ephemeral_public_key)

    # ✅ Derive AES Key from Shared Secret
    aes_key = HKDF(algorithm=SHA256(), length=32, salt=None, info=b"ECC Enc Key").derive(shared_secret)

    # ✅ Decrypt with AES-256
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    # ✅ Remove Padding
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()

    # ✅ Convert Data to Original Format
    try:
        return json.loads(decrypted_data.decode())  # Convert back to JSON
    except:
        return decrypted_data.decode() if decrypted_data.isascii() else decrypted_data


# =============================================================


def decode_symmetric_key(encoded_key):
    return base64.b64decode(encoded_key)  # Decodes the Base64 key into bytes

import cv2
import numpy as np

def read_image_as_bytes(image_path):
    """Reads an image from a file and returns it as bytes."""
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    return image_bytes

# Update the encryption function to accept image bytes
def symmetric_key_encryption(uniqueId, image_bytes, symmetricKey):
    """Encrypts image data using AES symmetric encryption, where the uniqueId and image bytes are concatenated."""
    
    # ✅ Decode the symmetric key
    KUiG = decode_symmetric_key(symmetricKey)
    
    # ✅ Convert the uniqueId to bytes and concatenate with image bytes
    uniqueId_bytes = uniqueId.encode()  # Ensure uniqueId is in bytes
    separator = b'|||'
    combined_data = uniqueId_bytes + separator + image_bytes  # Concatenate string and bytes properly
    
    # ✅ Generate Random IV for AES encryption
    iv = os.urandom(16)  # Generate Random IV
    
    # ✅ Perform AES encryption
    cipher = Cipher(algorithms.AES(KUiG), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # ✅ Apply PKCS7 Padding
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(combined_data) + padder.finalize()

    # ✅ Encrypt the data
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # ✅ Return Base64-encoded result (IV + Ciphertext)
    return base64.b64encode(iv + ciphertext).decode()  # Encode IV + Ciphertext as Base64

# ✅ Decrypt the Image Using Symmetric Key and Return Bytes
def symmetric_key_decryption(encrypted_data, symmetricKey):
    KUiG = decode_symmetric_key(symmetricKey)
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    cipher = Cipher(algorithms.AES(KUiG), modes.CBC(iv))
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    # Remove PKCS7 Padding
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()

    ID_i_decrypted, I_decrypted = decrypted_data.split(b'|||', 1)

    return ID_i_decrypted, I_decrypted  # Return the decrypted image bytes

# =============================================================

# ✅ AES Encryption for JSON (Excluding Unique ID)
def symmetric_key_encryption_JSON(jsonData, symmetricKey):
    """Encrypts a JSON object using AES-256-CBC without encrypting uniqueId."""
    KUiG = decode_symmetric_key(symmetricKey)  # Decode Key

    # ✅ Convert JSON to String & Encode
    json_string = json.dumps(jsonData)
    json_bytes = json_string.encode()

    # ✅ Generate IV
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(KUiG), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # ✅ Apply PKCS7 Padding
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(json_bytes) + padder.finalize()

    # ✅ Encrypt Data
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # ✅ Return IV + Ciphertext as Base64
    return base64.b64encode(iv + ciphertext).decode()

# ✅ AES Decryption for JSON
def symmetric_key_decryption_JSON(encrypted_data, key):
    """Decrypts AES-256-CBC encrypted JSON data."""
    key = decode_symmetric_key(key)  # Decode Key
    encrypted_data = base64.b64decode(encrypted_data)

    # ✅ Extract IV & Ciphertext
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    # ✅ Decrypt & Remove Padding
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_json = unpadder.update(decrypted_padded) + unpadder.finalize()

    return json.loads(decrypted_json.decode())  # ✅ Convert back to JSON