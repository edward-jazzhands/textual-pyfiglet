from textual.app import App
from textual.widgets import Footer
from textual.containers import Container
from textual_pyfiglet.figletwidget import FigletWidget
from random import choice

class TextualApp(App[None]):

    DEFAULT_CSS = """
    #my_container { align: center middle; }
    """

    words = [
        "Hello, World!",
        "Textual PyFiglet",
        "Sample Text",
        "Textual is awesome",
        "I love Python",
    ]

    def compose(self):

        with Container(id="my_container"):
            self.figlet_widget = FigletWidget(
                "sample",
                font="dos_rebel",
                justify="center",
                colors=["$primary", "$panel"],
                animate=True,
                # gradient_quality=50,
                # fps=4,
            )
            yield self.figlet_widget

        yield Footer()

    def on_resize(self) -> None:
        """Handle the resize event."""
        self.figlet_widget.refresh_size()

    def on_mount(self) -> None:
        """Handle the mount event."""
        self.set_interval(3, self.change_text)

    def change_text(self) -> None:
        """Change the text of the Figlet widget.""" 
        new_text = choice(self.words)
        self.figlet_widget.update(new_text)

TextualApp().run()
