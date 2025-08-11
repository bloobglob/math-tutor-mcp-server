import requests
from dotenv import load_dotenv
import os

def solve(problem: str, app_id: str) -> str:
    api_url = "https://www.wolframalpha.com/api/v1/llm-api"
    params = {
        "appid": app_id,
        "input": problem.strip(r'`'),
        "maxchars": 1000,
    }
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        print(response.text)
        return "Error: Unable to reach WolframAlpha API."
    
    return response.text

# Example usage:
if __name__ == "__main__":
    load_dotenv()
    print(solve("solve |2x+3|=5", app_id=os.getenv("WOLFRAMALPHA_APP_ID")))