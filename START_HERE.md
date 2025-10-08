# 🚀 START HERE - Quick Launch Guide

## ✅ Good News - Your App is Ready!

All tests have passed. The app is fully functional and ready to use!

---

## 📋 Pre-Flight Checklist

✅ Python 3.12 installed
✅ All packages installed (Flask, Gemini API, etc.)
✅ Database files ready (3 subjects configured)
✅ Static files present (CSS, JS, HTML)
✅ Environment configured
✅ API key set (verify it's correct)

---

## 🎯 How to Start the App

### Option 1: Simple Start (Recommended)

```bash
# Navigate to the project folder
cd /Users/jibines/Desktop/AVA/AI_study/study-assistant

# Run the app
python3 app.py
```

### Option 2: Using the Script

```bash
# Navigate to the project folder
cd /Users/jibines/Desktop/AVA/AI_study/study-assistant

# Run setup script (first time only)
./setup.sh

# Run the app
python3 app.py
```

---

## 🌐 Access the App

Once you run `python3 app.py`, you'll see:

```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

**Open your browser and go to:**
```
http://localhost:5000
```

---

## 🎓 First Test Run

1. **Start the app** (see above)
2. **Open browser** → http://localhost:5000
3. **Try this test:**
   - Enter Subject Code: `CS301`
   - Select Exam Type: `Internal 1`
   - Click: `Generate Study Material`
   - Wait 15-30 seconds for AI to generate content

If you see study notes, flashcards, and mind maps → **SUCCESS!** 🎉

---

## ⚠️ Important: API Key Check

Your `.env` file should have:
```
GEMINI_API_KEY=AIzaSy...your_actual_key
```

**If you see API errors:**
1. Open `.env` file
2. Verify your Gemini API key is correct
3. Get a key from: https://makersuite.google.com/app/apikey
4. Replace the placeholder with your real key

---

## 🛠️ Quick Commands Reference

```bash
# Start the app
python3 app.py

# Stop the app
Press Ctrl + C

# Check if running
curl http://localhost:5000

# View logs
python3 app.py --debug
```

---

## 📱 What You Can Do

Once running, you can:

### 📚 Study Tab (Default)
- Generate AI study notes
- Create flashcards
- View mind maps
- Chat with AI assistant

### 📅 Planner Tab
- Create study schedules
- Plan for multiple subjects
- Get AI-generated timetables

### ⏰ Zone Tab
- Use Pomodoro timer
- Track study sessions
- Build study streaks

### 📁 Resources Tab
- Access previous year questions
- View helpful links
- Check certifications

---

## 🐛 Troubleshooting

### Issue: Port Already in Use
```bash
# Try different port
python3 -c "from app import app; app.run(port=5001)"
```

### Issue: Module Not Found
```bash
pip install -r requirements.txt --upgrade
```

### Issue: API Key Error
1. Check `.env` file has correct key
2. No extra spaces around `=`
3. Key should start with `AIzaSy`

---

## 📊 Expected Output When Starting

```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
```

This is **NORMAL** and **CORRECT**! ✅

---

## 🎯 Quick Test Workflow

```
1. cd /Users/jibines/Desktop/AVA/AI_study/study-assistant
2. python3 app.py
3. Open browser → http://localhost:5000
4. Enter CS301 → Internal 1 → Generate
5. Wait for AI magic ✨
6. Enjoy your study materials!
```

---

## 💡 Pro Tips

- Keep terminal window open while using app
- First generation might take 30 seconds
- Try dark/light theme toggle (🌙 button)
- Use chat for quick questions
- Start Pomodoro timer for focused study

---

## ✅ Verification Commands

Run these to verify everything:

```bash
# Check Python
python3 --version

# Check packages
pip list | grep -E "Flask|google-generativeai|python-dotenv|flask-cors"

# Check files
ls -la database/ static/ templates/ utils/

# Test import
python3 -c "from app import app; print('✅ App ready!')"
```

---

## 🎉 You're All Set!

**Everything is confirmed working!**

### Next Steps:
1. Run: `python3 app.py`
2. Open: `http://localhost:5000`
3. Start studying smarter!

---

**Need Help?**
- Check README.md for full documentation
- See USAGE_EXAMPLES.md for tutorials
- Review TROUBLESHOOTING section

**Happy Studying!** 📚✨
