import argparse

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from agent.core.engine import AgentEngine


console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="quadton-agent",
        description="Quadton Coding Agent",
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Run the agent with a single prompt.",
    )

    parser.add_argument(
        "--model",
        help="Override the configured OpenRouter model.",
    )

    return parser


def display_response(content: str) -> None:
    """Display an assistant response as Markdown."""

    if not content:
        return

    console.print(
        Markdown(content)
    )


def run_one_shot(model: str | None, prompt: str) -> None:
    """Run the agent once and exit."""

    try:
        engine = AgentEngine(model=model)
        response = engine.send_message(prompt)

        content = response["message"].get("content", "")
        display_response(content)

    except ValueError as exc:
        console.print(
            f"[bold red]Configuration error:[/bold red] {exc}"
        )

    except RuntimeError as exc:
        console.print(
            f"[bold red]Provider error:[/bold red] {exc}"
        )


def run_repl(model: str | None) -> None:
    """Run the interactive terminal REPL."""

    try:
        engine = AgentEngine(model=model)

    except ValueError as exc:
        console.print(
            f"[bold red]Configuration error:[/bold red] {exc}"
        )
        return

    console.print(
        Panel.fit(
            "[bold]Quadton Coding Agent[/bold]\n"
            f"Provider: {engine.provider.name}\n"
            f"Model: {engine.model}",
            border_style="blue",
        )
    )

    console.print(
        "Type [bold]/help[/bold] for commands or "
        "[bold]/exit[/bold] to quit.\n"
    )

    while True:
        try:
            prompt = Prompt.ask("[bold cyan]You[/bold]")

        except (KeyboardInterrupt, EOFError):
            console.print("\nGoodbye.")
            break

        prompt = prompt.strip()

        if not prompt:
            continue

        if prompt == "/exit":
            console.print("Goodbye.")
            break

        if prompt == "/help":
            show_help()
            continue

        if prompt == "/new":
            engine.clear_history()
            console.print("[green]Conversation cleared.[/green]")
            continue

        try:
            response = engine.send_message(prompt)

            content = response["message"].get("content", "")
            display_response(content)

        except RuntimeError as exc:
            console.print(
                f"[bold red]Provider error:[/bold red] {exc}"
            )

        except Exception as exc:
            console.print(
                f"[bold red]Unexpected error:[/bold red] {exc}"
            )


def show_help() -> None:
    """Display available commands."""

    console.print(
        Panel(
            "\n".join(
                [
                    "[bold]/help[/bold] — Show this help message",
                    "[bold]/new[/bold] — Start a new conversation",
                    "[bold]/exit[/bold] — Exit Quadton Coding Agent",
                ]
            ),
            title="Commands",
            border_style="blue",
        )
    )


def main() -> None:
    """CLI entry point."""

    parser = create_parser()
    args = parser.parse_args()

    if args.prompt:
        run_one_shot(args.model, args.prompt)
    else:
        run_repl(args.model)
