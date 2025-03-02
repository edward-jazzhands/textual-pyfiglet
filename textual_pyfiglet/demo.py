"""Contains the demo app.
This module contains the demo application for PyFiglet.

It has its own entry script. Run with `textual-pyfiglet`.
"""
# Python imports
# from typing import cast

# Textual imports
from textual.app import App, on
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
)

# textual-pyfiglet imports
from textual_pyfiglet.figletwidget import FigletWidget
from textual_pyfiglet.pyfiglet import figlet_format

from rich import traceback
from rich.text import Text
traceback.install()         


class TextualPyFigletDemo(App):

    BINDINGS = [
        ("s", "focus_select", "Focus the font select"),
        ("t", "focus_text", "Focus the text input"),
        ("a", "toggle_fonts", "Toggle all fonts"),
    ]

    CSS_PATH = "styles.tcss"

    current_font = 'standard'       # starting font for the demo
    # font:          reactive[str] = reactive('standard')

    justifications = [
        ('Left', 'left'),
        ('Center', 'center'),
        ('Right', 'right'),
    ]

    # timers, used for notifications
    timer1 = None
    timer2 = None

    def compose(self):

        self.log("PyFiglet Demo started.")
        banner = figlet_format("Textual-PyFiglet\nDemo", font="smbraille")
        self.log(Text(banner, style="bold green"))

        self.theme = "gruvbox"

        self.figlet_widget = FigletWidget("Starter Text", id="figlet_widget")
        self.font_select   = Select([], id="font_select", allow_blank=True)      
        self.text_input    = TextArea(id="text_input")
        self.font_switch   = Switch(False, id="switch")
        self.notification1 = Static(id="notification_box1")
        self.notification2 = Static(id="notification_box2")
        self.width_input   = Input(id="width_input", classes="sidebar_input")
        self.height_input  = Input(id="height_input", classes="sidebar_input")        

        yield Header("PyFiglet Demo")

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("Set container width:", classes="sidebar_label")
                yield self.width_input
                yield Label("Set container height:", classes="sidebar_label")
                yield self.height_input
                yield Label("\n(Leave blank\n for 1.fr/100%)\n", classes="sidebar_label")
                yield Label("Justify:", classes="sidebar_label") 
                yield Select(self.justifications, id="justify_select", value='center', allow_blank=False)
                yield Button("Set", id="set_button", classes="sidebar_button")
                yield Button("Copy text\nto clipboard", id="copy_button", classes="sidebar_button")

            with VerticalScroll(id="main_window"):
                yield self.figlet_widget

        with Container(id="bottom_bar"):
            with Horizontal():
                yield self.notification1
                yield self.notification2
            with Horizontal():
                yield self.font_select
                with Horizontal(id="container_of_switch"):
                    yield self.font_switch
                    yield Label("Show all \nfonts")
                yield self.text_input

        yield Footer()

    def on_mount(self):

        self.log(f"Extended fonts installed: {self.figlet_widget.extended_fonts_installed}")

        # self.figlet_widget._inner_figlet.tooltip = "Inner Figlet Widget"
        # self.figlet_widget.tooltip = "Outer Figlet Widget"

        self.fonts_list = self.figlet_widget.get_fonts_list(get_all=True)
        self.base_fonts = self.figlet_widget.get_fonts_list(get_all=False)
        self.fonts_list.sort()
        self.font_options = [(font, font) for font in self.base_fonts]  # start with only base fonts.
        self.font_select.set_options(self.font_options)     # NOTE: This is setting the available fonts.
        self.font_select.value = self.current_font          # NOTE: This is setting the font.

        self.text_input.focus()
        end = self.text_input.get_cursor_line_end_location()
        self.text_input.move_cursor(end)

    # Because the select box has a default value, this will run on startup, and then set
    # the font to the default selection. You can also set a font in the constructor of the FigletWidget,
    # But for the purposes of the demo I'm not doing that here because this would override the constructor setting.
    @on(Select.Changed, selector="#font_select")           
    def font_changed(self, event: Select.Changed) -> None:
        if event.value == Select.BLANK:
            return
        self.figlet_widget.set_font(event.value)
        self.current_font = event.value
        self.log(f"Current font set to: {self.current_font}")

    # why this no work?
    # def on_key(self, event):
    #     if event.key == "up":
    #         self.font_select.scroll_up()
    #     elif event.key == "down":
    #         self.font_select.scroll_down()

    @on(Select.Changed, selector="#justify_select")
    def justify_changed(self, event: Select.Changed) -> None:
        self.figlet_widget.set_justify(event.value)
        self.log(f"Justify set to: {event.value}")

    @on(Switch.Changed)
    def toggle_fonts(self, event: Switch.Changed) -> None:
        "Toggle between base fonts and all fonts."

        if event.value:                            
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
            if self.figlet_widget.extended_fonts_installed:
                self.show_notification1("Scanning folder... Extended fonts detected.")
            else:
                self.show_notification1("Scanning folder...")


    @on(Button.Pressed, selector="#set_button")
    def set_container_size(self):
        width = self.width_input.value
        height = self.height_input.value
        self.log(f"Setting container size to: ({width} x {height})")
        if width:
            self.figlet_widget.styles.width = int(width)
            # self.figlet_widget.set_styles(f'width: {width}%;')
        else:
            self.figlet_widget.set_styles('width: 1fr;')
        if height:
            self.figlet_widget.styles.height = int(height)
        else:
            self.figlet_widget.set_styles('height: auto;')

    @on(Button.Pressed, selector="#copy_button")
    def copy_text(self):
        self.log("Copying text to clipboard.")
        self.figlet_widget.copy_figlet_to_clipboard()

    @on(FigletWidget.Updated)
    def figlet_updated(self, event: FigletWidget.Updated):
        outer_width, outer_height = event.widget.size
        inner_width, inner_height = event.widget._inner_figlet.size
        self.show_notification2(f"Outer: {outer_width}W x {outer_height}H | Inner: {inner_width}W x {inner_height}H")
        # self.show_notification2(f"Size: {outer_width}W x {outer_height}H")

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
        # if self.timer2:
        #     self.timer2.stop()
        # self.timer2 = self.set_timer(3, self.clear_notification2)

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

# This is for the entry script. Run the demo with:
#$ textual-pyfiglet
def run_demo():
    TextualPyFigletDemo().run()