import hashlib
import random
import h5py
import numpy as np
import pandas as pd
import os
import EncryptionDecryption as ED

# caliculating the hash of a file

def hash_file(file_path):
    # Open the file
    with open(file_path, "rb") as file:
        data = file.read()

    return hashlib.sha256(data).hexdigest()
    
def nonce_gen():
    nonce = random.randint(1,1000)
    return nonce

import json

def read_json_file(file_path):
    """Reads a JSON file and returns a dictionary."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Load JSON into a dictionary
    return data

def commonUpdateRegisteredDevices(uniqueIDGroup, encrypted_image, imageMetadata, accelMetadata):
    # Save encrypted image as bytes
    uniqueIDGroup.create_dataset("encrypted_image", data=encrypted_image)  # Assuming encrypted_image is already bytes
    uniqueIDGroup.create_dataset("imageMetadata", data=imageMetadata)
    uniqueIDGroup.create_dataset("accelMetadata", data=accelMetadata)

def UpdateRegisteredDevices(GatewayID, uniqueID, encrypted_image, imageMetadata, accelMetadata, hdf5_filename="DB/registeredDevices.hdf5"):
    with h5py.File(hdf5_filename, "a") as f:
        if GatewayID in f:
            print("❌ Duplicate GatewayID! Data already exists.")
            if uniqueID in f[GatewayID]:
                print("❌ Duplicate uniqueID! Data already exists.")
            else:
                # Create a new group for uniqueID under existing GatewayID
                group = f[GatewayID].create_group(uniqueID)
                commonUpdateRegisteredDevices(group, encrypted_image, imageMetadata, accelMetadata)
        else:
            # If GatewayID does not exist, create a new GatewayID group
            group = f.create_group(GatewayID)

            # Create uniqueID group inside the new GatewayID group
            uniqueIDGroup = group.create_group(uniqueID)
            commonUpdateRegisteredDevices(uniqueIDGroup, encrypted_image, imageMetadata, accelMetadata)

    print(f"Data for GatewayID: {GatewayID}, UniqueID: {uniqueID} successfully updated.")

def gatewayStore(uniqueId, encryptedsecret, usershare, hdf5_filename="DB/gatewayStorage.hdf5"):
    with h5py.File(hdf5_filename, "a") as f:
        if uniqueId in f:
            print("Unique ID already Exists")
        else:
            group = f.create_group(uniqueId)
            group.create_dataset("encryptedSecret", data=encryptedsecret)
            group.create_dataset("usershare", data=usershare)
            print("updated gateway storage")

def lastlogin(uniqueID, lastlogin, hdf5_filename="DB/lastlogin.hdf5"):
    with h5py.File(hdf5_filename, "a") as f:
        if uniqueID in f:
            f[uniqueID]["lastLogin"] = np.string_(lastlogin)
            print(f"✅ lastLogin for {uniqueID} updated to {lastlogin}")
        else:
            group = f.create_group(uniqueID)
            group.create_dataset("lastLogin", data=lastlogin)
            print(f"✅ New lastLogin entry for {uniqueID} created")

def AddNewDevice(trainingID, uniqueID , hdf5_filename="DB/DeviceList.hdf5"):
    with h5py.File(hdf5_filename, "a") as f:
        trainingID_str = str(trainingID)  # Ensure trainingID is a string
        if trainingID_str in f:
            return "duplicate trainingID"
        group = f.create_group(trainingID_str)
        hashed_id = hashlib.sha256(uniqueID.encode()).hexdigest()  # Encode before hashing
        group.create_dataset("uniqueID", data=np.bytes_(hashed_id.encode()))  # Store hashed unique ID as bytes
    print(f"🎯 Encrypted Data Saved for Training ID `{trainingID}` in {hdf5_filename}")
    return "success"


def hdf5_to_dict(group):
    extracted_data = {}
    for key, value in group.attrs.items():
        extracted_data[key] = value
    for key in group.keys():
        if isinstance(group[key], h5py.Dataset):  # If it's a dataset, extract the value
            extracted_data[key] = group[key][()].decode("utf-8")  # Convert bytes to string
        elif isinstance(group[key], h5py.Group):  # If it's a group, recurse
            extracted_data[key] = hdf5_to_dict(group[key])
    return extracted_data

def LoadData(record_id, hdf5_filename="DB/registeredDevices.hdf5"):
    record_id = str(record_id)
    with h5py.File(hdf5_filename, "r") as f:
        if record_id not in f:
            print("❌ Record not found!")
            return "RecordNotFound"
        group = f[record_id]  # ✅ Access group using primary key
        extracted_data = hdf5_to_dict(group)  # ✅ Convert Entire Group Automatically
        extracted_data["record_id"] = int(record_id)
    return extracted_data


def load_nested_groups(group):
    group_data = {}
    
    for key in group.keys():
        if isinstance(group[key], h5py.Group):
            # Recursively call the function for nested groups
            group_data[key] = load_nested_groups(group[key])
        elif isinstance(group[key], h5py.Dataset):
            # If it's a dataset, extract the data
            group_data[key] = group[key][()]
            if isinstance(group_data[key], bytes):
                group_data[key] = group_data[key].decode("utf-8")  # Decode if bytes
        else:
            group_data[key] = group[key]  # Handle other types of data (e.g., attributes)
    
    return group_data

def load_all_data(hdf5_filename):
    data_dict = {}  # This will store all the data
    
    with h5py.File(hdf5_filename, "r") as f:
        for training_id in f.keys():
            group = f[training_id]  # Get the group for each training_id
            group_data = load_nested_groups(group)  # Get all nested data
            data_dict[training_id] = group_data

    return data_dict  # Return the loaded data


def GetNewDeviceID(device_data):
    sorted_data = dict(sorted(device_data.items(), key=lambda x: x[0], reverse=True))

    print(f"sorted_data = {len(sorted_data.keys())}")
    if(len(sorted_data.keys()) == 0):
        return 1
    
    highest_training_id = max(sorted_data.keys())

    return int(highest_training_id) + 1

import sympy
def primeNumbergenerator():
    return sympy.randprime(0, 100)