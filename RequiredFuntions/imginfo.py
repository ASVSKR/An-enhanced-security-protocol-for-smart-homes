import os
import mimetypes
from PIL import Image
import piexif
import fitz  # PyMuPDF for PDF metadata

from datetime import datetime

def convert_timestamp(unix_time):
    """Converts Unix timestamp to human-readable date-time."""
    return datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S UTC')

def extract_metadata(file_path):
    """Extracts metadata for images, PDFs, and general files."""
    metadata = {"filePath": file_path}

    # ✅ File Size
    metadata["size"] = str(os.path.getsize(file_path)) + "B"

    # ✅ Determine File Type
    mime_type, _ = mimetypes.guess_type(file_path)
    metadata["fileType"] = mime_type

    # ✅ Handle Image Metadata (JPEG, TIFF)
    if mime_type and mime_type.startswith("image"):
        try:
            with Image.open(file_path) as img:
                metadata["format"] = img.format
                metadata["width"], metadata["height"] = img.size
                metadata["mode"] = img.mode
                metadata["bitDepth"] = len(metadata["mode"]) * 8
                metadata["colorType"] = metadata["mode"]

                # Extract EXIF Data (Only for JPEG, TIFF)
                exif_dict = piexif.load(img.info.get("exif", b""))
                metadata["make"] = exif_dict["0th"].get(piexif.ImageIFD.Make, b"").decode("utf-8")
                metadata["model"] = exif_dict["0th"].get(piexif.ImageIFD.Model, b"").decode("utf-8")
                metadata["dateTime"] = exif_dict["0th"].get(piexif.ImageIFD.DateTime, b"").decode("utf-8")
        except Exception:
            metadata["error"] = "Failed to extract image metadata"

    # ✅ Handle PDF Metadata
    elif mime_type == "application/pdf":
        try:
            doc = fitz.open(file_path)  # Open PDF
            metadata.update(doc.metadata)  # Extract metadata
            metadata["pageCount"] = len(doc)
        except Exception:
            metadata["error"] = "Failed to extract PDF metadata"

    # ✅ Handle General File Metadata (TXT, CSV, JSON)
    else:
        metadata["modificationTime"] = convert_timestamp(os.path.getmtime(file_path))
        metadata["creationTime"] = convert_timestamp(os.path.getctime(file_path))

    return metadata
