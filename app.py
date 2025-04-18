from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import json
import os
from main import MCQGrader

app = Flask(__name__)
app.secret_key = "mcq_grader_secret_key"  # For flash messages

# Ensure results directory exists
RESULTS_DIR = "results"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)


@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')


@app.route('/grade', methods=['GET', 'POST'])
def grade():
    """Handle grading form submissions"""
    if request.method == 'POST':
        # Check if files are uploaded
        if 'answer_key' not in request.files or 'submissions' not in request.files:
            flash('Both answer key and submissions files are required', 'error')
            return redirect(request.url)

        answer_key_file = request.files['answer_key']
        submissions_file = request.files['submissions']
        
        # Validate file uploads
        if answer_key_file.filename == '' or submissions_file.filename == '':
            flash('Both files must be selected', 'error')
            return redirect(request.url)
            
        try:
            # Load JSON data
            answer_key = json.load(answer_key_file)
            submissions = json.load(submissions_file)
            
            # Optional question text file
            question_text = {}
            if 'question_text' in request.files and request.files['question_text'].filename != '':
                question_text = json.load(request.files['question_text'])
            
            # Initialize grader and process submissions
            grader = MCQGrader(answer_key)
            results = grader.grade_batch(submissions)
            stats = grader.generate_statistics(results)
            
            # Export results
            csv_path = grader.export_results_csv(results)
            json_path = grader.export_statistics_json(stats)
            
            # Save file paths to session for download links
            session_data = {
                'csv_path': csv_path,
                'json_path': json_path,
                'results': results,
                'stats': stats,
                'question_text': question_text
            }
            
            # Store in a temporary file
            session_file = os.path.join(RESULTS_DIR, 'session_data.json')
            with open(session_file, 'w') as f:
                # Convert non-serializable data
                serializable_data = {
                    'csv_path': csv_path,
                    'json_path': json_path,
                    'results_count': len(results),
                    'stats_summary': {
                        'average_score': stats['average_score'],
                        'highest_score': stats['highest_score'],
                        'lowest_score': stats['lowest_score'],
                        'total_submissions': stats['total_submissions']
                    }
                }
                json.dump(serializable_data, f)
            
            flash('Grading completed successfully!', 'success')
            return redirect(url_for('results'))
            
        except Exception as e:
            flash(f'Error processing files: {str(e)}', 'error')
            return redirect(request.url)
    
    # GET request - show the form
    return render_template('grade.html')


@app.route('/results')
def results():
    """Display grading results and statistics"""
    session_file = os.path.join(RESULTS_DIR, 'session_data.json')
    
    if not os.path.exists(session_file):
        flash('No grading results available', 'error')
        return redirect(url_for('grade'))
        
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    return render_template('results.html', data=session_data)


@app.route('/download/<file_type>')
def download(file_type):
    """Download result files"""
    session_file = os.path.join(RESULTS_DIR, 'session_data.json')
    
    if not os.path.exists(session_file):
        flash('No files available for download', 'error')
        return redirect(url_for('index'))
        
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    if file_type == 'csv':
        file_path = session_data.get('csv_path')
        if file_path and os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
    
    elif file_type == 'json':
        file_path = session_data.get('json_path')
        if file_path and os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
    
    flash('Requested file not found', 'error')
    return redirect(url_for('results'))


@app.route('/student/<student_id>')
def student_feedback(student_id):
    """Generate feedback for a specific student"""
    session_file = os.path.join(RESULTS_DIR, 'session_data.json')
    
    if not os.path.exists(session_file):
        flash('No grading data available', 'error')
        return redirect(url_for('index'))
    
    # Since we can't store full results in session, we need to re-read the CSV
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    csv_path = session_data.get('csv_path')
    if not csv_path or not os.path.exists(csv_path):
        flash('Result data not found', 'error')
        return redirect(url_for('results'))
    
    # Load the CSV and find the student
    import pandas as pd
    df = pd.read_csv(csv_path)
    student_row = df[df['Student ID'] == student_id]
    
    if student_row.empty:
        flash(f'Student {student_id} not found', 'error')
        return redirect(url_for('results'))
    
    # Extract student data
    student_data = student_row.iloc[0].to_dict()
    
    return render_template('student.html', student=student_data)


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create simple templates if they don't exist
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MCQ Grader AI</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.2.3/css/bootstrap.min.css">
            </head>
            <body>
                <div class="container mt-5">
                    <h1>MCQ Grader AI</h1>
                    <p class="lead">Automatic grading system for multiple-choice questions</p>
                    <div class="mt-4">
                        <a href="/grade" class="btn btn-primary">Start Grading</a>
                    </div>
                </div>
            </body>
            </html>
            """)
    
    app.run(debug=True)