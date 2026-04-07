from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from pydantic import BaseModel
from models import Action,Observation
from s_rmm_logic import SRMMEnv

app=FastAPI(title="S-RMM Benchmark API")
env_instance=SRMMEnv()

class StepPayload(BaseModel):
    action:Action

@app.get("/")
def read_root():
    html_content="""
    <html>
        <head>
            <title>S-RMM: Cloud SRE Sandbox</title>
            <style>
                body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; padding: 50px; }
                h1 { color: #58a6ff; }
                .panel { background-color: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin-top:20px; }
                .status { color: #3fb950; font-weight: bold; }
                .metric { color: #d2a8ff; }
            </style>
        </head>
        <body>
            <h1>S-RMM: Autonomous Cloud Governance</h1>
            <p>Deterministic OpenEnv Benchmark for Atomic State Management</p>
            <div class="panel">
                <h3>[ SYSTEM TELEMETRY ]</h3>
                <p>Environment Status: <span class="status">ACTIVE & HEALTHY</span></p>
                <p>Circuit Breakers: <span class="status">READY</span></p>
                <p>Atomic Rollback Engine: <span class="status">ARMED</span></p>
            </div>
            <div class="panel">
                <h3>[ LIVE STATE ]</h3>
                <p>Identity Shard: <span class="metric">Encrypted</span></p>
                <p>Finance Shard: <span class="metric">Idempotent</span></p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content,status_code=200)

@app.get("/health")
def health():
    return {"status":"healthy"}

@app.get("/state")
def state():
    return env_instance.state()

@app.post("/reset")
def reset():
    return env_instance.reset()

@app.post("/step")
def step(payload:StepPayload):
    obs,reward,done,info=env_instance.step(payload.action)
    return {"observation":obs,"reward":reward,"done":done,"info":info}

@app.websocket("/ws")
async def ws_endpoint(websocket:WebSocket):
    await websocket.accept()
    env=SRMMEnv()
    try:
        while True:
            data=await websocket.receive_json()
            command_type=data.get("type")
            if command_type=="reset":
                obs=env.reset()
                await websocket.send_json({"type":"reset_result","observation":obs.model_dump()})
            elif command_type=="step":
                action=Action(**data["action"])
                obs,reward,done,info=env.step(action)
                await websocket.send_json({"type":"step_result","observation":obs.model_dump(),"reward":reward,"done":done,"info":info})
            elif command_type=="state":
                await websocket.send_json({"type":"state_result","state":env.state()})
    except WebSocketDisconnect:
        pass

def main():
    uvicorn.run(app,host="0.0.0.0",port=7860)

if __name__=="__main__":
    main()
