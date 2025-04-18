#!/usr/bin/env python3
import argparse
import json
import os
import sys
from main import MCQGrader


def load_json_file(file_path):
    """Load and validate a JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file: {file_path}")
        sys.exit(1)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="MCQ Grader AI - Command Line Interface")
    
    # Required arguments
    parser.add_argument('--answer-key', required=True, help='Path to answer key JSON file')
    parser.add_argument('--submissions', required=True, help='Path to student submissions JSON file')
    
    # Optional arguments
    parser.add_argument('--question-text', help='Path to question text JSON file')
    parser.add_argument('--output-dir', default='results', help='Directory for output files')
    parser.add_argument('--results-csv', help='Filename for results CSV')
    parser.add_argument('--stats-json', help='Filename for statistics JSON')
    parser.add_argument('--student-id', help='Generate feedback for specific student ID')
    
    args = parser.parse_args()
    
    # Load files
    answer_key = load_json_file(args.answer_key)
    submissions = load_json_file(args.submissions)
    question_text = load_json_file(args.question_text) if args.question_text else None
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize grader and process submissions
    grader = MCQGrader(answer_key)
    
    # Set results directory
    grader.results_dir = args.output_dir
    
    # Process submissions
    print(f"Processing {len(submissions)} submissions...")
    results = grader.grade_batch(submissions)
    
    # Export results
    csv_path = grader.export_results_csv(results, args.results_csv)
    print(f"Results exported to: {csv_path}")
    
    # Generate and export statistics
    stats = grader.generate_statistics(results)
    json_path = grader.export_statistics_json(stats, args.stats_json)
    print(f"Statistics exported to: {json_path}")
    
    # Print summary
    print("\nSummary:")
    print(f"Total submissions: {stats['total_submissions']}")
    print(f"Average score: {stats['average_score']:.1f}%")
    print(f"Highest score: {stats['highest_score']:.1f}%")
    print(f"Lowest score: {stats['lowest_score']:.1f}%")
    
    # Generate feedback for specific student if requested
    if args.student_id:
        student_found = False
        for result in results:
            if result["student_id"] == args.student_id:
                print("\nStudent Feedback:")
                print("=" * 50)
                print(grader.generate_feedback(result, question_text))
                student_found = True
                break
        
        if not student_found:
            print(f"\nError: Student ID {args.student_id} not found in submissions.")


if __name__ == "__main__":
    main()