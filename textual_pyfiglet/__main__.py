"""Contains the demo app.
This module contains the demo application for PyFiglet

Run this module directly to start the PyFiglet demo application.    
Either command works:   
- textual-pyfiglet
- python -m textual-pyfiglet

Note the font list is dynamically generated from the fonts folder.
If you also installed the extended fonts pack, you'll see it in the demo.

Also note that the first time it runs and detects the extended fonts pack,
it will copy the whole pack into the fonts folder (inside pyfiglet).
This might take about 2-3 seconds. It will only do this once.
"""

import os
from typing import cast

from rich import traceback
traceback.install()

from textual.app import App, on
from textual.events import Key
from textual.containers import Horizontal, Container, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, TextArea, Select, Switch, Label

from .figletwidget import FigletWidget
from .pyfiglet import fonts
from . import extended_fonts_installed

base_fonts = [
    'bigfig',
    'calvin_s',
    'chunky',
    'cybermedium',
    'small_slant',
    'small',
    'smblock',
    'smbraille',
    'standard',
    'stick_letters',
    'tmplr'
]

def get_all_fonts_list(show_all: bool = False) -> list:
    """Scans the fonts folder.
    Returns a list of all font filenames (without extensions)."""

    if not show_all:
        return base_fonts

    # first get the path of the fonts package:
    package_path = os.path.dirname(fonts.__file__)
    path_list = os.listdir(package_path)
    fonts_list = []

    for filename in path_list:
        if not filename.endswith('.py') and not filename.startswith('__pycache__'):
            fonts_list.append(os.path.splitext(filename)[0])
    return fonts_list


class PyFigletDemo(App):

    BINDINGS = [
        ("s", "focus_select", "Focus the font select"),
        ("t", "focus_text", "Focus the text input"),
        ("a", "toggle_fonts", "Toggle all fonts"),
    ]


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

    #switch_container {
        # margin: 0
        align: left middle; 
        width: 20;
    }

    #notification_box {
        padding: 0 0 0 23;
        content-align: left middle;
        height: 1;
        width: 1fr;
        dock: bottom;
    }

    TextArea {
        height: auto
    }

    FigletWidget {
        background: $boost;
        padding: 1 4 0 4;
        content-align: center middle;
    }

    Label {
        # padding: 1;
    }
    """

    fonts_list = get_all_fonts_list()
    fonts_list.sort()
    font_options =  [(font, font) for font in fonts_list]
    current_font = 'standard'


    def compose(self):

        self.log("PyFiglet Demo started.")
        self.log(f"Available fonts: {self.fonts_list}")
        self.log(f"Extended fonts installed: {extended_fonts_installed}")

        yield Header("PyFiglet Demo")

        with VerticalScroll(id="main_content"):
            yield FigletWidget(id="figlet", font=self.current_font)
            yield Static(id="notification_box")
        with Horizontal(id="options_bar"):
            yield Select(options=self.font_options, value=self.current_font, id="font_select", allow_blank=False)
            with Horizontal(id="switch_container"):
                yield Switch(False, id="switch")
                yield Label("Show all \nfonts")
            yield TextArea(id="text_input")

        yield Footer()

    def on_mount(self):

        self.font_select  = cast(Select, self.query_one("#font_select"))    # chad type hinting convenience vars
        self.text_input   = cast(TextArea, self.query_one("#text_input"))
        self.figlet       = cast(FigletWidget, self.query_one("#figlet"))
        self.font_switch  = cast(Switch, self.query_one("#switch"))
        self.notification = cast(Label, self.query_one("#notification_box"))

        self.set_timer(0.05, self.set_starter_text)
        # The timer is because starting with text in the TextArea makes it glitch out.
        # Giving it a 50ms delay to set the text fixes the problem.

    # This just sets the cursor to the end of the text in the TextArea when the app starts:
    def set_starter_text(self):
        self.text_input.focus()
        end = self.text_input.get_cursor_line_end_location()
        self.text_input.move_cursor(end)

    def on_resize(self, event):
        width, height = event.size          # TODO This needs to be tested in different terminals and app environments
        self.figlet.change_width(width-8)   # -8 to account for padding

    @on(Select.Changed)           
    def font_changed(self, event: Select.Changed) -> None:
        self.figlet.change_font(event.value)
        self.current_font = event.value
        self.log(f"Current font set to: {self.current_font}")

    @on(Switch.Changed)
    def toggle_fonts(self, event: Switch.Changed) -> None:

        self.fonts_list = get_all_fonts_list(event.value)
        self.fonts_list.sort()
        self.font_options = [(font, font) for font in self.fonts_list]
        self.font_select.set_options(self.font_options)

        if not event.value:                                     # if turning switch off:                         
            if self.current_font not in base_fonts:             # if the current font is not in the base fonts list,
                self.current_font = 'standard'                  # set back to standard.
                self.figlet.change_font('standard')             # Keeps font the same when toggling switch, if it can.
        self.font_select.value = self.current_font

        if event.value:
            if extended_fonts_installed:
                self.notification.update("Scanning folder... Extended fonts detected.")
                self.set_timer(3, self.clear_message)
            else:
                self.notification.update("Scanning folder... Note the Extended fonts are not installed.")
                self.set_timer(3, self.clear_message)


    @on(TextArea.Changed)
    async def text_updated(self):
        text = self.text_input.text
        self.figlet.update(text)

        # This just scrolls the text area to the end when the text changes:
        scroll_area = self.query_one("#main_content")
        if scroll_area.scrollbars_enabled == (True, False):
            scroll_area.action_scroll_end()

    def clear_message(self):
        self.notification.update('')

    def action_focus_select(self):
        self.font_select.focus()

    def action_focus_text(self):
        self.text_input.focus()

    def action_toggle_fonts(self):
        self.font_switch.value = not self.font_switch.value

# This is for the entry point script. You can run the demo with:
#$ textual-pyfiglet
def main():
    app = PyFigletDemo()
    app.run()
 
# This is another way to run the demo
#$ python -m textual-pyfiglet 
if __name__ == "__main__":
    app = PyFigletDemo()
    app.run()