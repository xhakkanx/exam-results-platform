import pandas as pd
import json
import os

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    else:
        return None

def save_json(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def update_students(csv_file, students_file):
    df = pd.read_csv(csv_file)
    students = load_json(students_file) or []
    existing_ids = {student['id'] for student in students}

    new_students = []
    for _, row in df.iterrows():
        student_id = row['id']
        name = row['name']
        if student_id not in existing_ids:
            new_students.append({
                "id": student_id,
                "name": name
            })

    if new_students:
        students.extend(new_students)
        save_json(students, students_file)
        print(f"Added {len(new_students)} new students.")
    else:
        print("No new students to add.")

def process_exam(csv_file, exam_name, exams_dir, students_file):
    df = pd.read_csv(csv_file)
    students = load_json(students_file)
    exam_file = os.path.join(exams_dir, f"{exam_name}.json")

    exam_data = load_json(exam_file)
    if not exam_data:
        # Initialize exam data
        sections = []
        # Assuming the first row contains section info
        for col in df.columns:
            if col not in ['id', 'name']:
                section_info = col.split('_')
                section_name = section_info[0]
                question_type = section_info[1]  # correct, wrong, notAttempted
                # Initialize sections
                if section_name not in [s['name'] for s in sections]:
                    sections.append({
                        "name": section_name,
                        "totalQuestions": 0,  # To be set manually or inferred
                        "negativeMarking": True,  # Default value
                        "cutoff": 40  # Default cutoff
                    })
        exam_data = {
            "examName": exam_name,
            "sections": sections,
            "results": []
        }

    for _, row in df.iterrows():
        student_id = row['id']
        student = next((s for s in students if s['id'] == student_id), None)
        if not student:
            print(f"Student ID {student_id} not found in students.json.")
            continue

        sections = {}
        for col in df.columns:
            if col.startswith('Math') or col.startswith('English') or col.startswith('Analytical'):
                section_info = col.split('_')
                section_name = section_info[0]
                metric = section_info[1]
                if section_name not in sections:
                    sections[section_name] = {"correct": 0, "wrong": 0, "notAttempted": 0}
                sections[section_name][metric] = int(row[col])

        exam_data['results'].append({
            "studentId": student_id,
            "sections": sections
        })

    save_json(exam_data, exam_file)
    print(f"Processed exam data for {exam_name}.")

def main():
    students_file = 'data/students.json'
    exams_dir = 'data/exams'

    if not os.path.exists(exams_dir):
        os.makedirs(exams_dir)

    # Example usage:
    # Update students from a CSV file
    students_csv = 'students.csv'  # CSV file with columns: id, name
    update_students(students_csv, students_file)

    # Process an exam
    exam_csv = 'mock1.csv'  # CSV file with columns: id, name, Math_correct, Math_wrong, Math_notAttempted, English_correct, etc.
    exam_name = 'mock1'
    process_exam(exam_csv, exam_name, exams_dir, students_file)

    # Similarly, process other exams
    # exam_csv = 'mock2.csv'
    # exam_name = 'mock2'
    # process_exam(exam_csv, exam_name, exams_dir, students_file)

if __name__ == "__main__":
    main()
