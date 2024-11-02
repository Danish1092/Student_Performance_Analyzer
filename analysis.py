import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from utils import extract_subject_credits

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
        sgpa = total_grade_points / total_credits if total_credits > 0 else 0
        sga_values.append(sgpa)
    
    df['SGPA'] = sga_values
    return df


def generate_plots(df):
    plots = {}
    
    # Set the style for all plots using a simple and appealing style
    sns.set_theme(style='whitegrid')

    # 1. SGPA Distribution Plot
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='SGPA', bins=30, kde=True, color='skyblue')
    plt.title('Distribution of SGPA', fontsize=16)
    plt.xlabel('SGPA', fontsize=14)
    plt.ylabel('Number of Students', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plots['sgpa_dist'] = save_plot_to_base64()

    # 2. Subject-wise Box Plot with data points
    plt.figure(figsize=(12, 6))
    subject_data = []
    subject_names = []
    for col in df.columns:
        subject, credits = extract_subject_credits(col)
        if subject and credits:
            subject_data.append(df[col])
            subject_names.append(subject)
    box = plt.boxplot(subject_data, labels=subject_names, vert=False, patch_artist=True)
    
    # Customize box plot colors
    for median in box['medians']:
        median.set(color='red', linewidth=2)
    
    plt.title('Subject-wise Marks Distribution', fontsize=16)
    plt.xlabel('Marks', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plots['subject_box'] = save_plot_to_base64()

    # 3. Pass Rate Comparison
    plt.figure(figsize=(10, 6))
    pass_rates = []
    for col in df.columns:
        subject, credits = extract_subject_credits(col)
        if subject and credits:
            pass_rate = (df[col] >= 40).mean() * 100
            pass_rates.append({'Subject': subject, 'Pass Rate': pass_rate})
    pass_df = pd.DataFrame(pass_rates)
    sns.barplot(data=pass_df, x='Subject', y='Pass Rate', palette='pastel')
    plt.title('Subject-wise Pass Rates', fontsize=16)
    plt.xticks(rotation=45)
    plt.ylabel('Pass Rate (%)', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plots['pass_rates'] = save_plot_to_base64()

    # 4. Grade Distribution Heatmap
    plt.figure(figsize=(12, 8))
    grade_data = []
    for col in df.columns:
        subject, credits = extract_subject_credits(col)
        if subject and credits:
            grades = pd.cut(df[col], 
                          bins=[0, 40, 45, 50, 60, 70, 80, 90, 100],
                          labels=['F', 'E', 'D', 'C', 'B', 'A', 'A+', 'O'])
            grade_counts = grades.value_counts()
            grade_data.append({
                'Subject': subject,
                **{grade: count for grade, count in grade_counts.items()}
            })
    grade_df = pd.DataFrame(grade_data).set_index('Subject').fillna(0)
    sns.heatmap(grade_df, annot=True, fmt='g', cmap='YlOrRd', cbar_kws={'label': 'Number of Students'})
    plt.title('Grade Distribution Across Subjects', fontsize=16)
    plt.ylabel('Subject', fontsize=14)
    plt.xlabel('Grade', fontsize=14)
    plt.xticks(rotation=45)
    plots['grade_dist'] = save_plot_to_base64()

    return plots

def save_plot_to_base64():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    return base64.b64encode(image_png).decode()

def get_subject_analysis(df):
    analysis = {
        'total_students': len(df),
        'subjects': [],
        'top_performers': {},
        'statistics': {},
        'plots': generate_plots(df)
    }
    
    # Overall Statistics
    analysis['statistics'] = {
        'average_sgpa': round(df['SGPA'].mean(), 2),
        'median_sgpa': round(df['SGPA'].median(), 2),
        'std_sgpa': round(df['SGPA'].std(), 2),
        'top_sgpa': round(df['SGPA'].max(), 2),
        'bottom_sgpa': round(df['SGPA'].min(), 2),
        'total_pass_rate': round((df['SGPA'] >= 4.0).mean() * 100, 2)
    }
    
    for col in df.columns:
        subject, credits = extract_subject_credits(col)
        if subject and credits:
            # Get top 3 performers for this subject
            top_performers = df.nlargest(3, col)[['Student Name', 'USN', col]]
            
            # Calculate detailed statistics
            marks = df[col]
            quartiles = marks.quantile([0.25, 0.5, 0.75])
            
            subject_stats = {
                'name': subject,
                'credits': credits,
                'average': round(marks.mean(), 2),
                'median': round(marks.median(), 2),
                'std_dev': round(marks.std(), 2),
                'max': marks.max(),
                'min': marks.min(),
                'q1': round(quartiles[0.25], 2),
                'q3': round(quartiles[0.75], 2),
                'pass_rate': round((marks >= 40).mean() * 100, 2),
                'distinction_rate': round((marks >= 75).mean() * 100, 2),
                'top_performers': [
                    {
                        'name': row['Student Name'],
                        'usn': row['USN'],
                        'marks': row[col]
                    } for _, row in top_performers.iterrows()
                ],
                'grade_distribution': {
                    'O (90-100)': len(marks[marks >= 90]),
                    'A+ (80-89)': len(marks[(marks >= 80) & (marks < 90)]),
                    'A (70-79)': len(marks[(marks >= 70) & (marks < 80)]),
                    'B (60-69)': len(marks[(marks >= 60) & (marks < 70)]),
                    'C (50-59)': len(marks[(marks >= 50) & (marks < 60)]),
                    'D (45-49)': len(marks[(marks >= 45) & (marks < 50)]),
                    'E (40-44)': len(marks[(marks >= 40) & (marks < 45)]),
                    'F (0-39)': len(marks[marks < 40])
                }
            }
            analysis['subjects'].append(subject_stats)
    
    # Calculate overall top performers by SGPA
    top_sgpa_performers = df.nlargest(3, 'SGPA')[['Student Name', 'USN', 'SGPA']]
    analysis['top_performers']['overall'] = [
        {
            'name': row['Student Name'],
            'usn': row['USN'],
            'sgpa': row['SGPA']
        } for _, row in top_sgpa_performers.iterrows()
    ]
    
    return analysis
