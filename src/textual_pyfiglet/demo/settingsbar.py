"settingsbar.py - Settings bar for the Textual-PyFiglet demo app.\n"

# ~ Type Checking (Pyright and MyPy) - Strict Mode
# ~ Linting - Ruff
# ~ Formatting - Black - max 110 characters / line

from __future__ import annotations
import random

# import random
# from pathlib import Path

# Textual imports
from textual import on  # , log
from textual.app import ComposeResult
from textual.containers import Horizontal, Container, VerticalScroll
from textual.validation import Number
from textual.widget import Widget
from textual.theme import Theme
from textual.widgets import (
    Static,
    Input,
    Select,
    Switch,
    Button,
)

# Local imports
from textual_pyfiglet.figletwidget import FigletWidget
from textual_pyfiglet.demo.validators import (
    QualityValidator,
    FPSValidator,
    SizeValidator,
    ColorValidator,
)
from textual_pyfiglet.demo.screens import ColorScreen


class SettingBox(Container):

    def __init__(
        self,
        widget: Widget,
        label: str = "",
        label_position: str = "beside",
        widget_width: int | None = None,
    ):
        """A setting box with a label and a widget. \n
        Static position can be either 'beside' or 'under'"""

        super().__init__()
        self.widget = widget
        self.label = label
        self.label_position = label_position
        self.widget_width = widget_width

    def compose(self) -> ComposeResult:

        if self.widget_width:
            self.widget.styles.width = self.widget_width

        if self.label_position == "beside":
            with Horizontal():
                yield Static(classes="setting_filler")
                if self.label:
                    yield Static(self.label, classes="setting_label")
                yield self.widget
        elif self.label_position == "under":
            with Horizontal():
                yield Static(classes="setting_filler")
                yield self.widget
            with Horizontal(classes="under_label"):
                yield Static(classes="setting_filler")
                if self.label:
                    yield Static(self.label, classes="setting_label")
            self.add_class("setting_under")


class SettingsWidget(VerticalScroll):

    justifications = [
        ("Left", "left"),
        ("Center", "center"),
        ("Right", "right"),
    ]

    animations = [
        ("gradient", "gradient"),
        ("smooth_strobe", "smooth_strobe"),
        ("fast_strobe", "fast_strobe"),
    ]

    patterns = [
        r"^[1-9][0-9]{0,2}$",  # Number between 1-999
        r"^(100|[1-9]?[0-9])%$",  # Percentage
        r"^\d*\.?\d+fr$",  # Float followed by 'fr'
    ]

    def __init__(self, figlet_widget: FigletWidget):
        super().__init__()
        self.figlet_widget = figlet_widget
        self.fonts_list = self.figlet_widget.fonts_list
        self.fonts_list.sort()
        self.font_options = [(font, font) for font in self.fonts_list]

    def compose(self) -> ComposeResult:

        randomize = Button("Random Font", id="randomize_button")
        self.font_select = Select(self.font_options, value="ansi_regular", id="font_select", allow_blank=True)
        self.width_input = Input(id="width_input", validators=[SizeValidator()], max_length=5)
        self.height_input = Input(id="height_input", validators=[SizeValidator()], max_length=5)
        justify_select = Select(self.justifications, value="center", id="justify_select", allow_blank=False)
        color_popup_button = Button("Enter Colors", id="color_list_button")
        animation_select = Select(self.animations, value="gradient", id="animation_select", allow_blank=False)
        animate_switch = Switch(id="animate_switch", value=False)
        horizontal_switch = Switch(id="horizontal_switch", value=False)
        reverse_switch = Switch(id="reverse_switch", value=False)
        gradient_quality = Input(
            id="gradient_quality",
            max_length=3,
            validators=[QualityValidator()],
        )
        animation_fps = Input(
            id="animation_fps",
            max_length=4,
            validators=[FPSValidator()],
        )
        border_switch = Switch(id="border_switch", value=False)
        padding_input = Input(value="0", id="padding_input", validators=[Number()], max_length=2)
        bg_color = Input(id="bg_color", validators=[ColorValidator(self.app.theme_variables)])

        yield Static("Settings", id="settings_title")
        yield Static("*=details in help (F1)", id="help_label")
        yield SettingBox(randomize)
        yield SettingBox(self.font_select, "Font", widget_width=20)
        yield SettingBox(self.width_input, "Width*", widget_width=12)
        yield SettingBox(self.height_input, "Height*", widget_width=12)
        yield SettingBox(justify_select, "Justify", widget_width=14)
        yield SettingBox(color_popup_button, "*")
        yield SettingBox(animation_select, "Animation Type*", widget_width=22, label_position="under")
        yield SettingBox(animate_switch, "Animate", widget_width=10)
        yield SettingBox(horizontal_switch, "Horizontal", widget_width=10)
        yield SettingBox(reverse_switch, "Reverse\nanimation", widget_width=10)
        yield SettingBox(gradient_quality, "Gradient\nquality*", widget_width=12)
        yield SettingBox(animation_fps, "Animation\nFPS*", widget_width=12)
        yield SettingBox(border_switch, "Border", widget_width=10)
        yield SettingBox(padding_input, "Padding", widget_width=10)
        yield SettingBox(bg_color, "Figlet bg color", widget_width=22, label_position="under")

    def on_mount(self) -> None:

        self.app.theme_changed_signal.subscribe(self, self._refresh_theme)  # type: ignore[unused-ignore]

    async def _refresh_theme(self, theme: Theme) -> None:

        bg_input = self.query_one("#bg_color", Input)
        await bg_input.action_submit()

    @on(Button.Pressed, "#randomize_button")
    def randomize_font(self) -> None:

        self.log("Randomizing font...")

        fonts = self.figlet_widget.fonts_list
        self.font_select.value = random.choice(fonts)  # triggers method font_changed (below)

    @on(Select.Changed, selector="#font_select")
    def font_changed(self, event: Select.Changed) -> None:

        if event.value == Select.BLANK:  #! Explain why blank is even allowed.
            return

        self.log(f"Setting font to: {event.value}...")
        self.figlet_widget.set_font(str(event.value))

    @on(Input.Submitted, selector="#width_input")
    def width_input_set(self, event: Input.Submitted) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:
                width = self.width_input.value if self.width_input.value != "" else "auto"
                height = self.height_input.value if self.height_input.value != "" else "auto"
                self.log(f"Setting container size to: ({width} x {height})")

                if width == "auto":
                    self.figlet_widget.styles.width = width
                    self.log(f"Width set to: {self.figlet_widget.styles.width}")
                else:
                    try:
                        self.figlet_widget.styles.width = int(width)
                        self.log(f"Width set to integer: {self.figlet_widget.styles.width}")
                    except ValueError:
                        self.figlet_widget.styles.width = width
                        self.log(f"Width set to: {self.figlet_widget.styles.width}")
            else:
                failures = event.validation_result.failure_descriptions
                self.log(f"Invalid width: {failures}")
                self.notify(f"Invalid width: {failures}", markup=False)

    @on(Input.Submitted, selector="#height_input")
    def height_input_set(self, event: Input.Submitted) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:
                width = self.width_input.value if self.width_input.value != "" else "auto"
                height = self.height_input.value if self.height_input.value != "" else "auto"
                self.log(f"Setting container size to: ({width} x {height})")

                if height == "auto":
                    self.figlet_widget.styles.height = height
                    self.log(f"Height set to: {self.figlet_widget.styles.height}")
                else:
                    try:
                        self.figlet_widget.styles.height = int(height)
                        self.log(f"Height set to integer: {self.figlet_widget.styles.height}")
                    except ValueError:
                        self.figlet_widget.styles.height = height
                        self.log(f"Height set to: {self.figlet_widget.styles.height}")
            else:
                failures = event.validation_result.failure_descriptions
                self.log(f"Invalid height: {failures}")
                self.notify(f"Invalid height: {failures}", markup=False)

    @on(Select.Changed, selector="#justify_select")
    def justify_changed(self, event: Select.Changed) -> None:

        self.log(f"Setting justify to: {event.value}...")
        self.figlet_widget.set_justify(str(event.value))

    @on(Button.Pressed, "#color_list_button")
    async def color_list_button_pressed(self) -> None:

        await self.app.push_screen(ColorScreen())

    @on(Switch.Changed, selector="#animate_switch")
    def animate_switch_toggled(self, event: Switch.Changed) -> None:

        self.figlet_widget.animated = event.value

    @on(Select.Changed, selector="#animation_select")
    def animation_selected(self, event: Select.Changed) -> None:

        self.figlet_widget.set_animation_type(str(event.value))

    @on(Switch.Changed, selector="#horizontal_switch")
    def horizontal_switch_toggled(self, event: Switch.Changed) -> None:

        self.figlet_widget.horizontal = event.value

    @on(Switch.Changed, selector="#reverse_switch")
    def reverse_switch_toggled(self, event: Switch.Changed) -> None:

        self.figlet_widget.reverse = event.value

    @on(Input.Submitted, selector="#gradient_quality")
    def gradient_quality_set(self, event: Input.Submitted) -> None:
        """Set the gradient quality. (Number of colors in the gradient)\n
        This must be a number between 1-100, or empty for auto.
        Auto mode will set the quality to the height of the widget."""

        if event.validation_result:
            if event.validation_result.is_valid:
                self.log(f"Gradient quality set to: {event.value if event.value else "auto"}")
                if event.value == "":
                    self.figlet_widget.gradient_quality = "auto"
                else:
                    self.figlet_widget.gradient_quality = int(event.value)
            else:
                failures = event.validation_result.failure_descriptions
                self.log(f"Invalid Gradient quality input: {failures}")
                self.notify(f"Invalid Gradient quality input: {failures}", markup=False)

    @on(Input.Submitted, selector="#animation_fps")
    def animation_fps_set(self, event: Input.Submitted) -> None:
        """Set the animation frames per second. \n
        This must be a number greater than 0 and maximum of 100."""

        if event.validation_result:
            if event.validation_result.is_valid:
                self.log(f"Animation speed set to: {event.value}")
                if event.value == "":
                    self.figlet_widget.animation_fps = "auto"
                else:
                    self.figlet_widget.animation_fps = float(event.value)
            else:
                failures = event.validation_result.failure_descriptions
                self.log(f"Invalid animation speed input: {failures}")
                self.notify(f"Invalid animation speed input: {failures}", markup=False)

    @on(Switch.Changed, selector="#border_switch")
    def border_switch_toggled(self, event: Switch.Changed) -> None:

        if event.value:
            self.figlet_widget.add_class("bordered")
        else:
            self.figlet_widget.remove_class("bordered")

    @on(Input.Submitted, selector="#padding_input")
    def padding_input_set(self, event: Input.Submitted) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:
                self.log(f"Padding set to: {event.value}")
                self.figlet_widget.styles.padding = int(event.value)
            else:
                failures = event.validation_result.failure_descriptions
                self.log(f"Invalid padding input: {failures}")

    @on(Input.Submitted, selector="#bg_color")
    def bg_color_set(self, event: Input.Submitted) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:
                self.log(f"Figlet background set to: {event.value if event.value else "auto"}")
                if event.value == "":
                    self.figlet_widget.styles.background = None
                else:
                    if event.value.startswith("$"):
                        self.figlet_widget.styles.background = self.app.theme_variables[event.value[1:]]
                    else:
                        self.figlet_widget.styles.background = event.value
            else:
                failures = event.validation_result.failure_descriptions
                self.log(f"Invalid color input: {failures}")
                self.notify(f"Invalid color input: {failures}", markup=False)
