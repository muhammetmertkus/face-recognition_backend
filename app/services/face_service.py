import face_recognition
import numpy as np
from PIL import Image
import io
import json
from flask import current_app
from typing import List, Optional, Dict, Any

from deepface import DeepFace
import cv2 # Import OpenCV for potential cropping/conversion

# Supported image formats (adjust as needed)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def find_face_encodings(image_file_storage):
    """
    Finds face locations and extracts encodings from an image file.

    Args:
        image_file_storage: FileStorage object from Flask request.

    Returns:
        A list of face encodings (numpy arrays) found in the image. 
        Returns an empty list if no faces are found or if the file is invalid.
    Raises:
        ValueError: If the file type is not allowed.
        Exception: For other image processing errors.
    """
    if not allowed_file(image_file_storage.filename):
        raise ValueError(f"Invalid file type. Allowed types: {ALLOWED_EXTENSIONS}")

    try:
        # Read the image file into memory
        img_bytes = image_file_storage.read()
        img = Image.open(io.BytesIO(img_bytes))

        # Convert PIL image to numpy array (RGB format)
        img_array = np.array(img.convert('RGB'))

        # Find face locations
        # model can be 'cnn' (more accurate, slower, requires dlib compiled with CUDA) or 'hog' (faster, less accurate)
        face_locations = face_recognition.face_locations(img_array, model="hog") 

        if not face_locations:
            current_app.logger.info("No faces found in the uploaded image.")
            return []
        
        if len(face_locations) > 1:
            current_app.logger.warning(f"Multiple faces ({len(face_locations)}) found in the image. Using the first one found.")
            # Optionally, you could return an error here or try to find the largest face

        # Extract face encodings (using the first face found for simplicity)
        # Specify known_face_locations to only encode the found faces
        face_encodings = face_recognition.face_encodings(img_array, known_face_locations=face_locations)
        
        current_app.logger.info(f"Found {len(face_encodings)} face encodings.")
        return face_encodings

    except Exception as e:
        current_app.logger.error(f"Error processing image: {e}")
        raise # Re-raise the exception to be handled by the route

def encode_encodings_for_json(encodings: List[np.ndarray]) -> Optional[str]:
    """Converts a list of numpy array encodings to a JSON serializable string."""
    if not encodings:
        return None
    # Convert list of numpy arrays to list of lists
    list_of_lists = [e.tolist() for e in encodings]
    return json.dumps(list_of_lists)

def decode_encodings_from_json(json_string: Optional[str]) -> List[np.ndarray]:
    """Converts a JSON string back to a list of numpy array encodings."""
    if not json_string:
        return []
    try:
        list_of_lists = json.loads(json_string)
        return [np.array(e) for e in list_of_lists]
    except json.JSONDecodeError:
        current_app.logger.error("Failed to decode face encodings from JSON string.")
        return []

def compare_faces(known_face_encodings: List[np.ndarray], face_encoding_to_check: np.ndarray, tolerance=0.6) -> List[bool]:
    """
    Compares a face encoding against a list of known encodings.

    Args:
        known_face_encodings: A list of known face encodings (numpy arrays).
        face_encoding_to_check: The single face encoding to compare (numpy array).
        tolerance: How much distance between faces to consider it a match. Lower is stricter.
                   0.6 is the typical default.

    Returns:
        A list of True/False values indicating if `face_encoding_to_check` matches
        any of the `known_face_encodings`.
    """
    if not known_face_encodings:
        return [False] * 1 # Compare against nothing results in no match
        
    # Compare the face encoding to check against all known encodings
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding_to_check, tolerance=tolerance)
    return matches

def face_distance(known_face_encodings: List[np.ndarray], face_encoding_to_check: np.ndarray) -> List[float]:
    """
    Calculates the distance between a face encoding and a list of known encodings.
    Lower distance indicates a better match.

    Args:
        known_face_encodings: A list of known face encodings.
        face_encoding_to_check: The single face encoding to compare.

    Returns:
        A list of distance values (floats).
    """
    if not known_face_encodings:
        # Return a high distance value if there are no known encodings to compare against
        # The length should match the expected number of comparisons if it were possible. 
        # Since we compare one face, we expect one distance result (even if it's meaningless).
        return [1.0] 
        
    # Calculate distances
    distances = face_recognition.face_distance(known_face_encodings, face_encoding_to_check)
    return distances.tolist() # Convert numpy array to list 

def analyze_face_attributes(image_data: Any, actions: List[str] = ['age', 'gender', 'emotion']) -> Optional[Dict[str, Any]]:
    """
    Analyzes a face image (path or numpy array) to predict attributes using DeepFace.

    Args:
        image_data: Path to the image file (str) or image as NumPy array.
        actions: List of attributes to analyze (e.g., ['age', 'gender', 'emotion']).

    Returns:
        A dictionary containing the analyzed attributes (e.g., 'age', 'gender', 'dominant_emotion')
        if analysis is successful, otherwise None.
    """
    # Define default result keys based on potential actions
    result_keys = {
        'age': 'age',
        'gender': 'dominant_gender',
        'emotion': 'dominant_emotion'
    }
    try:
        # Ensure actions list is not empty
        if not actions:
            current_app.logger.warning("No actions specified for DeepFace analysis.")
            return None
            
        # Use DeepFace.analyze
        results = DeepFace.analyze(
            img_path=image_data, # Can be path or numpy array
            actions=actions, 
            enforce_detection=False, # Don't raise error if no face or multiple faces
            detector_backend='opencv', # Choose a backend
            silent=True # Suppress DeepFace progress bars/messages in logs
        )

        # Handle list vs dict output (take first result if list)
        if isinstance(results, list) and len(results) > 0:
            result = results[0]
        elif isinstance(results, dict): 
             result = results
        else:
            # Log the image data type for debugging if it fails
            log_img_type = type(image_data)
            current_app.logger.warning(f"DeepFace could not analyze attributes for image data of type {log_img_type}. (No face detected or other issue)")
            return None

        # Extract requested attributes
        analysis_output = {}
        analysis_successful = False
        for action in actions:
            result_key = result_keys.get(action)
            if result_key and result_key in result:
                analysis_output[action] = result[result_key]
                analysis_successful = True # Mark success if at least one attribute is found
            else:
                analysis_output[action] = None # Indicate if a specific action failed
                current_app.logger.debug(f"DeepFace analysis did not return key '{result_key}' for action '{action}'.")

        if analysis_successful:
             # Add region for context if needed (though less useful for cropped faces)
             # analysis_output['region'] = result.get('region') 
             return analysis_output
        else:
             current_app.logger.warning(f"DeepFace analysis completed but found no requested attributes.")
             return None

    except FileNotFoundError:
        current_app.logger.error(f"Image file not found for attribute analysis: {image_data}")
        return None
    except ValueError as ve:
        # DeepFace might raise ValueError for issues like multiple faces with enforce_detection=True
        # or other internal problems. Let's log it specifically.
        current_app.logger.error(f"ValueError during DeepFace analysis: {ve}")
        return None
    except Exception as e:
        # Log other unexpected errors
        current_app.logger.error(f"Unexpected error during DeepFace analysis: {e}")
        return None 