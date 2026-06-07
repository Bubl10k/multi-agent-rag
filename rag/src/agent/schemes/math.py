from pydantic import BaseModel


class ParseProblemOutput(BaseModel):
    problem_type: str
    parsed_components: dict
    is_ambiguous: bool
    retry_count: int
    max_retries: int


class SolveOutput(BaseModel):
    solution_expr: str
    solution_numeric: float | None = None


class VerifyOutput(BaseModel):
    verification_passed: bool
    retry_count: int


class ExplainOutput(BaseModel):
    explanation: str
