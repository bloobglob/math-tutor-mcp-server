import os
import csv
import json
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import requests
import google.generativeai as genai
import re

@dataclass
class BenchmarkResult:
    question: str
    expected_solution: str
    scenario: str  # "perfect_student" or "imperfect_student"
    logic_correct: bool
    corrected_when_wrong: bool
    solution_matches: bool
    conversation_log: List[Dict[str, str]]
    evaluation_details: str

class MathTutorAgent:
    def __init__(self):
        load_dotenv()
        self.dify_api_key = os.getenv("DIFY_API_KEY")
        self.base_url = "http://127.0.0.1/v1"
        self.conversation_id = None
        
    def start_conversation(self, query: str) -> str:
        """Start a new conversation with the Math Tutor Agent."""
        body = {
            "query": query,
            "response_mode": "blocking",
            "user": "benchmark",
            "conversation_id": "",
            "inputs": {}
        }
        headers = {
            "Authorization": f"Bearer {self.dify_api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(f"{self.base_url}/chat-messages", json=body, headers=headers)
            if response.status_code == 200:
                self.conversation_id = response.json().get("conversation_id")
                return response.json().get("answer")
            return f"ERROR: {response.status_code}\n{response.text}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def continue_conversation(self, query: str) -> str:
        """Continue an existing conversation with the Math Tutor Agent."""
        if not self.conversation_id:
            return "ERROR: No active conversation"
            
        body = {
            "query": query,
            "response_mode": "blocking",
            "user": "benchmark",
            "conversation_id": self.conversation_id,
            "inputs": {}
        }
        headers = {
            "Authorization": f"Bearer {self.dify_api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(f"{self.base_url}/chat-messages", json=body, headers=headers)
            if response.status_code == 200:
                return response.json().get("answer")
            return f"ERROR: {response.status_code} - {response.text}"
        except Exception as e:
            return f"ERROR: {str(e)}"

class GeminiEvaluator:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-001')
        
    def act_as_perfect_student(self, tutor_response: str, question: str, expected_solution: str) -> str:
        """Gemini acts as a perfect student who understands everything correctly."""
        prompt = f"""
        You are a perfect 7th/8th grade student who always understands math concepts correctly and follows instructions well.
        
        Math Problem: {question}
        Expected Solution: {expected_solution}
        Tutor's Response: {tutor_response}
        
        Respond as a student would - ask clarifying questions if needed, show your work when solving, 
        and demonstrate understanding. Be engaged and cooperative. Keep responses concise but show your thinking.
        
        Student response:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating perfect student response: {str(e)}"
    
    def act_as_imperfect_student(self, tutor_response: str, question: str, expected_solution: str, 
                                conversation_history: List[Dict]) -> str:
        """Gemini acts as an imperfect student who makes common mistakes."""
        prompt = f"""
        You are a 7th/8th grade student who sometimes makes mistakes, gets confused, or misunderstands concepts.
        Make realistic errors that students at this level commonly make.
        
        Math Problem: {question}
        Expected Solution: {expected_solution}
        Tutor's Response: {tutor_response}
        
        Previous conversation: {json.dumps(conversation_history[-3:], indent=2)}
        
        Respond as a student would, but include some realistic mistakes or confusion:
        - Computational errors
        - Conceptual misunderstandings
        - Forgetting steps
        - Misreading the problem
        - Confusion about terminology
        
        Keep responses natural and concise. Show your (potentially incorrect) work.
        
        Student response:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"ERROR generating imperfect student response: {str(e)}"
    
    def evaluate_conversation(self, conversation_log: List[Dict], question: str, 
                            expected_solution: str, scenario: str) -> Tuple[bool, bool, bool, str]:
        """Evaluate the entire conversation for logic correctness, error correction, and solution accuracy."""
        
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_log])
        
        prompt = f"""
        Evaluate this math tutoring conversation between a tutor agent and a {scenario.replace('_', ' ')}.
        
        ORIGINAL PROBLEM: {question}
        EXPECTED SOLUTION: {expected_solution}
        SCENARIO: {scenario}
        
        CONVERSATION:
        {conversation_text}
        
        CRITICAL: Use STRICT TRUE/FALSE evaluation. FALSE means ANY mistake was made by the agent.
        
        Evaluate these criteria with ZERO TOLERANCE for errors:
        
        1. LOGIC_CORRECT: 
           - TRUE only if ALL mathematical reasoning is completely correct
           - FALSE if there are ANY logical errors, computational mistakes, or incorrect steps
        
        2. CORRECTED_WHEN_WRONG: 
           - TRUE only if the tutor identified and corrected ALL student errors
           - FALSE if any student error was missed, incorrectly identified, or poorly corrected
           - TRUE by default if student made no errors in perfect student scenario
        
        3. SOLUTION_MATCHES: 
           - TRUE only if the final answer matches the expected solution OR mathematically equivalent (e.g. fraction vs. decimal)
           - FALSE if the answer is wrong
        
        Respond in this exact JSON format:
        {{
            "logic_correct": true/false,
            "corrected_when_wrong": true/false,
            "solution_matches": true/false,
            "evaluation_details": "Detailed explanation of what went wrong (if anything)"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = re.search(r'```json\s*\n(.*?)\n```', response.text, re.DOTALL).group(1)
            print(text)
            evaluation = json.loads(text)
            
            return (
                evaluation.get("logic_correct", False),
                evaluation.get("corrected_when_wrong", False), 
                evaluation.get("solution_matches", False),
                evaluation.get("evaluation_details", "")
            )
        except Exception as e:
            return False, False, False, f"Evaluation ERROR: {str(e)}"

class MathTutorBenchmark:
    def __init__(self):
        self.agent = MathTutorAgent()
        self.evaluator = GeminiEvaluator()
        self.results: List[BenchmarkResult] = []
        with open("math_tutor_benchmark_results.json", 'r') as f:
            past_results = json.load(f)["detailed_results"]
            self.results = [BenchmarkResult(
                question=r["question"],
                expected_solution=r["expected_solution"],
                scenario=r["scenario"],
                logic_correct=r["logic_correct"],
                corrected_when_wrong=r["corrected_when_wrong"],
                solution_matches=r["solution_matches"],
                conversation_log="",
                evaluation_details=r["evaluation_details"]
            ) for r in past_results]

    def load_problems(self, csv_files: List[str]) -> List[Tuple[str, str]]:
        """Load math problems and solutions from CSV files."""
        problems = []
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Assuming CSV has 'question' and 'solution' columns
                        # Adjust column names as needed
                        question = row.get('question', row.get('Question', ''))
                        solution = row.get('solution', row.get('Solution', ''))
                        if question and solution:
                            problems.append((question.strip(), solution.strip()))
            except Exception as e:
                print(f"ERROR loading {csv_file}: {str(e)}")
        return problems
    
    def run_scenario(self, question: str, expected_solution: str, scenario: str, 
                    max_turns: int = 10) -> BenchmarkResult:
        """Run a single benchmark scenario."""
        print(f"\n{'='*50}")
        print(f"Running {scenario} scenario")
        print(f"Question: {question}")
        print(f"{'='*50}")
        
        # Reset agent for new conversation
        self.agent.conversation_id = None
        conversation_log = []
        
        # Start conversation
        initial_query = f"Help me solve this problem: {question}"
        tutor_response = self.agent.start_conversation(initial_query)
        
        conversation_log.append({"role": "student", "content": initial_query})
        conversation_log.append({"role": "tutor", "content": tutor_response})
        
        print(f"TUTOR: {tutor_response}")
        
        # Continue conversation based on scenario
        for turn in range(max_turns - 1):
            if "Finished" in tutor_response:
                break
            if scenario == "perfect_student":
                student_response = self.evaluator.act_as_perfect_student(
                    tutor_response, question, expected_solution
                )
            else:
                student_response = self.evaluator.act_as_imperfect_student(
                    tutor_response, question, expected_solution, conversation_log
                )
            
            if "ERROR" in student_response:
                print(student_response)
                break
                
            conversation_log.append({"role": "student", "content": student_response})
            print(f"STUDENT: {student_response}")
            
            # Check if conversation should end
            if any(phrase in student_response.lower() for phrase in 
                   ["i understand", "got it", "thank you", "makes sense now", "i see"]):
                if turn >= 2:  # Minimum conversation length
                    break
            
            tutor_response = self.agent.continue_conversation(student_response)
            conversation_log.append({"role": "tutor", "content": tutor_response})
            print(f"TUTOR: {tutor_response}")
            
            if "ERROR" in tutor_response:
                break
            
            time.sleep(5)
        
        # Evaluate the conversation
        logic_correct, corrected_when_wrong, solution_matches, details = \
            self.evaluator.evaluate_conversation(conversation_log, question, expected_solution, scenario)
            
        time.sleep(5)
        
        result = BenchmarkResult(
            question=question,
            expected_solution=expected_solution,
            scenario=scenario,
            logic_correct=logic_correct,
            corrected_when_wrong=corrected_when_wrong,
            solution_matches=solution_matches,
            conversation_log=conversation_log,
            evaluation_details=details
        )
        
        self.results.append(result)
        return result
    
    def run_benchmark(self, csv_files: List[str], start: Optional[int] = None, sample_size: Optional[int] = None):
        """Run the complete benchmark on problems from CSV files."""
        problems = self.load_problems(csv_files)
        
        if start and sample_size:
            problems = problems[start:start + sample_size]
        elif start:
            problems = problems[start:]
        elif sample_size:
            problems = problems[:sample_size]
        
        print(f"Loaded {len(problems)} problems from {csv_files}")
        
        for i, (question, solution) in enumerate(problems):
            if i < len(self.results):
                continue
            print(f"\n\nPROBLEM {i+1}/{len(problems)}")
            
            # Run perfect student scenario
            perfect_result = self.run_scenario(question, solution, "perfect_student")
            
            # Run imperfect student scenario  
            imperfect_result = self.run_scenario(question, solution, "imperfect_student")
            
            if "ERROR" in perfect_result.evaluation_details or \
                "ERROR" in str(perfect_result.conversation_log) or \
                "ERROR" in imperfect_result.evaluation_details or \
                "ERROR" in str(imperfect_result.conversation_log):
                print("Error encountered during benchmark, stopping further tests.")
                self.results.pop()
                self.results.pop()
                break
    
    def generate_report(self, output_file: str = "benchmark_report.json"):
        """Generate a comprehensive benchmark report."""
        perfect_results = [r for r in self.results if r.scenario == "perfect_student"]
        imperfect_results = [r for r in self.results if r.scenario == "imperfect_student"]
        
        def calculate_metrics(results):
            if not results:
                return {}
            return {
                "logic_correct_rate": sum(r.logic_correct for r in results) / len(results),
                "correction_rate": sum(r.corrected_when_wrong for r in results) / len(results),
                "solution_match_rate": sum(r.solution_matches for r in results) / len(results),
                "perfect_performance_rate": sum(all([r.logic_correct, r.corrected_when_wrong, r.solution_matches]) for r in results) / len(results),
                "total_problems": len(results)
            }
        
        report = {
            "benchmark_summary": {
                "total_problems_tested": len(self.results) // 2,
                "perfect_student_metrics": calculate_metrics(perfect_results),
                "imperfect_student_metrics": calculate_metrics(imperfect_results)
            },
            "detailed_results": []
        }
        
        for result in self.results:
            report["detailed_results"].append({
                "question": result.question,
                "expected_solution": result.expected_solution,
                "scenario": result.scenario,
                "logic_correct": result.logic_correct,
                "corrected_when_wrong": result.corrected_when_wrong,
                "solution_matches": result.solution_matches,
                "perfect_performance": all([result.logic_correct, result.corrected_when_wrong, result.solution_matches]),
                "evaluation_details": result.evaluation_details,
                "conversation_length": len(result.conversation_log)
            })
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{'='*60}")
        print("BENCHMARK RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total Problems Tested: {len(self.results) // 2}")
        print("\nPERFECT STUDENT SCENARIO:")
        perfect_metrics = report["benchmark_summary"]["perfect_student_metrics"]
        for metric, value in perfect_metrics.items():
            if metric != "total_problems":
                print(f"  {metric.replace('_', ' ').title()}: {value:.1%}")
        
        print("\nIMPERFECT STUDENT SCENARIO:")
        imperfect_metrics = report["benchmark_summary"]["imperfect_student_metrics"]
        for metric, value in imperfect_metrics.items():
            if metric != "total_problems":
                print(f"  {metric.replace('_', ' ').title()}: {value:.1%}")
        
        print(f"\nDetailed report saved to: {output_file}")

def main():
    """Example usage of the benchmark system."""
    benchmark = MathTutorBenchmark()
    
    # Run benchmark on sample of problems
    csv_files = ["benchmark_data/7th.csv"]
    benchmark.run_benchmark(csv_files) 
    
    # Generate report
    benchmark.generate_report("math_tutor_benchmark_results.json")

if __name__ == "__main__":
    main()