from pathlib import Path

from fastapi import HTTPException, status

from rag.src.agent.types import AgentType

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

_PROMPT_FILES: dict[AgentType, str] = {
    AgentType.GENERAL: "base_prompt.md",
    AgentType.RESEARCHER: "researcher_prompt.md",
    AgentType.MATH: "math_prompt.md",
    AgentType.PROGRAMMING: "programming_prompt.md",
    AgentType.INVOICE: "invoice_prompt.md",
    AgentType.ROUTER: "router_prompt.md",
}


class PromptService:
    @staticmethod
    def get(agent_type: AgentType) -> str:
        filename = _PROMPT_FILES.get(agent_type)
        if not filename:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PROMPT_NOT_FOUND")
        path = _PROMPTS_DIR / filename
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PROMPT_FILE_NOT_FOUND")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def get_all() -> dict[AgentType, str]:
        return {agent_type: PromptService.get(agent_type) for agent_type in _PROMPT_FILES}
