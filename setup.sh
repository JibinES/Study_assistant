#!/bin/bash

# AI Study Assistant - Quick Setup Script

echo "🎓 AI Study Assistant - Setup"
echo "=============================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your Gemini API key"
echo "   GEMINI_API_KEY=your_actual_api_key_here"
echo ""
echo "2. Get your API key from: https://makersuite.google.com/app/apikey"
echo ""
echo "3. Run the application:"
echo "   python3 app.py"
echo ""
echo "4. Open your browser to: http://localhost:5000"
echo ""
echo "Happy studying! 📚✨"
