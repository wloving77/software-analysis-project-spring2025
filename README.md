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
├── LICENSE
├── README.md
└── agent-tester
    ├── README.md
    ├── agent
    │   ├── agent.py
    │   ├── prompt_templates.py
    │   ├── tool_wrappers.py
    │   └── tools
    │       ├── afl.py
    │       ├── code_loader.py
    │       ├── klee.py
    │       ├── runner.py
    │       └── testgen.py
    ├── c_program
    │   ├── Makefile
    │   ├── include
    │   └── src
    │       └── proof_of_concept.c
    ├── docker
    │   ├── Dockerfile
    │   ├── build_and_run_container.sh
    │   └── build_and_run_container_native.sh
    ├── requirements.txt
    └── scripts
        ├── afl
        │   └── run_afl_only.py
        ├── klee
        │   ├── generate_klee_rewrite.py
        │   └── run_klee_only.py
        └── klee_orchestrator.py
```