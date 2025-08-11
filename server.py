from fastmcp import FastMCP
from dotenv import load_dotenv
from tools import math_solver
from tools import note_retriever
import os

load_dotenv()
app_id = os.getenv("WOLFRAMALPHA_APP_ID")

mcp = FastMCP("math-tutor-mcp-server", json_response=True, stateless_http=True)

@mcp.tool
def solve_math(problem: str) -> str:
    """
    Solve a math problem using WolframAlpha. Does not give step-by-step, only the final answer. Does not work for word problems.
    
    Args:
        problem (str): The math problem to solve.
    
    Returns:
        str: The solution to the problem.
    """
    return math_solver.solve(problem, app_id)

@mcp.tool
def retrieve_notes(grade: str, section: str) -> str:
    """
    Retrieve notes from a specific section.

    Args:
        grade (str): The grade level of the notes. Ex: 7th or 8th.
        section (str): The section to retrieve notes from. Ex: 1.1, 4.3, etc.

    Returns:
        str: The retrieved notes.
    """
    return note_retriever.retrieve(grade, section)

@mcp.tool
def list_sections(grade: str) -> str:
    """
    Get all section identifiers and their titles for a specific grade.

    Args:
        grade (str): The grade level to retrieve sections for. Ex: 7th or 8th.

    Returns:
        str: A string with each section_id and title on a new line.
    """
    return note_retriever.get_sections(grade)

def main():
    mcp.run(transport='streamable-http', host='0.0.0.0', port=8001)
    # print(note_retriever.get_sections())
    
if __name__ == "__main__":
    main()