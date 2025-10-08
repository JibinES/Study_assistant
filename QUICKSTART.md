# Quick Start Guide 🚀

## Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Or use the setup script:
```bash
./setup.sh
```

### Step 2: Configure API Key

1. Get your Gemini API key from: https://makersuite.google.com/app/apikey
2. Open `.env` file
3. Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSy...your_key_here
   ```

### Step 3: Run the App
```bash
python app.py
```

Then open: http://localhost:5000

## Quick Test

1. Go to **Study Tab**
2. Enter subject code: `CS301`
3. Select exam type: `Internal 1`
4. Click "Generate Study Material"
5. Wait for AI to generate content!

## Available Subjects

- **CS301** - Data Structures
- **CS302** - Database Management Systems  
- **CS303** - Operating Systems

Add more subjects in `database/subjects.json`

## Tips

- 💡 Use the chat for quick questions
- ⏰ Try the Pomodoro timer for focused study
- 📅 Create study schedules with the Planner
- 📚 Check PYQs in the Resources tab

## Troubleshooting

**API Error?**
- Check your API key in `.env`
- Verify key is active at Google AI Studio
- Check internet connection

**Module not found?**
```bash
pip install -r requirements.txt --upgrade
```

**Port in use?**
Edit `app.py` and change port:
```python
app.run(debug=True, port=5001)
```

---

For detailed documentation, see [README.md](README.md)
