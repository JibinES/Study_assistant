import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class GeminiHelper:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_study_notes(self, subject_code, exam_type, subject_info, stream=False):
        """Generate comprehensive study notes"""
        modules_text = "\n".join([f"Module {m['id']}: {m['name']} - Topics: {', '.join(m['topics'])}" 
                                  for m in subject_info.get('modules', [])])
        
        prompt = f"""Generate comprehensive study notes for {subject_info.get('name', subject_code)} focusing on {exam_type} exam.

Subject: {subject_info.get('name', subject_code)}
Modules covered:
{modules_text}

Please provide:
1. Key concepts and definitions
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
        modules_text = "\n".join([f"Module {m['id']}: {m['name']} - Topics: {', '.join(m['topics'])}" 
                                  for m in subject_info.get('modules', [])])
        
        prompt = f"""Create 20 flashcards for {subject_info.get('name', subject_code)} {exam_type} exam.

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
        """Generate mind map structure"""
        modules_text = "\n".join([f"Module {m['id']}: {m['name']} - Topics: {', '.join(m['topics'])}" 
                                  for m in subject_info.get('modules', [])])
        
        prompt = f"""Create a hierarchical mind map structure for {subject_info.get('name', subject_code)} {exam_type} topics.

Subject: {subject_info.get('name', subject_code)}
Modules:
{modules_text}

Return ONLY a valid JSON structure with this exact format (no additional text):
{{
  "topic": "{subject_info.get('name', subject_code)}",
  "subtopics": [
    {{
      "topic": "Module 1 Name",
      "subtopics": [
        {{"topic": "Subtopic 1"}},
        {{"topic": "Subtopic 2"}}
      ]
    }}
  ]
}}

Create a comprehensive hierarchical structure covering all important topics."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Extract JSON from response
            if text.startswith('{'):
                return text
            else:
                # Try to extract JSON from markdown code block
                if '```json' in text:
                    json_start = text.find('{')
                    json_end = text.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        return text[json_start:json_end]
                elif '```' in text:
                    json_start = text.find('{')
                    json_end = text.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        return text[json_start:json_end]
            return text
        except Exception as e:
            return json.dumps({"topic": "Error", "subtopics": [{"topic": str(e)}]})
    
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
