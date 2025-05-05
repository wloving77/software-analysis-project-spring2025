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

from scripts.afl.generate_afl_seeds import read_c_programs_with_filenames

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    temperature=0.3,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

# Define tools (already decorated, no need for Tool.from_function)
tools = [
    run_afl_pipeline,
    # run_klee_pipeline,
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

    with open(f"{ROOT_DIR}/c_program/src/tcc.c", "r") as f:
        c_program = f.read()

    iteration_results = []

    for i in range(args.iterations):
        print(f"\n🧠 Agent Iteration {i+1}/{args.iterations}")

        run_prompt = (
            "You are testing a C binary with the defined tools provided to you.\n"
            "Here is the program you are testing:\n\n" + c_program + "\n\n"
            "Your goal is to maximize program coverage above all else.\n"
            "Utilize the provided tools for that purpose.\n\n"
            "Here is some tool information:\n\n"
            "Generate AFL Seeds and Run AFL: Run AFL with generated seeds. Example Flags:\n"
            "--num-seeds 10 --afl-runtime 30 --additional-prompt 'any additional prompting for seed generation'\n"
            "-- This will generate seeds with AFL and then run AFL with those seeds for the specified runtime.\n"
            "-- You can run AFL for up to 5 minutes which is an afl-runtime of 300 seconds.\n"
            "-- Be sure to add any additional prompting for seed generation to the --additional-prompt flag.\n\n"
            "LLM Generated Test Cases: Generate test cases using Gemini. Example Flags:\n"
            "--num-tests 10 --additional-prompt 'any additional prompting for test case generation'\n"
            "-- These test cases will only be used upon coverage testing with the coverage test tool.\n"
            "-- Be sure to add any additional prompting for test case generation to the --additional-prompt flag.\n\n"
            "Generate Coverage Report: Generate a coverage report using gcov\n"
            "-- This will generate a coverage report using gcov by combining all relevant generated test cases from both of the previous tools.\n"
            "-- Use this as a final step check.\n\n"
            "If flags were not mentioned for a tool, the tool has no flags.\n"
            "The additional-prompt flag is simply appending whatever you add to what the model attempts to generate. These generated tests are simply .c files, request complexity and specific attributes about those c files. \n"
            "Always use all of the tools in each iteration, even if you believe some may be redundant.\n"
            "DO NOT INSTRUCT THE MODEL TO USE FLAGS, THE MODEL ONLY GENERATES STATIC TEXT AND IS RUNNING NOTHING.\n"
        )

        if i > 0:
            run_prompt += (
                "\n\n"
                f"The results of the previous iteration: {iteration_results[i-1]}"
                "\n\n"
            )

        result = agent.run(run_prompt)
        print(result)
        iteration_results.append(result)
