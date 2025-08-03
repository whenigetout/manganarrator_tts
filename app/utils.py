from pathlib import Path
import time
from rich.console import Console

import traceback

def log_exception(context: str = "Unhandled exception", label: str = "💀"):
    print(f"\n{label} {context}:")
    traceback.print_exc()

def ensure_folder(path: Path):
    path.mkdir(parents=True, exist_ok=True)

class Timer:
    last_duration = 0.0

    def __init__(self, label: str = "", use_spinner: bool = True):
        self.label = label
        self.start_time = None
        self.use_spinner = use_spinner
        self.console = Console()
        self.status = None

    def __enter__(self):
        if self.use_spinner:
            self.status = self.console.status(
                f"[bold cyan]{self.label}...[/]",
                spinner="bouncingBar",
                spinner_style="bold green",
            )
            self.status.__enter__()

        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        Timer.last_duration = duration

        if self.use_spinner and self.status:
            self.status.__exit__(exc_type, exc_val, exc_tb)

        if self.label:
            self.console.print(
                f"✅ [green]{self.label}[/] done in [yellow]{duration:.2f}s[/]"
            )