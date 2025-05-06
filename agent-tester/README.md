# LLM-C-Tester

A LangChain-powered agent that uses LLMs, KLEE symbolic execution, and AFL++ fuzzing to generate and refine tests for C programs.

# Setup Guide
- Ensure a `.env` file exists in this directory containing a `GEMINI_API_KEY=<YOUR_KEY>`
- Navigate to `./Docker` and execute the relevant bash script to enter the container (1 of the 2)
- Once within the container, navigate to  `./agent` and execute `python3 agent_runner.py --iterations <num_iterations>` and watch it go
