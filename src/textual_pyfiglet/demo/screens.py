"""
screens.py
This module defines the ColorScreen and HelpScreen classes
"""

# ~ Type Checking (Pyright and MyPy) - Strict Mode
# ~ Linting - Ruff
# ~ Formatting - Black - max 110 characters / line

# Python imports
from __future__ import annotations
from importlib import resources

# Textual imports
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Container, VerticalScroll
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.color import Color
from textual.widgets import (
    Static,
    Input,
    Markdown,
    Button,
    ListItem,
)


# Local imports
from textual_pyfiglet.demo.custom_listview import CustomListView
from textual_pyfiglet.demo.datawidget import ActiveColors
from textual_pyfiglet.demo.validators import ColorValidator
from textual_pyfiglet.demo.custom_listview import Selected


class ColorScreen(ModalScreen[bool]):

    BINDINGS = [
        Binding("escape,enter", "close_screen", description="Close the help window.", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.app_active_colors = self.app.query_one(ActiveColors)
        self.new_colors: list[tuple[str, Color]] = self.app_active_colors.copy()

    def compose(self) -> ComposeResult:

        with Container(id="colors_container"):
            yield Static(
                "Enter your colors into the Input below.\n" "Select a color in the list to remove it.\n"
            )
            yield Input(id="colorscreen_input", validators=[ColorValidator(self.app.theme_variables)])
            self.listview = CustomListView(id="colorscreen_list")
            yield self.listview
            with Horizontal(id="colorscreen_buttonbar"):
                yield Button("Cancel", id="cancel")
                yield Button("Accept", id="accept")

    def on_mount(self) -> None:
        self.refresh_listview()
        self.query_one(Container).focus()

    def refresh_listview(self) -> None:

        self.listview.clear()
        for i, item in enumerate(self.new_colors):
            self.listview.append(ListItem(Static(f"{i+1}. {item[0]} - {item[1]}")))

    @on(Input.Submitted, selector="#colorscreen_input")
    def colorscreen_input_set(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.value == "":
                return

            elif event.validation_result.is_valid:
                if event.value.startswith("$"):
                    color_obj = Color.parse(self.app.theme_variables[event.value[1:]])
                else:
                    color_obj = Color.parse(event.value)
                i = len(self.new_colors) + 1  # 0-based indexing adjustment
                self.new_colors.append((event.value, color_obj))
                self.listview.append(ListItem(Static(f"{i}. {event.value} - {color_obj}")))
                event.input.clear()
            else:
                failures = event.validation_result.failure_descriptions
                self.log(f"Invalid color input: {failures}")

    @on(CustomListView.Selected)
    def item_selected(self, event: Selected) -> None:

        self.new_colors.pop(event.index)
        self.refresh_listview()

    def action_close_screen(self) -> None:
        self.dismiss()

    @on(Button.Pressed, selector="#cancel")
    def cancel_pressed(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, selector="#accept")
    def accept_pressed(self) -> None:
        self.app_active_colors.clear()
        self.app_active_colors.extend(self.new_colors)
        self.dismiss(True)


class HelpScreen(ModalScreen[None]):

    BINDINGS = [
        Binding("escape,enter", "close_screen", description="Close the help window.", show=True),
    ]

    def compose(self) -> ComposeResult:

        with resources.open_text("textual_pyfiglet", "help.md") as f:
            self.help = f.read()

        with VerticalScroll(id="help_container"):
            yield Markdown(self.help)

    def on_mount(self) -> None:
        self.query_one(VerticalScroll).focus()

    def on_click(self) -> None:
        self.dismiss()

    def action_close_screen(self) -> None:
        self.dismiss()
