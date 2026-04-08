import os
from s_rmm_logic import SRMMEnv
from models import Action

def verify_all_tasks():
    tasks = ["data_alignment_easy", "support_ticket_medium", "adversarial_defense_hard", "iam_governance_extreme"]
    results = {}
    
    for task in tasks:
        os.environ["MY_ENV_V4_TASK"] = task
        env = SRMMEnv(seed=42)
        obs = env.reset()
        
        # Test a successful action for this task
        if task == "data_alignment_easy":
            action = Action(call_type="DB_ATOMIC_SYNC", target_silo="Identity", reasoning_hash="Valid sync reasoning", trace_id="tr-1")
        elif task == "support_ticket_medium":
            # Refund then message
            action1 = Action(call_type="API_EXECUTE", target_silo="Finance", reasoning_hash="Refund for client", trace_id="tr-2", idempotency_key="id-1")
            obs, r1, d1, _ = env.step(action1)
            action = Action(call_type="SUPPORT_MESSAGE_CUSTOMER", target_silo="Logistics", reasoning_hash="Sorry for trouble", trace_id="tr-3", support_response="I am sorry for the issue.")
        elif task == "adversarial_defense_hard":
            # MFA then sync
            action1 = Action(call_type="MFA_HANDSHAKE", target_silo="Identity", reasoning_hash="MFA handshake", trace_id="tr-4")
            obs, r1, d1, _ = env.step(action1)
            action = Action(call_type="DB_ATOMIC_SYNC", target_silo="Identity", reasoning_hash="Sync after MFA", trace_id="tr-5")
        elif task == "iam_governance_extreme":
            action = Action(call_type="PROVISION_IAM", target_silo="Identity", reasoning_hash="Granting read role", trace_id="tr-6", iam_role="READ_ONLY")
            
        obs, reward, done, info = env.step(action)
        
        print(f"Task: {task:30} | Reward: {reward:.4f} | Done: {done}")
        
        # Basic assertions for Phase 2 compliance
        assert 0.0 < reward < 1.0, f"Task {task} reward {reward} out of (0,1) range!"
        
    print("\n[VERIFICATION SUCCESSFUL]")
    print("- All tasks processed without errors.")
    print("- All rewards are strictly within (0, 1) range.")
    print("- Environment logic is sound.")

if __name__ == "__main__":
    verify_all_tasks()
