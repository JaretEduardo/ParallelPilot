from __future__ import annotations
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


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

