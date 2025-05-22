from textual.app import App
from textual.widgets import Footer
from textual.containers import Container
from textual_pyfiglet.figletwidget import FigletWidget


class TextualApp(App[None]):

    DEFAULT_CSS = """
    #my_container { align: center middle; }
    """

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


TextualApp().run()
