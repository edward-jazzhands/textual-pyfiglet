"""Contains the demo app.
This module contains the demo application for PyFiglet

Run this module directly to start the PyFiglet demo application.    
Either command works:   
- textual-pyfiglet
- python -m textual-pyfiglet

Note the fonts list is dynamically generated from the fonts folder.
If you also installed the extended fonts pack, You can toggle the switch
in the demo, and it will scan the fonts folder for all fonts.
(You can add your own, as well, or download them individually.)

Also note that the first time it runs and detects the extended fonts pack,
it will copy the whole pack into the fonts folder (inside pyfiglet).
This might take about 1-2 seconds. It will only do this once.
"""

import os
from typing import cast

from rich import traceback
traceback.install()

from rich.text import Text

from textual.app import App, on
from textual.events import Key, Resize
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    Button,
    Static,
    Input,
    TextArea,
    Select,
    Switch,
    Label,
    TabbedContent,
    Placeholder
)

from .figletwidget import FigletWidget
from .pyfiglet import fonts
from . import extended_fonts_installed


class PyFigletDemo(App):

    BINDINGS = [
        ("s", "focus_select", "Focus the font select"),
        ("t", "focus_text", "Focus the text input"),
        ("a", "toggle_fonts", "Toggle all fonts"),
    ]

    CSS_PATH = "styles.tcss"
    current_font = 'standard'

    # debounce timers, used for notifications
    timer1 = None
    timer2 = None

    def compose(self):

        self.log("PyFiglet Demo started.")
        self.log(f"Extended fonts installed: {extended_fonts_installed}")

        yield Header("PyFiglet Demo")

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("Set container width:", classes="sidebar_label")
                yield Input(id="width_input", classes="sidebar_input")
                yield Label("Set container height:", classes="sidebar_label")
                yield Input(id="height_input", classes="sidebar_input")
                yield Label("\nLeave blank for auto", classes="sidebar_label")
                yield Button("Set", id="set_button")

            with VerticalScroll(id="main_window"):
                yield FigletWidget("Starter Text", id="figlet_widget")

        with Container(id="bottom_bar"):
            with Horizontal():
                yield Static(id="notification_box1")
                yield Static(id="notification_box2")
            with Horizontal():
                yield Select([], id="font_select", allow_blank=True)
                with Horizontal(id="container_of_switch"):
                    yield Switch(False, id="switch")
                    yield Label("Show all \nfonts")
                yield TextArea(id="text_input")

        yield Footer()

    def on_mount(self):

        self.figlet_widget    = cast(FigletWidget, self.query_one("#figlet_widget")) 
        self.font_select  = cast(Select, self.query_one("#font_select"))            
        self.text_input   = cast(TextArea, self.query_one("#text_input"))       # chad type hinting convenience vars
        self.font_switch  = cast(Switch, self.query_one("#switch"))
        self.notification1 = cast(Label, self.query_one("#notification_box1"))
        self.notification2 = cast(Label, self.query_one("#notification_box2"))
        self.width_input  = cast(Input, self.query_one("#width_input"))
        self.height_input = cast(Input, self.query_one("#height_input"))

        self.fonts_list = self.figlet_widget.get_fonts_list(get_all=True)
        self.base_fonts = self.figlet_widget.get_fonts_list(get_all=False)
        self.fonts_list.sort()
        self.font_options = [(font, font) for font in self.base_fonts]
        self.font_select.set_options(self.font_options)
        self.font_select.value = self.current_font

        self.text_input.focus()
        end = self.text_input.get_cursor_line_end_location()
        self.text_input.move_cursor(end)

    @on(Select.Changed)           
    def font_changed(self, event: Select.Changed) -> None:
        if event.value == Select.BLANK:
            return
        self.figlet_widget.set_font(event.value)
        self.current_font = event.value
        self.log(f"Current font set to: {self.current_font}")

    @on(Switch.Changed)
    def toggle_fonts(self, event: Switch.Changed) -> None:
        if event.value:                                         # turn on extended
            self.font_options = [(font, font) for font in self.fonts_list]
        else:
            self.font_options = [(font, font) for font in self.base_fonts]
        self.font_select.set_options(self.font_options)

        if not event.value:                                     # if turning switch off:                         
            if self.current_font not in self.base_fonts:        # if the current font is not in the base fonts list,
                self.current_font = 'standard'                  # set back to standard.
                self.figlet_widget.set_font('standard')         # Keeps font the same when toggling switch, if it can.
        self.font_select.value = self.current_font

        if event.value:
            if extended_fonts_installed:
                self.show_notification1("Scanning folder... Extended fonts detected.")
            else:
                self.show_notification1("Scanning folder... Note the Extended fonts are not installed.")

    @on(Button.Pressed)
    def set_container_size(self):
        width = self.width_input.value
        height = self.height_input.value
        self.log(f"Setting container size to: ({width} x {height})")
        if width:
            self.figlet_widget.styles.width = int(width)
        if height:
            self.figlet_widget.styles.height = int(height)
        if not width:
            self.figlet_widget.set_styles('width: 1fr;')
        if not height:
            self.figlet_widget.set_styles('height: auto;')

        self.figlet_widget.update()

    @on(FigletWidget.Updated)
    def figlet_updated(self, event: FigletWidget.Updated):
        width, height = event.widget.size
        self.show_notification2(f"width: {width}, height: {height}")

    @on(TextArea.Changed)
    async def text_updated(self):
        text = self.text_input.text
        self.figlet_widget.update(text)

        # This just scrolls the text area to the end when the text changes:
        scroll_area = self.query_one("#main_window")
        if scroll_area.scrollbars_enabled == (True, False):
            scroll_area.action_scroll_end()

    def show_notification1(self, message: str):
        self.notification1.update(message)
        if self.timer1:
            self.timer1.stop()
        self.timer1 = self.set_timer(3, self.clear_notification1)

    def show_notification2(self, message: str):
        self.notification2.update(message)
        if self.timer2:
            self.timer2.stop()
        self.timer2 = self.set_timer(3, self.clear_notification2)

    def clear_notification1(self):
        self.notification1.update('')
        self.timer = None

    def clear_notification2(self):
        self.notification2.update('')
        self.timer = None

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