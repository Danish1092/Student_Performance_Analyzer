from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import pandas as pd
from utils import allowed_file, extract_subject_credits, calculate_sgpa, get_subject_analysis

app = Flask(__name__)
app.secret_key = "anonymous"
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                df = pd.read_excel(filepath)
                df = calculate_sgpa(df)
                df.to_excel(filepath, index=False)  # Save the updated Excel file
                
                return redirect(url_for('analyze_data', filename=filename))
            
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        else:
            flash('Allowed file types are xlsx, xls')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/analyze/<filename>')
def analyze_data(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('File not found')
        return redirect(url_for('upload_file'))
    
    try:
        df = pd.read_excel(filepath)
        analysis = get_subject_analysis(df)
        return render_template('analysis.html', analysis=analysis)
        
    except Exception as e:
        flash(f'Error analyzing data: {str(e)}')
        return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)