import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from io import BytesIO
import markdown
import re
from html.parser import HTMLParser
import tempfile
import subprocess
import base64

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class GeminiHelper:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def _filter_modules_by_exam_type(self, modules, exam_type):
        """Filter modules based on exam type"""
        if not modules:
            return []
        
        if exam_type == 'internal1':
            # Modules 1-2
            return [m for m in modules if m.get('module') in ['Module: 1', 'Module: 2']]
        elif exam_type == 'internal2':
            # Modules 1-4
            return [m for m in modules if m.get('module') in ['Module: 1', 'Module: 2', 'Module: 3', 'Module: 4']]
        elif exam_type == 'internal3':
            # Modules 5-6
            return [m for m in modules if m.get('module') in ['Module: 5', 'Module: 6']]
        else:  # semester
            # All modules
            return modules
    
    def generate_study_notes(self, subject_code, exam_type, subject_info, stream=False):
        """Generate comprehensive study notes"""
        # Filter modules based on exam type
        all_modules = subject_info.get('modules', [])
        filtered_modules = self._filter_modules_by_exam_type(all_modules, exam_type)
        
        modules_text = "\n".join([f"{m.get('module', 'Module')}: {m.get('name', 'Unknown')} - Topics: {', '.join(m.get('topics', []))}" 
                                  for m in filtered_modules])
        
        exam_type_text = {
            'internal1': 'Internal 1 (Modules 1-2)',
            'internal2': 'Internal 2 (Modules 1-4)',
            'internal3': 'Internal 3 (Modules 5-6)',
            'semester': 'Semester Exam (All Modules)'
        }.get(exam_type, exam_type)
        
        prompt = f"""Generate comprehensive study notes for {subject_info.get('name', subject_code)} focusing on {exam_type_text}.

Subject: {subject_info.get('name', subject_code)}
Modules covered:
{modules_text}

Please provide:
1. Key concepts and definitions for each module
2. Important formulas and algorithms (if applicable)
3. Real-world examples and applications
4. Important points to remember
5. Common mistakes to avoid

Format the response in markdown with clear headings, bullet points, and code examples where applicable.
Make it comprehensive but concise, suitable for exam preparation."""

        try:
            if stream:
                # Return streaming response
                response = self.model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            else:
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            if stream:
                yield f"Error generating study notes: {str(e)}"
            else:
                return f"Error generating study notes: {str(e)}"
    
    def generate_flashcards(self, subject_code, exam_type, subject_info):
        """Generate flashcards in JSON format"""
        # Filter modules based on exam type
        all_modules = subject_info.get('modules', [])
        filtered_modules = self._filter_modules_by_exam_type(all_modules, exam_type)
        
        modules_text = "\n".join([f"{m.get('module', 'Module')}: {m.get('name', 'Unknown')} - Topics: {', '.join(m.get('topics', []))}" 
                                  for m in filtered_modules])
        
        exam_type_text = {
            'internal1': 'Internal 1 (Modules 1-2)',
            'internal2': 'Internal 2 (Modules 1-4)',
            'internal3': 'Internal 3 (Modules 5-6)',
            'semester': 'Semester Exam (All Modules)'
        }.get(exam_type, exam_type)
        
        prompt = f"""Create EXACTLY 5 flashcards for {subject_info.get('name', subject_code)} {exam_type_text}.

Subject: {subject_info.get('name', subject_code)}
Modules:
{modules_text}

Generate flashcards covering:
- Important concepts and definitions
- Key formulas and algorithms
- Important facts and figures
- Common interview questions

Return ONLY a valid JSON array with this exact format (no additional text):
[
  {{"question": "What is...", "answer": "..."}},
  {{"question": "Explain...", "answer": "..."}}
]

IMPORTANT: Generate EXACTLY 5 flashcards, no more, no less.
Make sure questions are clear and answers are concise but complete."""

        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            text = response.text.strip()
            # Try to find JSON array in the response
            if text.startswith('['):
                return text
            else:
                # Try to extract JSON from markdown code block
                if '```json' in text:
                    json_start = text.find('[')
                    json_end = text.rfind(']') + 1
                    if json_start != -1 and json_end > json_start:
                        return text[json_start:json_end]
                elif '```' in text:
                    json_start = text.find('[')
                    json_end = text.rfind(']') + 1
                    if json_start != -1 and json_end > json_start:
                        return text[json_start:json_end]
            return text
        except Exception as e:
            return json.dumps([{"question": "Error", "answer": str(e)}])
    
    def generate_mindmap(self, subject_code, exam_type, subject_info):
        """Generate mind map in Mermaid.js format"""
        # Filter modules based on exam type
        all_modules = subject_info.get('modules', [])
        filtered_modules = self._filter_modules_by_exam_type(all_modules, exam_type)
        
        modules_text = "\n".join([f"{m.get('module', 'Module')}: {m.get('name', 'Unknown')} - Topics: {', '.join(m.get('topics', []))}" 
                                  for m in filtered_modules])
        
        exam_type_text = {
            'internal1': 'Internal 1 (Modules 1-2)',
            'internal2': 'Internal 2 (Modules 1-4)',
            'internal3': 'Internal 3 (Modules 5-6)',
            'semester': 'Semester Exam (All Modules)'
        }.get(exam_type, exam_type)
        
        prompt = f"""Create a mind map in Mermaid.js syntax for {subject_info.get('name', subject_code)} - {exam_type_text}.

Subject: {subject_info.get('name', subject_code)}
Modules:
{modules_text}

Generate a Mermaid.js mindmap diagram with the following structure:
- Root node: Subject name
- Child nodes: Module names
- Sub-child nodes: Key topics from each module

Return ONLY the Mermaid.js code (no additional text, no markdown code blocks).
Start with: mindmap
Use proper indentation for hierarchy.

Example format:
mindmap
  root((Subject Name))
    Module 1
      Topic 1
      Topic 2
    Module 2
      Topic 3
      Topic 4

Generate a comprehensive mind map covering all important topics."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract mermaid code from markdown if present
            if '```mermaid' in text:
                start = text.find('```mermaid') + 10
                end = text.find('```', start)
                if end != -1:
                    return text[start:end].strip()
            elif '```' in text:
                start = text.find('```') + 3
                end = text.find('```', start)
                if end != -1:
                    return text[start:end].strip()
            
            return text
        except Exception as e:
            return f"mindmap\n  root((Error))\n    {str(e)}"
    
    def create_study_schedule(self, subjects, start_date, end_date, hours_per_day, stream=False):
        """Create personalized study timetable with detailed topics and time slots"""
        
        # Calculate number of days
        from datetime import datetime, timedelta
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        total_days = (end - start).days + 1
        
        prompt = f"""Create a comprehensive day-by-day study timetable for the following:

**Study Period:** {start_date} to {end_date} ({total_days} days)
**Subjects:** {subjects}
**Daily Study Hours:** {hours_per_day} hours per day (minimum 2 hours)

Generate a detailed timetable in **MARKDOWN TABLE FORMAT** for each day.

## Format Instructions:

For each day, create a section with:
- A heading with the date (e.g., "### Monday, October 8, 2024")
- A markdown table with the following columns:

| Time Slot | Subject | Topic | Activities |
|-----------|---------|-------|------------|
| 9:00 - 10:30 | Data Structures | Arrays and Linked Lists | Study concepts, solve 5 problems |
| 10:30 - 10:45 | Break | - | Rest and refresh |
| 10:45 - 12:15 | Algorithms | Sorting Algorithms | Understand theory, implement quicksort |

## Important Guidelines:
1. **Start time:** Begin at 9:00 AM by default (or suggest appropriate times)
2. **Break periods:** Include 15-minute breaks after every 90 minutes of study
3. **Subject rotation:** Distribute subjects evenly across days
4. **Topics:** Be specific - mention actual chapters/topics from each subject
5. **Activities:** Include concrete tasks (read pages X-Y, solve problems, practice coding, review notes, etc.)
6. **Realistic pacing:** Allocate appropriate time based on topic difficulty
7. **Revision days:** Include quick revision sessions for previously covered topics

**Output Format:** Use markdown tables as shown above for EACH day

## Requirements:
1. **Distribute {hours_per_day} hours across all subjects** each day
2. **Include specific topics/chapters** for each study session
3. **Add 15-minute breaks** between subjects
4. **Rotate subjects** to avoid monotony
5. **Include revision days** (last 2-3 days)
6. **Suggest time slots** (e.g., 9:00 AM - 11:00 AM)
7. **Balance difficulty** - mix hard and easy topics
8. **Include practice problems/mock tests** in later days

Start the timetable now:"""

        try:
            if stream:
                # Return streaming response
                response = self.model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            else:
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            if stream:
                yield f"Error generating schedule: {str(e)}"
            else:
                return f"Error generating schedule: {str(e)}"
    
    def answer_question(self, question, context):
        """Answer student questions with context"""
        prompt = f"""You are a helpful study assistant. Answer the following question based on the context provided.

Context: {context}

Question: {question}

Provide a clear, concise, and accurate answer. Include examples if helpful."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error answering question: {str(e)}"
    
    def chat_response(self, message, chat_history="", stream=False):
        """General chat response for study assistance"""
        prompt = f"""You are a helpful AI study assistant. Help the student with their question.

Previous conversation:
{chat_history}

Student: {message}

Provide a helpful, encouraging, and educational response."""

        try:
            if stream:
                # Return streaming response
                response = self.model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            else:
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            if stream:
                yield f"Error: {str(e)}"
            else:
                return f"Error: {str(e)}"
    
    def _markdown_to_pdf_elements(self, md_text, styles):
        """Convert markdown text to PDF elements with proper formatting"""
        elements = []
        
        # Convert markdown to HTML first
        html = markdown.markdown(md_text, extensions=['extra', 'codehilite', 'fenced_code'])
        
        # Parse HTML and create PDF elements
        lines = md_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Handle headings
            if line.startswith('# '):
                text = line[2:].strip()
                elements.append(Paragraph(text, styles['Heading1']))
                elements.append(Spacer(1, 12))
            elif line.startswith('## '):
                text = line[3:].strip()
                elements.append(Paragraph(text, styles['Heading2']))
                elements.append(Spacer(1, 10))
            elif line.startswith('### '):
                text = line[4:].strip()
                elements.append(Paragraph(text, styles['Heading3']))
                elements.append(Spacer(1, 8))
            elif line.startswith('#### '):
                text = line[5:].strip()
                elements.append(Paragraph(text, styles['Heading4']))
                elements.append(Spacer(1, 6))
            
            # Handle code blocks
            elif line.startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if code_lines:
                    code_text = '<br/>'.join(code_lines)
                    elements.append(Paragraph(f'<font name="Courier" size="9">{code_text}</font>', styles['CustomCode']))
                    elements.append(Spacer(1, 12))
            
            # Handle bullet points
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                # Convert markdown bold/italic with error handling
                try:
                    text = self._convert_markdown_inline(text)
                    elements.append(Paragraph(f'• {text}', styles['Normal']))
                except Exception as e:
                    # If formatting fails, use plain text
                    from xml.sax.saxutils import escape
                    elements.append(Paragraph(f'• {escape(line[2:].strip())}', styles['Normal']))
                elements.append(Spacer(1, 4))
            
            # Handle numbered lists
            elif re.match(r'^\d+\.\s', line):
                text = re.sub(r'^\d+\.\s', '', line)
                try:
                    text = self._convert_markdown_inline(text)
                    elements.append(Paragraph(text, styles['Normal']))
                except Exception:
                    from xml.sax.saxutils import escape
                    elements.append(Paragraph(escape(text), styles['Normal']))
                elements.append(Spacer(1, 4))
            
            # Regular paragraph
            else:
                try:
                    text = self._convert_markdown_inline(line)
                    if text:
                        elements.append(Paragraph(text, styles['BodyText']))
                        elements.append(Spacer(1, 8))
                except Exception:
                    from xml.sax.saxutils import escape
                    if line:
                        elements.append(Paragraph(escape(line), styles['BodyText']))
                        elements.append(Spacer(1, 8))
            
            i += 1
        
        return elements
    
    def _convert_markdown_inline(self, text):
        """Convert inline markdown (bold, italic, code) to ReportLab format"""
        # Escape special XML characters first
        from xml.sax.saxutils import escape
        
        # Process in order to avoid nesting issues:
        # 1. First, handle inline code (most specific)
        # 2. Then bold (before italic to handle ** before *)
        # 3. Finally italic
        
        # Inline code: `text` - handle first to avoid conflicts
        def replace_code(match):
            code_text = escape(match.group(1))
            return f'<font name="Courier" size="9">{code_text}</font>'
        text = re.sub(r'`([^`]+?)`', replace_code, text)
        
        # Bold: **text** (must be before single * for italic)
        def replace_bold(match):
            return f'<b>{match.group(1)}</b>'
        text = re.sub(r'\*\*([^*]+?)\*\*', replace_bold, text)
        
        # Italic: *text* (after ** is processed)
        def replace_italic(match):
            return f'<i>{match.group(1)}</i>'
        text = re.sub(r'\*([^*]+?)\*', replace_italic, text)
        
        return text
    
    def _mermaid_to_image(self, mermaid_code):
        """Convert Mermaid code to HIGH-QUALITY PNG image using Playwright"""
        try:
            from playwright.sync_api import sync_playwright
            
            print("🎨 Converting mind map to HIGH-QUALITY image using Playwright...")
            
            # Create HTML with Mermaid diagram - optimized for quality
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    body {{
                        margin: 0;
                        padding: 40px;
                        background: white;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                    }}
                    .mermaid {{
                        background: white;
                        font-family: 'Arial', 'Helvetica', sans-serif;
                        font-size: 16px;
                    }}
                    /* Ensure high quality text rendering */
                    svg {{
                        shape-rendering: geometricPrecision;
                        text-rendering: geometricPrecision;
                    }}
                </style>
            </head>
            <body>
                <div class="mermaid">
{mermaid_code}
                </div>
                <script>
                    mermaid.initialize({{ 
                        startOnLoad: true, 
                        theme: 'default',
                        themeVariables: {{
                            fontSize: '16px',
                            fontFamily: 'Arial, Helvetica, sans-serif'
                        }},
                        mindmap: {{
                            padding: 20,
                            useMaxWidth: false
                        }}
                    }});
                </script>
            </body>
            </html>
            """
            
            # Use Playwright to render and screenshot at HIGH RESOLUTION
            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                
                # Create page with HIGH RESOLUTION viewport (2x for retina quality)
                page = browser.new_page(
                    viewport={'width': 2400, 'height': 1600},  # 2x resolution for crisp images
                    device_scale_factor=2  # Retina/HiDPI quality
                )
                
                # Set the HTML content
                page.set_content(html_content)
                
                # Wait for Mermaid to fully render (increased for complex diagrams)
                page.wait_for_timeout(3000)  # 3 seconds for complete rendering
                
                # Take HIGH-QUALITY screenshot of the mermaid element
                screenshot_bytes = page.locator('.mermaid').screenshot(
                    type='png',
                    scale='device',  # Use device scale factor for quality
                    animations='disabled'  # Ensure stable rendering
                )
                
                browser.close()
                
            print("✓ HIGH-QUALITY mind map image created successfully!")
            print(f"✓ Image size: {len(screenshot_bytes)} bytes")
            return screenshot_bytes
            
        except ImportError:
            print("⚠ Playwright not installed. Installing browsers...")
            print("ℹ Run: playwright install chromium")
            return None
        except Exception as e:
            print(f"⚠ Mind map image conversion failed: {str(e)}")
            print("ℹ Mind map will be included as Mermaid code in PDF")
            return None
    
    def generate_pdf_from_notes(self, notes_text, subject_name, exam_type, mindmap_code=None):
        """Generate PDF from study notes with proper markdown formatting and mindmap"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=36)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            
            # Add custom styles only if they don't exist
            if 'CustomTitle' not in styles:
                styles.add(ParagraphStyle(
                    name='CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#4f46e5'),
                    spaceAfter=20,
                    spaceBefore=10,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold'
                ))
            
            # Add custom styles only if they don't exist
            if 'CustomHeading1' not in styles:
                styles.add(ParagraphStyle(
                    name='CustomHeading1',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#4f46e5'),
                    spaceAfter=12,
                    spaceBefore=12,
                    fontName='Helvetica-Bold'
                ))
            
            if 'CustomCode' not in styles:
                styles.add(ParagraphStyle(
                    name='CustomCode',
                    parent=styles['Normal'],
                    fontSize=9,
                    fontName='Courier',
                    textColor=colors.HexColor('#1e293b'),
                    backColor=colors.HexColor('#f1f5f9'),
                    leftIndent=20,
                    rightIndent=20,
                    spaceAfter=12,
                    spaceBefore=6
                ))
            
            exam_type_text = {
                'internal1': 'Internal 1',
                'internal2': 'Internal 2',
                'internal3': 'Internal 3',
                'semester': 'Semester Exam'
            }.get(exam_type, exam_type)
            
            # Title
            title = Paragraph(f"{subject_name}<br/>{exam_type_text} - Study Notes", styles['CustomTitle'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Add a separator line
            elements.append(Paragraph('<hr/>', styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Convert markdown notes to PDF elements
            note_elements = self._markdown_to_pdf_elements(notes_text, styles)
            elements.extend(note_elements)
            
            # Add mindmap if provided
            # Add mind map section if available
            temp_img_path = None  # Track temp file for cleanup
            if mindmap_code:
                elements.append(PageBreak())
                elements.append(Paragraph("Mind Map", styles['CustomHeading1']))
                elements.append(Spacer(1, 12))
                
                # Try to convert mermaid to image
                mindmap_image = self._mermaid_to_image(mindmap_code)
                
                if mindmap_image:
                    # Save HIGH-QUALITY image to temporary file (delete=False so it persists)
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                        tmp_img.write(mindmap_image)
                        temp_img_path = tmp_img.name
                    
                    # Add HIGH-QUALITY image to PDF with better sizing
                    # Using larger dimensions and proportional scaling for crisp output
                    img = Image(temp_img_path, width=500, height=350, kind='proportional')
                    img.hAlign = 'CENTER'  # Center the image
                    elements.append(img)
                    elements.append(Spacer(1, 12))
                    elements.append(Paragraph(
                        '<i>High-resolution mind map visualization</i>', 
                        styles['Normal']
                    ))
                else:
                    # If image conversion failed, add mermaid code as text
                    elements.append(Paragraph("Mind Map Diagram (Mermaid Code):", styles['Heading3']))
                    elements.append(Spacer(1, 6))
                    code_text = mindmap_code.replace('\n', '<br/>')
                    elements.append(Paragraph(f'<font name="Courier" size="8">{code_text}</font>', styles['CustomCode']))
            
            # Build PDF (reads the temp image file if it exists)
            doc.build(elements)
            
            # Clean up temp image file AFTER PDF is built
            if temp_img_path and os.path.exists(temp_img_path):
                os.unlink(temp_img_path)
            
            # Get the value of the BytesIO buffer
            pdf = buffer.getvalue()
            buffer.close()
            
            return pdf
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
