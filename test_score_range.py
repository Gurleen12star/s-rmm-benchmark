from s_rmm_logic import SRMMEnv
from models import Action

def test_rewards():
    env = SRMMEnv(seed=42)
    obs = env.reset()
    
    # Test a successful action (should be near 1.0 but not 1.0)
    action = Action(
        call_type="DB_ATOMIC_SYNC",
        target_silo="Identity",
        reasoning_hash="Validating the sync logic for profile data.",
        trace_id="test-123"
    )
    obs, reward, done, info = env.step(action)
    print(f"Task: data_alignment_easy | Success Reward: {reward}")
    assert 0.0 < reward < 1.0
    
    # Test a failing action (should be near 0.0 but not 0.0)
    env.reset()
    action = Action(
        call_type="DB_ATOMIC_SYNC",
        target_silo="Identity",
        reasoning_hash="shrt", # Too short
        trace_id="test-456"
    )
    obs, reward, done, info = env.step(action)
    print(f"Task: data_alignment_easy | Failure Reward: {reward}")
    assert 0.0 < reward < 1.0
    
    print("Verification successful: All rewards are strictly within (0, 1).")

if __name__ == "__main__":
    test_rewards()
