from __future__ import annotations
import json
import os
import subprocess
from dataclasses import dataclass
import tempfile
from pathlib import Path
from time import time


@dataclass
class CodexRunResult:
    thread_id: str | None
    final_response: str


class CodexSDKClient:
    def __init__(self, repo_dir: str | Path, model: str = "gpt-5.6-sol"):
        from openai_codex import Codex, Sandbox  # deferred import
        self._Sandbox = Sandbox
        self.repo_dir = Path(repo_dir).resolve()
        self.model = model
        self._codex = Codex()
        self._thread = None
        self._prev_cwd = None

    def __enter__(self):
        self._prev_cwd = os.getcwd()
        os.chdir(self.repo_dir)
        self._codex.__enter__()
        return self

    def __exit__(self, *exc):
        self._codex.__exit__(*exc)
        if self._prev_cwd:
            os.chdir(self._prev_cwd)

    def _extract_id(self):
        return getattr(self._thread, "id", None) or getattr(self._thread, "thread_id", None)

    def start(self, prompt: str) -> CodexRunResult:
        self._thread = self._codex.thread_start(model=self.model, sandbox=self._Sandbox.workspace_write)
        result = self._thread.run(prompt)
        return CodexRunResult(self._extract_id(), result.final_response)

    def continue_with(self, prompt: str) -> CodexRunResult:
        if self._thread is None:
            raise RuntimeError("Call start() first.")
        result = self._thread.run(prompt)
        return CodexRunResult(self._extract_id(), result.final_response)

class CodexExecClient:
    def __init__(self, repo_dir: str | Path, model: str = "gpt-5.6-sol"):
        self.repo_dir = Path(repo_dir).resolve()
        self.model = model
        self._thread_id = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def _run_codex(self, prompt: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        try:
            cmd = f'echo "{prompt}" | codex --model {self.model} --no-sandbox'
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout + result.stderr
            return output
        except Exception as e:
            return f"Error running codex: {e}"
        finally:
            os.unlink(prompt_file)

    def start(self, prompt: str):
        response = self._run_codex(prompt)
        self._thread_id = f"cli-session-{int(time())}"
        return CodexRunResult(thread_id=self._thread_id, final_response=response)

    def continue_with(self, prompt: str):
        response = self._run_codex(prompt)
        return CodexRunResult(thread_id=self._thread_id, final_response=response)