from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from agent.agent import QuadtonAgent


console = Console()


def main() -> None:
    """Run the Quadton Coding Agent CLI."""

    console.print(
        "[bold cyan]Quadton Coding Agent[/bold cyan]"
    )
    console.print(
        "Type your task and press Enter."
    )
    console.print(
        "Type [bold]exit[/bold] to quit.\n"
    )

    agent = QuadtonAgent()

    while True:
        try:
            prompt = Prompt.ask(
                "[bold cyan]You[/bold cyan]"
            )

        except (KeyboardInterrupt, EOFError):
            console.print(
                "\n[dim]Goodbye.[/dim]"
            )
            break

        if not prompt.strip():
            continue

        if prompt.lower() in {
            "exit",
            "quit",
            "q",
        }:
            console.print(
                "[dim]Goodbye.[/dim]"
            )
            break

        try:
            response = agent.run(prompt)

            content = (
                response
                .get("message", {})
                .get("content")
                or ""
            )

            if content:
                console.print()
                console.print(
                    Markdown(content)
                )
                console.print()

        except Exception as exc:
            console.print(
                f"[bold red]Error:[/bold red] {exc}"
            )


if __name__ == "__main__":
    main()
