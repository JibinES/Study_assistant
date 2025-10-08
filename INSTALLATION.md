# Installation Guide 📦

## Prerequisites

### Required Software
- **Python**: 3.8 or higher
- **pip**: Python package manager (usually included with Python)
- **Web Browser**: Chrome, Firefox, Safari, or Edge

### Required API Key
- **Google Gemini API Key**: Free tier available
  - Get it from: https://makersuite.google.com/app/apikey

---

## Installation Methods

### Method 1: Automatic Setup (Recommended)

#### For macOS/Linux:
```bash
# Navigate to project directory
cd study-assistant

# Run setup script
chmod +x setup.sh
./setup.sh

# Configure API key
nano .env
# Add: GEMINI_API_KEY=your_key_here

# Run the app
python3 app.py
```

#### For Windows:
```cmd
# Navigate to project directory
cd study-assistant

# Install dependencies
pip install -r requirements.txt

# Configure API key
notepad .env
# Add: GEMINI_API_KEY=your_key_here

# Run the app
python app.py
```

---

### Method 2: Manual Installation

#### Step 1: Install Python Dependencies
```bash
pip install Flask==2.3.0
pip install flask-cors==4.0.0
pip install google-generativeai==0.3.0
pip install python-dotenv==1.0.0
```

Or use requirements file:
```bash
pip install -r requirements.txt
```

#### Step 2: Configure Environment
```bash
# Copy .env template
cp .env .env.local

# Edit .env file
nano .env
```

Add your API key:
```
GEMINI_API_KEY=AIzaSy...your_actual_key_here
```

#### Step 3: Verify Installation
```bash
python3 -c "import flask; import google.generativeai; print('✅ All packages installed')"
```

#### Step 4: Run Application
```bash
python3 app.py
```

---

## Getting Gemini API Key

### Step-by-Step Guide

1. **Visit Google AI Studio**
   ```
   https://makersuite.google.com/app/apikey
   ```

2. **Sign in with Google Account**
   - Use your personal Gmail
   - Accept terms of service

3. **Create API Key**
   - Click "Create API Key"
   - Select or create a project
   - Copy the generated key

4. **Add to .env File**
   ```
   GEMINI_API_KEY=AIzaSyC...your_key
   ```

5. **Test API Key**
   ```bash
   python3 -c "
   import os
   from dotenv import load_dotenv
   import google.generativeai as genai
   
   load_dotenv()
   genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
   model = genai.GenerativeModel('gemini-pro')
   response = model.generate_content('Hello')
   print('✅ API Key Working:', response.text[:50])
   "
   ```

---

## Troubleshooting Installation

### Issue 1: pip not found
```bash
# Install pip
python3 -m ensurepip --upgrade

# Or use system package manager
# macOS:
brew install python3

# Ubuntu/Debian:
sudo apt-get install python3-pip
```

### Issue 2: Permission Denied
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue 3: Module Import Errors
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall packages
pip install --force-reinstall -r requirements.txt

# Check Python version
python3 --version  # Should be 3.8+
```

### Issue 4: Port Already in Use
```python
# Edit app.py, change port number:
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed from 5000
```

### Issue 5: API Key Not Working
```bash
# Verify .env file location
ls -la .env

# Check file contents
cat .env

# Ensure no extra spaces
GEMINI_API_KEY=your_key  # ✅ Correct
GEMINI_API_KEY = your_key  # ❌ Wrong (spaces)
```

---

## Virtual Environment Setup (Recommended)

### Why Use Virtual Environment?
- Isolates project dependencies
- Prevents version conflicts
- Easy to replicate environment

### Setup Steps

#### Create Virtual Environment
```bash
# Navigate to project
cd study-assistant

# Create venv
python3 -m venv venv
```

#### Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Run Application
```bash
python app.py
```

#### Deactivate (when done)
```bash
deactivate
```

---

## Docker Installation (Advanced)

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["python", "app.py"]
```

### Build and Run
```bash
# Build image
docker build -t ai-study-assistant .

# Run container
docker run -p 5000:5000 \
  -e GEMINI_API_KEY=your_key \
  ai-study-assistant
```

---

## Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed
- [ ] All packages installed (`pip list`)
- [ ] .env file configured with API key
- [ ] Database files present (subjects.json, pyqs.json)
- [ ] Static files present (CSS, JS)
- [ ] Templates folder present
- [ ] App runs without errors
- [ ] Can access http://localhost:5000
- [ ] Can generate study materials
- [ ] Chat functionality works

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04
- **RAM**: 2 GB
- **Disk**: 100 MB free space
- **Internet**: Required for API calls

### Recommended Requirements
- **OS**: Latest version
- **RAM**: 4 GB
- **Disk**: 500 MB free space
- **Internet**: Stable broadband

---

## Running in Production

### Using Gunicorn (Linux/macOS)
```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Waitress (Windows)
```bash
pip install waitress

waitress-serve --port=5000 app:app
```

### Environment Variables
```bash
export FLASK_ENV=production
export GEMINI_API_KEY=your_key

python app.py
```

---

## Updating the Application

### Pull Latest Changes
```bash
git pull origin main
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Restart Application
```bash
# Stop current process (Ctrl+C)
# Start again
python app.py
```

---

## Uninstallation

### Remove Virtual Environment
```bash
deactivate
rm -rf venv
```

### Remove Python Packages
```bash
pip uninstall -r requirements.txt -y
```

### Remove Application Files
```bash
rm -rf study-assistant
```

---

## Getting Help

### Check Logs
```bash
# Run with verbose output
python app.py --debug

# Check Python errors
python -v app.py
```

### Common Commands
```bash
# Check installed packages
pip list

# Check Python path
which python3

# Check Flask version
python -c "import flask; print(flask.__version__)"

# Check API package
python -c "import google.generativeai; print('OK')"
```

### Support Resources
- GitHub Issues: [Your Repo]
- Documentation: README.md
- Examples: USAGE_EXAMPLES.md

---

**Installation Complete! Ready to Study!** 🎓✨
