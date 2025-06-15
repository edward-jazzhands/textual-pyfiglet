"""Contains the demo app.
This module contains the demo application for PyFiglet.

It has its own entry script. Run with `textual-pyfiglet`.
"""

# ~ Type Checking (Pyright and MyPy) - Strict Mode
# ~ Linting - Ruff
# ~ Formatting - Black - max 110 characters / line

# Python imports
from __future__ import annotations
from typing import Any, cast
from importlib import resources
import re
import random

# Textual imports
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, VerticalScroll, ScrollableContainer
from textual.widget import Widget
from textual.message import Message
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.color import Color, ColorParseError
from textual.validation import Validator, ValidationResult, Number
from textual.widgets import (
    Header,
    Footer,
    Static,
    Input,
    TextArea,
    Select,
    Switch,
    Markdown,
    Button,
    ListView,
    ListItem,
)

# textual-pyfiglet imports
from textual_pyfiglet.datawidget import ListDataWidget
from textual_pyfiglet.figletwidget import FigletWidget
from textual_slidecontainer import SlideContainer

from rich import traceback
from rich.text import Text

traceback.install()


###############################
# ListView Class modification #
###############################
# This was all done to add indexing abilities
# into the ListView class. Will probably turn this into a PR
# for Textual.
# The monkey patching is not ideal but its the only way to add this stuff
# until I submit a full PR.


def _on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:  # type: ignore
    event.stop()
    self.focus()  # type: ignore[unused-ignore]
    self.index = self._nodes.index(event.item)  # type: ignore[unused-ignore]
    self.post_message(self.Selected(self, event.item, self.index))  # type: ignore[unused-ignore]


# Monkey patch the ListView class
ListView._on_list_item__child_clicked = _on_list_item__child_clicked  # type: ignore


class Selected(Message):

    ALLOW_SELECTOR_MATCH = {"item"}

    def __init__(self, list_view: MyListView, item: ListItem, index: int) -> None:
        super().__init__()
        self.list_view: MyListView = list_view
        """The view that contains the item selected."""
        self.item: ListItem = item
        """The selected item."""
        self.index: int = index

    @property
    def control(self) -> MyListView:
        return self.list_view


# Instead of directly assigning, create a new attribute using setattr
setattr(ListView, "Selected", Selected)


class MyListView(ListView):

    def action_select_cursor(self) -> None:
        selected_child = self.highlighted_child
        if selected_child is None:
            return
        index = self._nodes.index(selected_child)
        self.post_message(self.Selected(self, selected_child, index))  # type: ignore

    # HERE FOR EXAMPLE ONLY. This is monkey patched above. It would be
    # preferable to do it this way, but it doesn't work:
    # def _on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:
    #     event.stop()
    #     self.focus()
    #     self.index = self._nodes.index(event.item)
    #     self.post_message(self.Selected(self, event.item, self.index))

    def get_index(self, widget: ListItem) -> int | None:
        try:
            index = self._nodes.index(widget)
        except Exception as e:
            self.log.error(f"Node not found: {e}")
            return None
        else:
            return index

    def __getitem__(self, index: int) -> ListItem:
        return cast(ListItem, self._nodes[index])


######################################
# End of ListView Class modification #
######################################


class ActiveColors(ListDataWidget[tuple[str, Color]]):
    pass


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
            self.listview = MyListView(id="colorscreen_list")
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

    @on(MyListView.Selected)
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


class SizeValidator(Validator):

    patterns = [
        r"^[1-9][0-9]{0,2}$",  # Number between 1-999
        r"^(100|[1-9]?[0-9])%$",  # Percentage
        r"^\d*\.?\d+fr$",  # Float followed by 'fr'
    ]

    def validate(self, value: str) -> ValidationResult:

        if any(re.match(pattern, value) for pattern in self.patterns):
            return self.success()
        elif value == "":
            return self.success()
        else:
            return self.failure(
                "Invalid size format. Must be a number between 1-999, a percentage, "
                "a float followed by 'fr', or 'auto'."
            )


class ColorValidator(Validator):

    def __init__(self, theme_variables: dict[str, str]) -> None:
        super().__init__()
        self.theme_variables = theme_variables

    def validate(self, value: str) -> ValidationResult:

        if value == "":
            return self.success()

        if value.startswith("$"):
            try:
                value = self.theme_variables[value[1:]]
            except KeyError:
                return self.failure(f"Color variable {value} not found in theme variables.")

        try:
            Color.parse(value)
        except ColorParseError:
            return self.failure("Invalid color format. Must be a valid color name or hex code.")
        else:
            return self.success()


class QualityValidator(Validator):

    def validate(self, value: str) -> ValidationResult:

        if value == "":
            return self.success()
        try:
            value_int = int(value)
        except ValueError:
            return self.failure(
                "Invalid quality format. Must be empty (for auto), or an integer between 3-100."
            )
        else:
            if 3 <= value_int <= 100:
                return self.success()
            else:
                return self.failure(
                    "Invalid quality format. Must be empty (for auto), or an integer between 3-100."
                )


class FPSValidator(Validator):

    def validate(self, value: str) -> ValidationResult:

        if value == "":
            return self.success()
        try:
            value_float = float(value)
        except ValueError:
            return self.failure(
                "Invalid FPS format. Must be empty (for auto), or a float greater than 0 with max 100."
            )
        else:
            if 0 < value_float <= 100:
                return self.success()
            else:
                return self.failure(
                    "Invalid FPS format. Must be empty (for auto), or a float greater than 0 with max 100."
                )


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

        self.randomize = Button("Random Font", id="randomize_button")
        self.font_select = Select(self.font_options, value="ansi_regular", id="font_select", allow_blank=True)
        self.width_input = Input(id="width_input", validators=[SizeValidator()], max_length=5)
        self.height_input = Input(id="height_input", validators=[SizeValidator()], max_length=5)
        self.justify_select = Select(
            self.justifications, value="center", id="justify_select", allow_blank=False
        )
        self.color_popup_button = Button("Enter Colors", id="color_list_button")
        self.animation_select = Select(
            self.animations, value="gradient", id="animation_select", allow_blank=False
        )
        self.animate_switch = Switch(id="animate_switch", value=False)
        self.horizontal_switch = Switch(id="horizontal_switch", value=False)
        self.reverse_switch = Switch(id="reverse_switch", value=False)
        self.gradient_quality = Input(
            id="gradient_quality",
            max_length=3,
            validators=[QualityValidator()],
        )
        self.animation_fps = Input(
            id="animation_fps",
            max_length=4,
            validators=[FPSValidator()],
        )
        self.border_switch = Switch(id="border_switch", value=False)
        self.padding_input = Input(value="0", id="padding_input", validators=[Number()], max_length=2)
        self.background_switch = Switch(id="background_switch", value=False)

        yield Static("Settings", id="settings_title")
        yield Static("*=details in help (F1)", id="help_label")
        yield SettingBox(self.randomize)
        yield SettingBox(self.font_select, "Font", widget_width=20)
        yield SettingBox(self.width_input, "Width*", widget_width=12)
        yield SettingBox(self.height_input, "Height*", widget_width=12)
        yield SettingBox(self.justify_select, "Justify", widget_width=14)
        yield SettingBox(self.color_popup_button, "*")
        yield SettingBox(self.animation_select, "Animation Type*", widget_width=22, label_position="under")
        yield SettingBox(self.animate_switch, "Animate", widget_width=10)
        yield SettingBox(self.horizontal_switch, "Horizontal", widget_width=10)
        yield SettingBox(self.reverse_switch, "Reverse\nanimation", widget_width=10)
        yield SettingBox(self.gradient_quality, "Gradient\nquality*", widget_width=12)
        yield SettingBox(self.animation_fps, "Animation\nFPS*", widget_width=12)
        yield SettingBox(self.border_switch, "Border", widget_width=10)
        yield SettingBox(self.padding_input, "Padding", widget_width=10)
        yield SettingBox(self.background_switch, "Background", widget_width=10)

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

    @on(Switch.Changed, selector="#background_switch")
    def background_switch_toggled(self, event: Switch.Changed) -> None:

        if event.value:
            self.figlet_widget.add_class("backgrounded")
        else:
            self.figlet_widget.remove_class("backgrounded")

    @on(Input.Submitted, selector="#padding_input")
    def padding_input_set(self, event: Input.Submitted) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:
                self.log(f"Padding set to: {event.value}")
                self.figlet_widget.styles.padding = int(event.value)
            else:
                failures = event.validation_result.failure_descriptions
                self.log(f"Invalid padding input: {failures}")


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

    #! Needs better bindings.
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

        self.size_display_bar.update(
            f"Parent width: {event.parent_width} | "
            f"Size: {event.width}W x {event.height}H | "
            f"Fig max width: {event.width_setting}"
        )
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


def main() -> None:
    """Run the demo app."""
    app = TextualPyFigletDemo()
    app.run()
