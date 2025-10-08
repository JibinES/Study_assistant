import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from io import BytesIO
import markdown
import re

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
            # First 2 modules
            return modules[:2]
        elif exam_type == 'internal2':
            # First 4 modules
            return modules[:4]
        elif exam_type == 'internal3':
            # Modules 5 and 6 (index 4 and 5)
            return modules[4:6] if len(modules) >= 5 else modules[4:]
        else:  # semester
            # All modules
            return modules
    
    def generate_study_notes(self, subject_code, exam_type, subject_info, stream=False):
        """Generate comprehensive study notes"""
        # Filter modules based on exam type
        all_modules = subject_info.get('modules', [])
        filtered_modules = self._filter_modules_by_exam_type(all_modules, exam_type)
        
        modules_text = "\n".join([f"Module {m['id']}: {m['name']} - Topics: {', '.join(m['topics'])}" 
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
        
        modules_text = "\n".join([f"Module {m['id']}: {m['name']} - Topics: {', '.join(m['topics'])}" 
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
        
        modules_text = "\n".join([f"Module {m['id']}: {m['name']} - Topics: {', '.join(m['topics'])}" 
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
    
    def create_study_schedule(self, subjects, exam_date, hours_per_day, stream=False):
        """Create personalized study timetable"""
        prompt = f"""Create a detailed study schedule for the following:

Subjects: {subjects}
Exam Date: {exam_date}
Study Hours per Day: {hours_per_day}

Please create a day-by-day study plan that includes:
1. Topics to cover each day for each subject
2. Time allocation for each subject
3. Regular breaks (Pomodoro technique recommended)
4. Revision days before the exam
5. Practice/mock test days

Format the schedule clearly with dates, subjects, topics, and time slots.
Make it realistic and achievable."""

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
    
    def generate_pdf_from_notes(self, notes_text, subject_name, exam_type):
        """Generate PDF from study notes"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#4f46e5',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            exam_type_text = {
                'internal1': 'Internal 1',
                'internal2': 'Internal 2',
                'internal3': 'Internal 3',
                'semester': 'Semester Exam'
            }.get(exam_type, exam_type)
            
            title = Paragraph(f"{subject_name}<br/>{exam_type_text} - Study Notes", title_style)
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Convert markdown to simple text and add to PDF
            # Clean the text
            clean_text = notes_text.replace('**', '').replace('*', '').replace('#', '')
            
            # Split into paragraphs
            paragraphs = clean_text.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    # Check if it looks like a heading (short line)
                    if len(para) < 100 and not para.startswith(' '):
                        elements.append(Paragraph(para, styles['Heading2']))
                    else:
                        elements.append(Paragraph(para.replace('\n', '<br/>'), styles['BodyText']))
                    elements.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(elements)
            
            # Get the value of the BytesIO buffer
            pdf = buffer.getvalue()
            buffer.close()
            
            return pdf
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return None
