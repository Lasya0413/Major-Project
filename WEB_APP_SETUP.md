# Vehicle License Plate Recognition Web Application

## 🚀 Features

- ✅ **User Authentication** - Login and Registration system
- ✅ **Vehicle Management** - Register vehicle numbers in Excel
- ✅ **Plate Recognition** - Automatic license plate detection from images
- ✅ **Excel Comparison** - Compare detected plates with registered vehicles
- ✅ **Email Alerts** - Automatic email notifications with photos
- ✅ **Verification History** - View all processed images

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection (for API calls)
- Email account for sending alerts (Gmail recommended)

## 🔧 Installation

### Step 1: Install Required Packages

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install Flask openpyxl requests Pillow Werkzeug
```

### Step 2: Configure Email Settings

Edit `config.py` and update your email credentials:

```python
MAIL_USERNAME = 'your-email@gmail.com'  # Your Gmail address
MAIL_PASSWORD = 'your-app-password'     # Gmail App Password (see below)
```

**For Gmail:**
1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an App Password for "Mail"
4. Use that password in `config.py`

### Step 3: Run the Application

**Option 1: Using the batch file (Windows)**
```bash
run_web_app.bat
```

**Option 2: Using Python directly**
```bash
python web_app.py
```

The application will start on: **http://127.0.0.1:5000**

## 📖 How to Use

### 1. Register a New Account
- Go to http://127.0.0.1:5000
- Click "Register here"
- Fill in your details and create an account

### 2. Login
- Use your email and password to login

### 3. Register Vehicle Numbers
- Click "Register Vehicle" in the navigation
- Enter vehicle number and owner name
- Click "Register Vehicle"
- Vehicle will be saved to `vehicles.xlsx`

### 4. Verify Vehicle (Detect & Compare)
- Click "Verify Vehicle" in the navigation
- Upload an image containing a license plate
- System will:
  - Detect the license plate using AI
  - Compare with registered vehicles in Excel
  - Send email alert to your registered email
  - Show results on screen

### 5. View History
- Click "Verification History" to see all processed images

## 📁 File Structure

```
├── web_app.py                # Main Flask application
├── plate_recognition.py      # Plate recognition functions
├── config.py                 # Email configuration
├── vehicles.xlsx             # Excel file with registered vehicles
├── users.db                  # SQLite database for users
├── uploads/                  # Uploaded images
│   └── verification/         # Verification images
│       └── annotated/        # YOLO annotated images
├── templates/                # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── register_vehicle.html
│   ├── verify_vehicle.html
│   └── verification_history.html
├── static/                   # CSS and static files
│   └── css/style.css
└── best.pt                   # YOLO model weights file (in root directory)
```

## 🤖 YOLO License Plate Detection

YOLO is used to draw bounding boxes around detected license plates.

1. **Install dependencies**  
   ```bash
   pip install ultralytics opencv-python
   ```

2. **YOLO Model**  
   - The application uses `best.pt` in the root directory by default
   - Make sure `best.pt` is in the project root folder
     _(You can override this path with the `YOLO_WEIGHTS_PATH` environment variable)_

3. **Restart the app**  
   - Run `python web_app.py` again
   - On the Verify page you will now see YOLO bounding boxes and confidence scores

> If YOLO is not configured, the app will still work, but you will see a warning and no bounding boxes.

## 🔐 Security Notes

- Change `SECRET_KEY` in `web_app.py` for production
- Use environment variables for sensitive data
- Don't commit `config.py` with real credentials to Git
- Use HTTPS in production

## 🐛 Troubleshooting

### Email not sending?
- Check `config.py` has correct credentials
- Verify Gmail App Password is correct
- Check internet connection
- Check spam folder

### Plate not detected?
- Use clear, well-lit images
- Ensure license plate is visible
- Try different image angles
- Check image format (JPG, PNG supported)

### Excel file errors?
- Make sure `vehicles.xlsx` exists (created automatically)
- Check file permissions
- Close Excel if it's open

## 📧 Email Alert Format

When a vehicle is detected, you'll receive an email with:
- Vehicle number
- Detection status (Registered/Not Registered)
- Detection timestamp
- Attached image of the vehicle

## 🎯 API Key

The API key for plate recognition is already configured in the code:
- Default: `b21fc6a678b12c50da9aad4a72cde7fd879fb3b7`
- Can be changed in `plate_recognition.py` or via environment variable

## 📝 Excel Format

The `vehicles.xlsx` file contains:
- Vehicle Number
- Owner Name
- Email
- Registered Date
- Status

## 🚀 Production Deployment

For production:
1. Set `debug=False` in `web_app.py`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Set up proper database (PostgreSQL, MySQL)
4. Use environment variables for secrets
5. Enable HTTPS
6. Set up proper logging

## 💡 Tips

- Register vehicles before verification for better results
- Use high-quality images for better detection
- Check email spam folder for alerts
- Excel file is automatically created on first run

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all requirements are installed
3. Check console for error messages
4. Ensure email configuration is correct

---

**Enjoy using the Vehicle License Plate Recognition System!** 🚗📸


