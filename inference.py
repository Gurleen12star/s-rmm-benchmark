"""
Support-Recursive-Mentor-Meta (S-RMM) Inference Loop.
Provides the entrypoint for automated agentic evaluation.
"""
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
        sys_prompt="You are a Tier-3 Support agent. Respond with strictly valid JSON matching this schema: {'call_type': 'DB_ATOMIC_SYNC'|'MFA_HANDSHAKE'|'API_EXECUTE'|'DENY_SIGNAL'|'PROVISION_IAM'|'SUPPORT_MESSAGE_CUSTOMER', 'target_silo': 'Identity'|'Finance'|'Logistics', 'reasoning_hash': 'your reasoning here (>10 chars)', 'idempotency_key': 'string or null', 'trace_id': 'req-123', 'iam_role': 'READ_ONLY'|'ADMIN_WRITE'|null, 'support_response': 'message to customer'|null}. Do NOT wrap in markdown."
        user_prompt=f"Task: {task_name}. Observation: {obs.payload}. Active Constraints: {obs.active_constraints}. Chat Frustration: {getattr(obs,'customer_frustration',0)}/10. Current Step: {step_n}. Produce the next Action JSON."
        try:
            response=client.chat.completions.create(model=model_name,messages=[{"role":"system","content":sys_prompt},{"role":"user","content":user_prompt}],temperature=0.0,max_tokens=200)
            raw_text=response.choices[0].message.content.strip()
            match=re.search(r'\{.*\}',raw_text,re.DOTALL)
            json_str=match.group(0) if match else raw_text
            payload=json.loads(json_str)
            action_val=Action(**payload)
        except Exception as e:
            err_str=str(e).replace('\n',' ').replace('\r','')
            action_val=Action(call_type="DENY_SIGNAL",target_silo="Finance",reasoning_hash=f"fallback due to api error: {err_str[:40]}",trace_id="err-101")
        obs,reward,done,_=env.step(action_val)
        rewards.append(reward)
        done_str=str(done).lower()
        reasoning=action_val.reasoning_hash
        call=action_val.call_type
        print(f"[STEP] step={step_n} action={call} reward={reward:.2f} done={done_str} error=null reasoning_hash={reasoning}",flush=True)
        if done:
            break
    score=sum(rewards)/len(rewards) if rewards else 0.0
    score=max(0.0,min(1.0,score))
    success_str=str(score>0.0).lower()
    rewards_str=",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={success_str} steps={step_n} score={score:.3f} rewards={rewards_str}",flush=True)

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
