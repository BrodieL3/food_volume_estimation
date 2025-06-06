import argparse
import numpy as np
import cv2
import os
import json
import logging
import base64
from flask import Flask, request, jsonify, make_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
estimator = None
density_db = None

# Simplified dummy classes for testing
class DummyVolumeEstimator:
    def __init__(self):
        self.loaded = True
    
    def estimate_volume(self, img, fov=70, plate_diameter_prior=0):
        # Return dummy volume data based on image size
        height, width = img.shape[:2]
        # Simulate volume estimation based on image area
        base_volume = (width * height) / 1000000  # Convert pixels to cubic meters
        return [base_volume * 0.5, base_volume * 0.3]  # dummy volumes

class DummyDensityDatabase:
    def __init__(self, source):
        self.data = {
            'apple': ('apple', 0.6),  # (name, density in g/mL)
            'banana': ('banana', 0.5),
            'rice': ('rice', 0.75),
            'chicken': ('chicken', 1.0),
            'pasta': ('pasta', 0.4),
            'salad': ('salad', 0.3),
            'default': ('unknown', 0.8)
        }
    
    def query(self, food_type):
        return self.data.get(food_type.lower(), self.data['default'])

def load_volume_estimator(depth_model_architecture, depth_model_weights,
        segmentation_model_weights, density_db_source):
    """Loads volume estimator object and sets up its parameters."""
    try:
        global estimator, density_db
        
        # Use dummy estimator since we don't have real models
        estimator = DummyVolumeEstimator()
        density_db = DummyDensityDatabase(density_db_source)
        
        logger.info('Volume estimator loaded successfully (dummy mode).')
        return True
        
    except Exception as e:
        logger.error(f"Error loading volume estimator: {str(e)}")
        return False

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run."""
    if estimator is None:
        return make_response(jsonify({'status': 'unhealthy', 'reason': 'models not loaded'}), 503)
    return make_response(jsonify({'status': 'healthy', 'message': 'Food Volume Estimation API is running'}), 200)

@app.route('/predict', methods=['POST'])
def volume_estimation():
    """Receives an HTTP request and returns the estimated 
    volumes of the foods in the image given.

    JSON payload:
        img: The image data as base64 string
        food_type: The type of food to estimate
        plate_diameter: The expected plate diameter (optional)

    Returns:
        The estimated weight in JSON format.
    """
    if estimator is None:
        return make_response(jsonify({'error': 'Models not loaded'}), 503)
        
    # Decode incoming data to get an image
    try:
        content = request.get_json()
        if not content:
            return make_response(jsonify({'error': 'No JSON data provided'}), 400)
            
        if 'img' in content:
            img_encoded = content['img']
            if isinstance(img_encoded, str):
                # Assume base64 encoded
                try:
                    img_data = base64.b64decode(img_encoded)
                    np_img = np.frombuffer(img_data, np.uint8)
                except Exception:
                    return make_response(jsonify({'error': 'Invalid base64 image data'}), 400)
            else:
                # Assume byte array
                try:
                    img_byte_string = ' '.join([str(x) for x in img_encoded])
                    np_img = np.fromstring(img_byte_string, np.int8, sep=' ')
                except Exception:
                    return make_response(jsonify({'error': 'Invalid byte array image data'}), 400)
            
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            if img is None:
                return make_response(jsonify({'error': 'Could not decode image'}), 400)
        else:
            return make_response(jsonify({'error': 'Missing img field in request'}), 400)
            
    except Exception as e:
        logger.error(f"Error decoding image: {str(e)}")
        return make_response(jsonify({'error': 'Image decoding failed'}), 400)

    # Get food type
    food_type = content.get('food_type', 'default')

    # Get expected plate diameter from form data or set to 0 and ignore
    try:
        plate_diameter = float(content.get('plate_diameter', 0))
    except (ValueError, TypeError):
        plate_diameter = 0

    # Estimate volumes
    try:
        volumes = estimator.estimate_volume(img, fov=70, plate_diameter_prior=plate_diameter)
        # Convert to mL
        volumes_ml = [v * 1e6 for v in volumes]
        
        # Convert volumes to weight - assuming a single food type
        db_entry = density_db.query(food_type)
        density = db_entry[1]
        weight = sum(v * density for v in volumes_ml)

        # Return values
        return_vals = {
            'food_type_match': db_entry[0],
            'weight_grams': round(weight, 2),
            'volumes_ml': [round(v, 2) for v in volumes_ml],
            'density_g_per_ml': density,
            'status': 'success',
            'image_shape': img.shape
        }
        return make_response(jsonify(return_vals), 200)
        
    except Exception as e:
        logger.error(f"Error estimating volume: {str(e)}")
        return make_response(jsonify({'error': 'Volume estimation failed', 'details': str(e)}), 500)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Food volume estimation API.')
    parser.add_argument('--depth_model_architecture', type=str,
                        help='Path to depth model architecture (.json).',
                        default=os.environ.get('DEPTH_MODEL_ARCHITECTURE', 'models/architecture.json'))
    parser.add_argument('--depth_model_weights', type=str,
                        help='Path to depth model weights (.h5).',
                        default=os.environ.get('DEPTH_MODEL_WEIGHTS', 'models/depth_weights.h5'))
    parser.add_argument('--segmentation_model_weights', type=str,
                        help='Path to segmentation model weights (.h5).',
                        default=os.environ.get('SEGMENTATION_MODEL_WEIGHTS', 'models/segmentation_weights.h5'))
    parser.add_argument('--density_db_source', type=str,
                        help='Path to food density database (.xlsx) or Google Sheets ID.',
                        default=os.environ.get('DENSITY_DB_SOURCE', 'models/density_db.xlsx'))
    args = parser.parse_args()

    logger.info("Starting Food Volume Estimation API...")
    success = load_volume_estimator(
        args.depth_model_architecture,
        args.depth_model_weights, 
        args.segmentation_model_weights,
        args.density_db_source
    )
    
    if not success:
        logger.warning("Models could not be loaded. API will run in limited mode.")
    
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

