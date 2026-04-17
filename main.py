"""
=============================================================
Project 3 — Supervisor Multi-Agent RAG System
=============================================================
"""

# ── 1. IMPORTS ────────────────────────────────────────────
import os
from dotenv import load_dotenv
from typing import List

from langchain.chat_models import init_chat_model
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.agents import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor


# ── 2. ENV SETUP ──────────────────────────────────────────
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")


# ── 3. LLM ────────────────────────────────────────────────
llm = init_chat_model("openai:gpt-4o-mini")


# ── 4. TOOLS ──────────────────────────────────────────────

# Web Search Tool
web_search = TavilySearchResults(max_results=5)


# RAG Retriever Tool (factory)
def make_retrieval_tool(texts: List[str], name: str, description: str):
    from langchain_core.documents import Document

    docs = [Document(page_content=t) for t in texts]

    splits = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    ).split_documents(docs)

    vector_store = FAISS.from_documents(splits, OpenAIEmbeddings())
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    @tool
    def retrieve(query: str) -> str:
        results = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in results])

    retrieve.name = name
    retrieve.description = description

    return retrieve


# Internal Knowledge Base
internal_knowledge = make_retrieval_tool(
    texts=[
        "The company's remote work policy allows employees to work from home up to 3 days per week.",
        "Performance review cycles occur twice per year — June and December.",
        "Sensitive data must be encrypted and access requires MFA.",
        "Travel expenses above $500 require VP approval.",
        "System architecture is microservices on AWS with Kafka."
    ],
    name="Internal_Knowledge_Base",
    description="Company policies and internal information"
)


# Calculation Tools
@tool
def calculate(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def percentage_change(old_value: float, new_value: float) -> str:
    if old_value == 0:
        return "Cannot calculate from zero."
    change = ((new_value - old_value) / old_value) * 100
    return f"{abs(change):.2f}% {'increase' if change > 0 else 'decrease'}"


# ── 5. AGENTS ─────────────────────────────────────────────

research_agent = create_react_agent(
    llm,
    tools=[web_search, internal_knowledge],
    prompt="You retrieve facts only. No calculations or summaries.",
    name="research_agent"
)

analysis_agent = create_react_agent(
    llm,
    tools=[calculate, percentage_change],
    prompt="You perform calculations only. No retrieval.",
    name="analysis_agent"
)

summary_agent = create_react_agent(
    llm,
    tools=[],
    prompt="You summarise and format responses only.",
    name="summary_agent"
)


# ── 6. SUPERVISOR ─────────────────────────────────────────

supervisor = create_supervisor(
    model=llm,
    agents=[research_agent, analysis_agent, summary_agent],
    prompt=(
        "Route tasks to the correct agent:\n"
        "- research_agent for retrieval\n"
        "- analysis_agent for calculations\n"
        "- summary_agent for writing\n"
        "Assign one agent at a time."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history"
).compile()


# ── 7. RUN FUNCTION ───────────────────────────────────────

def ask(query: str):
    result = supervisor.invoke({
        "messages": [HumanMessage(content=query)]
    })

    print("\n--- FINAL ANSWER ---\n")
    print(result["messages"][-1].content)
    print("\n--------------------\n")


# ── 8. TEST ───────────────────────────────────────────────

if __name__ == "__main__":
    ask("What is the company's travel policy?")
    ask("If cost reduced from 250000 to 190000, what is percentage saving?")
    ask(
        "Explain travel policy, calculate excess for $750, "
        "and summarise in 2 bullet points."
    )
