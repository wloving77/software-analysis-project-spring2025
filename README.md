# 🧪 Agent-Driven Automated Software Testing

This project is a prototype for **agent-based software testing**, where we use a LangChain-powered LLM (backed by Gemini) to generate symbolic test rewrites and drive fuzzing/symbolic execution tools like **KLEE** and **AFL++**.

The key goals of the project are:
- 🧠 Use an LLM to **analyze C source code**
- ✍️ Automatically **rewrite programs** with symbolic input hooks (`klee_make_symbolic`)
- ⚙️ Compile and run them through **KLEE** and **AFL++** in a reproducible pipeline
- 📊 Capture outputs and artifacts to later evaluate test coverage, path exploration, and error detection
- 🔁 Wrap the entire process in reusable LangChain tools

---

## 📁 Project Structure

```
├── agent-tester
│   ├── agent
│   │   ├── agent_runner.py
│   │   ├── temp_input.o
│   │   └── tools
│   ├── artifacts
│   │   ├── afl
│   │   ├── coverage
│   │   ├── final-results
│   │   ├── llm-testgen
│   │   └── standard_binary
│   ├── c_program
│   │   ├── include
│   │   ├── Makefile
│   │   ├── src
│   │   ├── tcc_source
│   │   └── tcc.gcno
│   ├── docker
│   │   ├── build_and_run_container_apple_silicon.sh
│   │   ├── build_and_run_container.sh
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── README.md
│   ├── results
│   │   ├── final-results_1
│   │   ├── final-results_2
│   │   └── sandbox.ipynb
│   └── scripts
│       ├── __init__.py
│       ├── __pycache__
│       ├── afl
│       ├── afl_orchestrator.py
│       ├── coverage_orchestrator.py
│       ├── klee
│       ├── klee_orchestrator.py
│       └── testgen_orchestrator.py
├── LICENSE
└── README.md
```


# Setup Guide 
- See README in `./agent-tester`