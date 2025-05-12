from textual_pyfiglet.rich_figlet import RichFiglet

from rich.console import Console


rich_fig = RichFiglet(
    "Rich is awesome",
    font="pagga_lite",
    colors=["#ff0000", "bright_blue"],
    gradient_dir="none",
    border="HEAVY",
    border_padding=(1, 2),
    border_color="red",
    animate=True,
    # quality=30,
    # speed=0.2,
    # dev_mode=True,
)

console = Console()
console.print(rich_fig)
