"""Contains the demo app.
This module contains the demo application for PyFiglet using the Textual framework.
Classes:
    PyFigletDemo(App): A Textual application demonstrating the usage of PyFiglet with various fonts and text input.
Functions:
    get_all_fonts_list(package_path: str) -> list: Returns a list of all font filenames (without extensions) in the specified package path.
Usage:
    Run this module directly to start the PyFiglet demo application.
    Example: python -m textual-pyfiglet
Notes:
    - The application uses Rich for enhanced traceback formatting.
    - The application defines a default CSS for styling the layout and widgets.
    - The font list is dynamically generated from the specified directory.
    - The application includes a timer to set initial text in the TextArea to avoid glitches.
    - The application handles font changes and text input changes to update the FigletWidget accordingly."""

import os


from rich import traceback
traceback.install()


from textual.app import App, on
from textual.containers import Horizontal, Container, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, TextArea, Select, Switch, Label

# NOTE: There are HUNDREDS of fonts available for Figlet.
# The fonts included are just a small selection, to keep the library size down.
# Also note, you can simply download more and add them.
# Any FIGlet fonts you drop in the fonts folder will be automatically loaded by PyFiglet
# as well as this demo. The selection list in the demo will update automatically.


from .figletwidget import FigletWidget
from .pyfiglet import fonts


def get_all_fonts_list() -> list:
    """Scans the fonts folder.
    Returns a list of all font filenames (without extensions)."""

    # first get the path of the fonts package:
    package_path = os.path.dirname(fonts.__file__)
    path_list = os.listdir(package_path)
    fonts_list = []
    for filename in path_list:
        if not filename.endswith('.py') and not filename.startswith('__pycache__'):
            fonts_list.append(os.path.splitext(filename)[0])
    return fonts_list


class PyFigletDemo(App):


    DEFAULT_CSS = """
    #main_content {
        align: center middle;
        width: 1fr;
        height: 1fr;
    }

    #font_select {
        width: 22;
    }

    #options_bar {
        content-align: center middle;
        align: center middle;
        height: 4;
        padding: 0;
        background: $boost;
    }

    TextArea {
        height: auto
    }

    FigletWidget {
        background: $boost;
        padding: 1 4 0 4;
        content-align: center middle;
    }
    """

    fonts_list = get_all_fonts_list()
    fonts_list.sort()
    font_options =  [(font, font) for font in fonts_list]

    def compose(self):

        self.log.info("PyFiglet Demo started.")
        self.log.debug(f"Available fonts: {self.fonts_list}")

        yield Header("PyFiglet Demo")

        with VerticalScroll(id="main_content"):
            yield FigletWidget("Hello, World!", id="figlet", font="standard")
        with Horizontal(id="options_bar"):
            yield Select(options=self.font_options, value="standard", id="font_select", allow_blank=False)
            yield TextArea("", id="text_input")

        yield Footer()

    def on_mount(self):

        self.set_timer(0.05, self.set_starter_text)
        # The timer is because starting with text in the TextArea makes it glitch out.
        # Giving it a 50ms delay to set the text fixes the problem.

    # This just sets the cursor to the end of the text in the TextArea when the app starts:
    def set_starter_text(self):
        self.query_one("#text_input").text = "Hello, World!"
        self.query_one("#text_input").focus()
        end = self.query_one("#text_input").get_cursor_line_end_location()
        self.query_one("#text_input").move_cursor(end)
        # self.query_one("#options_bar").set_styles("height: auto;")

    def on_resize(self, event):
        width, height = event.size      # TODO This needs to be tested in different terminals and app environments
        self.query_one("#figlet").change_width(width-8)    # -8 to account for padding

    @on(Select.Changed, selector="#font_select")           
    def font_changed(self, event: Select.Changed) -> None:
        self.query_one("#figlet").change_font(event.value)

    @on(TextArea.Changed)
    async def text_changed(self):
        text = self.query_one("#text_input").text
        self.query_one("#figlet").update(text)  # Thats it! The FigletWidget will update the text for you.

        # This just scrolls the text area to the end when the text changes:
        scroll_area = self.query_one("#main_content")
        if scroll_area.scrollbars_enabled == (True, False):
            scroll_area.action_scroll_end()

# This is for the entry point script. You can run the demo with:
#$ textual-pyfiglet
def main():
    app = PyFigletDemo()
    app.run()
 
# TODO remove me when confirmed working everywhere
# This is another way to run the demo
#$ python -m textual-pyfiglet 
if __name__ == "__main__":
    app = PyFigletDemo()
    app.run()