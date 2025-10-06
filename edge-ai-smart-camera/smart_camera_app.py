"""
Edge AI Smart Surveillance Camera System
Real-time object detection and anomaly detection on edge devices
"""

import cv2
import numpy as np
import time
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, Response
from flask_socketio import SocketIO, emit
import logging
import os
from collections import deque, defaultdict
import queue
import math

# Feature flags for logging control
ENABLE_DEBUG_LOGGING = os.getenv('ENABLE_DEBUG_LOGGING', 'false').lower() == 'true'
ENABLE_FLASK_DEBUG = os.getenv('ENABLE_FLASK_DEBUG', 'false').lower() == 'true'

# Configure logging based on feature flags
log_level = logging.DEBUG if ENABLE_DEBUG_LOGGING else logging.WARNING
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Reduce werkzeug (Flask) logging noise
logging.getLogger('werkzeug').setLevel(logging.ERROR if not ENABLE_FLASK_DEBUG else logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-camera-demo-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class SmartCameraSystem:
    def __init__(self):
        self.detection_confidence = 0.5
        self.tracking_enabled = True
        self.anomaly_detection = True
        
        # Detection statistics
        self.stats = {
            'total_detections': 0,
            'people_count': 0,
            'vehicles_count': 0,
            'current_people': 0,
            'alerts': [],
            'avg_processing_time': 0,
            'fps': 0
        }
        
        # Tracking data
        self.tracks = {}
        self.track_id_counter = 0
        self.processing_times = deque(maxlen=100)
        
        # Anomaly detection
        self.person_positions = deque(maxlen=1000)
        self.normal_patterns = {}
        
        # Video capture
        self.camera = None
        self.frame_queue = queue.Queue(maxsize=10)
        self.latest_frame = None
        self.is_processing = False
        self.use_webcam = True  # Always try to use webcam first
        self.selected_camera_index = 1  # Use camera 1 instead of camera 0
        self.available_cameras = []
        self.camera_switch_requested = False  # Flag to handle camera switching
        
        # AI Model setup
        self.net = None
        self.model_loaded = False
        self.output_layers = []
        self.input_size = (416, 416)  # YOLO input size
        
        # COCO class names for MobileNet SSD
        self.class_names = [
            'background', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant', '', 'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
            'elephant', 'bear', 'zebra', 'giraffe', '', 'backpack', 'umbrella', '', '',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', '', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
            'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', '', 'dining table',
            '', '', 'toilet', '', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
            'microwave', 'oven', 'toaster', 'sink', 'refrigerator', '', 'book',
            'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
        # Load AI model
        self.load_model()
        
        # Discover available cameras
        self.discover_cameras()
        
    def load_model(self):
        """Load YOLOv4-tiny model for lightweight object detection"""
        try:
            weights_path = os.path.join(os.path.dirname(__file__), 'models', 'yolov4-tiny.weights')
            config_path = os.path.join(os.path.dirname(__file__), 'models', 'yolov4-tiny.cfg')
            names_path = os.path.join(os.path.dirname(__file__), 'models', 'coco.names')
            
            if os.path.exists(weights_path) and os.path.exists(config_path):
                self.net = cv2.dnn.readNet(weights_path, config_path)
                
                # Load class names
                if os.path.exists(names_path):
                    with open(names_path, 'r') as f:
                        self.class_names = [line.strip() for line in f.readlines()]
                
                # Set backend and target for better performance
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                
                # Get output layer names
                self.output_layers = self.net.getUnconnectedOutLayersNames()
                
                self.model_loaded = True
                logger.info("YOLOv4-tiny model loaded successfully")
            else:
                logger.warning("YOLO model files not found. Using fallback detection.")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            self.model_loaded = False

    def discover_cameras(self):
        """Discover all available cameras on the system"""
        logger.info("Discovering available cameras...")
        self.available_cameras = []
        
        # Try different backends
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        
        for camera_idx in range(10):  # Check first 10 camera indices
            for backend in backends:
                try:
                    test_camera = cv2.VideoCapture(camera_idx, backend)
                    if test_camera.isOpened():
                        ret, frame = test_camera.read()
                        if ret and frame is not None:
                            camera_info = {
                                'index': camera_idx,
                                'backend': backend,
                                'backend_name': self.get_backend_name(backend),
                                'name': f"Camera {camera_idx}"
                            }
                            
                            # Check if this camera is already in the list
                            if not any(cam['index'] == camera_idx for cam in self.available_cameras):
                                self.available_cameras.append(camera_info)
                                logger.info(f"Found camera {camera_idx} with backend {self.get_backend_name(backend)}")
                            
                            test_camera.release()
                            break  # Found working backend for this camera
                    else:
                        test_camera.release()
                except:
                    if 'test_camera' in locals():
                        test_camera.release()
        
        logger.info(f"Found {len(self.available_cameras)} available cameras")

    def get_backend_name(self, backend):
        """Get human-readable backend name"""
        backend_names = {
            cv2.CAP_DSHOW: "DirectShow",
            cv2.CAP_MSMF: "Media Foundation", 
            cv2.CAP_ANY: "Auto"
        }
        return backend_names.get(backend, f"Backend {backend}")

    def set_camera(self, camera_index):
        """Set the selected camera index and trigger camera switch"""
        old_camera_index = self.selected_camera_index
        self.selected_camera_index = camera_index
        logger.info(f"Requesting camera switch from index {old_camera_index} to {camera_index}")
        
        # Release current camera if active
        if self.camera is not None:
            logger.info("Releasing current camera...")
            self.camera.release()
            self.camera = None
            
        # Set flag to trigger camera switch in camera thread
        self.camera_switch_requested = True
        
        # Wait a moment for the switch to happen
        import time
        time.sleep(3)
        
        # Check if camera is working
        if self.camera is not None and self.camera.isOpened():
            logger.info(f"Successfully switched to camera {camera_index}")
            return True
        else:
            logger.error(f"Failed to switch to camera {camera_index}")
            return False

    def initialize_camera(self):
        """Initialize built-in webcam for real-time processing"""
        logger.info(f"Attempting to initialize built-in webcam (index {self.selected_camera_index})...")
        
        try:
            # Always try DirectShow first for Windows built-in webcams
            logger.info(f"Using camera {self.selected_camera_index} with DirectShow backend (best for built-in webcams)")
            self.camera = cv2.VideoCapture(self.selected_camera_index, cv2.CAP_DSHOW)
            
            # Wait a moment for camera to initialize
            import time
            time.sleep(0.8)  # Longer wait for built-in cameras
            
            if self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    # Set optimal properties for built-in webcam
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.camera.set(cv2.CAP_PROP_FPS, 30)
                    self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
                    
                    logger.info(f"Built-in webcam initialized successfully!")
                    self.use_webcam = True
                    return True
                else:
                    logger.warning("Camera opened but cannot read frames")
                    self.camera.release()
            
            # If DirectShow fails, try other backends
            logger.info("DirectShow failed, trying other backends...")
            for backend in [cv2.CAP_MSMF, cv2.CAP_ANY]:
                backend_name = self.get_backend_name(backend)
                logger.info(f"Trying {backend_name} backend...")
                
                self.camera = cv2.VideoCapture(self.selected_camera_index, backend)
                time.sleep(0.5)
                
                if self.camera.isOpened():
                    ret, frame = self.camera.read()
                    if ret and frame is not None:
                        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.camera.set(cv2.CAP_PROP_FPS, 30)
                        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        
                        logger.info(f"Built-in webcam initialized with {backend_name}!")
                        self.use_webcam = True
                        return True
                    else:
                        self.camera.release()
                        
            raise Exception("Built-in webcam not accessible")
                    
        except Exception as e:
            logger.warning(f"Built-in webcam initialization failed: {e}")
            logger.info("Using test video pattern instead")
            self.camera = None
            self.use_webcam = False
            return False
    
    def generate_test_frame(self, frame_count):
        """Generate test frames with moving objects for demo"""
        height, width = 480, 640
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add background pattern
        frame[:] = (20, 30, 40)
        
        # Simulate moving people
        time_factor = frame_count * 0.1
        
        # Person 1 - walking horizontally
        x1 = int((math.sin(time_factor * 0.5) * 200 + 320))
        y1 = 300
        cv2.circle(frame, (x1, y1), 30, (0, 255, 0), -1)
        cv2.putText(frame, 'Person', (x1-30, y1-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Person 2 - walking vertically  
        x2 = 150
        y2 = int((math.cos(time_factor * 0.3) * 100 + 240))
        cv2.circle(frame, (x2, y2), 25, (0, 255, 0), -1)
        cv2.putText(frame, 'Person', (x2-30, y2-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Vehicle
        if frame_count % 200 < 100:  # Intermittent vehicle
            x3 = int((frame_count % 200) * 6)
            y3 = 400
            cv2.rectangle(frame, (x3, y3), (x3+80, y3+40), (255, 0, 0), -1)
            cv2.putText(frame, 'Car', (x3, y3-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"DEMO FEED - {timestamp}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def detect_objects_ai(self, frame):
        """
        Real AI object detection using YOLOv4-tiny
        """
        start_time = time.time()
        detections = []
        
        if not self.model_loaded or self.net is None:
            # Fallback to simple detection if model not loaded
            return self.fallback_detection(frame)
        
        try:
            height, width = frame.shape[:2]
            
            # Create blob from image for YOLO
            blob = cv2.dnn.blobFromImage(
                frame, 1/255.0, (416, 416), (0, 0, 0), True, crop=False
            )
            
            # Set input to the network
            self.net.setInput(blob)
            
            # Run forward pass
            outputs = self.net.forward(self.output_layers)
            
            # Parse YOLO outputs
            boxes = []
            confidences = []
            class_ids = []
            
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > self.detection_confidence:
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else "unknown"
                        
                        # Only detect people, vehicles, and some other relevant objects
                        if class_name in ['person', 'car', 'truck', 'bus', 'motorbike', 'bicycle']:
                            # Object detected
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)
                            
                            # Rectangle coordinates
                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)
                            
                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)
            
            # Apply Non-Maximum Suppression to eliminate redundant overlapping boxes
            indices = cv2.dnn.NMSBoxes(boxes, confidences, self.detection_confidence, 0.4)
            
            if len(indices) > 0:
                for i in indices.flatten():
                    x, y, w, h = boxes[i]
                    class_name = self.class_names[class_ids[i]] if class_ids[i] < len(self.class_names) else "unknown"
                    confidence = confidences[i]
                    
                    # Ensure coordinates are within frame bounds
                    x = max(0, x)
                    y = max(0, y)
                    w = min(w, width - x)
                    h = min(h, height - y)
                    
                    # Filter out very small detections
                    if w > 30 and h > 30:
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        detections.append({
                            'class': class_name,
                            'confidence': confidence,
                            'bbox': [x, y, w, h],
                            'center': [center_x, center_y]
                        })
            
        except Exception as e:
            logger.error(f"AI detection error: {e}")
            return self.fallback_detection(frame)
        
        processing_time = (time.time() - start_time) * 1000
        self.processing_times.append(processing_time)
        
        return detections, processing_time
    
    def fallback_detection(self, frame):
        """
        Simple fallback detection when AI model is not available
        """
        start_time = time.time()
        
        # Use motion detection as fallback
        detections = []
        
        # Convert to grayscale for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Simple background subtraction (very basic)
        if hasattr(self, 'background'):
            diff = cv2.absdiff(self.background, gray)
            _, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Filter small movements
                    x, y, w, h = cv2.boundingRect(contour)
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    detections.append({
                        'class': 'person',  # Assume person for motion
                        'confidence': 0.6,
                        'bbox': [x, y, w, h],
                        'center': [center_x, center_y]
                    })
        else:
            self.background = gray.copy()
        
        processing_time = (time.time() - start_time) * 1000
        self.processing_times.append(processing_time)
        
        return detections, processing_time
    
    def track_objects(self, detections):
        """Simple object tracking for demo"""
        if not self.tracking_enabled:
            return detections
        
        current_tracks = {}
        
        for detection in detections:
            center = detection['center']
            best_match = None
            min_distance = float('inf')
            
            # Find closest existing track
            for track_id, track_data in self.tracks.items():
                distance = math.sqrt(
                    (center[0] - track_data['center'][0]) ** 2 + 
                    (center[1] - track_data['center'][1]) ** 2
                )
                
                if distance < min_distance and distance < 100:  # 100 pixel threshold
                    min_distance = distance
                    best_match = track_id
            
            if best_match:
                # Update existing track
                detection['track_id'] = best_match
                current_tracks[best_match] = detection
            else:
                # Create new track
                self.track_id_counter += 1
                detection['track_id'] = self.track_id_counter
                current_tracks[self.track_id_counter] = detection
        
        self.tracks = current_tracks
        return detections
    
    def detect_anomalies(self, detections):
        """Simple anomaly detection based on movement patterns"""
        if not self.anomaly_detection:
            return []
        
        anomalies = []
        current_time = datetime.now()
        
        for detection in detections:
            if detection['class'] == 'person':
                center = detection['center']
                
                # Record position
                self.person_positions.append({
                    'position': center,
                    'timestamp': current_time,
                    'track_id': detection.get('track_id', 0)
                })
                
                # Check for loitering (same area for extended time)
                recent_positions = [
                    p for p in self.person_positions 
                    if (current_time - p['timestamp']).seconds < 30 and 
                       p['track_id'] == detection.get('track_id', 0)
                ]
                
                if len(recent_positions) > 10:  # 10 positions in 30 seconds
                    # Check if person stayed in same area
                    positions = [p['position'] for p in recent_positions]
                    max_distance = max([
                        math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
                        for p1 in positions for p2 in positions
                    ])
                    
                    if max_distance < 50:  # Stayed within 50 pixel radius
                        anomalies.append({
                            'type': 'Loitering Detected',
                            'position': center,
                            'track_id': detection.get('track_id', 0),
                            'confidence': 0.85,
                            'timestamp': current_time.isoformat()
                        })
                
                # Check for rapid movement (potential running/emergency)
                if len(recent_positions) >= 2:
                    last_pos = recent_positions[-2]['position']
                    current_pos = center
                    distance = math.sqrt(
                        (current_pos[0] - last_pos[0])**2 + 
                        (current_pos[1] - last_pos[1])**2
                    )
                    
                    if distance > 80:  # Moved more than 80 pixels between frames
                        anomalies.append({
                            'type': 'Rapid Movement',
                            'position': center,
                            'track_id': detection.get('track_id', 0),
                            'confidence': 0.75,
                            'timestamp': current_time.isoformat()
                        })
        
        return anomalies
    
    def update_statistics(self, detections, anomalies, processing_time):
        """Update system statistics"""
        self.stats['total_detections'] += len(detections)
        
        current_people = len([d for d in detections if d['class'] == 'person'])
        current_vehicles = len([d for d in detections if d['class'] in ['car', 'truck', 'bus']])
        
        self.stats['current_people'] = current_people
        self.stats['people_count'] = max(self.stats['people_count'], current_people)
        self.stats['vehicles_count'] += current_vehicles
        
        if self.processing_times:
            self.stats['avg_processing_time'] = np.mean(self.processing_times)
        
        # Add anomalies to alerts
        for anomaly in anomalies:
            self.stats['alerts'].append(anomaly)
        
        # Keep only recent alerts
        if len(self.stats['alerts']) > 100:
            self.stats['alerts'] = self.stats['alerts'][-100:]
    
    def process_frame(self, frame):
        """Process single frame with real AI detection"""
        # Detect objects using AI
        detections, processing_time = self.detect_objects_ai(frame)
        
        # Track objects
        detections = self.track_objects(detections)
        
        # Detect anomalies
        anomalies = self.detect_anomalies(detections)
        
        # Update statistics
        self.update_statistics(detections, anomalies, processing_time)
        
        # Draw visualizations
        annotated_frame = self.draw_annotations(frame.copy(), detections, anomalies)
        
        return annotated_frame, detections, anomalies
    
    def draw_annotations(self, frame, detections, anomalies):
        """Draw detection bounding boxes only - no green zone boxes"""
        # Draw detection bounding boxes
        for detection in detections:
            x, y, w, h = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            # Color based on class
            color = (0, 255, 0) if class_name == 'person' else (0, 0, 255)
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{class_name} {confidence:.0%}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame

# Global camera system
camera_system = SmartCameraSystem()
frame_count = 0

def camera_thread():
    """Background thread for real-time webcam processing"""
    global frame_count
    
    camera_initialized = camera_system.initialize_camera()
    
    while True:
        try:
            # Check if camera switch was requested
            if camera_system.camera_switch_requested:
                logger.info("Camera switch detected, reinitializing...")
                camera_initialized = camera_system.initialize_camera()
                camera_system.camera_switch_requested = False
                continue
            
            if camera_initialized and camera_system.camera is not None and camera_system.camera.isOpened():
                ret, frame = camera_system.camera.read()
                if not ret:
                    logger.warning("Failed to read frame from webcam, trying to reinitialize...")
                    camera_initialized = camera_system.initialize_camera()
                    time.sleep(0.1)
                    continue
                    
                # Flip frame horizontally for mirror effect (more natural for users)
                frame = cv2.flip(frame, 1)
                
            else:
                # Use test pattern as fallback
                logger.info("Using test pattern - webcam not available")
                frame = camera_system.generate_test_frame(frame_count)
                frame_count += 1
            
            # Process frame with real AI detection
            annotated_frame, detections, anomalies = camera_system.process_frame(frame)
            camera_system.latest_frame = annotated_frame
            
            # Calculate and update FPS
            camera_system.stats['fps'] = min(10, 1.0 / max(0.1, camera_system.stats['avg_processing_time'] / 1000.0))
            
            # Emit real-time updates
            socketio.emit('camera_update', {
                'detections': len(detections),
                'anomalies': len(anomalies),
                'stats': camera_system.stats,
                'using_webcam': camera_system.use_webcam,
                'model_loaded': camera_system.model_loaded
            })
            
            # Adaptive frame rate based on processing time
            sleep_time = max(0.05, 0.1 - (camera_system.stats['avg_processing_time'] / 1000.0))
            time.sleep(sleep_time)
            
        except Exception as e:
            logger.error(f"Error in camera thread: {e}")
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if camera_system.latest_frame is not None:
                ret, jpeg = cv2.imencode('.jpg', camera_system.latest_frame)
                if ret:
                    frame = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    return jsonify(camera_system.stats)

# Camera API routes removed - using fixed camera 1

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to smart camera')
    emit('camera_update', {'stats': camera_system.stats})

if __name__ == '__main__':
    # Start camera processing thread
    camera_thread_instance = threading.Thread(target=camera_thread, daemon=True)
    camera_thread_instance.start()
    
    print("Starting Edge AI Smart Camera System...")
    print("Access dashboard at: http://localhost:5002")
    
    socketio.run(app, host='0.0.0.0', port=5002, debug=ENABLE_FLASK_DEBUG, log_output=ENABLE_FLASK_DEBUG)