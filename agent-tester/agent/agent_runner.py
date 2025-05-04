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

    full_c_program = read_c_programs_with_filenames(f"{ROOT_DIR}/c_program/src")

    iteration_results = []

    for i in range(args.iterations):
        print(f"\n🧠 Agent Iteration {i+1}/{args.iterations}")

        run_prompt = (
            "You are testing a C binary with the defined tools provided to you. "
            "Here is the program you are testing:"
            "\n\n"
            f"{full_c_program}"
            "\n\n"
            "Your goal is to maximize program coverage above all else. "
            "Utilize the provided tools for that purpose."
            "\n\n"
            "Here is some tool information:"
            "\n"
            "AFL: Run AFL with specified flags. Example Flags: '--num-seeds 10 --afl-runtime 30 --additional-prompt 'any additional prompting for gemini's seed geenration'"
            "-- This will generate seeds with AFL and then run AFL with those seeds."
            "\n"
            "KLEE: Runs the full KLEE symbolic execution pipeline. Example Flags: '--additional-prompt 'any additional prompting for gemini's klee rewrite for the program under test'"
            "-- This will rewrite the program for KLEE symbolic execution and then run KLEE."
            "\n"
            "Generate Test Cases: Generate test cases using Gemini. Example Flags: '--additional-prompt 'any additional prompting for gemini's test case geenration'"
            "-- This will generate test cases using Gemini."
            "\n"
            "Generate Coverage Report: Generate a coverage report using gcov"
            "-- This will generate a coverage report using gcov by combining all of relevant generated test cases from all of the previous tools, use this as a final step check."
            "\n\n"
            "\n\n"
            "If flags were not mentioned for a tool, the tool has no flags."
            "Please modify the flags as you see fit. For example, if you want to run AFL, Klee, or Test Case Generation with different flags, simply modify the flags in the input string."
            "Be sure to modify the flags to explore different behavior, longer afl runtimes and more test cases etc."
            "Always use all of the tools, even if you have results from previous iterations."
        )
        if i > 0:
            run_prompt += (
                "\n\n"
                f"The results of the previous iteration: {iteration_results[i-1]}"
            )

        print(run_prompt)
        result = agent.run(run_prompt)
        print(result)
        iteration_results.append(result)

    print("\n\n")
    print("\n".join(iteration_results))
