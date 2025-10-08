import json
import os
from datetime import datetime, timedelta

class DatabaseHelper:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        # Use data.json from parent directory instead of subjects.json
        self.subjects_file = os.path.join(os.path.dirname(self.base_dir), 'data.json')
        self.pyqs_file = os.path.join(self.base_dir, 'database', 'pyqs.json')
    
    def load_subjects(self):
        """Load subjects database"""
        try:
            with open(self.subjects_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading subjects: {e}")
            return {}
    
    def load_pyqs(self):
        """Load previous year questions database"""
        try:
            with open(self.pyqs_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading PYQs: {e}")
            return {}
    
    def get_subject_info(self, subject_code):
        """Get information for a specific subject"""
        subjects = self.load_subjects()
        subject_data = subjects.get(subject_code, None)
        
        if not subject_data:
            return None
        
        # Transform data.json structure to match expected format
        return {
            'code': subject_code,
            'name': subject_data.get('title', subject_code),
            'modules': subject_data.get('modules', [])
        }
    
    def get_pyqs_for_subject(self, subject_code, exam_type=None):
        """Get PYQs for a specific subject and exam type"""
        pyqs = self.load_pyqs()
        subject_pyqs = pyqs.get(subject_code, {})
        
        if exam_type:
            return subject_pyqs.get(exam_type, [])
        return subject_pyqs
    
    def get_all_subjects(self):
        """Get list of all available subjects"""
        subjects = self.load_subjects()
        return [{"code": code, "name": info.get("title", code)} 
                for code, info in subjects.items()]
    
    def search_subjects(self, query):
        """Search subjects by code or name"""
        subjects = self.load_subjects()
        query = query.lower()
        results = []
        
        for code, info in subjects.items():
            subject_name = info.get('title', code)
            if query in code.lower() or query in subject_name.lower():
                results.append({"code": code, "name": subject_name})
        
        return results
    
    def get_study_resources(self):
        """Get additional study resources"""
        resources = {
            "links": [
                {
                    "title": "GeeksforGeeks",
                    "url": "https://www.geeksforgeeks.org/",
                    "category": "Computer Science"
                },
                {
                    "title": "W3Schools",
                    "url": "https://www.w3schools.com/",
                    "category": "Web Development"
                },
                {
                    "title": "Stack Overflow",
                    "url": "https://stackoverflow.com/",
                    "category": "Problem Solving"
                },
                {
                    "title": "MDN Web Docs",
                    "url": "https://developer.mozilla.org/",
                    "category": "Web Development"
                },
                {
                    "title": "LeetCode",
                    "url": "https://leetcode.com/",
                    "category": "Coding Practice"
                }
            ],
            "certifications": [
                {
                    "name": "Google IT Support Professional Certificate",
                    "provider": "Coursera",
                    "category": "IT Support"
                },
                {
                    "name": "AWS Certified Cloud Practitioner",
                    "provider": "Amazon",
                    "category": "Cloud Computing"
                },
                {
                    "name": "Microsoft Azure Fundamentals",
                    "provider": "Microsoft",
                    "category": "Cloud Computing"
                },
                {
                    "name": "CompTIA A+",
                    "provider": "CompTIA",
                    "category": "IT Fundamentals"
                },
                {
                    "name": "Python for Everybody",
                    "provider": "Coursera",
                    "category": "Programming"
                }
            ]
        }
        return resources
