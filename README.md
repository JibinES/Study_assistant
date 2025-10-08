# AI Study Assistant 🎓

A comprehensive AI-powered study assistant web application built with Python Flask backend and modern HTML/CSS/JavaScript frontend. Uses Google's Gemini API for intelligent study material generation.

## Features

### 📚 Study Tab
- **AI-Generated Study Notes**: Get comprehensive notes tailored to your subject and exam type
- **Interactive Flashcards**: Click to flip and test your knowledge
- **Mind Maps**: Visual hierarchical structure of topics
- **Chat Assistant**: Ask questions and get instant answers with context awareness

### 📅 Planner Tab
- **Smart Study Schedules**: AI-generated personalized study timetables
- **Exam-Focused Planning**: Input subjects, exam dates, and study hours
- **Balanced Distribution**: Includes breaks and revision time

### ⏰ Zone Tab
- **Pomodoro Timer**: Customizable focus sessions
- **Session Tracking**: Keep track of all your study sessions
- **Streak Counter**: Visualize your consistency with daily streaks
- **Browser Notifications**: Get notified when sessions complete

### 📁 Resources Tab
- **Previous Year Questions**: Access subject-wise PYQ database
- **Helpful Links**: Curated learning resources
- **Certifications**: Recommended professional certifications

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd study-assistant
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Gemini API key**
   
   Edit the `.env` file and add your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

   To get a Gemini API key:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy and paste it in the `.env` file

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   
   Navigate to: `http://localhost:5000`

## Usage Guide

### Study Tab

1. **Generate Study Material**
   - Enter subject code (e.g., CS301, CS302, CS303)
   - Select exam type (Internal 1/2/3 or Semester)
   - Click "Generate Study Material"
   - Wait for AI to generate notes, flashcards, and mind maps

2. **Use Chat Assistant**
   - Type questions in the chat input
   - Get instant AI-powered answers
   - Context is maintained from generated materials

### Planner Tab

1. **Create Study Schedule**
   - Enter subjects separated by commas (e.g., "CS301, CS302, CS303")
   - Select exam date
   - Specify daily study hours
   - Click "Generate Schedule"

### Zone Tab

1. **Use Pomodoro Timer**
   - Set desired minutes (default: 25)
   - Click "Start" to begin
   - Click "Pause" to pause
   - Click "Reset" to restart
   
2. **Track Progress**
   - Completed sessions are automatically saved
   - View your study streak
   - Monitor session history

### Resources Tab

1. **Access Previous Year Questions**
   - Enter subject code
   - Optionally filter by exam type
   - Click "Get PYQs"

2. **Browse Learning Resources**
   - Helpful links for various topics
   - Certification recommendations

## Customization

### Adding New Subjects

Edit `database/subjects.json`:

```json
{
  "CS304": {
    "name": "Your Subject Name",
    "modules": [
      {
        "id": 1,
        "name": "Module Name",
        "topics": ["Topic 1", "Topic 2"]
      }
    ]
  }
}
```

### Adding Previous Year Questions

Edit `database/pyqs.json`:

```json
{
  "CS304": {
    "internal1": [
      {
        "year": "2024",
        "questions": ["Question 1", "Question 2"]
      }
    ]
  }
}
```

### Theme Customization

Edit `static/css/style.css` and modify CSS variables:

```css
:root {
  --primary: #6366f1;      /* Primary color */
  --secondary: #8b5cf6;    /* Secondary color */
  --accent: #10b981;       /* Accent color */
  /* ... other variables ... */
}
```

## Project Structure

```
study-assistant/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── database/
│   ├── subjects.json     # Subject information
│   └── pyqs.json        # Previous year questions
├── static/
│   ├── css/
│   │   └── style.css    # Styles
│   ├── js/
│   │   └── script.js    # Frontend logic
│   └── images/          # Images and icons
├── templates/
│   └── index.html       # Main HTML template
└── utils/
    ├── gemini_helper.py # Gemini API integration
    └── database_helper.py # Database operations
```

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI**: Google Gemini API
- **Storage**: JSON files, localStorage
- **Styling**: Custom CSS with CSS variables

## Features Breakdown

### AI Integration
- Study notes generation with context
- Flashcard creation with Q&A format
- Mind map structure generation
- Intelligent chat responses
- Personalized schedule creation

### User Experience
- Responsive design (mobile, tablet, desktop)
- Dark/light theme toggle
- Smooth animations and transitions
- Real-time updates
- Notification system

### Data Persistence
- localStorage for sessions and streaks
- JSON database for subjects and PYQs
- Session tracking and history

## Troubleshooting

### API Key Issues
- Ensure `.env` file has correct API key
- Verify API key is active in Google AI Studio
- Check for API quota limits

### Module Not Found
```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

### Browser Notifications Not Working
- Check browser notification permissions
- Some browsers require HTTPS for notifications

## Future Enhancements

Potential features to add:
- User authentication and profiles
- Database integration (PostgreSQL/MongoDB)
- PDF export for study materials
- Collaborative study groups
- Mobile app version
- Voice-based interaction
- Progress analytics dashboard

## Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available for educational purposes.

## Support

For issues or questions:
- Check the troubleshooting section
- Review the documentation
- Open an issue on GitHub

## Credits

- Built with Flask and Google Gemini API
- Icons and emojis from system fonts
- Inspired by modern study techniques and AI capabilities

---

**Happy Studying! 📚✨**
