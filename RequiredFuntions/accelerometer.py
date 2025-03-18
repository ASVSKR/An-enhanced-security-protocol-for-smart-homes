import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from scipy.fftpack import fft
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import OneClassSVM
from sklearn.ensemble import RandomForestClassifier

def detect_flat_static_state_windowed(data, window_size=50, threshold=0.2):
    static_indices = []
    
    for i in range(len(data) - window_size):
        window = data[i:i + window_size]  # Extract a window of `window_size` samples
        std_dev = np.std(window, axis=0)  # Compute standard deviation for (X, Y, Z)
        
        if np.all(std_dev < threshold):  # Check if all axes have low variation
            static_indices.append(i)
    
    return static_indices

def extract_20_features(data):
    features = []
    
    # 1-6: Time-Domain Features
    features.append(np.mean(data))      # Mean
    features.append(np.std(data))       # Standard Deviation
    features.append(skew(data))         # Skewness
    features.append(kurtosis(data))     # Kurtosis
    features.append(np.min(data))       # Minimum Value
    features.append(np.max(data))       # Maximum Value

    # 7-12: Signal Power and Energy
    features.append(np.sum(np.square(data)))  # Signal Energy
    features.append(np.mean(np.abs(data)))    # Mean Absolute Value
    features.append(np.median(data))          # Median
    features.append(np.percentile(data, 25))  # 25th Percentile
    features.append(np.percentile(data, 75))  # 75th Percentile
    features.append(np.var(data))             # Variance

    # 13-20: Frequency-Domain Features (FFT)
    fft_values = np.abs(fft(data))  
    features.append(np.mean(fft_values))  # Mean FFT Amplitude
    features.append(np.max(fft_values))   # Max FFT Amplitude
    features.append(np.std(fft_values))   # FFT Standard Deviation
    features.append(np.percentile(fft_values, 25))  # FFT 25th Percentile
    features.append(np.percentile(fft_values, 75))  # FFT 75th Percentile
    features.append(np.var(fft_values))   # FFT Variance
    features.append(np.sum(np.square(fft_values)))  # FFT Energy
    features.append(np.median(fft_values)) # FFT Median
    
    return features

def AccelerometerTraining(inputdataset):
    # Load Dataset
    df = inputdataset
    # Extract Accelerometer Data and Device IDs
    device_ids = df['user']  # Assuming 'user' is the device ID
    X_raw = df[['X', 'Y', 'Z']].values  # Extract (X, Y, Z) sensor data    

    # Apply the function
    static_indices = detect_flat_static_state_windowed(X_raw, window_size=50, threshold=0.2)

    # Get filtered dataset
    if len(static_indices) == 0:
        X_filtered = X_raw
        device_ids_filtered = device_ids
    else:
        X_filtered = X_raw[static_indices]
        device_ids_filtered = device_ids.iloc[static_indices]

    # Normalize Data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_filtered)

    # Apply feature extraction on each sample
    X_features = np.array([extract_20_features(sample) for sample in X_filtered])

    # Normalize extracted features
    X_features_scaled = scaler.fit_transform(X_features)

    # Train-Test Split after Feature Extraction
    X_train, X_test, y_train, y_test = train_test_split(X_features_scaled, device_ids_filtered, test_size=0.2, random_state=42)

    # Train One-Class SVM for unknown device detection
    one_class_model = OneClassSVM(nu=0.1, kernel="rbf")
    one_class_model.fit(X_train)

    # Train Multi-Class Classifier for known device identification
    multi_class_model = RandomForestClassifier(n_estimators=100, random_state=42)
    multi_class_model.fit(X_train, y_train)

    import joblib

    # Save Models
    joblib.dump(one_class_model, "./Model/Accelerometer/one_class_svm.pkl")
    joblib.dump(multi_class_model, "./Model/Accelerometer/multi_class_rf.pkl")
    joblib.dump(scaler, "./Model/Accelerometer/scaler.pkl")