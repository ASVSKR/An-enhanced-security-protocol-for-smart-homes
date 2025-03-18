import hashlib
import random
import h5py
import numpy as np
import pandas as pd
import os

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


def UpdateRegisteredDevices(uniqueID, encrypted_image, imageMetadata, accelerometerMetadata, hdf5_filename="DB/registeredDevices.hdf5"):
    with h5py.File(hdf5_filename, "a") as f:
        if uniqueID in f:
            print("❌ Duplicate uniqueID! Data already exists.")
        group = f.create_group(uniqueID)
        group.create_dataset("encrypted_image", data=np.string_(encrypted_image))  
        image = group.create_group("imageMetadata")
        for key, value in imageMetadata.items():
            image.attrs[key] = value
        accelerometer = group.create_group("accelerometerMetadata")
        for key, value in accelerometerMetadata.items():
            accelerometer.attrs[key] = value
    print(f"🎯 Encrypted Data Successfully Saved for `{uniqueID}` in {hdf5_filename}")


def AddNewDevice(trainingID, uniqueID, hdf5_filename="DB/DeviceList.hdf5"):
    with h5py.File(hdf5_filename, "a") as f:  # ✅ Use "a" to append instead of overwriting
        trainingID_str = str(trainingID)  # ✅ Convert trainingID to string (HDF5 requires string names)
        if trainingID_str in f:
            print(f"⚠️ Training ID `{trainingID}` already exists! Skipping entry.")
            return "duplicate_trainingID"

        group = f.create_group(trainingID_str)
        hashed_id = hashlib.sha256(uniqueID.encode()).hexdigest()  # ✅ Encode before hashing
        group.create_dataset("uniqueID", data=np.string_(hashed_id))  # ✅ Store hashed unique ID

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


def load_all_data(hdf5_filename="DB/DeviceList.hdf5"):
    """Loads all data from an HDF5 file and returns it as a dictionary."""
    data_dict = {}

    # ✅ Check if the file exists
    if not os.path.exists(hdf5_filename):
        print(f"❌ File '{hdf5_filename}' not found! Returning empty dictionary.")
        return {}

    with h5py.File(hdf5_filename, "r") as f:
        for training_id in f.keys():  # Iterate over all training IDs
            group = f[training_id]
            group_data = {key: group[key][()].decode("utf-8") for key in group.keys()}  # Extract datasets
            group_data.update({key: group.attrs[key] for key in group.attrs})  # Extract attributes

            data_dict[int(training_id)] = group_data  # Store in dictionary

    return data_dict

def GetNewDeviceID(device_data):
    sorted_data = dict(sorted(device_data.items(), key=lambda x: x[0], reverse=True))
    highest_training_id = max(sorted_data.keys())

    return highest_training_id + 1