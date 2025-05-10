from __future__ import annotations
from typing import get_args
import click

# from textual_pyfiglet.pyfiglet.fonts import ALL_FONTS


font_help = "Specify the font to use. Use 'list' to see available fonts."
color_help = "Set two colors to create a gradient."
animate_help = "Animate the text. Requires --color1 and --color2 to be set."
quality_help = (
    "Set the gradient quality (1-100). Default is auto, which will set it to the height of the figlet."
)
speed_help = "Set the animation speed (in seconds). Default is 0.08 seconds."
dir_help = "Set the gradient direction. Can be vertical or horizontal. Default is vertical."


@click.command(context_settings={"ignore_unknown_options": False})
@click.argument("text", type=str, default=None, required=False)
@click.option("--font", "-f", type=str, default=None, help=font_help)
@click.option("--color1", type=str, default=None, help=color_help)
@click.option("--color2", type=str, default=None, help=color_help)
@click.option("--animate", "-a", is_flag=True, default=False, help=animate_help)
@click.option("--quality", "-q", type=int, default=None, help=quality_help)
@click.option("--speed", "-s", type=float, default=0.10, help=speed_help)
@click.option("--gradient_dir", "-dir", type=str, default="vertical", help=dir_help)
@click.option("--list", is_flag=True, default=False, help="List available fonts.")
def cli(
    text: str | None,
    font: str | None,
    color1: str | None,
    color2: str | None,
    animate: bool,
    quality: int | None,
    speed: float,
    gradient_dir: str,
    list: bool,
) -> None:
    """Textual-PyFiglet CLI.

    If no main argument is provided, the demo app will be launched.
    If a main argument is provided (text), it will be processed in CLI mode.
    """
    # If no main argument is provided, run the Textual UI
    if text is None:
        if list:
            from textual_pyfiglet.pyfiglet.fonts import ALL_FONTS

            click.echo("Available fonts:")
            for fontfoo in get_args(ALL_FONTS):
                click.echo(f"- {fontfoo}")
            return
        else:
            from textual_pyfiglet.demo import TextualPyFigletDemo

        TextualPyFigletDemo().run()
    # Providing a main argument will run the RichFiglet class in CLI mode.
    else:
        from textual_pyfiglet.rich_figlet import RichFiglet

        rich_figlet = RichFiglet(
            "Rich is awesome",
            font=font,
        )


def main() -> None:
    """Entry point for the application."""
    cli()


if __name__ == "__main__":
    main()
