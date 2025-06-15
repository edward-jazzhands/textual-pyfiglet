"""Contains the demo app.
This module contains the demo application for PyFiglet.

It has its own entry script. Run with `textual-pyfiglet`.
"""

# ~ Type Checking (Pyright and MyPy) - Strict Mode
# ~ Linting - Ruff
# ~ Formatting - Black - max 110 characters / line

# Python imports
from __future__ import annotations
from typing import Any  # , cast

# from pathlib import Path
# import random

# Textual imports
from textual import on  # , log
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, ScrollableContainer
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, TextArea  # , Button, Select
from rich.text import Text

# Textual library imports
from textual_slidecontainer import SlideContainer

# Local imports
from textual_pyfiglet.figletwidget import FigletWidget
from textual_pyfiglet.demo.datawidget import ActiveColors
from textual_pyfiglet.demo.settingsbar import SettingsWidget
from textual_pyfiglet.demo.screens import HelpScreen


class BottomBar(Horizontal):

    def __init__(self, figlet_widget: FigletWidget):
        super().__init__()
        self.figlet_widget = figlet_widget

    def compose(self) -> ComposeResult:

        self.text_input = TextArea(id="text_input")
        yield self.text_input

    @on(TextArea.Changed)
    async def text_updated(self) -> None:

        self.figlet_widget.update(self.text_input.text)

        # This just scrolls the text area to the end when the text changes:
        scroll_area = self.app.query_one("#main_window")
        if scroll_area.scrollbars_enabled == (True, False):  # Vertical True, Horizontal False
            scroll_area.action_scroll_end()

    def focus_textarea(self) -> None:
        # Used when the demo boots to focus the text input.

        self.text_input.focus()
        end = self.text_input.get_cursor_line_end_location()
        self.text_input.move_cursor(end)


class TextualPyFigletDemo(App[Any]):

    BINDINGS = [
        Binding("ctrl+b", "toggle_menu", "Expand/collapse the menu"),
        Binding("f1", "show_help", "Show help"),
    ]

    CSS_PATH = "styles.tcss"
    TITLE = "Textual-PyFiglet Demo"

    def on_resize(self) -> None:
        self.figlet_widget.refresh_size()  # <-- This is how you make it resize automatically.

    def compose(self) -> ComposeResult:

        yield ActiveColors()  # this is a fancy data widget I built for the demo. Not part of the library.

        self.figlet_widget = FigletWidget("Starter Text", id="figlet_widget")  # * <- This is the widget.
        # You can input all kinds of arguments directly.
        # But for the purposes of the demo, all these
        # are set in real-time in the demo sidebar.

        banner = FigletWidget.figlet_quick("Textual-PyFiglet", font="smblock")
        self.log(Text.from_markup(f"[bold blue]{banner}"))

        self.settings_widget = SettingsWidget(self.figlet_widget)
        self.bottom_bar = BottomBar(self.figlet_widget)
        self.size_display_bar = Static(id="size_display", expand=True)
        self.menu_container = SlideContainer(id="menu_container", slide_direction="left", floating=False)

        # Note: Layout is horizontal. (top of styles.tcss)
        yield Header(name="Textual-PyFiglet Demo")
        with self.menu_container:
            yield self.settings_widget
        with Container():
            with ScrollableContainer(id="main_window"):
                yield self.figlet_widget
            yield self.size_display_bar
            yield self.bottom_bar
        yield Footer()

    def on_mount(self) -> None:

        self.bottom_bar.focus_textarea()

    @on(FigletWidget.Updated)
    def figlet_updated(self, event: FigletWidget.Updated) -> None:

        self.size_display_bar.update(f"Size: {event.width}W x {event.height}H")
        # If the widget is animating but one of the colors is removed, it will
        # internally stop the animation. When it does that, we need to update the
        # animate switch in the demo menu to reflect that.
        self.settings_widget.animate_switch.value = self.figlet_widget.animated
        active_colors = self.query_one(ActiveColors)
        if len(active_colors) <= 1:
            self.settings_widget.animate_switch.disabled = True
            self.settings_widget.animate_switch.tooltip = "Set at least 2 colors to animate."
        else:
            self.settings_widget.animate_switch.disabled = False
            self.settings_widget.animate_switch.tooltip = None

    @on(ActiveColors.Updated)
    def activecolors_updated(self) -> None:

        active_colors = self.query_one(ActiveColors)
        self.log(active_colors)
        color_name_strings: list[str] = []
        for item in active_colors:
            color_name_strings.append(item[0])

        self.figlet_widget.set_color_list(color_name_strings)

    @on(SlideContainer.SlideCompleted, "#menu_container")
    def slide_completed(self) -> None:
        self.on_resize()

    def action_toggle_menu(self) -> None:
        self.menu_container.toggle()

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())


def run_demo() -> None:
    """Run the demo app."""
    app = TextualPyFigletDemo()
    app.run()


if __name__ == "__main__":
    run_demo()
