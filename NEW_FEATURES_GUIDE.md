# Installation Guide for New Features

## New Dependencies Required

The following new features have been added:
1. **PDF Generation** - Download study notes as PDF
2. **Mermaid.js Mind Maps** - Visual mind maps
3. **Module Filtering** - Smart module selection based on exam type
4. **5 Flashcards** - Exactly 5 focused flashcards

## Installation Steps

### 1. Install Python Dependencies

```bash
cd /Users/jibines/Desktop/AVA/AI_study/study-assistant
pip install -r requirements.txt
```

This will install:
- `reportlab` - For PDF generation
- `markdown` - For markdown to HTML conversion
- `playwright` - For potential future image rendering

### 2. Verify Installation

Test if the packages are installed:

```bash
python -c "import reportlab; import markdown; print('✅ All packages installed successfully!')"
```

### 3. Restart Flask Server

**IMPORTANT:** Stop your current server (Ctrl+C) and restart:

```bash
python app.py
```

### 4. Clear Browser Cache

Hard refresh your browser:
- **Mac:** `Cmd + Shift + R`
- **Windows:** `Ctrl + Shift + R`

## New Features Overview

### 📊 Module Filtering by Exam Type

| Exam Type | Modules Covered |
|-----------|----------------|
| Internal 1 | Modules 1-2 |
| Internal 2 | Modules 1-4 |
| Internal 3 | Modules 5-6 |
| Semester | All Modules |

### 📥 PDF Download

- Click "Generate Study Material"
- Wait for notes to stream
- Click **"📥 Download PDF"** button
- PDF will download automatically with filename: `{SubjectCode}_{SubjectName}_{ExamType}_Notes.pdf`

### 🧠 Mermaid.js Mind Map

- Automatically generates visual mind map
- Interactive and hierarchical
- Shows modules and topics
- Rendered using Mermaid.js library

### 🎴 5 Flashcards

- Generates exactly 5 focused flashcards
- Click to flip and see answers
- Covers key concepts for the exam

## Testing the Features

### Test 1: Module Filtering

1. Enter subject code: **CS301**
2. Select **Internal 1**
3. Generate study material
4. Check that notes only cover Modules 1-2

### Test 2: PDF Download

1. Generate study notes
2. Click **"📥 Download PDF"**
3. Check downloaded PDF in your Downloads folder
4. Verify it contains all notes with proper formatting

### Test 3: Mind Map

1. Generate study material
2. Look at the Mind Map card
3. Should see an interactive Mermaid diagram
4. Should show hierarchical structure of topics

### Test 4: Flashcards

1. Generate study material
2. Should see exactly 5 flashcards
3. Click on a flashcard to flip it
4. Should show question and answer

## Troubleshooting

### PDF Generation Fails

**Error:** `Import "reportlab" could not be resolved`

**Solution:**
```bash
pip install reportlab
```

### Mind Map Not Showing

**Issue:** Mind map shows placeholder text

**Solution:**
1. Check browser console for errors
2. Make sure Mermaid.js CDN is loaded
3. Hard refresh browser cache

### Wrong Modules Showing

**Issue:** Internal 1 shows all modules instead of 1-2

**Solution:**
1. Restart Flask server
2. Check that gemini_helper.py was updated correctly
3. Clear browser cache

## API Changes

### New Endpoint: `/api/download-pdf`

**Method:** POST

**Request Body:**
```json
{
  "notes": "markdown text...",
  "subject_name": "Data Structures",
  "exam_type": "internal1",
  "subject_code": "CS301"
}
```

**Response:** PDF file download

### Updated Endpoint: `/api/generate-study-content`

**New Response Fields:**
```json
{
  "success": true,
  "subject_name": "Data Structures",
  "subject_code": "CS301",
  "exam_type": "internal1",
  "flashcards": "[...]",
  "mindmap": "mindmap\n  root((...))\n    ..."
}
```

## File Changes Summary

### Modified Files:
1. `utils/gemini_helper.py` - Module filtering, PDF generation, Mermaid mindmaps
2. `app.py` - New PDF endpoint, error handling
3. `static/js/script.js` - PDF download, Mermaid rendering
4. `static/css/style.css` - Download button, Mermaid styling
5. `templates/index.html` - Mermaid CDN, download button
6. `requirements.txt` - New dependencies

### New Functionality:
- `_filter_modules_by_exam_type()` - Filters modules by exam type
- `generate_pdf_from_notes()` - Generates PDF from markdown
- `downloadPDF()` - Downloads PDF client-side
- `displayMermaidMindMap()` - Renders Mermaid diagram

## Next Steps

After installation:
1. ✅ Install dependencies
2. ✅ Restart server
3. ✅ Clear browser cache
4. ✅ Test all features
5. ✅ Generate study material
6. ✅ Download PDF
7. ✅ View mind map
8. ✅ Check flashcards

Enjoy your enhanced AI Study Assistant! 🎉
