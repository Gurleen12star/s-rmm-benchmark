import os
import json
import re
from typing import List, Optional
from openai import OpenAI
from s_rmm_logic import SRMMEnv
from models import Action

def run_task(client:OpenAI,model_name:str,task_name:str)->None:
    os.environ["MY_ENV_V4_TASK"]=task_name
    env=SRMMEnv(seed=42)
    log_start(task_name, "autonomous_cloud_sre_v1", model_name)
    obs = env.reset()
    rewards = []
    steps_taken = 0
    for step_n in range(1, 9):
        sys_prompt = "You are a professional support agent. Respond with strictly valid JSON matching the schema."
        user_prompt = f"Task: {task_name}. Observation: {obs.payload}. Current Step: {step_n}."
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.0,
                max_tokens=200
            )
            raw_text = response.choices[0].message.content.strip()
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            json_str = match.group(0) if match else raw_text
            payload = json.loads(json_str)
            action_val = Action(**payload)
            action_str = action_val.call_type
        except Exception:
            action_val = Action(call_type="DENY_SIGNAL", target_silo="Finance", reasoning_hash="fallback", trace_id="err-101")
            action_str = "DENY_SIGNAL"
        
        obs, reward, done, _ = env.step(action_val)
        rewards.append(reward)
        steps_taken = step_n
        log_step(step_n, action_str, reward, done, None)
        
        if done:
            break
            
    score = sum(rewards) / len(rewards) if rewards else 0.5
    score = max(0.05, min(0.95, score))
    success = score >= 0.6
    log_end(success, steps_taken, score, rewards)

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.3f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.3f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def main():
    API_BASE_URL=os.getenv("API_BASE_URL","https://api.openai.com/v1")
    MODEL_NAME=os.getenv("MODEL_NAME","Qwen/Qwen2.5-72B-Instruct")
    HF_TOKEN=os.getenv("HF_TOKEN")
    client=OpenAI(base_url=API_BASE_URL,api_key=HF_TOKEN)
    env_target=os.getenv("MY_ENV_V4_TASK")
    if env_target:
        tasks=[env_target]
    else:
        tasks=["data_alignment_easy","support_ticket_medium","adversarial_defense_hard","iam_governance_extreme"]
    for task in tasks:
        run_task(client,MODEL_NAME,task)

if __name__=="__main__":
    main()
