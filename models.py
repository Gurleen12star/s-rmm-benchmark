from typing import List,Literal,Optional
from pydantic import BaseModel,Field

class Action(BaseModel):
    call_type:Literal["DB_ATOMIC_SYNC","MFA_HANDSHAKE","API_EXECUTE","DENY_SIGNAL","PROVISION_IAM","SUPPORT_MESSAGE_CUSTOMER"]
    target_silo:str=Field(...,description="Finance, Identity, or Logistics")
    reasoning_hash:str=Field(...,description="Mandatory audit trail for the Mentor")
    idempotency_key:Optional[str]=Field(default=None,description="Prevents double-charging during API falls")
    trace_id:Optional[str]=Field(default=None,description="Correlation ID for telemetry tagging")
    iam_role:Optional[Literal["READ_ONLY","ADMIN_WRITE"]]=Field(default=None,description="IAM Provisioning Governance")
    support_response:Optional[str]=Field(default=None,description="Response content for CS interactions")

class Observation(BaseModel):
    payload:str
    system_latency:float
    active_constraints:List[str]
    circuit_status:Literal["CLOSED","OPEN_BREACH"]
    integrity_status:bool
    customer_frustration:int
    server_trace_id:str

class Reward(BaseModel):
    value:float=Field(...,description="Normalized step score (0.0 to 1.0)")
