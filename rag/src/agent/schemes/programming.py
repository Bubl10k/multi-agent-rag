from pydantic import BaseModel


class PlanOutput(BaseModel):
    plan: str
    retry_count: int
    max_retries: int


class WriteCodeOutput(BaseModel):
    code: str


class ExecuteOutput(BaseModel):
    stdout: str
    stderr: str
    exit_code: int


class ReviewOutput(BaseModel):
    plan: str
    retry_count: int


class FinalAnswerOutput(BaseModel):
    final_answer: str
