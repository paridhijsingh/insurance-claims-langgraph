"""
Module: mock_tools.py
System: Multi-Agent Insurance Claims Resolution Framework
Component: Step 2 - Decoupled Asynchronous Tool Integration Registry

Description:
    This module implements the mock service layer requested by the system boundaries.
    To ensure architectural parity across all four target frameworks (LangGraph, OpenAI,
    Anthropic, and Google ADK), all core utilities are exposed as stateless, asynchronous 
    Python callables, decoupled from framework-specific wrappers.

Mandatory Specs Satisfied (WhiteboxHub README):
    - Policy Lookup API (GET /policy/{customer_id})
    - Fraud Check API (POST /fraud/check)
    - OCR Processing Tool
"""

import asyncio
import random

# =====================================================================
# 1. POLICY LOOKUP API (WhiteboxHub Spec: Mandatory Tools #1)
# =====================================================================
async def policy_lookup_api(customer_id: str) -> dict:
    """
    Simulates: GET /policy/{customer_id}
    Retrieves internal database contract records to verify policy terms.
    """
    print(f"   [Tool Run] 🔍 Querying Policy Database for Client: {customer_id}...")
    await asyncio.sleep(0.4)  # Simulate non-blocking I/O network latency
    
    # Internal Database Mock Contents
    mock_policy_database = {
        "CUS-921": {
            "policy_active": True, 
            "coverage_limit": 10000.0, 
            "deductible": 500.0, 
            "policy_type": "Auto"
        },
        "CUS-101": {
            "policy_active": True, 
            "coverage_limit": 3500.0, 
            "deductible": 250.0, 
            "policy_type": "Health"
        },
        "CUS-000": {
            "policy_active": False, 
            "coverage_limit": 0.0, 
            "deductible": 0.0, 
            "policy_type": "None"
        }
    }
    
    # Return matched database record, fallback cleanly to default inactive configuration
    return mock_policy_database.get(
        customer_id, 
        {"policy_active": False, "coverage_limit": 0.0, "deductible": 0.0, "policy_type": "Unknown"}
    )


# =====================================================================
# 2. FRAUD CHECK API (WhiteboxHub Spec: Mandatory Tools #2)
# =====================================================================
async def fraud_check_api(customer_id: str, estimated_damage: float) -> dict:
    """
    Simulates: POST /fraud/check
    Evaluates historical telemetry metrics against fraud indicators.
    """
    print(f"   [Tool Run] 🛡️ Evaluating Fraud Signal Matrices for Client: {customer_id}...")
    await asyncio.sleep(0.6)
    
    # Deterministic evaluation boundaries to test downstream routing edges easily
    if customer_id == "CUS-000":
        return {"risk_score": 0.95, "signals": ["high_claim_frequency", "flagged_identity"]}
    elif estimated_damage > 12000.0:
        return {"risk_score": 0.78, "signals": ["exceeds_average_payout_threshold"]}
    
    return {"risk_score": 0.12, "signals": []}


# =====================================================================
# 3. OCR EXTRACTION TOOL WITH RETRY FLAGS (WhiteboxHub Spec: Mandatory Tools #3)
# =====================================================================
async def ocr_extraction_tool(document_name: str) -> dict:
    """
    Simulates extracting raw text elements from an uploaded binary attachment.
    Includes an intentional failure vector to test graph fallback logic loops!
    """
    print(f"   [Tool Run] 📄 Scanning unstructured file elements via OCR: {document_name}...")
    await asyncio.sleep(0.5)
    
    # The assignment requires building a 3-pass OCR retry loop.
    # We code an artificial 30% failure rate to ensure our loops actually activate during testing!
    if random.random() < 0.30:
        return {"text": "", "confidence": 0.35, "error": "Low visibility/Blurry text capture failure."}
        
    return {
        "text": "Invoice itemized repair breakdown details. Total parts costs: $4800.50. Verified by field operator.",
        "confidence": 0.98,
        "error": None
    }


# =====================================================================
# STANDALONE ASYNC LIFECYCLE RUNNER
# =====================================================================
if __name__ == "__main__":
    async def main():
        print("==========================================================")
        print("⚙️ TESTING STEP 2: ASYNC EXTERNAL MOCK TOOL INTEGRATIONS ⚙️")
        print("==========================================================\n")
        
        print("--- Run A: Standard Active Customer Check ---")
        policy_res = await policy_lookup_api("CUS-921")
        print(f"✅ Policy API Response Dictionary: {policy_res}\n")
        
        print("--- Run B: Evaluating Risk Flags ---")
        fraud_res = await fraud_check_api("CUS-921", 4800.50)
        print(f"✅ Fraud API Response Dictionary: {fraud_res}\n")
        
        print("--- Run C: OCR Execution Check ---")
        ocr_res = await ocr_extraction_tool("repair_invoice.pdf")
        print(f"✅ OCR Tool Response Dictionary: {ocr_res}\n")

    # Native Python Async entry runtime context
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())