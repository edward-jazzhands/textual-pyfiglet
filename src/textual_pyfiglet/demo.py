"""Contains the demo app.
This module contains the demo application for PyFiglet.

It has its own entry script. Run with `textual-pyfiglet`.
"""
# Python imports
from typing import cast
# from pathlib import Path
from importlib import resources
import re


# Textual imports
from textual import on
from textual.app import App
# from textual.reactive import reactive
from textual.containers import Horizontal, Container, VerticalScroll, ScrollableContainer
from textual.widget import Widget
from textual.binding import Binding
from textual.screen import ModalScreen
# from textual.geometry import Offset
from textual.validation import Validator, ValidationResult, Number
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
    Markdown,
)

# textual-pyfiglet imports
from textual_pyfiglet.figletwidget import FigletWidget
from textual_pyfiglet.pyfiglet import figlet_format
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
                yield Label(self.label, classes="setting_label")
                yield self.widget                
        elif self.label_position == "under" or isinstance(self.widget, Button):
            yield self.widget
            yield Static("", classes="setting_filler")
            yield Label(self.label, classes="setting_label")
            self.styles.height = 4


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

    colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]

    def validate(self, value: str) -> ValidationResult:

        if value in self.colors:
            return self.success()
        else:
            return self.failure(
                "color must be one of: red, green, blue, yellow, cyan, magenta."
            )

class SettingsWidget(VerticalScroll):

    #* Settings desired:
    # - Set font
    # - Set container width
    # - Set container height
    # - Toggle between absolute and relative width/height
    # - Toggle word wrap on/off
    # - Set justify
    # - Color gradient on/off
    # - Set gradient colors
    # - Animate gradient on/off
    # - Set animation speed('quality')
    # - Kerning if possible

    # BINDINGS = [
    #     Binding("enter", "submit", "Submit settings changes"),
    # ]

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

    current_font = 'standard'       # starting font for the demo
    # font:          reactive[str] = reactive('standard') #! MAKE THIS REACTIVE?


    def __init__(self, figlet_widget: FigletWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.figlet_widget = figlet_widget

    def compose(self):

        self.fonts_list = self.figlet_widget.get_fonts_list()
        self.fonts_list.sort()
        self.font_options = [(font, font) for font in self.fonts_list] 

        self.width_input  = Input(id="width_input", validators=[SizeValidator()], max_length=5)
        self.height_input = Input(id="height_input", validators=[SizeValidator()], max_length=5)
        self.justify_select = Select(self.justifications, id="justify_select", value='center', allow_blank=False)
        self.font_select = Select([], id="font_select", allow_blank=True)  #! explain why not start with a selection.
        self.copy_to_clipboard_button = Button("Copy to clipboard", id="copy_button")
        self.padding_input = Input(value="0", id="padding_input", validators=[Number()], max_length=2)
        self.color1_input = Input(id="color1_input", validators=[ColorValidator()])
        self.color2_input = Input(id="color2_input", validators=[ColorValidator()])

        yield Label("Settings", id="settings_title")
        yield Label("*=details in help (F1)", id="help_label")
        yield SettingBox(self.copy_to_clipboard_button)        
        yield SettingBox(self.font_select, "Font", widget_width=20)
        yield SettingBox(self.width_input, "Width*", widget_width=12)
        yield SettingBox(self.height_input, "Height*", widget_width=12)
        yield SettingBox(self.justify_select, "Justify", widget_width=14)
        yield SettingBox(self.padding_input, "Padding", widget_width=7)
        yield SettingBox(self.color1_input, "Color 1", widget_width=16)
        yield SettingBox(self.color2_input, "Color 2", widget_width=16)

        # yield Button("Set", id="set_button", classes="sidebar_button")

    def on_mount(self):

        # This must be done in on_mount - can't use set_options unless font_select is already mounted.
        self.font_select.set_options(self.font_options)     #~ This is setting the available fonts.
        self.font_select.value = self.current_font          #~ This is setting the font. 


    @on(Input.Submitted, selector="#width_input")
    @on(Input.Blurred, selector="#width_input")
    def width_input_blurred(self, event: Input.Blurred) -> None:
        if not event.validation_result:
            self.log.error("No validation result")
            return

        if event.validation_result.is_valid:          
            self.log(f"Width set to: {event.value}")
            width = self.width_input.value
            height = self.height_input.value
            self.log(f"Setting container size to: ({width} x {height})")

            if width == '':
                self.figlet_widget.styles.width = 'auto'
                self.log(f"Width set to: {self.figlet_widget.styles.width}")
            else:
                # self.figlet_widget.set_styles(f'width: {width};')
                try:
                    self.figlet_widget.styles.width = int(width)
                    self.log(f"Width set to integer: {self.figlet_widget.styles.width}")
                except ValueError:
                    self.figlet_widget.styles.width = width
                    self.log(f"Width set to: {self.figlet_widget.styles.width}")               
        else: 
            failures = event.validation_result.failure_descriptions   
            self.log(f"Invalid width: {failures}")
            # do something here with the failures     

    @on(Input.Submitted, selector="#height_input")
    @on(Input.Blurred, selector="#height_input")
    def height_input_blurred(self, event: Input.Blurred) -> None:
        if not event.validation_result:
            self.log.error("No validation result")
            return
        
        if event.validation_result.is_valid:          
            width = self.width_input.value
            height = self.height_input.value
            self.log(f"Setting container size to: ({width} x {height})")
            
            if height == '':
                self.figlet_widget.styles.height = "auto"
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
            self.log(f"Invalid width: {failures}")
            # do something here with the failures 


    @on(Select.Changed, selector="#justify_select")
    def justify_changed(self, event: Select.Changed) -> None:

        justify_str: str = cast(str, event.value)   #! for type checker

        self.figlet_widget.set_justify(justify_str)
        self.log(f"Justify set to: {event.value}")

    @on(Button.Pressed, selector="#copy_button")
    def copy_text(self):
        self.log("Copying text to clipboard.")
        # self.figlet_widget.copy_figlet_to_clipboard()

    # Because the select box has a default value, this will run on startup, and then set
    # the font to the default selection. You can also set a font in the constructor of the FigletWidget,
    # But for the purposes of the demo I'm not doing that here because this would override the constructor setting.
    @on(Select.Changed, selector="#font_select")           
    def font_changed(self, event: Select.Changed) -> None:

        if event.value == Select.BLANK:
            return
        
        font_str = cast(str, event.value)   #! for type checker
        
        self.figlet_widget.set_font(font_str)
        self.current_font = event.value
        self.log(f"Current font set to: {self.current_font}")    

    @on(Input.Submitted, selector="#padding_input")
    @on(Input.Blurred, selector="#padding_input")
    def padding_input_blurred(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:                            
                self.log(f"Padding set to: {event.value}")
                self.figlet_widget.styles.padding = int(event.value)
            else: 
                failures = event.validation_result.failure_descriptions   
                self.log(f"Invalid padding input: {failures}")

    @on(Input.Submitted, selector="#color1_input")
    @on(Input.Blurred, selector="#color1_input")
    def color1_input_blurred(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:                        
                self.log(f"Color1 set to: {event.value}")
                self.figlet_widget.styles.padding = int(event.value)
            else: 
                failures = event.validation_result.failure_descriptions 
                self.log(f"Invalid padding input: {failures}")         

    @on(Input.Submitted, selector="#color2_input")
    @on(Input.Blurred, selector="#color2_input")
    def color2_input_blurred(self, event: Input.Blurred) -> None:

        if event.validation_result:
            if event.validation_result.is_valid:                        
                self.log(f"Color2 set to: {event.value}")
                self.figlet_widget.styles.padding = int(event.value)
            else: 
                failures = event.validation_result.failure_descriptions 
                self.log(f"Invalid padding input: {failures}")                     



class BottomBar(Horizontal):

    def __init__(self, figlet_widget: FigletWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.figlet_widget = figlet_widget   

    def compose(self):

        self.text_input = TextArea(id="text_input")
        yield self.text_input

    @on(TextArea.Changed)
    async def text_updated(self):
        text = self.text_input.text
        self.figlet_widget.update(text)

        # This just scrolls the text area to the end when the text changes:
        scroll_area = self.app.query_one("#main_window")
        if scroll_area.scrollbars_enabled == (True, False): # Vertical True, Horizontal False
            scroll_area.action_scroll_end()

    def focus_textarea(self):
        
        self.text_input.focus()
        end = self.text_input.get_cursor_line_end_location()
        self.text_input.move_cursor(end)

class TextualPyFigletDemo(App):

    #! Needs better bindings.
    BINDINGS = [
        Binding("ctrl+b", "toggle_menu", "Expand/collapse the menu"),
        Binding("f1", "show_help", "Show help"),
        # ("s", "focus_select", "Focus the font select"),
        # ("t", "focus_text", "Focus the text input"),
    ]

    CSS_PATH = "styles.tcss"
    TITLE = "Textual-PyFiglet Demo"

    figlet_widget = FigletWidget(           #~ <--- This is the main widget.
        "Starter Text",
        id="figlet_widget",
    ) 

    # theme = "gruvbox"

    def on_resize(self):
        self.call_after_refresh(self.figlet_widget.on_resize, caused_by_terminal_resize=True)

    def compose(self):

        # self.title = "Textual-PyFiglet Demo"

        #! this ability should be built into figlet widget
        banner = figlet_format("Textual-PyFiglet", font="smblock")
        self.log(Text.from_markup(f"[bold blue]{banner}"))

        # self.figlet_widget.styles.width = 45    #! Note setting desired width here. CSS works as well.

        self.settings_widget = SettingsWidget(self.figlet_widget)

        self.bottom_bar = BottomBar(self.figlet_widget)
        self.size_display_bar = Static(id="size_display", expand=True)
        self.menu_container = SlideContainer(
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

        # self.settings_widget.width_input.value = "45"   #! Note setting the manual width in the settings widget.

        self.bottom_bar.focus_textarea()

    @on(FigletWidget.Updated)
    def figlet_updated(self, event: FigletWidget.Updated):

        self.log(f"{event.widget} updated")

        self.size_display_bar.update(
            f"Parent width: {event.parent_width} | "
            f"Size: {event.width}W x {event.height}H | "
            f"Fig internal render: {event.fig_width} | "
            f"Fig reported: {event.fig_width_reported}W x {event.fig_height_reported}H"
        )

    @on(SlideContainer.SlideCompleted)
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