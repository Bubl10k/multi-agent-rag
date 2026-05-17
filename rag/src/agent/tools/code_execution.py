import asyncio
import os
import sys
import tempfile
from dataclasses import dataclass

_DEFAULT_ALLOWED = ["math", "json", "re", "itertools", "datetime"]

# Modules that the sandbox wrapper itself needs — always permitted
_ALWAYS_ALLOWED = {"builtins", "sys", "_io", "io", "abc", "types", "typing", "codecs", "encodings"}

_WRAPPER_TEMPLATE = """\
import sys
import builtins

_allowed = {allowed!r}
_builtin_import = builtins.__import__


def _restricted_import(name, *args, **kwargs):
    base = name.split(".")[0]
    if base not in _allowed:
        raise ImportError(f"import of '{{name}}' is not allowed in this sandbox")
    return _builtin_import(name, *args, **kwargs)


builtins.__import__ = _restricted_import

{code}
"""


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int


async def execute_in_sandbox(
    code: str,
    timeout: float = 10.0,
    allowed_modules: list[str] | None = None,
) -> ExecutionResult:
    permitted = _ALWAYS_ALLOWED | set(allowed_modules or _DEFAULT_ALLOWED)
    wrapped = _WRAPPER_TEMPLATE.format(allowed=sorted(permitted), code=code)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(wrapped)
        tmp_path = f.name

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            tmp_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return ExecutionResult(
                stdout="",
                stderr=f"Execution timed out after {timeout:.0f}s",
                exit_code=1,
            )

        return ExecutionResult(
            stdout=stdout_b.decode(errors="replace"),
            stderr=stderr_b.decode(errors="replace"),
            exit_code=proc.returncode,
        )
    finally:
        os.unlink(tmp_path)
