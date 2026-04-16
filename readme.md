##  Problem This System Solves

In real enterprise environments, users rarely ask single-purpose questions.

A single query often combines multiple tasks that require different types of intelligence — such as information retrieval, numerical reasoning, and structured communication.

For example:

> "What is our company's approval policy for expenses over $500, and can you calculate how much over-budget this $750 travel claim is, and summarise both in a quick bullet point for my manager?"

This single request contains three different workloads:
- **Policy retrieval** → requires searching internal knowledge (RAG)
- **Calculation** → requires deterministic arithmetic reasoning
- **Summarisation** → requires structured natural language generation

---

## Why Single-Agent LLM Systems Fail

When handled by a single general-purpose LLM with multiple tools, two core issues appear:

**1. Tool confusion**
The model has access to retrieval, calculation, and writing capabilities, but no strict separation of responsibilities. This often leads to:
- incorrect tool selection  
- reasoning done in the wrong component  
- hallucinated or incomplete answers  

**2. Inconsistent output quality**
A single agent must simultaneously retrieve facts, compute values, and write responses. This leads to a trade-off where:
- retrieval accuracy drops
- calculations are less reliable
- final responses lack structure

---

## What This System Implements

This project introduces a **Supervisor-based Multi-Agent Architecture**

                    User Query (single or multi-task)
                ↓
      ┌──────────────────────┐
      │  Supervisor LLM      │
      │ - reads full query   │
      │ - decomposes tasks   │
      │ - routes agents      │
      └──────────────────────┘
        ↓         ↓          ↓
   Research   Analysis   Summary
    Agent       Agent      Agent
 (RAG + web)  (math tools) (LLM only)
        ↓         ↓          ↓
   ┌────────┐ ┌────────┐ ┌────────┐
   │Tavily  │ │calc()  │ │writing │
   │FAISS   │ │% change│ │format  │
   └────────┘ └────────┘ └────────┘
        ↓         ↓          ↓
   factual     numeric     structured
   output      output      response
        ↓         ↓          ↓
            Supervisor
        (aggregation layer)
                ↓
        Final structured answer
                

## Real-World Relevance

This architecture directly maps to enterprise workflows:

**Financial Services**
- Policy lookup + exposure calculation + executive summary

**Legal & Compliance**
- Regulation retrieval + deadline computation + compliance reporting

**Customer Operations**
- Contract lookup + penalty calculation + customer response generation

---

## Why a Supervisor-Based Design

A rule-based router breaks as complexity grows. Instead, this system uses an LLM-based supervisor that dynamically interprets the query and assigns tasks.

This makes the system:
- adaptable to unseen query types  
- extensible without code changes  
- more robust in real-world usage  

---

## One-Line Problem Statement

Enterprise queries often require retrieval, reasoning, and generation simultaneously. Single-agent systems struggle with this complexity, so this project introduces a supervisor-driven multi-agent architecture that delegates tasks to specialized agents for improved accuracy, structure, and reliability.
