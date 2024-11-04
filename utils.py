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

def calculate_sgpa(df):
    # Define a function to calculate SGPA based on the DataFrame structure
    # Assuming columns are named like "Python(3)", "java(2)", etc.

    # Define credit mapping for subjects if applicable
    credits = {'Python(3)': 3, 'java(2)': 2, 'ada(3)': 3, 'Dbms(3)': 3, 'Computer network(2)': 2}
    
    def get_grade_point(marks):
        if marks >= 90:
            return 10
        elif marks >= 80:
            return 9
        elif marks >= 70:
            return 8
        elif marks >= 60:
            return 7
        elif marks >= 50:
            return 6
        elif marks >= 40:
            return 5
        else:
            return 0  # Fail
    
    # Calculate SGPA for each student
    sga_values = []
    
    for index, row in df.iterrows():
        total_credits = sum(credits[subject] for subject in credits if subject in df.columns)
        total_grade_points = sum(get_grade_point(row[subject]) * credits[subject] for subject in credits if subject in df.columns)
        sgpa = round(total_grade_points / total_credits, 2) if total_credits > 0 else 0
        sga_values.append(sgpa)
    
    df['SGPA'] = sga_values
    return df

def get_subject_analysis(df):
    analysis = {
        'total_students': len(df),
        'subjects': [],
        'top_performers': {},
    }
    
    # Overall Top Performers
    top_sgpa_performers = df.nlargest(5, 'SGPA')[['Student Name', 'USN', 'SGPA']]
    analysis['top_performers']['overall'] = [
        {
            'name': row['Student Name'],
            'usn': row['USN'],
            'sgpa': row['SGPA']
        } for _, row in top_sgpa_performers.iterrows()
    ]
    
    for col in df.columns:
        subject, credits = extract_subject_credits(col)
        if subject and credits:
            # Get top 5 performers for this subject
            top_performers = df.nlargest(5, col)[['Student Name', 'USN', col]]
            
            subject_stats = {
                'name': subject,
                'credits': credits,
                'top_performers': [
                    {
                        'name': row['Student Name'],
                        'usn': row['USN'],
                        'marks': row[col]
                    } for _, row in top_performers.iterrows()
                ],
            }
            analysis['subjects'].append(subject_stats)
    
    return analysis