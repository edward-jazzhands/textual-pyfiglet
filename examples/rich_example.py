from textual_pyfiglet.rich_figlet import RichFiglet

from rich.console import Console

console = Console()

console.print(
    RichFiglet(
        "Rich is awesome",
        font="ansi_shadow",
        color1="#ff0000",
        color2="#0000ff",
        animate=True,
        gradient_dir="vertical",
        # speed=0.05,
    )
)
