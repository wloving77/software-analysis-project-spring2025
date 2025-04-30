import sys
import os
import argparse
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")
sys.path.insert(0, str(ROOT_DIR))

from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI

# Import tool objects (already decorated with @tool)
from tools.afl import run_afl_pipeline
from tools.klee import run_klee_pipeline
from tools.testgen import generate_test_cases
from tools.coverage import generate_coverage_report

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    temperature=0.3,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

# Define tools (already decorated, no need for Tool.from_function)
tools = [
    run_afl_pipeline,
    run_klee_pipeline,
    generate_test_cases,
    generate_coverage_report,
]

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Run the agent
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of steps for the agent to take",
    )
    args = parser.parse_args()

    for i in range(args.iterations):
        print(f"\n🧠 Agent Iteration {i+1}/{args.iterations}")
        result = agent.run(
            "You are testing a C binary with the defined tools provided to you. "
            "Your goal is to maximize program coverage above all else. "
            "Utilize the provided tools for that purpose."
            "Here is some tool information:"
            "AFL: Run AFL with specified flags. Example input: '--num-seeds 10 --afl-runtime 30'"
            "-- This will generate seeds with AFL and then run AFL with those seeds."
            "KLEE: Runs the full KLEE symbolic execution pipeline."
            "-- This will rewrite the program for KLEE symbolic execution and then run KLEE."
            "Generate Test Cases: Generate test cases using Gemini."
            "-- This will generate test cases using Gemini."
            "Generate Coverage Report: Generate a coverage report using gcov"
            "-- This will generate a coverage report using gcov by combining all of relevant generated test cases from all of the previous tools, use this as a final step check."
        )
        print(result)
