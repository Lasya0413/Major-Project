import yaml
import numpy as np
import cv2
from ultralytics import YOLO
import requests
import json
from datetime import datetime
import threading
import time
import os

# Load YOLOv8 model
print("Loading YOLOv8 model...")
model = YOLO("yolov8s.pt")
print("Model loaded!")

# Create folder for capturing parking events
capture_folder = capture_folder = os.path.join(os.getcwd(), "captures")

if not os.path.exists(capture_folder):
    os.makedirs(capture_folder)
    print(f"✓ Created capture folder: {capture_folder}")
else:
    print(f"✓ Capture folder exists: {capture_folder}")

# Configurations
fn_yaml = r"D:\output.yml"
config = {
    'save_video': False,
    'text_overlay': True,
    'parking_overlay': True,
    'parking_detection': True,
    'min_confidence': 0.1,
    'demo_mode': False  # LIVE CAMERA MODE
}

# Firebase Configuration
FIREBASE_DATABASE_URL = "https://lite-bc5e2-default-rtdb.asia-southeast1.firebasedatabase.app"
firebase_enabled = True

# Last update time (to avoid flooding Firebase)
last_firebase_update = 0
firebase_update_interval = 2  # Send to Firebase every 2 seconds

# Track occupied slots to avoid duplicate captures
occupied_slots_history = {}  # {slot_id: last_capture_time}
capture_debounce_interval = 5  # Capture once per 5 seconds per slot

def save_parking_event_photo(frame, slot_id, parking_status_list):
    """Save a photo when a parking slot is occupied"""
    global occupied_slots_history, capture_folder
    
    try:
        current_time = time.time()
        slot_key = f"slot_{slot_id}"
        
        # Check if we've recently captured this slot (debounce)
        if slot_key in occupied_slots_history:
            if current_time - occupied_slots_history[slot_key] < capture_debounce_interval:
                return  # Skip if captured recently
        
        # Ensure folder exists
        if not os.path.exists(capture_folder):
            os.makedirs(capture_folder)
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        
        # Determine occupancy status for all slots in filename
        # Replace colons with hyphens for Windows filename compatibility
        status_str = "_".join([f"S{i+1}-{'FULL' if status else 'FREE'}" for i, status in enumerate(parking_status_list)])
        
        # Create filename: timestamp_slotX_occupancyStatus.jpg
        filename = f"{timestamp}_slot{slot_id}_occupied_{status_str}.jpg"
        filepath = os.path.join(capture_folder, filename)
        
        # Save the frame with absolute path
        success = cv2.imwrite(filepath, frame)
        if success:
            occupied_slots_history[slot_key] = current_time
            relative_path = os.path.relpath(filepath, os.getcwd())
            print(f"[CAPTURE] 📸 Saved: {filename}")
            print(f"           📁 Path: {filepath}")
        else:
            print(f"[CAPTURE] ❌ Failed to save: {filepath}")
        
    except Exception as e:
        print(f"[CAPTURE] Error saving photo: {e}")

def send_to_firebase(empty_spaces, occupied_spaces):
    """Send parking data to Firebase Realtime Database in real-time"""
    global last_firebase_update
    
    # Rate limit to prevent too many requests
    current_time = time.time()
    if current_time - last_firebase_update < firebase_update_interval:
        return
    
    last_firebase_update = current_time
    
    try:
        timestamp = datetime.now().isoformat()
        total_spaces = empty_spaces + occupied_spaces
        
        data = {
            "empty_spaces": empty_spaces,
            "occupied_spaces": occupied_spaces,
            "total_spaces": total_spaces,
            "timestamp": timestamp,
            "occupancy_rate": round((occupied_spaces / total_spaces * 100), 2) if total_spaces > 0 else 0,
            "status": "FULL" if occupied_spaces == total_spaces else ("EMPTY" if empty_spaces == total_spaces else "PARTIAL")
        }
        
        # Send to Firebase REST API
        url = f"{FIREBASE_DATABASE_URL}/parking_status.json"
        response = requests.put(url, json=data, timeout=5)
        
        if response.status_code == 200:
            print(f"[Firebase] ✓ Data sent at {timestamp} | Empty={empty_spaces}, Occupied={occupied_spaces}, Rate={data['occupancy_rate']}%")
        else:
            print(f"[Firebase] Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[Firebase] Connection error: {e}")

# Try to open camera
print("\nAttempting to open camera...")
print("Device 0 = Built-in webcam")
print("Device 1 = USB camera")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Device 0 not available, trying device 1...")
    cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("ERROR: Could not open any camera device!")
    print("Make sure your camera is connected and not in use by another application.")
    exit()

print("✓ Camera opened successfully!")

# Set camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
cap.set(cv2.CAP_PROP_FPS, 30)

# Read YAML data (parking space polygons)
print(f"\nLoading parking spaces from {fn_yaml}...")
try:
    with open(fn_yaml, 'r') as stream:
        parking_data = yaml.safe_load(stream)
    if parking_data and isinstance(parking_data, list):
        print(f"✓ Loaded {len(parking_data)} parking spaces from YAML")
    else:
        raise ValueError("YAML data is empty or invalid")
except Exception as e:
    print(f"⚠ Could not load YAML ({e})")
    print("Using FALLBACK parking spaces...")
    # Fallback: 2 large parking spaces
    parking_data = [
        {'id': 1, 'points': [[150, 100], [350, 100], [350, 400], [150, 400]]},
        {'id': 2, 'points': [[450, 100], [650, 100], [650, 400], [450, 400]]}
    ]
    print(f"✓ Using {len(parking_data)} fallback parking spaces")

parking_contours = []
parking_bounding_rects = []
parking_status = [False] * len(parking_data)

# Prepare parking slot data
print("\nParking Slots Configuration:")
for i, park in enumerate(parking_data):
    points = np.array(park['points'])
    rect = cv2.boundingRect(points)
    parking_contours.append(points)
    parking_bounding_rects.append(rect)
    print(f"  Slot {i+1}: ID={park.get('id', i+1)}, Bounds={rect}")

print("\n" + "="*70)
print("YOLOv8 Car Parking Detection System - LIVE CAMERA MODE")
print("="*70)
print("Press 'Q' to quit")
print("Firebase: ENABLED - Sending data every 2 seconds")
print(f"📸 Photo Capture: ENABLED")
print(f"   📁 Location: {capture_folder}")
print(f"   💾 Files: Auto-saved when slots occupied")
print(f"   ⏱️  Debounce: 5 seconds per slot")
print("="*70 + "\n")

# Show helpful command to open capture folder
print("💡 Tip: To view captured photos, run in a separate terminal:")
print(f'   explorer "{capture_folder}"')
print()

frame_count = 0
start_time = time.time()

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from camera")
            break

        frame_count += 1
        frame_out = frame.copy()
        
        # Run YOLOv8 detection
        results = model(frame, verbose=False)
        
        detected_cars = []
        parking_status = [False] * len(parking_data)

        # Process YOLO detections
        detections_count = 0
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0].item())
                if cls != 2:  # Only detect cars (class 2)
                    continue
                
                detections_count += 1
                conf = box.conf[0].item()
                if conf < config['min_confidence']:
                    continue
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detected_cars.append((x1, y1, x2, y2, conf))
                
                # Draw car detection box (blue)
                cv2.rectangle(frame_out, (x1, y1), (x2, y2), (255, 100, 0), 2)
                cv2.putText(frame_out, f"Car {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 0), 2)

        # Check overlaps - determine which parking slots are occupied
        for car in detected_cars:
            x1, y1, x2, y2, conf = car
            for ind, rect in enumerate(parking_bounding_rects):
                px, py, pw, ph = rect
                # Check if car overlaps with parking slot
                if x1 < px + pw and x2 > px and y1 < py + ph and y2 > py:
                    parking_status[ind] = True

        # Overlay parking slot information
        if config['parking_overlay']:
            for ind, park in enumerate(parking_data):
                points = np.array(park['points'])
                # GREEN = Empty, RED = Occupied
                color = (0, 255, 0) if not parking_status[ind] else (0, 0, 255)
                cv2.drawContours(frame_out, [points], contourIdx=-1, color=color, thickness=3, lineType=cv2.LINE_8)
                
                # Add slot label and status
                center_x = int(np.mean([p[0] for p in park['points']]))
                center_y = int(np.mean([p[1] for p in park['points']]))
                slot_id = park.get('id', ind+1)
                status_text = "FULL" if parking_status[ind] else "FREE"
                cv2.putText(frame_out, f"S{slot_id}:{status_text}", (center_x-40, center_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Save photo when slot becomes occupied
                if parking_status[ind]:
                    save_parking_event_photo(frame_out, slot_id, parking_status)

        # Text overlay - occupancy statistics
        if config['text_overlay']:
            empty_spaces = parking_status.count(False)
            occupied_spaces = parking_status.count(True)
            total_spaces = len(parking_data)
            occupancy_rate = round((occupied_spaces / total_spaces * 100), 1) if total_spaces > 0 else 0
            
            # Background box
            cv2.rectangle(frame_out, (1, 5), (450, 120), (0, 0, 0), -1)
            cv2.rectangle(frame_out, (1, 5), (450, 120), (0, 255, 0), 2)
            
            # Text info
            str_status = f"Empty: {empty_spaces}/{total_spaces} | Occupied: {occupied_spaces}/{total_spaces}"
            str_percent = f"Occupancy: {occupancy_rate}%"
            str_fps = f"FPS: {frame_count / (time.time() - start_time):.1f}"
            str_detections = f"Cars detected: {detections_count}"
            
            cv2.putText(frame_out, str_status, (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame_out, str_percent, (5, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame_out, str_detections, (5, 90), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame_out, str_fps, (5, 115), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 100, 100), 2, cv2.LINE_AA)
            
            # Console output
            if frame_count % 10 == 0:  # Print every 10 frames
                print(f"[Frame {frame_count}] {str_status} | {str_percent}")
            
            # Send to Firebase (non-blocking thread)
            if firebase_enabled:
                thread = threading.Thread(target=send_to_firebase, args=(empty_spaces, occupied_spaces), daemon=True)
                thread.start()

        # Display the frame
        cv2.imshow('Parking Detection - YOLOv8 (LIVE)', frame_out)
        
        # Check for quit key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            print("\n[User] Pressed 'Q' - Stopping...")
            break

except KeyboardInterrupt:
    print("\n[System] Interrupted by user")

print("\nShutting down...")
cap.release()
cv2.destroyAllWindows()
print(f"✓ Processed {frame_count} frames in {time.time() - start_time:.1f} seconds")
print("✓ Done!")
