# MCQ Grader AI

An intelligent system for automated grading of multiple-choice questions (MCQs) with detailed feedback and statistical analysis.

## Features

- Automatic grading of MCQ submissions
- Detailed feedback generation for students
- Statistical analysis of class performance
- Question-by-question analysis to identify difficult topics
- Export results to CSV and JSON formats
- Web interface for easy usage
- Command-line interface for batch processing

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/mcq-grader-ai.git
   cd mcq-grader-ai
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Web Interface

1. Start the web server:
   ```
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Upload your answer key and submissions files in JSON format

4. View results and download reports

### Command Line Interface

For batch processing, use the CLI:

```
python cli.py --answer-key examples/answer_key.json --submissions examples/submissions.json
```

Additional options:
```
python cli.py --help
```

## File Formats

### Answer Key (JSON)

```json
{
  "1": "B",
  "2": "A",
  "3": "D",
  "4": "C",
  "5": "A"
}
```

### Submissions (JSON)

```json
[
  {
    "student_id": "S001",
    "answers": {
      "1": "B",
      "2": "A",
      "3": "D",
      "4": "C",
      "5": "A"
    }
  },
  {
    "student_id": "S002",
    "answers": {
      "1": "B",
      "2": "B",
      "3": "C",
      "4": "C",
      "5": "A"
    }
  }
]
```

### Question Text (JSON, optional)

```json
{
  "1": "What is the capital of France?",
  "2": "Which planet is closest to the Sun?",
  "3": "Who wrote 'Romeo and Juliet'?",
  "4": "What is the chemical symbol for water?",
  "5": "Which of these is a prime number: 1, 9, 11, 15?"
}
```

## Example

```python
from main import MCQGrader

# Define answer key
answer_key = {
    "1": "B",
    "2": "A",
    "3": "D",
    "4": "C",
    "5": "A"
}

# Initialize grader
grader = MCQGrader(answer_key)

# Grade a single submission
result = grader.grade_submission("S001", {
    "1": "B",
    "2": "A",
    "3": "D",
    "4": "C",
    "5": "B"  # Wrong answer
})

# Generate feedback
feedback = grader.generate_feedback(result)
print(feedback)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.