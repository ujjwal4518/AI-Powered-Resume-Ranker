from flask import Flask, request, render_template, send_file
import os
from werkzeug.utils import secure_filename
from resume_utils import process_resumes, save_report

UPLOAD_FOLDER = 'app/resumes'
REPORT_FOLDER = 'app/reports'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('resumes')
    if not files:
        return "No files uploaded"

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    filenames = []
    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        filenames.append(filename)

    jd_path = 'job_description.txt'
    scores = process_resumes(filenames, UPLOAD_FOLDER, jd_path)
    save_report(filenames, scores, os.path.join(REPORT_FOLDER, 'hr_report.csv'))

    ranked = sorted(zip(filenames, scores), key=lambda x: x[1], reverse=True)
    return render_template('results.html', ranked=ranked)

@app.route('/download')
def download():
    return send_file(os.path.join(REPORT_FOLDER, 'hr_report.csv'), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
