# Stateful AI Insurance Claims Router (LangGraph Framework)

An enterprise-grade orchestration pipeline that implements a highly structural state machine network using LangGraph. This architecture completely replaces standard text-history `while` loops with explicit executing Nodes, permanent highway Edges, and conditional state routing paths.

This project serves as **Step 3** of an end-to-end modular claims framework, proving that complex business logic loops and automated recovery systems can be hardcoded and verified deterministically.

## 🧠 The Architectural Shift: State Machine vs. Chat History

In traditional chat-completion event loops, execution tracking is completely implicit—relying on appending text frames to a growing list of messages and hoping the model calls tools accurately.

This repository moves the entire workload into a **State Machine Graph**:

- **Central Memory Packet (`GraphState`)**: A single centralized `TypedDict` object that moves through our network. Every node receives a snapshot of this state, processes data, and returns isolated dictionary updates that LangGraph automatically merges back into the master state.
- **Executing Nodes (The Workers)**: Standard asynchronous Python functions that isolate specialized operations (e.g., verifying database eligibility or running file OCR extraction).
- **Conditional Edges (The Router)**: Dedicated Python routing logic that inspects live state variables and physically maps data paths backward or forward across the network topology.

```text
               ┌───────────────────────────┐
               │         START Node        │
               └───────────────────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │        intake Node        │
               └───────────────────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │    verify_policy Node     │
               └───────────────────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │     process_ocr Node      │ <──────────────────────┐
               └───────────────────────────┘                        │
                             │                                      │
               [Invokes ocr_error_router]                           │
                 /           │           \                          │
       (Clear Text)   (Error & Retries < 3)  (Max Retries Exceeded)  │
           /                 │                 \                    │
          ▼                  ▼                  ▼                   │
┌──────────────────┐   [ Loop Path ]   ┌──────────────────────────┐ │
│assess_fraud Node │         └─────────►│ Re-route back to OCR... ├─┘
└──────────────────┘                   └──────────────────────────┘
          │                                         │
          ▼                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    finalize_resolution Node                     │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │          END Node         │
               └───────────────────────────┘
```
