import os
import json
import re
from openai import OpenAI
from s_rmm_logic import SRMMEnv
from models import Action

def run_task(client:OpenAI,model_name:str,task_name:str)->None:
    os.environ["MY_ENV_V4_TASK"]=task_name
    env=SRMMEnv(seed=42)
    print(f"[START] task={task_name} env=s_rmm_benchmark model={model_name}",flush=True)
    obs=env.reset()
    rewards=[]
    for step_n in range(1,9):
        sys_prompt="You are a professional support agent. Respond with strictly valid JSON matching the schema."
        user_prompt=f"Task: {task_name}. Observation: {obs.payload}. Current Step: {step_n}."
        try:
            response=client.chat.completions.create(model=model_name,messages=[{"role":"system","content":sys_prompt},{"role":"user","content":user_prompt}],temperature=0.0,max_tokens=200)
            raw_text=response.choices[0].message.content.strip()
            match=re.search(r'\{.*\}',raw_text,re.DOTALL)
            json_str=match.group(0) if match else raw_text
            payload=json.loads(json_str)
            action_val=Action(**payload)
        except Exception:
            action_val=Action(call_type="DENY_SIGNAL",target_silo="Finance",reasoning_hash="fallback",trace_id="err-101")
        obs,reward,done,_=env.step(action_val)
        rewards.append(reward)
        print(f"[STEP] step={step_n} reward={reward:.4f} done={str(done).lower()}",flush=True)
        if done:
            break
    avg_reward=sum(rewards)/len(rewards) if rewards else 0.0
    success=avg_reward>0.5
    print(f"[END] success={str(success).lower()} steps={step_n} score={avg_reward:.4f}",flush=True)

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
