# YOLOv8 Car Parking Detection System

A real-time parking lot occupancy monitoring system using YOLOv8 object detection and OpenCV.

## Features

- ✅ Real-time car detection using YOLOv8
- ✅ Automatic parking slot occupancy tracking
- ✅ Visual overlay with status indicators (GREEN=Empty, RED=Occupied)
- ✅ Real-time occupancy statistics
- ✅ Firebase integration (optional)
- ✅ Demo mode with synthetic data
- ✅ Production mode with live camera feed

## System Requirements

- Python 3.10+
- Webcam or USB camera (optional for demo mode)
- 4GB+ RAM
- CUDA-capable GPU (optional, for faster inference)

## Installation

### 1. Create Virtual Environment
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
# or
source .venv/bin/activate      # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Demo Mode (No camera required)
```bash
python yolov8_car_parking_demo.py
```
Shows 2 parking slots with both marked as occupied, full car detection visualization, and real-time occupancy analysis.

### Production Mode (Requires webcam/USB camera)
```bash
python yolov8_car_parking.py
```
Connects to your camera and monitors parking spaces in real-time.

## Configuration

Edit the config dictionary in either script:

```python
config = {
    'save_video': False,           # Save output video
    'text_overlay': True,          # Show occupancy stats
    'parking_overlay': True,       # Show parking slot zones
    'parking_detection': True,     # Enable occupancy detection
    'min_area_motion_contour': 60, # Minimum car size
    'park_sec_to_wait': 5,         # Idle time before marking as empty
    'demo_mode': True,             # Use synthetic data
    'frames_to_process': 30        # Number of demo frames
}
```

## Parking Slot Configuration

Define parking spaces in YAML format (output.yml):
```yaml
- id: 1
  points: [[150, 100], [320, 100], [320, 280], [150, 280]]
- id: 2
  points: [[480, 100], [650, 100], [650, 280], [480, 280]]
```

Or use the fallback hardcoded slots in demo mode.

## Output

The system displays:
- **Per-frame analysis**:
  - Number of cars detected
  - Empty spaces: X/Y
  - Occupied spaces: X/Y
  - Occupancy percentage

- **Visual indicators**:
  - GREEN box = Empty slot
  - RED box = Occupied slot
  - Status label = "S1:FREE" or "S1:FULL"

## Firebase Integration

To enable Firebase data logging, update the Firebase URL in the script:
```python
FIREBASE_DATABASE_URL = "https://your-firebase-url.firebasedatabase.app"
firebase_enabled = True
```

Data sent includes:
- Timestamp
- Empty/occupied space counts
- Total spaces
- Occupancy rate percentage

## Performance

- YOLOv8s model: ~1-2 seconds per frame
- Resolution: 640x480 (configurable)
- FPS: ~5-10 FPS (depending on hardware)

## Model Information

Using YOLOv8s (Small) model:
- ~35.5M parameters
- ~45.0 FLOPs
- Optimized for real-time detection
- Pre-trained on COCO dataset (80 classes)
- Car detection uses class ID 2

## Files

- `yolov8_car_parking.py` - Production script with live camera
- `yolov8_car_parking_demo.py` - Demo script with synthetic data
- `requirements.txt` - Python dependencies
- `output.yml` - Parking slot configuration
- `parking.json` - Alternative JSON format (LabelImg)
- `yolov8s.pt` - YOLOv8 model weights

## Troubleshooting

### Camera not detected
- Ensure webcam is plugged in
- Check permissions: `ls /dev/video*` (Linux)
- Try changing device ID (0 → 1)

### Slow performance
- Reduce input resolution
- Use smaller YOLOv8n model
- Enable GPU acceleration if available

### No detections
- Check parking slot boundaries
- Adjust confidence threshold
- Ensure good lighting

## Future Enhancements

- [ ] Real-time dashboard/web UI
- [ ] Mobile app integration
- [ ] SMS/Email alerts
- [ ] Historical analytics
- [ ] AI-based plate recognition
- [ ] Multi-camera support
- [ ] Edge device optimization

## License

Open source - MIT License

## Support

For issues and questions, check the configuration and ensure:
1. All dependencies are installed
2. Model files are present
3. Camera permissions are granted
4. YAML configuration is valid
