import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple

class MCQGrader:
    """
    A class to grade multiple-choice questions, provide feedback, and generate statistics.
    """
    
    def __init__(self, answer_key: Dict[str, str]):
        """
        Initialize the MCQ grader with an answer key.
        
        Args:
            answer_key: Dictionary with question IDs as keys and correct answers as values
        """
        self.answer_key = answer_key
        self.results_dir = "results"
        
        # Create results directory if it doesn't exist
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def grade_submission(self, student_id: str, student_answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Grade a student's submission against the answer key.
        
        Args:
            student_id: Unique identifier for the student
            student_answers: Dictionary with question IDs and student's answers
            
        Returns:
            Dictionary containing grading results and feedback
        """
        # Initialize result structure
        result = {
            "student_id": student_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "questions_total": len(self.answer_key),
            "questions_attempted": 0,
            "correct_answers": 0,
            "score_percentage": 0.0,
            "question_details": [],
        }
        
        # Process each question
        for q_id, correct_answer in self.answer_key.items():
            question_result = {
                "question_id": q_id,
                "correct_answer": correct_answer,
            }
            
            # Check if student answered this question
            if q_id in student_answers:
                result["questions_attempted"] += 1
                student_answer = student_answers[q_id]
                question_result["student_answer"] = student_answer
                question_result["is_correct"] = student_answer == correct_answer
                
                if question_result["is_correct"]:
                    result["correct_answers"] += 1
            else:
                question_result["student_answer"] = None
                question_result["is_correct"] = False
            
            result["question_details"].append(question_result)
        
        # Calculate overall score
        if result["questions_total"] > 0:
            result["score_percentage"] = (result["correct_answers"] / result["questions_total"]) * 100
        
        return result
    
    def grade_batch(self, submissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Grade multiple submissions at once.
        
        Args:
            submissions: List of dictionaries, each containing student_id and answers
            
        Returns:
            List of grading results
        """
        results = []
        
        for submission in submissions:
            student_id = submission.get("student_id")
            answers = submission.get("answers", {})
            
            if student_id and answers:
                result = self.grade_submission(student_id, answers)
                results.append(result)
        
        return results
    
    def generate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics from a set of graded submissions.
        
        Args:
            results: List of graded submission results
            
        Returns:
            Dictionary containing statistical analysis
        """
        if not results:
            return {"error": "No results to analyze"}
        
        stats = {
            "total_submissions": len(results),
            "average_score": 0.0,
            "highest_score": 0.0,
            "lowest_score": 100.0,
            "median_score": 0.0,
            "question_analysis": {},
        }
        
        # Calculate overall statistics
        scores = [r["score_percentage"] for r in results]
        stats["average_score"] = sum(scores) / len(scores)
        stats["highest_score"] = max(scores)
        stats["lowest_score"] = min(scores)
        stats["median_score"] = sorted(scores)[len(scores) // 2]
        
        # Analyze performance by question
        for q_id in self.answer_key.keys():
            question_stats = {
                "attempts": 0,
                "correct": 0,
                "correct_percentage": 0.0,
            }
            
            for result in results:
                for q_detail in result["question_details"]:
                    if q_detail["question_id"] == q_id and q_detail["student_answer"] is not None:
                        question_stats["attempts"] += 1
                        if q_detail["is_correct"]:
                            question_stats["correct"] += 1
            
            if question_stats["attempts"] > 0:
                question_stats["correct_percentage"] = (question_stats["correct"] / question_stats["attempts"]) * 100
            
            stats["question_analysis"][q_id] = question_stats
        
        return stats
    
    def export_results_csv(self, results: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export grading results to a CSV file.
        
        Args:
            results: List of graded submission results
            filename: Optional filename for the CSV
            
        Returns:
            Path to the created CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcq_results_{timestamp}.csv"
        
        filepath = os.path.join(self.results_dir, filename)
        
        # Prepare data for DataFrame
        data = []
        for result in results:
            row = {
                "Student ID": result["student_id"],
                "Timestamp": result["timestamp"],
                "Questions Attempted": result["questions_attempted"],
                "Correct Answers": result["correct_answers"],
                "Score (%)": result["score_percentage"]
            }
            
            # Add question-specific data
            for q_detail in result["question_details"]:
                q_id = q_detail["question_id"]
                row[f"Q{q_id} Answer"] = q_detail["student_answer"] if q_detail["student_answer"] else "Unanswered"
                row[f"Q{q_id} Correct"] = "Yes" if q_detail["is_correct"] else "No"
            
            data.append(row)
        
        # Create and save DataFrame
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    def export_statistics_json(self, stats: Dict[str, Any], filename: str = None) -> str:
        """
        Export statistics to a JSON file.
        
        Args:
            stats: Dictionary containing statistical analysis
            filename: Optional filename for the JSON
            
        Returns:
            Path to the created JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcq_statistics_{timestamp}.json"
        
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return filepath
    
    def generate_feedback(self, result: Dict[str, Any], question_text: Dict[str, str] = None) -> str:
        """
        Generate human-readable feedback for a student.
        
        Args:
            result: Grading result for a single submission
            question_text: Optional dictionary mapping question IDs to question text
            
        Returns:
            String containing formatted feedback
        """
        feedback = [
            f"Feedback for: {result['student_id']}",
            f"Date: {result['timestamp']}",
            f"Overall Score: {result['score_percentage']:.1f}% ({result['correct_answers']}/{result['questions_total']})",
            "\nQuestion Details:"
        ]
        
        for q_detail in result["question_details"]:
            q_id = q_detail["question_id"]
            q_text = question_text.get(q_id, f"Question {q_id}") if question_text else f"Question {q_id}"
            
            if q_detail["student_answer"] is None:
                feedback.append(f"\n{q_text}: Not attempted")
                feedback.append(f"  Correct answer: {q_detail['correct_answer']}")
            else:
                status = "✓ Correct" if q_detail["is_correct"] else "✗ Incorrect"
                feedback.append(f"\n{q_text}: {status}")
                feedback.append(f"  Your answer: {q_detail['student_answer']}")
                if not q_detail["is_correct"]:
                    feedback.append(f"  Correct answer: {q_detail['correct_answer']}")
        
        return "\n".join(feedback)


# Example usage
def example():
    # Sample answer key (question_id: correct_answer)
    answer_key = {
        "1": "B",
        "2": "A",
        "3": "D",
        "4": "C",
        "5": "A"
    }
    
    # Question text for better feedback
    question_text = {
        "1": "What is the capital of France?",
        "2": "Which planet is closest to the Sun?",
        "3": "Who wrote 'Romeo and Juliet'?",
        "4": "What is the chemical symbol for water?",
        "5": "Which of these is a prime number: 1, 9, 11, 15?"
    }
    
    # Initialize the grader
    grader = MCQGrader(answer_key)
    
    # Sample student submissions
    submissions = [
        {
            "student_id": "S001",
            "answers": {"1": "B", "2": "A", "3": "D", "4": "C", "5": "A"}
        },
        {
            "student_id": "S002",
            "answers": {"1": "B", "2": "B", "3": "C", "4": "C", "5": "A"}
        },
        {
            "student_id": "S003",
            "answers": {"1": "B", "2": "A", "3": "D", "5": "B"}  # Missing answer for Q4
        }
    ]
    
    # Grade all submissions
    results = grader.grade_batch(submissions)
    
    # Print individual feedback for the first student
    print(grader.generate_feedback(results[0], question_text))
    print("\n" + "="*50 + "\n")
    
    # Generate statistics
    stats = grader.generate_statistics(results)
    print(f"Average score: {stats['average_score']:.1f}%")
    print(f"Question analysis: {json.dumps(stats['question_analysis'], indent=2)}")
    
    # Export results
    csv_path = grader.export_results_csv(results)
    json_path = grader.export_statistics_json(stats)
    
    print(f"\nResults exported to: {csv_path}")
    print(f"Statistics exported to: {json_path}")


if __name__ == "__main__":
    example()