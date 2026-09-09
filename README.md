# An Enhanced Security Protocol for Smart Homes

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Domain](https://img.shields.io/badge/Domain-IoT%20Security%20%7C%20Applied%20AI-orange.svg)](#)
[![Cryptography](https://img.shields.io/badge/Crypto-ECC%20%7C%20AES--256%20%7C%20ECDH-red.svg)](#)

An end-to-end, multi-factor mutual authentication protocol engineered for smart home IoT ecosystems. This framework integrates **hybrid asymmetric/symmetric cryptography (ECC + AES-256)** with **machine-learning-based physical layer verification**—featuring **biometric anti-spoofing liveness detection** and **hardware sensor fingerprinting** to defend against replay, man-in-the-middle, presentation, and physical device cloning attacks.

---

## 📌 Table of Contents
- [Architecture Overview](#-architecture-overview)
- [Key Features](#-key-features)
  - [1. Hybrid Cryptographic Mutual Authentication](#1-hybrid-cryptographic-mutual-authentication)
  - [2. Biometric Liveness Detection (Anti-Spoofing)](#2-biometric-liveness-detection-anti-spoofing)
  - [3. Hardware Sensor Fingerprinting](#3-hardware-sensor-fingerprinting)
- [Repository Structure](#-repository-structure)
- [Threat Model & Security Guarantees](#-threat-model--security-guarantees)
- [Prerequisites & Installation](#-prerequisites--installation)
- [Usage & Execution Workflow](#-usage--execution-workflow)
- [Feature Extraction Pipeline](#-feature-extraction-pipeline)
- [Academic Context](#-academic-context)

---

## 🏛 Architecture Overview

Traditional smart home protocols rely solely on static credentials or symmetric pre-shared keys, leaving them susceptible to side-channel key extraction, physical device cloning, and replay attacks. 

This protocol establishes trust through a three-entity verification scheme:
```
+---------------+              +------------------+              +---------------+
|   IoT Edge    |  (ECDH/AES)  |    Smart Home    |  (ECDH/AES)  |  Mobile User  |
|    Device     |<============>|     Gateway      |<============>|    Client     |
+---------------+              +------------------+              +---------------+
        |                                                                |
   [Sensor Noise                                                   [Biometric Liveness
   Fingerprint:                                                     Anti-Spoofing:
   3-Axis Accel.]                                                   SSD + LBP]
```

1. **User-to-Gateway Phase:** Authenticates legitimate users via biometric liveness verification (distinguishing live human skin from silicon/latex spoof presentations) and ECC public-key challenge-response.
2. **Device-to-Gateway Phase:** Verifies authentic edge devices using physical hardware fingerprinting extracted from minute manufacturing anomalies in MEMS accelerometer telemetry.
3. **Session Key Negotiation:** Once physical and biometric proofs pass, ephemeral session keys are dynamically derived via ECDH and HKDF-SHA256.

---

## 🚀 Key Features

### 1. Hybrid Cryptographic Mutual Authentication
* **Curve SECP256R1 (NIST P-256):** Used for asymmetric public/private key generation.
* **Ephemeral ECDH (Elliptic Curve Diffie-Hellman):** Provides **Perfect Forward Secrecy (PFS)**—compromise of long-term keys does not compromise past session traffic.
* **HKDF Key Derivation:** Uses HMAC-SHA256 extract-and-expand functions to derive cryptographic material.
* **AES-256-CBC:** High-throughput symmetric payload encryption with secure PKCS7 padding and cryptographically random initialization vectors (IVs).

### 2. Biometric Liveness Detection (Anti-Spoofing)
* **ROI Extraction:** Uses **SSD MobileNet V2** (Single Shot Detector) to detect and isolate finger bounding boxes from varying backgrounds.
* **Micro-Texture Descriptors:** Extracts **Local Binary Patterns (LBP)** with parameter configuration ($P=24, R=3$, uniform) to analyze microscopic skin ridge variations.
* **Classification:** Distinguishes genuine biometric presentations from artificial spoof replicas (gelatin, silicone, printed artifacts).

### 3. Hardware Sensor Fingerprinting
* **Physical Device Identification:** Exploits inherent manufacturing imperfections in MEMS 3-axis accelerometer silicon chips.
* **Windowed Static State Analysis:** Dynamically isolates stationary intervals using variance thresholding across $(X, Y, Z)$ axes.
* **Feature Engineering (20 Descriptors):** Computes time-domain statistics and frequency-domain Fast Fourier Transform (FFT) metrics:
  * Statistical moments: Mean, standard deviation, skewness, kurtosis, min, max.
  * Signal energy, power, and spectral characteristics.
* **Classifiers:** Leverages **One-Class SVM** and **Random Forest** models to detect hardware cloning or emulated rogue devices.

---

## 📂 Repository Structure

```plaintext
.
├── Model/
│   └── Fingerprint/
│       ├── ssd_mobilenet_v2_320x320_coco17_tpu-8/   # Object detection for finger localization
│       └── naive_bayes_fingerprint_model.pkl        # Biometric liveness classifier
├── Paper/
│   ├── An_Enhanced_Security_Protocol_For_Smart_Home version(2).pdf
│   └── An_Enhanced_Security_Protocol_For_Smart_Homes version(1).pdf
├── RequiredData/
│   ├── Accelerometer/                               # Accelerometer telemetry for fingerprinting
│   └── Fingerprint/                                 # Real and spoof fingerprint dataset
├── RequiredFuntions/
│   ├── accelerometerModelTraining.py                # 20-feature extraction & SVM/RF training
│   ├── dataTransfer.py                              # TCP socket client/server communication
│   ├── EncryptionDecryption.py                      # ECC, ECDH, HKDF, & AES-256 cryptographic suite
│   ├── FingerBiometrics.py                          # LBP feature extraction & liveness inference
│   ├── functions.py                                 # Nonces, SHA-256 hashing, byte transformations
│   ├── imginfo.py                                   # Image decoding and visualization utilities
│   └── InitializationPhase.py                       # ECC & symmetric key bootstrap routines
├── Initialization.ipynb                             # Entity credential provisioning notebook
├── deviceGatewayPhase.ipynb                         # Device-to-Gateway authentication simulation
├── userGatewayPhase.ipynb                           # User-to-Gateway authentication simulation
├── security.ipynb                                   # Security validation & attack scenario testing
└── README.md
```

---

## 🛡 Threat Model & Security Guarantees

| Attack Vector | Countermeasure in Protocol |
| :--- | :--- |
| **Eavesdropping / Sniffing** | Payloads encrypted via ephemeral AES-256 session keys. |
| **Replay Attacks** | Cryptographic nonces (`secrets.randbelow`) and synchronized timestamps incorporated into challenge payloads. |
| **Biometric Presentation Spoofs** | LBP micro-texture feature analysis combined with classification models to flag fake/synthetic prints. |
| **Rogue / Cloned Device Attack** | Hardware sensor fingerprinting (One-Class SVM / Random Forest) verifying unique MEMS silicon variations. |
| **Key Compromise Impersonation** | Ephemeral ECDH exchange ensures compromise of one session key does not expose others. |

---

## ⚙️ Prerequisites & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ASVSKR/An-enhanced-security-protocol-for-smart-homes.git
cd An-enhanced-security-protocol-for-smart-homes
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install numpy pandas scipy scikit-learn scikit-image opencv-python cryptography tensorflow sympy matplotlib joblib h5py
```

---

## 💻 Usage & Execution Workflow

The protocol can be executed in sequence using Jupyter Notebooks:

### Step 1: System Initialization
Run `Initialization.ipynb` to generate root master keys, device identities, and cryptographic parameters:
* Generates SECP256R1 key pairs for User, Gateway, and Device.
* Prepares identity parameters and public key distribution.

### Step 2: Device-to-Gateway Verification
Run `deviceGatewayPhase.ipynb`:
1. The edge device captures 3-axis accelerometer sensor readings.
2. 20 features are extracted and submitted over the encrypted channel.
3. The gateway verifies the hardware fingerprint against the trained One-Class SVM model.
4. Mutual session key is derived upon verification.

### Step 3: User-to-Gateway Verification
Run `userGatewayPhase.ipynb`:
1. User provides biometric credential image.
2. SSD MobileNet localizes the finger boundary; LBP extracts the texture vector.
3. Liveness model classifies sample as `Real` vs `Spoof`.
4. If `Real`, gateway issues an ECDH challenge to complete user session provisioning.

---

## 📊 Feature Extraction Pipeline (Hardware Fingerprinting)

The 20 accelerometer features extracted in `accelerometerModelTraining.py` are grouped into:

| Feature Index | Category | Metric | Purpose |
| :---: | :--- | :--- | :--- |
| **1 – 6** | Time-Domain | Mean, Std Dev, Skewness, Kurtosis, Min, Max | Quantifies static gravity distribution and noise shape |
| **7 – 12** | Signal Power | Root Mean Square (RMS), Energy, Peak-to-Peak | Detects inherent analog amplifier gain differences |
| **13 – 20** | Frequency-Domain | Spectral Centroid, FFT Energy, Dominant Frequency | Captures physical silicon resonant characteristics |

---

## 🎓 Academic Context
* **Institution:** Amrita Vishwa Vidyapeetham, Amrita School of Engineering
* **Program:** M.Tech in Artificial Intelligence (2023 – 2025)
* **Author:** A S V S Krishna Rajesh ([LinkedIn](https://linkedin.com/in/asvskr) | [GitHub](https://github.com/ASVSKR))
