"""
Module: agent_graph.py
System: AI Insurance Claims Resolution Framework
Component: Step 3 - LangGraph Compiled State Machine Network

Description:
    Implements an explicit state-graph network mapping out the claims pipeline.
    Replaces conversational while loops with discrete executing Nodes, explicit Edges, 
    and conditional state-routing logic.
"""

import json
from typing import Dict, Any, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

from schemas import ClaimSubmission
from mock_tools import policy_lookup_api, fraud_check_api, ocr_extraction_tool

# =====================================================================
# 1. DEFINE THE GRAPH STATE DEFINITION
# =====================================================================
class GraphState(TypedDict):
    """
    Represents the central memory packet moving through our network nodes.
    Each node receives this state, reads data, and returns updates.
    """
    claim_id: str
    customer_id: str
    estimated_damage: float
    documents: list
    is_policy_active: bool
    coverage_limit: float
    deductible: float
    ocr_extracted_text: str
    document_authenticity_score: float
    fraud_score: float
    fraud_signals: list
    retry_counts: dict
    final_decision: str
    decision_reasoning: str

# =====================================================================
# 2. IMPLEMENT THE EXECUTING GRAPH NODES
# =====================================================================

async def intake_node(state: GraphState) -> Dict[str, Any]:
    print("\n📥 [Node: Intake] Parsing incoming claim data structure...")
    # Extract structural baseline variables from state dictionary
    return {
        "claim_id": state.get("claim_id"),
        "customer_id": state.get("customer_id"),
        "estimated_damage": state.get("estimated_damage"),
        "documents": state.get("documents", []),
        "retry_counts": {"ocr": 0},
        "final_decision": "pending"
    }

async def verify_policy_node(state: GraphState) -> Dict[str, Any]:
    print("🔍 [Node: Policy Verification] Querying core contract databases...")
    cust_id = state.get("customer_id")
    
    # Trigger our asynchronous tool primitive directly
    tool_result = await policy_lookup_api(customer_id=cust_id)
    
    return {
        "is_policy_active": tool_result.get("policy_active", False),
        "coverage_limit": tool_result.get("coverage_limit", 0.0),
        "deductible": tool_result.get("deductible", 0.0)
    }

async def process_ocr_node(state: GraphState) -> Dict[str, Any]:
    print("📄 [Node: OCR Extraction] Processing attached raw invoice items...")
    docs = state.get("documents", [])
    target_doc = docs[0] if docs else "unknown.pdf"
    current_retries = state.get("retry_counts", {}).get("ocr", 0)
    
    tool_result = await ocr_extraction_tool(document_name=target_doc)
    
    if tool_result.get("error") is not None:
        new_retry_count = current_retries + 1
        print(f"   ⚠️ [OCR Node Error Intercepted] Attempt {new_retry_count}/3 failed.")
        return {
            "retry_counts": {"ocr": new_retry_count},
            "ocr_extracted_text": "",
            "document_authenticity_score": tool_result.get("confidence", 0.0)
        }
    
    return {
        "ocr_extracted_text": tool_result.get("text", ""),
        "document_authenticity_score": tool_result.get("confidence", 1.0)
    }

async def assess_fraud_node(state: GraphState) -> Dict[str, Any]:
    print("🛡️ [Node: Fraud Assessment] Evaluating risk pattern matrices...")
    cust_id = state.get("customer_id")
    damage = state.get("estimated_damage", 0.0)
    
    tool_result = await fraud_check_api(customer_id=cust_id, estimated_damage=damage)
    
    return {
        "fraud_score": tool_result.get("risk_score", 0.0),
        "fraud_signals": tool_result.get("signals", [])
    }

async def finalize_resolution_node(state: GraphState) -> Dict[str, Any]:
    print("📝 [Node: Finalize Resolution] Compiling graph network state outcomes...")
    
    is_active = state.get("is_policy_active", False)
    fraud = state.get("fraud_score", 0.0)
    
    if not is_active:
        reasoning = "Claim rejected: Customer policy is inactive or expired."
        decision = "rejected"
    elif fraud > 0.5:
        reasoning = f"Claim flagged: Elevated risk profile detected (Score: {fraud})."
        decision = "rejected"
    else:
        reasoning = "Claim approved: Policy active, clear telemetry, minimal risk bounds."
        decision = "approved"
        
    print(f"\n📊 Graph Output Summary:\n   Decision: {decision.upper()}\n   Reasoning: {reasoning}\n")
    return {"final_decision": decision, "decision_reasoning": reasoning}

# =====================================================================
# 3. DEFINE ROUTING EDGES (CONDITIONAL ROUTERS)
# =====================================================================

def ocr_error_router(state: GraphState) -> Literal["assess_fraud", "process_ocr", "finalize_resolution"]:
    """Evaluates state errors and determines if the network loops or halts."""
    retries = state.get("retry_counts", {}).get("ocr", 0)
    text = state.get("ocr_extracted_text", "")
    
    if not text and retries < 3:
        print("   🔄 Loop Triggered: Re-routing execution path back into OCR node...")
        return "process_ocr"
    elif not text and retries >= 3:
        print("   ❌ Max Fault Threshold Breached: Routing instantly to finalization for escalation.")
        return "finalize_resolution"
    
    print("   ✅ Document Clear: Proceeding down network to risk analysis phase.")
    return "assess_fraud"

# =====================================================================
# 4. COMPILE THE WORKFLOW GRAPH
# =====================================================================

# Initialize the StateGraph architecture blueprint with our State type
workflow = StateGraph(GraphState)

# Register our executing functions as Nodes
workflow.add_node("intake", intake_node)
workflow.add_node("verify_policy", verify_policy_node)
workflow.add_node("process_ocr", process_ocr_node)
workflow.add_node("assess_fraud", assess_fraud_node)
workflow.add_node("finalize_resolution", finalize_resolution_node)

# Map the fixed structural pathways (Edges)
workflow.add_edge(START, "intake")
workflow.add_edge("intake", "verify_policy")
workflow.add_edge("verify_policy", "process_ocr")

# Inject our dynamic Conditional Routing Edge right after the OCR phase
workflow.add_conditional_edges(
    "process_ocr",
    ocr_error_router,
    {
        "process_ocr": "process_ocr",            # Loop path
        "assess_fraud": "assess_fraud",          # Happy path
        "finalize_resolution": "finalize_resolution" # Escalation path
    }
)

# Connect remaining trailing execution elements
workflow.add_edge("assess_fraud", "finalize_resolution")
workflow.add_edge("finalize_resolution", END)

# Compile the workflow blueprint into an active runtime executable
app = workflow.compile()

# =====================================================================
# LOCAL EXECUTIVE APPLICATION EXECUTER
# =====================================================================
if __name__ == "__main__":
    import asyncio
    
    sample_input_claim = {
        "claim_id": "CLM-9009",
        "customer_id": "CUS-921",
        "estimated_damage": 4800.50,
        "documents": ["repair_invoice.pdf"]
    }
    
    async def main():
        print("==========================================================")
        print("🕸️ RUNNING STATE-GRAPH NETWORK VIA LANGGRAPH RUNTIME      🕸️")
        print("==========================================================")
        await app.ainvoke(sample_input_claim)
        print("==========================================================")
        print("✅ LANGGRAPH STATE ROUTING SYSTEM EXECUTION COMPLETE      ✅")
        print("==========================================================")

    asyncio.run(main())