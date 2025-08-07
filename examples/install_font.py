from textual.app import App
from textual.widgets import Footer
from textual.containers import Container
from textual_pyfiglet.figletwidget import FigletWidget

class TextualApp(App[None]):

    DEFAULT_CSS = """
    #my_container { align: center middle; }
    """

    # FigletWidget.install_font("examples/smblock.tlf")

    def compose(self):

        with Container(id="my_container"):
            self.figlet_widget = FigletWidget("sample", font_path="examples/smblock.tlf")

            # After install the font, it could be used directly by name for other widgets:
            # self.figlet_widget = FigletWidget("sample", font="smblock") # type: ignore
            yield self.figlet_widget

        yield Footer()

TextualApp().run()
