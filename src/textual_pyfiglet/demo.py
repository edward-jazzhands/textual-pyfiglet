"""Contains the demo app.
This module contains the demo application for PyFiglet.

It has its own entry script. Run with `textual-pyfiglet`.
"""
# Python imports
from typing import cast
from importlib import resources
import re
import random

# Textual imports
from textual import on
from textual.app import App
from textual.containers import Horizontal, Container, VerticalScroll, ScrollableContainer
from textual.widget import Widget
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.color import Color, ColorParseError
from textual.validation import Validator, ValidationResult, Number
from textual.widgets import (
    Header, Footer, Static, Input, TextArea,
    Select, Switch, Label, Markdown, Button
)

# textual-pyfiglet imports
from textual_pyfiglet.figletwidget import FigletWidget, JUSTIFY_OPTIONS
from textual_pyfiglet.pyfiglet.fonts import ALL_FONTS
from textual_slidecontainer import SlideContainer

from rich import traceback
from rich.text import Text
traceback.install()


class HelpScreen(ModalScreen):

    BINDINGS = [
        Binding("escape,enter", "close_screen", description="Close the help window.", show=True),
    ]

    def compose(self):

        with resources.open_text('textual_pyfiglet', 'help.md') as f:
            self.help = f.read()

        with VerticalScroll(id='help_container'):
            yield Markdown(self.help)

    def on_mount(self):
        self.query_one(VerticalScroll).focus()

    def on_click(self):
        self.dismiss()

    def action_close_screen(self):
        self.dismiss()

class SettingBox(Container):

    def __init__(
        self,
        widget: Widget,
        label: str = "",
        label_position: str = "beside",
        widget_width: int | None = None,
        *args,
        **kwargs
    ):
        """A setting box with a label and a widget. \n
        Label position can be either 'beside' or 'under'"""

        super().__init__(*args, **kwargs)
        self.widget = widget
        self.label = label
        self.label_position = label_position
        self.widget_width = widget_width

    def compose(self):

        if self.widget_width:
            self.widget.styles.width = self.widget_width

        if self.label_position == "beside":
            with Horizontal():
                yield Static(classes="setting_filler")
                if self.label:
                    yield Label(self.label, classes="setting_label")
                yield self.widget                
        elif self.label_position == "under":
            with Horizontal():
                yield Static(classes="setting_filler")
                yield self.widget
            with Horizontal(classes="under_label"):
                yield Static(classes="setting_filler")
                if self.label:
                    yield Label(self.label, classes="setting_label")
            self.add_class("setting_under")


class SizeValidator(Validator):

    patterns = [
        r'^[1-9][0-9]{0,2}$',       # Number between 1-999
        r'^(100|[1-9]?[0-9])%$',    # Percentage
        r'^\d*\.?\d+fr$',           # Float followed by 'fr'
    ]

    def validate(self, value: str) -> ValidationResult:

        if any(re.match(pattern, value) for pattern in self.patterns):
            return self.success()
        elif value == '':
            return self.success()
        else:
            return self.failure(
                "Invalid size format. Must be a number between 1-999, a percentage, "
                "a float followed by 'fr', or 'auto'."
            )
        

class ColorValidator(Validator):

    def validate(self, value: str) -> ValidationResult:

        if value == '':
            return self.success()

        try:
            Color.parse(value)
        except ColorParseError:
            return self.failure(
                "Invalid color format. Must be a valid color name or hex code."
            )
        else:
            return self.success()
        
class QualityValidator(Validator):

    def validate(self, value: str) -> ValidationResult:

        if value == '':
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
          

class SettingsWidget(VerticalScroll):

    justifications = [
        ('Left', 'left'),
        ('Center', 'center'),
        ('Right', 'right'),
    ]  

    patterns = [
        r'^[1-9][0-9]{0,2}$',       # Number between 1-999
        r'^(100|[1-9]?[0-9])%$',    # Percentage
        r'^\d*\.?\d+fr$',           # Float followed by 'fr'
    ]

    def __init__(self, figlet_widget: FigletWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.figlet_widget = figlet_widget

    def compose(self):

        self.fonts_list = self.figlet_widget.get_fonts_list()
        self.fonts_list.sort()
        self.font_options = [(font, font) for font in self.fonts_list] 

        self.randomize = Button("Random Font", id="randomize_button")
        self.font_select = Select(
            self.font_options, value="ansi_regular", id="font_select", allow_blank=True
        )
        self.width_input  = Input(id="width_input", validators=[SizeValidator()], max_length=5)
        self.height_input = Input(id="height_input", validators=[SizeValidator()], max_length=5)
        self.justify_select = Select(
            self.justifications, value='center', id="justify_select", allow_blank=False
            )
        self.padding_input = Input(
            value="0", id="padding_input", validators=[Number()], max_length=2
        )
        self.color1_input = Input(id="color1_input", validators=[ColorValidator()])
        self.color2_input = Input(id="color2_input", validators=[ColorValidator()])
        self.animate_switch = Switch(id="animate_switch", value=False)
        self.gradient_quality = Input(
            id="gradient_quality", max_length=3, 
            validators=[QualityValidator()], 
        )
        self.animation_speed = Input(
            id="animation_speed", value="0.08", max_length=4,
            validators=[Number(minimum=0.05, maximum=1.0)], 
        )

        yield Label("Settings", id="settings_title")
        yield Label("*=details in help (F1)", id="help_label")
        yield SettingBox(self.randomize)
        yield SettingBox(self.font_select, "Font", widget_width=20)
        yield SettingBox(self.width_input, "Width*", widget_width=12)
        yield SettingBox(self.height_input, "Height*", widget_width=12)
        yield SettingBox(self.justify_select, "Justify", widget_width=14)
        yield SettingBox(self.padding_input, "Padding", widget_width=8)
        yield SettingBox(self.color1_input, "Color 1*", widget_width=24, label_position="under")
        yield SettingBox(self.color2_input, "Color 2*", widget_width=24, label_position="under")
        yield SettingBox(self.animate_switch, "Animate", widget_width=10)
        yield SettingBox(self.gradient_quality, "Gradient\nQuality*", widget_width=12)
        yield SettingBox(self.animation_speed, "Animation\nSpeed*", widget_width=12)

    @on(Button.Pressed, "#randomize_button")
    def randomize_font(self) -> None:
        """Randomize the font. This is just a demo function."""

        self.log("Randomizing font...")

        fonts = self.figlet_widget.get_fonts_list()
        self.font_select.value = random.choice(fonts)


    @on(Select.Changed, selector="#font_select")           
    def font_changed(self, event: Select.Changed) -> None:

        if event.value == Select.BLANK:   #! Explain why blank is even allowed.
            return
        
        self.log(f"Setting font to: {event.value}...")         
        self.figlet_widget.set_font(cast(ALL_FONTS, event.value))

    @on(Input.Submitted, selector="#width_input")
    @on(Input.Blurred, selector="#width_input")
    def width_input_set(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:          
                self.log(f"Width set to: {event.value}")
                width = self.width_input.value if self.width_input.value != '' else 'auto'
                height = self.height_input.value if self.height_input.value != '' else 'auto'
                self.log(f"Setting container size to: ({width} x {height})")

                if width == 'auto':
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
    @on(Input.Blurred, selector="#height_input")
    def height_input_set(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:          
                width = self.width_input.value if self.width_input.value != '' else 'auto'
                height = self.height_input.value if self.height_input.value != '' else 'auto'
                self.log(f"Setting container size to: ({width} x {height})")
                
                if height == 'auto':
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
        self.figlet_widget.set_justify(cast(JUSTIFY_OPTIONS, event.value))
   
    @on(Input.Submitted, selector="#padding_input")
    @on(Input.Blurred, selector="#padding_input")
    def padding_input_set(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:                            
                self.log(f"Padding set to: {event.value}")
                self.figlet_widget.styles.padding = int(event.value)
            else: 
                failures = event.validation_result.failure_descriptions   
                self.log(f"Invalid padding input: {failures}")

    @on(Input.Submitted, selector="#color1_input")
    @on(Input.Blurred, selector="#color1_input")
    def color1_input_set(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:                        
                self.log(f"Color1 set to: {event.value}")
                self.figlet_widget.set_color1(event.value)
            else: 
                failures = event.validation_result.failure_descriptions 
                self.log(f"Invalid color1 input: {failures}")  
                self.notify(f"Invalid color1 input: {failures}", markup=False)

    @on(Input.Submitted, selector="#color2_input")
    @on(Input.Blurred, selector="#color2_input")
    def color2_input_set(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:                        
                self.log(f"Color2 set to: {event.value}")
                self.figlet_widget.set_color2(event.value)
            else: 
                failures = event.validation_result.failure_descriptions 
                self.log(f"Invalid color2 input: {failures}") 
                self.notify(f"Invalid color2 input: {failures}", markup=False)   

    @on(Switch.Changed, selector="#animate_switch")    
    def animate_switch_toggled(self, event: Switch.Changed) -> None:

        self.figlet_widget.set_animated(event.value)

    @on(Input.Submitted, selector="#gradient_quality")
    @on(Input.Blurred, selector="#gradient_quality")
    def gradient_quality_set(self, event: Input.Blurred) -> None:
        """Set the gradient quality. (Number of colors in the gradient)\n
        This must be a number between 1-100, or empty for auto.
        Auto mode will set the quality to the height of the widget."""

        if event.validation_result:
            if event.validation_result.is_valid:                            
                self.log(f"Gradient quality set to: {event.value}")
                if event.value == '':
                    self.figlet_widget.set_gradient_quality('auto')
                else:
                    self.figlet_widget.set_gradient_quality(int(event.value))
            else: 
                failures = event.validation_result.failure_descriptions   
                self.log(f"Invalid Gradient quality input: {failures}")
                self.notify(f"Invalid Gradient quality input: {failures}", markup=False)

    @on(Input.Submitted, selector="#animation_speed")
    @on(Input.Blurred, selector="#animation_speed")
    def animation_speed_set(self, event: Input.Blurred) -> None:
        """Set the animation speed in seconds. \n
        This must be a number between 0.05 - 1.0"""

        if event.validation_result:
            if event.validation_result.is_valid:                            
                self.log(f"Animation speed set to: {event.value}")
                self.figlet_widget.set_animation_speed(float(event.value))
            else: 
                failures = event.validation_result.failure_descriptions   
                self.log(f"Invalid animation speed input: {failures}")
                self.notify(f"Invalid animation speed input: {failures}", markup=False)


class BottomBar(Horizontal):

    def __init__(self, figlet_widget: FigletWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.figlet_widget = figlet_widget   

    def compose(self):

        self.text_input = TextArea(id="text_input")
        yield self.text_input

    @on(TextArea.Changed)
    async def text_updated(self):

        self.figlet_widget.update(self.text_input.text)

        # This just scrolls the text area to the end when the text changes:
        scroll_area = self.app.query_one("#main_window")
        if scroll_area.scrollbars_enabled == (True, False): # Vertical True, Horizontal False
            scroll_area.action_scroll_end()

    def focus_textarea(self):
        # Used when the demo boots to focus the text input.
        
        self.text_input.focus()
        end = self.text_input.get_cursor_line_end_location()
        self.text_input.move_cursor(end)

class TextualPyFigletDemo(App):

    #! Needs better bindings.
    BINDINGS = [
        Binding("ctrl+b", "toggle_menu", "Expand/collapse the menu"),
        Binding("f1", "show_help", "Show help"),
    ]

    CSS_PATH = "styles.tcss"
    TITLE = "Textual-PyFiglet Demo"

    def on_resize(self):                    
        self.figlet_widget.refresh_size()   # <-- This is how you make it resize automatically.

    def compose(self):

        self.figlet_widget = FigletWidget(      #~ <--- This is the main widget.
            "Starter Text",                     # You can input all kinds of arguments directly.
            id="figlet_widget",                 # But for the purposes of the demo, all these
            # color1="red",                 # Every setting can be changed in real-time.
            # color2="blue",          
        )

        banner = FigletWidget.figlet_quick("Textual-PyFiglet", font="smblock")
        self.log(Text.from_markup(f"[bold blue]{banner}"))

        self.settings_widget  = SettingsWidget(self.figlet_widget)
        self.bottom_bar       = BottomBar(self.figlet_widget)
        self.size_display_bar = Static(id="size_display", expand=True)
        self.menu_container   = SlideContainer(
            id="menu_container", slide_direction="left", floating=False
        )

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

    def on_mount(self):

        self.bottom_bar.focus_textarea()

    @on(FigletWidget.Updated)
    def figlet_updated(self, event: FigletWidget.Updated):

        self.size_display_bar.update(
            f"Parent width: {event.parent_width} | "
            f"Size: {event.width}W x {event.height}H | "
            f"Fig max width: {event.fig_width}"
        )

    @on(SlideContainer.SlideCompleted, "#menu_container")
    def slide_completed(self):
        self.on_resize()

    def action_toggle_menu(self):
        self.menu_container.toggle()

    def action_show_help(self):
        self.push_screen(HelpScreen())

# This is for the entry script. Run the demo with:
#$ textual-pyfiglet
def run_demo():
    TextualPyFigletDemo().run()