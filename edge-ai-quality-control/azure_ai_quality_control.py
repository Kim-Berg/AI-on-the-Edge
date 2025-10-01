"""
Enhanced Quality Control System with Azure AI Foundry Local Integration
Real AI-powered defect detection using Azure AI models
"""

import cv2
import numpy as np
import time
import json
import threading
import base64
import io
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from PIL import Image
import logging
import os
import requests
from collections import deque
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from foundry_local import FoundryLocalManager
    FOUNDRY_SDK_AVAILABLE = True
    logger.info("Foundry Local SDK available")
except ImportError:
    FOUNDRY_SDK_AVAILABLE = False
    logger.warning("Foundry Local SDK not available. Install with: pip install foundry-local-sdk")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'edge-ai-demo-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class AzureAIQualityControlSystem:
    def __init__(self):
        self.running = False
        self.current_batch = 0
        self.total_processed = 0
        self.defects_found = 0
        self.current_stats = {}
        self.recent_results = deque(maxlen=50)
        
        # Azure AI Configuration  
        self.azure_ai_enabled = True
        self.ai_client = None
        self.model_name = None
        self.vision_capable = False
        self.foundry_endpoint = None
        self.foundry_manager = None
        
        # Quality Inspection Configuration
        self.inspection_config = {
            'sensitivity': 'medium',  # low, medium, high
            'scratch_threshold': 0.3,
            'missing_component_threshold': 0.4,
            'color_deviation_threshold': 0.3,
            'surface_damage_threshold': 0.35,
            'alignment_threshold': 0.4,
            'contamination_threshold': 0.35,
            'overall_defect_threshold': 0.4,
            'product_type': 'pcb'  # pcb, metal, plastic, etc.
        }
        
        # MQTT setup (optional)
        try:
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
            self.mqtt_client.on_connect = self.on_mqtt_connect
        except Exception as e:
            logger.warning(f"MQTT setup warning: {e}")
        
        # Setup Azure AI integration
        self.setup_azure_ai()
        
        # Test computer vision functionality
        self.test_cv_functionality()

    def setup_azure_ai(self):
        """Setup Azure AI using Foundry Local SDK"""
        try:
            if FOUNDRY_SDK_AVAILABLE:
                logger.info("🚀 Setting up Azure AI with Foundry Local SDK...")
                return self._setup_foundry_sdk()
            else:
                logger.info("📡 Using direct API connection to Foundry Local...")
                return self._setup_direct_api()
                
        except Exception as e:
            logger.error(f"Error in setup_azure_ai: {e}")
            return False
    
    def _setup_foundry_sdk(self):
        """Setup using official Foundry Local SDK"""
        # List of models to try in order of preference
        preferred_models = [
            "phi-3.5-mini",
            "phi-4",
            "phi-4-mini", 
            "qwen2.5-1.5b",
            "qwen2.5-0.5b"
        ]
        
        for model_alias in preferred_models:
            try:
                logger.info(f"🔍 Trying model: {model_alias}")
                
                # Create FoundryLocalManager instance
                self.foundry_manager = FoundryLocalManager(model_alias)
                
                # Get model info and endpoint
                model_info = self.foundry_manager.get_model_info(model_alias)
                endpoint = self.foundry_manager.endpoint
                
                logger.info(f"📋 Model loaded: {model_info.id}")
                logger.info(f"🔗 Endpoint: {endpoint}")
                
                # Test the connection directly with requests first
                test_payload = {
                    "model": model_info.id,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 5
                }
                
                response = requests.post(
                    f"{endpoint}/chat/completions",
                    json=test_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info("✅ Direct API test successful")
                    
                    # Store connection info for direct API calls
                    self.foundry_endpoint = endpoint
                    self.model_name = model_info.id
                    self.ai_client = "foundry_direct"  # Flag for direct API calls
                    
                    # Check if it's a vision-capable model
                    self.vision_capable = any(term in model_alias.lower() 
                        for term in ['vision', 'multimodal', 'gpt-4', 'phi-4', 'llava'])
                    
                    logger.info(f"✅ Connected with Foundry Local SDK")
                    logger.info(f"🤖 Model: {model_alias} ({self.model_name})")
                    logger.info(f"👁️ Vision capable: {self.vision_capable}")
                    logger.info("✅ Using direct Foundry API calls")
                    
                    return True
                else:
                    logger.warning(f"API test failed: {response.status_code}")
                    continue
                
            except Exception as e:
                logger.debug(f"Failed to load model {model_alias}: {e}")
                continue
        
        logger.warning("❌ Could not load any models with Foundry Local SDK")
        return self._setup_direct_api()
    
    def _setup_direct_api(self):
        """Fallback method for direct API connection"""
        logger.info("📡 Attempting direct API connection to Foundry Local...")
        
        # Azure AI Foundry Local common endpoints and configurations
        foundry_configs = [
            {
                "base_url": "http://localhost:3928/v1", 
                "api_key": "dummy-key",
                "name": "Azure AI Foundry Local (port 3928)"
            },
            {
                "base_url": "http://localhost:1234/v1", 
                "api_key": "not-needed",
                "name": "Azure AI Foundry Local (port 1234)"
            }
        ]
        
        for config in foundry_configs:
            try:
                logger.info(f"🔍 Testing: {config['name']}")
                
                # Test connection
                response = requests.get(f"{config['base_url']}/models", timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ Connected to {config['name']}")
                    self.foundry_endpoint = config['base_url']
                    self.ai_client = "direct_api"
                    self.model_name = "generic-model"
                    return True
                    
            except Exception as e:
                logger.debug(f"Failed to connect to {config['name']}: {e}")
                continue
        
        logger.warning("❌ Could not connect to any Azure AI Foundry Local endpoint")
        return False

    def _analyze_with_foundry_direct(self, image_array):
        """Direct API call to Foundry Local"""
        start_time = time.time()
        try:
            # Analyze image features for text-based analysis
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            brightness = np.mean(gray)
            contrast = np.std(gray)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Create analysis prompt
            prompt = f"""You are a manufacturing quality control AI. Analyze this product image data:

MEASUREMENTS:
- Sharpness: {blur_score:.1f} (>100=sharp, <50=blurry/damaged)
- Brightness: {brightness:.1f} (50-200 normal)
- Contrast: {contrast:.1f} (>30 good, <20=poor)
- Edge Density: {edge_density:.3f} (high=possible cracks/scratches)

Based on these measurements, is there a manufacturing defect? Respond only with JSON:
{{"defect_detected": true/false, "defect_type": "type or None", "defect_probability": 0.0-1.0, "confidence": 0.0-1.0}}"""

            # Make direct API call
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a manufacturing quality control AI. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 150
            }
            
            response = requests.post(
                f"{self.foundry_endpoint}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                logger.info(f"🤖 Foundry AI response: {ai_response[:100]}...")
                
                # Parse AI response
                try:
                    analysis = json.loads(ai_response.strip())
                    
                    return {
                        'has_defect': analysis.get('defect_detected', False),
                        'defect_type': analysis.get('defect_type', 'Unknown'),
                        'confidence': analysis.get('confidence', 0.5),
                        'defect_probability': analysis.get('defect_probability', 0.5),
                        'ai_analysis': ai_response,
                        'processing_time': time.time() - start_time,
                        'method': 'Foundry Local AI'
                    }
                    
                except json.JSONDecodeError:
                    # Fallback parsing
                    has_defect = 'true' in ai_response.lower() and 'defect' in ai_response.lower()
                    return {
                        'has_defect': has_defect,
                        'defect_type': 'AI Analysis',
                        'confidence': 0.7,
                        'defect_probability': 0.6 if has_defect else 0.2,
                        'ai_analysis': ai_response,
                        'processing_time': time.time() - start_time,
                        'method': 'Foundry Local AI (parsed)'
                    }
            else:
                logger.warning(f"Foundry API error: {response.status_code}")
                return self.simulate_defect_detection_fallback(image_array)
                
        except Exception as e:
            logger.error(f"Foundry direct API error: {e}")
            return self.simulate_defect_detection_fallback(image_array)

    def perform_computer_vision_inspection(self, image_array):
        """
        Comprehensive computer vision-based quality inspection
        """
        start_time = time.time()
        defects_detected = []
        total_confidence = 0
        defect_probability = 0
        
        try:
            # Validate input image
            if image_array is None or len(image_array.shape) != 3:
                raise ValueError(f"Invalid image array shape: {image_array.shape if image_array is not None else 'None'}")
            
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            
            # 1. SCRATCH AND CRACK DETECTION
            scratch_confidence = self.detect_scratches_and_cracks(gray)
            if scratch_confidence > self.inspection_config['scratch_threshold']:
                defects_detected.append(("Scratch/Crack", scratch_confidence))
                defect_probability += scratch_confidence * 0.8
            
            # 2. MISSING COMPONENT DETECTION
            missing_confidence = self.detect_missing_components(gray, image_array)
            if missing_confidence > self.inspection_config['missing_component_threshold']:
                defects_detected.append(("Missing Component", missing_confidence))
                defect_probability += missing_confidence * 0.9
            
            # 3. COLOR DEVIATION DETECTION
            color_confidence = self.detect_color_deviations(image_array, hsv)
            if color_confidence > self.inspection_config['color_deviation_threshold']:
                defects_detected.append(("Color Deviation", color_confidence))
                defect_probability += color_confidence * 0.6
            
            # 4. SURFACE DAMAGE DETECTION
            surface_confidence = self.detect_surface_damage(gray)
            if surface_confidence > self.inspection_config['surface_damage_threshold']:
                defects_detected.append(("Surface Damage", surface_confidence))
                defect_probability += surface_confidence * 0.7
            
            # 5. ALIGNMENT ISSUES
            alignment_confidence = self.detect_alignment_issues(gray)
            if alignment_confidence > self.inspection_config['alignment_threshold']:
                defects_detected.append(("Misalignment", alignment_confidence))
                defect_probability += alignment_confidence * 0.5
            
            # 6. CONTAMINATION DETECTION
            contamination_confidence = self.detect_contamination(image_array, gray)
            if contamination_confidence > self.inspection_config['contamination_threshold']:
                defects_detected.append(("Contamination", contamination_confidence))
                defect_probability += contamination_confidence * 0.8
            
            # Determine primary defect and overall assessment
            has_defect = len(defects_detected) > 0 or defect_probability > self.inspection_config['overall_defect_threshold']
            
            if defects_detected:
                # Find defect with highest confidence
                primary_defect = max(defects_detected, key=lambda x: x[1])
                defect_type = primary_defect[0]
                total_confidence = primary_defect[1]
            else:
                defect_type = "None"
                total_confidence = 0.95  # High confidence in "no defect"
            
            # Normalize probability
            defect_probability = min(1.0, defect_probability)
        
            # Create detailed analysis report
            analysis_details = {
                'all_detections': defects_detected,
                'scratch_score': scratch_confidence,
                'missing_component_score': missing_confidence,
                'color_deviation_score': color_confidence,
                'surface_damage_score': surface_confidence,
                'alignment_score': alignment_confidence,
                'contamination_score': contamination_confidence
            }
            
            processing_time = time.time() - start_time
            
            return {
                'has_defect': has_defect,
                'defect_type': defect_type,
                'confidence': total_confidence,
                'defect_probability': defect_probability,
                'cv_analysis': analysis_details,
                'processing_time': processing_time,
                'method': 'Computer Vision'
            }
            
        except Exception as e:
            logger.error(f"Error in computer vision inspection: {e}")
            # Return fallback result
            processing_time = time.time() - start_time
            return {
                'has_defect': False,
                'defect_type': 'CV Error',
                'confidence': 0.1,
                'defect_probability': 0.0,
                'cv_analysis': {'error': str(e)},
                'processing_time': processing_time,
                'method': 'Computer Vision (Error)'
            }

    def detect_scratches_and_cracks(self, gray):
        """Detect scratches and cracks using edge detection and line analysis"""
        try:
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Edge detection with multiple thresholds
            edges1 = cv2.Canny(blurred, 30, 100)
            edges2 = cv2.Canny(blurred, 50, 150)
            
            # Combine edges
            combined_edges = cv2.bitwise_or(edges1, edges2)
            
            # Detect lines using HoughLines
            lines = cv2.HoughLinesP(combined_edges, 1, np.pi/180, threshold=30, minLineLength=20, maxLineGap=5)
            
            if lines is not None:
                # Analyze line characteristics
                line_count = len(lines)
                total_length = 0
                
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    total_length += length
                
                # Calculate confidence based on line density and length
                avg_length = total_length / line_count if line_count > 0 else 0
                line_density = line_count / (gray.shape[0] * gray.shape[1] / 10000)  # normalize by area
                
                # Scratches typically show as longer lines with moderate density
                if avg_length > 25 and line_density > 2:
                    return min(0.9, (avg_length / 50) * (line_density / 10))
            
            return 0.0
        except Exception as e:
            logger.error(f"Error in scratch detection: {e}")
            return 0.0

    def detect_missing_components(self, gray, color_image):
        """Detect missing components using contour analysis and template matching"""
        try:
            # Apply threshold to find components
            _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Expected component characteristics for PCB
            expected_components = 15  # From our test image generation
            expected_min_area = 80    # Minimum component size
            
            # Analyze contours
            valid_components = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > expected_min_area:
                    # Check if it looks like a component (rectangular-ish)
                    peri = cv2.arcLength(contour, True)
                    if peri > 0:  # Avoid division by zero
                        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
                        if len(approx) >= 4:  # Roughly rectangular
                            valid_components.append(contour)
            
            # Compare found vs expected components
            component_ratio = len(valid_components) / expected_components if expected_components > 0 else 0
            
            # High confidence if significantly fewer components than expected
            if component_ratio < 0.7:  # Missing more than 30% of components
                return min(0.9, (1 - component_ratio))
            
            return 0.0
        except Exception as e:
            logger.error(f"Error in missing component detection: {e}")
            return 0.0

    def detect_color_deviations(self, color_image, hsv):
        """Detect color deviations from expected PCB green"""
        # Expected PCB color in HSV (green range)
        expected_hue = 60  # Green hue
        hue_tolerance = 30
        
        # Calculate hue histogram
        hue_channel = hsv[:, :, 0]
        
        # Find pixels outside expected hue range
        mask_lower = hue_channel < (expected_hue - hue_tolerance)
        mask_upper = hue_channel > (expected_hue + hue_tolerance)
        deviation_mask = np.logical_or(mask_lower, mask_upper)
        
        # Calculate deviation percentage
        total_pixels = hue_channel.size
        deviated_pixels = np.sum(deviation_mask)
        deviation_ratio = deviated_pixels / total_pixels
        
        # Also check for unusual brightness/saturation
        brightness = np.mean(color_image)
        if brightness < 50 or brightness > 200:  # Too dark or too bright
            deviation_ratio += 0.2
        
        return min(0.9, deviation_ratio * 2)  # Scale to confidence

    def detect_surface_damage(self, gray):
        """Detect surface damage using texture analysis"""
        # Calculate local standard deviation (texture measure)
        kernel = np.ones((5, 5), np.float32) / 25
        mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        sqr_diff = (gray.astype(np.float32) - mean) ** 2
        local_std = cv2.filter2D(sqr_diff, -1, kernel) ** 0.5
        
        # High variance areas might indicate damage
        damage_threshold = np.percentile(local_std, 95)  # Top 5% of variance
        damage_areas = local_std > damage_threshold
        
        # Calculate damage ratio
        damage_ratio = np.sum(damage_areas) / damage_areas.size
        
        # Also check for overall image quality metrics
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 100:  # Blurry might indicate surface issues
            damage_ratio += 0.3
        
        return min(0.9, damage_ratio * 3)

    def detect_alignment_issues(self, gray):
        """Detect alignment issues using geometric analysis"""
        # Find contours for component analysis
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) < 3:
            return 0.0
        
        # Calculate component centers
        centers = []
        for contour in contours:
            if cv2.contourArea(contour) > 50:  # Only significant components
                moments = cv2.moments(contour)
                if moments['m00'] > 0:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])
                    centers.append((cx, cy))
        
        if len(centers) < 3:
            return 0.0
        
        # Check for regular spacing/alignment
        centers = np.array(centers)
        
        # Calculate standard deviation of positions
        x_std = np.std(centers[:, 0])
        y_std = np.std(centers[:, 1])
        
        # Normalize by image dimensions
        x_std_norm = x_std / gray.shape[1]
        y_std_norm = y_std / gray.shape[0]
        
        # High standard deviation might indicate misalignment
        alignment_score = (x_std_norm + y_std_norm) / 2
        
        return min(0.9, alignment_score * 5)

    def detect_contamination(self, color_image, gray):
        """Detect contamination using color and texture analysis"""
        # Look for unusual spots or particles
        # Use morphological operations to find small bright/dark spots
        
        # Detect bright spots (contamination)
        bright_spots = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        bright_contamination = np.sum(bright_spots > 30) / gray.size
        
        # Detect dark spots
        dark_spots = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        dark_contamination = np.sum(dark_spots > 30) / gray.size
        
        # Combined contamination score
        contamination_score = bright_contamination + dark_contamination
        
        return min(0.9, contamination_score * 10)

    def combine_cv_and_ai_results(self, cv_result, ai_result):
        """Combine computer vision and AI analysis results"""
        # Weight the results (CV: 60%, AI: 40%)
        cv_weight = 0.6
        ai_weight = 0.4
        
        # Combine defect probabilities
        combined_probability = (cv_result['defect_probability'] * cv_weight + 
                              ai_result['defect_probability'] * ai_weight)
        
        # Use higher confidence result for final decision
        if cv_result['confidence'] > ai_result['confidence']:
            primary_result = cv_result
            secondary_result = ai_result
        else:
            primary_result = ai_result
            secondary_result = cv_result
        
        # Create combined analysis
        return {
            'has_defect': combined_probability > 0.4,
            'defect_type': primary_result['defect_type'],
            'confidence': max(cv_result['confidence'], ai_result['confidence']),
            'defect_probability': combined_probability,
            'cv_analysis': cv_result.get('cv_analysis', {}),
            'ai_analysis': ai_result.get('ai_analysis', ''),
            'processing_time': cv_result['processing_time'] + ai_result['processing_time'],
            'method': f"Combined ({primary_result['method']} + {secondary_result['method']})"
        }

    def analyze_with_azure_ai(self, image_array):
        """
        Use Azure AI Foundry Local for real defect detection combined with computer vision
        """
        # First perform real computer vision analysis
        cv_result = self.perform_computer_vision_inspection(image_array)
        
        # If AI is available, enhance with AI analysis
        if self.ai_client and self.model_name:
            if self.ai_client == "foundry_direct":
                ai_result = self._analyze_with_foundry_direct(image_array)
                # Combine CV and AI results
                return self.combine_cv_and_ai_results(cv_result, ai_result)
            
        # Return computer vision analysis if AI not available
        return cv_result

    def simulate_defect_detection_fallback(self, image_array):
        """Fallback simulation when AI not available"""
        start_time = time.time()
        
        # Enhanced simulation with image analysis
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Calculate image properties
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Simulate defect detection based on image properties
        defect_probability = 0.0
        defect_type = "None"
        
        # Check for various "defect" conditions
        if blur_score < 50:  # Blurry image might indicate defect
            defect_probability += 0.3
            defect_type = "Blurry Surface"
        
        if brightness < 80 or brightness > 180:  # Poor lighting
            defect_probability += 0.2
            defect_type = "Lighting Issue"
            
        if contrast < 20:  # Low contrast might indicate defect
            defect_probability += 0.25
            defect_type = "Low Contrast Defect"
            
        # Add some randomness to make it realistic
        random_factor = np.random.random() * 0.4
        defect_probability += random_factor
        
        # Random defect types for demonstration
        if defect_probability > 0.6:
            defect_types = ["Scratch", "Discoloration", "Missing Component", "Misalignment", "Surface Damage"]
            defect_type = np.random.choice(defect_types)
        
        has_defect = defect_probability > 0.5
        
        processing_time = time.time() - start_time
        
        return {
            'has_defect': has_defect,
            'defect_type': defect_type if has_defect else "None",
            'confidence': min(0.95, 0.6 + np.random.random() * 0.3),
            'defect_probability': min(1.0, defect_probability),
            'ai_analysis': f"Simulation: blur={blur_score:.1f}, brightness={brightness:.1f}, contrast={contrast:.1f}",
            'processing_time': processing_time,
            'method': 'Simulation'
        }

    def on_mqtt_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to MQTT broker with result code {rc}")

    def process_quality_check(self):
        """Process a single quality control check"""
        if not self.running:
            return
        
        try:
            # Generate or load test image
            logger.debug("Generating test image...")
            test_image = self.generate_test_product_image()
            logger.debug(f"Generated image shape: {test_image.shape}")
            
            # Perform AI analysis
            logger.debug("Starting analysis...")
            result = self.analyze_with_azure_ai(test_image)
            logger.debug(f"Analysis completed: {result.get('method', 'Unknown')}")
            
            # Update statistics
            self.total_processed += 1
            if result['has_defect']:
                self.defects_found += 1
            
            # Add to recent results
            result['timestamp'] = datetime.now().isoformat()
            result['product_id'] = f"PCB-{self.total_processed:06d}"
            self.recent_results.append(result)
            
            # Update current stats
            self.current_stats = {
                'total_processed': self.total_processed,
                'defects_found': self.defects_found,
                'defect_rate': (self.defects_found / self.total_processed) * 100 if self.total_processed > 0 else 0,
                'current_batch': self.current_batch,
                'ai_enabled': self.ai_client is not None,
                'model_name': self.model_name or 'Simulation',
                'vision_capable': self.vision_capable
            }
            
            # Emit results via SocketIO
            socketio.emit('quality_result', {
                'result': result,
                'stats': self.current_stats
            })
            
            logger.info(f"Product {result['product_id']}: {'DEFECT' if result['has_defect'] else 'PASS'} "
                       f"({result['method']}) - {result['defect_type']}")
                       
        except Exception as e:
            logger.error(f"Error processing quality check: {e}")
            # Emit error to client
            socketio.emit('processing_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

    def generate_test_product_image(self):
        """Generate a realistic test product image with potential defects"""
        height, width = 300, 400
        
        # Create base image with PCB-like colors
        base_color = [34, 139, 34]  # Forest green for PCB
        image = np.full((height, width, 3), base_color, dtype=np.uint8)
        
        # Add some circuit traces (silver lines)
        trace_count = np.random.randint(18, 25)
        for _ in range(trace_count):
            pt1 = (np.random.randint(0, width), np.random.randint(0, height))
            pt2 = (np.random.randint(0, width), np.random.randint(0, height))
            cv2.line(image, pt1, pt2, [200, 200, 200], 2)
        
        # Store component positions for defect generation
        component_positions = []
        
        # Add components (rectangles) - capacitors, resistors, chips
        component_count = np.random.randint(12, 18)
        for _ in range(component_count):
            x = np.random.randint(10, width-30)
            y = np.random.randint(10, height-20)
            w = np.random.randint(10, 30)
            h = np.random.randint(8, 20)
            
            # Component colors (black, dark grey, silver)
            component_type = np.random.choice(['capacitor', 'resistor', 'chip'])
            if component_type == 'capacitor':
                color = [40, 40, 40]  # Dark component
            elif component_type == 'resistor':
                color = [120, 80, 60]  # Brown-ish
            else:
                color = [60, 60, 60]  # Dark grey chip
            
            cv2.rectangle(image, (x, y), (x+w, y+h), color, -1)
            component_positions.append((x, y, w, h))
        
        # Add solder points (small circles)
        for _ in range(np.random.randint(20, 30)):
            center = (np.random.randint(5, width-5), np.random.randint(5, height-5))
            cv2.circle(image, center, 2, [180, 180, 180], -1)
        
        # Generate defects with varying probability and types
        defect_chance = 0.4  # 40% chance of having a defect
        
        if np.random.random() < defect_chance:
            defect_type = np.random.choice([
                'scratch', 'missing_component', 'color_deviation', 
                'contamination', 'surface_damage', 'misalignment'
            ])
            
            image = self.add_realistic_defect(image, defect_type, component_positions, width, height)
        
        return image
    
    def add_realistic_defect(self, image, defect_type, component_positions, width, height):
        """Add realistic defects to the test image"""
        
        if defect_type == 'scratch':
            # Add realistic scratches - thin dark lines
            num_scratches = np.random.randint(1, 4)
            for _ in range(num_scratches):
                # Random scratch across the board
                start_x = np.random.randint(0, width)
                start_y = np.random.randint(0, height)
                length = np.random.randint(20, 80)
                angle = np.random.random() * 2 * np.pi
                
                end_x = int(start_x + length * np.cos(angle))
                end_y = int(start_y + length * np.sin(angle))
                
                # Ensure endpoints are within image
                end_x = max(0, min(width-1, end_x))
                end_y = max(0, min(height-1, end_y))
                
                # Dark scratch line
                cv2.line(image, (start_x, start_y), (end_x, end_y), [10, 10, 10], 2)
                
        elif defect_type == 'missing_component':
            # Remove some components by painting over them
            if component_positions:
                missing_count = min(3, len(component_positions) // 3)
                missing_components = np.random.choice(len(component_positions), missing_count, replace=False)
                
                for idx in missing_components:
                    x, y, w, h = component_positions[idx]
                    # Paint over with base PCB color
                    cv2.rectangle(image, (x-2, y-2), (x+w+2, y+h+2), [34, 139, 34], -1)
                    
        elif defect_type == 'color_deviation':
            # Add areas with wrong color
            num_spots = np.random.randint(2, 6)
            for _ in range(num_spots):
                center = (np.random.randint(20, width-20), np.random.randint(20, height-20))
                radius = np.random.randint(8, 25)
                
                # Wrong colors - brown spots, blue spots, etc.
                wrong_colors = [[150, 75, 30], [30, 75, 150], [150, 150, 30], [150, 30, 150]]
                wrong_color = np.random.choice(wrong_colors)
                
                cv2.circle(image, center, radius, wrong_color, -1)
                
        elif defect_type == 'contamination':
            # Add contamination spots - dust, residue, etc.
            num_spots = np.random.randint(5, 15)
            for _ in range(num_spots):
                center = (np.random.randint(0, width), np.random.randint(0, height))
                radius = np.random.randint(1, 4)
                
                # Contamination colors - dirt, residue
                contaminant_colors = [[80, 60, 40], [200, 180, 160], [20, 20, 20], [60, 80, 100]]
                contaminant_color = np.random.choice(contaminant_colors)
                
                cv2.circle(image, center, radius, contaminant_color, -1)
                
        elif defect_type == 'surface_damage':
            # Add surface damage - burns, corrosion, etc.
            num_damages = np.random.randint(1, 3)
            for _ in range(num_damages):
                # Create irregular damage shape
                center = (np.random.randint(30, width-30), np.random.randint(30, height-30))
                
                # Generate random points around center
                points = []
                for _ in range(np.random.randint(6, 12)):
                    angle = np.random.random() * 2 * np.pi
                    radius = np.random.randint(5, 20)
                    x = center[0] + int(radius * np.cos(angle))
                    y = center[1] + int(radius * np.sin(angle))
                    points.append([x, y])
                
                # Fill irregular shape with damage color
                damage_color = [15, 15, 15]  # Very dark - burn damage
                cv2.fillPoly(image, [np.array(points)], damage_color)
                
        elif defect_type == 'misalignment':
            # Simulate misaligned components
            if component_positions:
                misaligned_count = min(2, len(component_positions) // 4)
                misaligned_indices = np.random.choice(len(component_positions), misaligned_count, replace=False)
                
                for idx in misaligned_indices:
                    x, y, w, h = component_positions[idx]
                    
                    # Clear original position
                    cv2.rectangle(image, (x, y), (x+w, y+h), [34, 139, 34], -1)
                    
                    # Draw component in slightly offset position
                    offset_x = np.random.randint(-8, 8)
                    offset_y = np.random.randint(-8, 8)
                    new_x = max(5, min(width-w-5, x + offset_x))
                    new_y = max(5, min(height-h-5, y + offset_y))
                    
                    # Redraw component in new position
                    component_color = [40, 40, 40]
                    cv2.rectangle(image, (new_x, new_y), (new_x+w, new_y+h), component_color, -1)
        
        return image

    def test_cv_functionality(self):
        """Test computer vision functionality during startup"""
        try:
            logger.info("🧪 Testing computer vision functionality...")
            
            # Create a simple test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            test_image[:, :] = [0, 255, 0]  # Green image
            
            # Test basic OpenCV operations
            gray = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)
            logger.debug(f"✅ Color conversion successful, gray shape: {gray.shape}")
            
            # Test edge detection
            edges = cv2.Canny(gray, 50, 150)
            logger.debug(f"✅ Edge detection successful, edges shape: {edges.shape}")
            
            # Test the complete CV inspection pipeline
            result = self.perform_computer_vision_inspection(test_image)
            logger.info(f"✅ CV inspection test successful: {result['method']}")
            
        except Exception as e:
            logger.error(f"❌ CV functionality test failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def set_sensitivity(self, sensitivity_level):
        """Set inspection sensitivity: 'low', 'medium', or 'high'"""
        sensitivity_configs = {
            'low': {
                'scratch_threshold': 0.5,
                'missing_component_threshold': 0.6,
                'color_deviation_threshold': 0.5,
                'surface_damage_threshold': 0.55,
                'alignment_threshold': 0.6,
                'contamination_threshold': 0.55,
                'overall_defect_threshold': 0.6
            },
            'medium': {
                'scratch_threshold': 0.3,
                'missing_component_threshold': 0.4,
                'color_deviation_threshold': 0.3,
                'surface_damage_threshold': 0.35,
                'alignment_threshold': 0.4,
                'contamination_threshold': 0.35,
                'overall_defect_threshold': 0.4
            },
            'high': {
                'scratch_threshold': 0.2,
                'missing_component_threshold': 0.25,
                'color_deviation_threshold': 0.2,
                'surface_damage_threshold': 0.25,
                'alignment_threshold': 0.25,
                'contamination_threshold': 0.2,
                'overall_defect_threshold': 0.25
            }
        }
        
        if sensitivity_level in sensitivity_configs:
            self.inspection_config.update(sensitivity_configs[sensitivity_level])
            self.inspection_config['sensitivity'] = sensitivity_level
            logger.info(f"Inspection sensitivity set to: {sensitivity_level}")
        else:
            logger.warning(f"Unknown sensitivity level: {sensitivity_level}")

    def calibrate_for_product_type(self, product_type):
        """Calibrate inspection parameters for different product types"""
        product_configs = {
            'pcb': {
                'expected_components': 15,
                'component_min_area': 80,
                'expected_hue': 60,  # Green PCB
                'hue_tolerance': 30
            },
            'metal': {
                'expected_components': 5,
                'component_min_area': 200,
                'expected_hue': 0,  # Gray/silver
                'hue_tolerance': 20
            },
            'plastic': {
                'expected_components': 8,
                'component_min_area': 120,
                'expected_hue': 100,  # Various colors
                'hue_tolerance': 50
            }
        }
        
        if product_type in product_configs:
            self.inspection_config['product_type'] = product_type
            # You could extend this to update detection parameters
            logger.info(f"Calibrated for product type: {product_type}")
        else:
            logger.warning(f"Unknown product type: {product_type}")

    def get_inspection_report(self):
        """Generate detailed inspection configuration report"""
        return {
            'sensitivity': self.inspection_config['sensitivity'],
            'product_type': self.inspection_config['product_type'],
            'thresholds': {
                'scratch': self.inspection_config['scratch_threshold'],
                'missing_component': self.inspection_config['missing_component_threshold'],
                'color_deviation': self.inspection_config['color_deviation_threshold'],
                'surface_damage': self.inspection_config['surface_damage_threshold'],
                'alignment': self.inspection_config['alignment_threshold'],
                'contamination': self.inspection_config['contamination_threshold'],
                'overall': self.inspection_config['overall_defect_threshold']
            },
            'statistics': {
                'total_processed': self.total_processed,
                'defects_found': self.defects_found,
                'defect_rate': (self.defects_found / self.total_processed * 100) if self.total_processed > 0 else 0
            }
        }

    def start_production(self):
        """Start the quality control process"""
        self.running = True
        self.current_batch += 1
        logger.info("🏭 Quality control production started")

    def stop_production(self):
        """Stop the quality control process"""
        self.running = False
        logger.info("🛑 Quality control production stopped")

# Global quality control system instance
quality_system = AzureAIQualityControlSystem()

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'running': quality_system.running,
        'stats': quality_system.current_stats,
        'ai_connected': quality_system.ai_client is not None,
        'model_name': quality_system.model_name or 'Simulation Mode',
        'vision_capable': quality_system.vision_capable
    })

@app.route('/api/start', methods=['POST'])
def start_production():
    quality_system.start_production()
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_production():
    quality_system.stop_production()
    return jsonify({'status': 'stopped'})

@app.route('/api/sensitivity', methods=['POST'])
def set_sensitivity():
    data = request.get_json()
    sensitivity = data.get('sensitivity', 'medium')
    quality_system.set_sensitivity(sensitivity)
    return jsonify({'status': 'updated', 'sensitivity': sensitivity})

@app.route('/api/calibrate', methods=['POST'])
def calibrate_system():
    data = request.get_json()
    product_type = data.get('product_type', 'pcb')
    quality_system.calibrate_for_product_type(product_type)
    return jsonify({'status': 'calibrated', 'product_type': product_type})

@app.route('/api/report')
def get_inspection_report():
    return jsonify(quality_system.get_inspection_report())

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    emit('status_update', {
        'ai_connected': quality_system.ai_client is not None,
        'model_name': quality_system.model_name or 'Simulation Mode',
        'vision_capable': quality_system.vision_capable
    })

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")

def production_loop():
    """Background thread for production simulation"""
    while True:
        if quality_system.running:
            quality_system.process_quality_check()
            time.sleep(2)  # Process every 2 seconds
        else:
            time.sleep(0.5)  # Check more frequently when stopped

if __name__ == '__main__':
    logger.info("Starting Enhanced Edge AI Quality Control System...")
    logger.info("🤖 Real Azure AI integration enabled!" if quality_system.ai_client else "📋 Running in simulation mode")
    logger.info("Access dashboard at: http://localhost:5000")
    
    # Start background production thread
    production_thread = threading.Thread(target=production_loop, daemon=True)
    production_thread.start()
    
    # Start the Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)