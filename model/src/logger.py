from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "bold red",
        "data": "magenta",
    }
)

console = Console(theme=custom_theme)


def log_info(msg: str) -> None:
    console.print(f"[info][INFO][/info] {msg}")


def log_success(msg: str) -> None:
    console.print(f"[success][DONE][/success] {msg}")


def log_warning(msg: str) -> None:
    console.print(f"[warning][WARN][/warning] {msg}")


def log_error(msg: str) -> None:
    console.print(f"[error][FAIL][/error] {msg}")
