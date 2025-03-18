# INTIALIZATION PHASE REQUIRED LIBRARIES

#ECC
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def ECCPublicPrivateKeyGeneration():
    private_key = ec.generate_private_key(ec.SECP256R1())  # Using SECP256R1 curve
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return public_pem, private_pem


#SYMMETRIC KEY GENERATION
import os
import base64

def SymmetricKeyGeneration():
    symmetric_key = os.urandom(32)
    encoded_key = base64.b64encode(symmetric_key).decode()
    
    return encoded_key

#==========================================================================================