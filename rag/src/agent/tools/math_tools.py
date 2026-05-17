import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from langchain_core.tools import StructuredTool

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="sympy")


def _sympy_evaluate(expression: str) -> str:
    try:
        import sympy as sp

        parsed = sp.sympify(expression, evaluate=True)
        simplified = sp.simplify(parsed)
        return str(simplified)
    except Exception as exc:
        return f"SymPy error: {exc}"


async def sympy_compute(expression: str, timeout: float = 5.0) -> str:
    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(_executor, _sympy_evaluate, expression),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return f"Computation timed out after {timeout:.0f}s"


def make_sympy_tool(timeout: float = 5.0) -> StructuredTool:
    async def _compute(expression: str) -> str:
        return await sympy_compute(expression, timeout=timeout)

    return StructuredTool.from_function(
        coroutine=_compute,
        name="sympy_compute",
        description="Evaluate or simplify a mathematical expression using SymPy symbolic computation.",
    )
