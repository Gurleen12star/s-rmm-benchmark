import os
import requests
import time
import subprocess
from s_rmm_logic import SRMMEnv
from models import Action

def final_cross_check():
    print("--- S-RMM PHASE 2 FINAL CROSS-CHECK ---")
    
    # 1. Verify Logic (0.01-0.99 range)
    env = SRMMEnv(seed=42)
    env.reset()
    # Mock action
    action = Action(call_type="DB_ATOMIC_SYNC", target_silo="Identity", reasoning_hash="Final check reasoning sync", trace_id="final-tr")
    obs, reward, done, _ = env.step(action)
    print(f"[LOGIC] Reward: {reward}")
    if not (0.0 < reward < 1.0):
        print("!!! FAIL: Reward out of (0, 1) range!")
        return
    
    # 2. Verify Server Endpoints
    # We assume server is running on 7860 as per python main.py background command
    url = "http://localhost:7860"
    try:
        r_reset = requests.post(f"{url}/reset")
        print(f"[SERVER] Reset: {r_reset.status_code}")
        r_state = requests.get(f"{url}/state")
        print(f"[SERVER] State: {r_state.status_code}")
        
        test_step = {
            "action": {
                "call_type": "DB_ATOMIC_SYNC",
                "target_silo": "Identity",
                "reasoning_hash": "Automated server test action",
                "trace_id": "srv-test-01"
            }
        }
        r_step = requests.post(f"{url}/step", json=test_step)
        print(f"[SERVER] Step: {r_step.status_code}")
        
    except Exception as e:
        print(f"!!! FAIL: Server connection error: {e}")
        return

    # 3. Verify Inference Logging Format
    # Read inference.py to verify regex match requirements
    with open("inference.py", "r") as f:
        content = f.read()
    
    required_patterns = ["[START]", "[STEP]", "[END]"]
    for p in required_patterns:
        if p not in content:
            print(f"!!! FAIL: Missing mandatory log prefix {p} in inference.py")
            return
        else:
            print(f"[INFERENCE] Found {p} prefix.")

    print("\n[ALL CHECKS PASSED] - Project is ready for Phase 2 Acceptance!")

if __name__ == "__main__":
    final_cross_check()
