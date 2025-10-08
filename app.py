from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_file
from flask_cors import CORS
from utils.gemini_helper import GeminiHelper
from utils.database_helper import DatabaseHelper
import json
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Initialize helpers
gemini = GeminiHelper()
db = DatabaseHelper()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate-study-content', methods=['POST'])
def generate_study_content():
    """Generate study content (notes, flashcards, mindmap)"""
    try:
        data = request.json
        subject_code = data.get('subject_code', '').upper()
        exam_type = data.get('exam_type', 'semester')
        
        # Get subject information
        subject_info = db.get_subject_info(subject_code)
        
        if not subject_info:
            return jsonify({
                'success': False,
                'error': f'Subject {subject_code} not found in database'
            }), 404
        
        # Generate all content types (non-streaming for flashcards and mindmap)
        flashcards = gemini.generate_flashcards(subject_code, exam_type, subject_info)
        mindmap = gemini.generate_mindmap(subject_code, exam_type, subject_info)
        
        return jsonify({
            'success': True,
            'subject_name': subject_info['name'],
            'subject_code': subject_code,
            'exam_type': exam_type,
            'flashcards': flashcards,
            'mindmap': mindmap
        })
    
    except Exception as e:
        print(f"Error in generate_study_content: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF of study notes"""
    try:
        data = request.json
        notes = data.get('notes', '')
        subject_name = data.get('subject_name', 'Study Notes')
        exam_type = data.get('exam_type', 'semester')
        subject_code = data.get('subject_code', '')
        mindmap = data.get('mindmap', None)  # Get mindmap code
        
        if not notes:
            return jsonify({
                'success': False,
                'error': 'No notes provided'
            }), 400
        
        # Generate PDF with mindmap
        pdf_buffer = gemini.generate_pdf_from_notes(notes, subject_name, exam_type, mindmap)
        
        if not pdf_buffer:
            return jsonify({
                'success': False,
                'error': 'Failed to generate PDF'
            }), 500
        
        # Create a BytesIO object
        pdf_io = BytesIO(pdf_buffer)
        pdf_io.seek(0)
        
        # Generate filename
        exam_type_text = {
            'internal1': 'Internal1',
            'internal2': 'Internal2',
            'internal3': 'Internal3',
            'semester': 'Semester'
        }.get(exam_type, exam_type)
        
        filename = f"{subject_code}_{subject_name.replace(' ', '_')}_{exam_type_text}_Notes.pdf"
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/create-schedule', methods=['POST'])
def create_schedule():
    """Create study schedule"""
    try:
        data = request.json
        subjects = data.get('subjects', '')
        exam_date = data.get('exam_date', '')
        hours_per_day = data.get('hours_per_day', 4)
        
        if not subjects or not exam_date:
            return jsonify({
                'success': False,
                'error': 'Please provide subjects and exam date'
            }), 400
        
        schedule = gemini.create_study_schedule(subjects, exam_date, hours_per_day)
        
        return jsonify({
            'success': True,
            'schedule': schedule
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-pyqs', methods=['GET'])
def get_pyqs():
    """Get previous year questions"""
    try:
        subject_code = request.args.get('subject_code', '').upper()
        exam_type = request.args.get('exam_type', None)
        
        if not subject_code:
            return jsonify({
                'success': False,
                'error': 'Please provide subject code'
            }), 400
        
        pyqs = db.get_pyqs_for_subject(subject_code, exam_type)
        subject_info = db.get_subject_info(subject_code)
        
        return jsonify({
            'success': True,
            'subject_name': subject_info['name'] if subject_info else subject_code,
            'pyqs': pyqs
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-session', methods=['POST'])
def save_session():
    """Save pomodoro session"""
    try:
        data = request.json
        session_data = {
            'duration': data.get('duration', 25),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'subject': data.get('subject', 'General Study')
        }
        
        # In a real application, you would save this to a database
        # For now, we'll just return success
        return jsonify({
            'success': True,
            'message': 'Session saved successfully',
            'session': session_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-sessions', methods=['GET'])
def get_sessions():
    """Get previous study sessions"""
    try:
        # In a real application, you would fetch from database
        # For now, return empty array
        return jsonify({
            'success': True,
            'sessions': []
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-resources', methods=['GET'])
def get_resources():
    """Get additional resources"""
    try:
        resources = db.get_study_resources()
        
        return jsonify({
            'success': True,
            'resources': resources
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        context = data.get('context', '')
        chat_history = data.get('chat_history', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Please provide a message'
            }), 400
        
        if context:
            response = gemini.answer_question(message, context)
        else:
            response = gemini.chat_response(message, chat_history)
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Handle streaming chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        context = data.get('context', '')
        chat_history = data.get('chat_history', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Please provide a message'
            }), 400
        
        def generate():
            try:
                if context:
                    # For now, answer_question doesn't support streaming
                    # We can add it if needed
                    response = gemini.answer_question(message, context)
                    yield f"data: {json.dumps({'text': response, 'done': True})}\n\n"
                else:
                    for chunk in gemini.chat_response(message, chat_history, stream=True):
                        yield f"data: {json.dumps({'text': chunk})}\n\n"
                    yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        response = Response(stream_with_context(generate()), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'
        return response
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-notes/stream', methods=['POST'])
def generate_notes_stream():
    """Generate study notes with streaming"""
    try:
        data = request.json
        subject_code = data.get('subject_code', '').upper()
        exam_type = data.get('exam_type', 'semester')
        
        # Get subject information
        subject_info = db.get_subject_info(subject_code)
        
        if not subject_info:
            return jsonify({
                'success': False,
                'error': f'Subject {subject_code} not found in database'
            }), 404
        
        def generate():
            try:
                yield f"data: {json.dumps({'subject_name': subject_info['name']})}\n\n"
                for chunk in gemini.generate_study_notes(subject_code, exam_type, subject_info, stream=True):
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        response = Response(stream_with_context(generate()), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'
        return response
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/create-schedule/stream', methods=['POST'])
def create_schedule_stream():
    """Create study schedule with streaming"""
    try:
        data = request.json
        subjects = data.get('subjects', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        hours_per_day = data.get('hours_per_day', 2)
        
        if not subjects or not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': 'Please provide subjects, start date, and end date'
            }), 400
        
        # Validate hours per day (minimum 2)
        if hours_per_day < 2:
            return jsonify({
                'success': False,
                'error': 'Minimum study hours is 2 hours per day'
            }), 400
        
        def generate():
            try:
                for chunk in gemini.create_study_schedule(subjects, start_date, end_date, hours_per_day, stream=True):
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        response = Response(stream_with_context(generate()), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'
        return response
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get all available subjects"""
    try:
        subjects = db.get_all_subjects()
        
        return jsonify({
            'success': True,
            'subjects': subjects
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Enable threading for proper streaming support
    app.run(debug=True, port=5000, threaded=True)
