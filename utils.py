import re
import pandas as pd

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}

def extract_subject_credits(column_name):
    match = re.match(r'(.*?)\s*\((\d+)\)', column_name)
    if match:
        subject = match.group(1).strip()
        credits = int(match.group(2))
        return subject, credits
    return None, None

def validate_excel_structure(df):
    if 'Student Name' not in df.columns or 'USN' not in df.columns:
        return False, "Missing required columns: Student Name and USN"
    
    subject_columns = [col for col in df.columns if extract_subject_credits(col)[0] is not None]
    
    if len(subject_columns) < 5:
        return False, "Excel sheet must contain at least 5 subject columns with credits in brackets"
    
    for col in subject_columns:
        if not pd.to_numeric(df[col], errors='coerce').between(0, 100).all():
            return False, f"Invalid marks found in column {col}. Marks should be between 0 and 100"
    
    return True, "Validation successful"
