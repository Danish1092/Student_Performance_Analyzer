def calculate_sgpa():
    total_credits = 0
    total_grade_points = 0
    
    num_subjects = int(input("Enter the number of subjects: "))
    
    for i in range(num_subjects):
        subject_name = input(f"\nEnter the name of subject {i + 1}: ")
        credits = int(input(f"Enter the credits for {subject_name}: "))
        marks = int(input(f"Enter the marks obtained in {subject_name}: "))
        
        # Determine grade point based on marks
        if marks >= 90:
            grade_point = 10
        elif marks >= 80:
            grade_point = 9
        elif marks >= 70:
            grade_point = 8
        elif marks >= 60:
            grade_point = 7
        elif marks >= 50:
            grade_point = 6
        elif marks >= 40:
            grade_point = 5
        else:
            grade_point = 0  # Fail
        
        # Debug print for each subject
        print(f"Subject: {subject_name}, Credits: {credits}, Marks: {marks}, Grade Point: {grade_point}")

        # Accumulate total credits and grade points
        total_credits += credits
        total_grade_points += grade_point * credits
    
    # Calculate SGPA
    sgpa = total_grade_points / total_credits if total_credits > 0 else 0
    print(f"\nTotal Credits: {total_credits}, Total Grade Points: {total_grade_points}")
    print(f"Calculated SGPA: {sgpa:.2f}")

# Run the SGPA calculator
calculate_sgpa()
