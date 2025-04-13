from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatGoogleGenerativeAI
from agent.tools.afl import run_afl_pipeline
from agent.tools.klee import run_klee_pipeline
from langchain.tools import Tool

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)

tools = [
    Tool.from_function(func=run_afl_pipeline, name="AFLPipeline", description="Fuzz C programs with AFL++"),
    Tool.from_function(func=run_klee_pipeline, name="KLEEPipeline", description="Run symbolic execution with KLEE"),
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

if __name__ == "__main__":
    result = agent.run("Fuzz and analyze C code for bugs and path coverage.")
    print(result)
