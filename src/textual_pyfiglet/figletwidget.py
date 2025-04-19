"""Module for the FigletWidget class.

Import FigletWidget into your project to use it."""

# STANDARD LIBRARY IMPORTS
from __future__ import annotations
from typing import Literal, get_args
import os
import importlib.util
from collections import deque
# import datetime

# Textual and Rich imports
# from textual.app import ComposeResult
# from textual.containers import Center
from textual.strip import Strip
# from textual.widget import Widget
# from textual.widgets import Footer
# from textual.geometry import Region
from textual.color import Gradient, Color
# import textual.events as events
from rich.segment import Segment
from rich.style import Style
# from rich.bar import Bar
from rich.rule import Rule
# from rich.markdown import Markdown
from textual.css.scalar import Scalar, Unit

# For type checking:
from rich.console import RenderableType
from textual.visual import SupportsVisual, Visual #, VisualType


# For the widget:   #! why is this a separate category? Explain
from textual.message import Message
from textual.widgets import Static
from textual.widget import Widget
from textual.reactive import reactive
# from textual.content import Content
# from textual.events import Resize

from rich.text import Text

# Line API stuff
# from rich.segment import Segment      #! why tf is this stuff here again?
# from rich.style import Style
# from textual.strip import Strip
# from textual.widget import Widget
from copy import deepcopy

# Textual-Pyfiglet imports:
from textual_pyfiglet.pyfiglet import Figlet, FigletError
from textual_pyfiglet.pyfiglet.fonts import ALL_FONTS   # not the actual fonts, just the names.

# LITERALS: 
JUSTIFY_OPTIONS = Literal['left', 'center', 'right']

class FigletWidget(Static):


    figlet_input:  reactive[str] = reactive('', always_update=True)     
    font:          reactive[str] = reactive('standard')              
    justify:       reactive[str] = reactive('center')                

    figlet_lines: reactive[list[str]] = reactive(list, layout=True) 

    line_color: reactive[Style] = reactive(Style)   # part of reactive/gradient system (why?)
    line_colors: deque[Style] = deque()       

    target_render_width: reactive[int] = reactive(200, always_update=True)
    "Used to control the figlet's internal render setting."
    # Will trigger the figlet to re-render even if the target has not changed.

    fig_width_reported:  reactive[int] = reactive(0, always_update=True)  # width of figlet_lines
    fig_height_reported: reactive[int] = reactive(0, always_update=True)  # height of figlet_lines
    # The reason the above two reactives are set to always update is that the check to see
    # if the FigletWidget is in auto mode, and to change the size accordingly.

    stored_width_style: Scalar = Scalar(1.0, Unit.AUTO, Unit.AUTO)
    stored_height_style: Scalar = Scalar(1.0, Unit.AUTO, Unit.AUTO)

    size_fully_initialized = False  # Set to true the first time it gets a resize event greater than 0
 
    # Side note: I had to go into the pyfiglet source code to create a setter method for justify
    # to allow changing it in real-time. (It previously only had a getter method).

    DEFAULT_CSS = """
    FigletWidget {
        width: auto;
        height: auto;
        padding: 0;
    }
    """

    base_fonts = [
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

  

    class Updated(Message):
        """This is here to provide a message to the app that the widget has been updated.
        You might need this to trigger something else in your app resizing, adjusting, etc.
        The size of FIG fonts can vary greatly, so this might help you adjust other widgets.
        
        available properties:
        - width (width of the widget)
        - height (height of the widget)
        - fig_width (width render setting of the Pyfiglet object)
        - fig_width_reported (reported width of the rendered ASCII)
        - fig_height_reported (reported height of the rendered ASCII)
        - widget/control (the FigletWidget that was updated)
        """

        def __init__(self, widget: FigletWidget) -> None:
            super().__init__()
            assert isinstance(widget.parent, Widget)

            self.widget = widget
            "The FigletWidget that was updated."
            
            self.width = widget.size.width
            "The width of the widget. This is the size of the widget as it appears to Textual."
            self.height = widget.size.height
            "The height of the widget. This is the size of the widget as it appears to Textual."

            self.parent_width = widget.parent.size.width
            "The width of the parent widget or container that is holding the FigletWidget."

            self.fig_width = widget.figlet.width
            """This is the width of the Pyfiglet object. It's the internal width setting
            Used by the Pyfiglet object to render the text. It's not the same as the widget width."""

            self.fig_width_reported = widget.fig_width_reported
            "This is the actual width of the figlet ASCII after rendering."
            self.fig_height_reported = widget.fig_height_reported
            "This is the actual height of the figlet ASCII after rendering."

        @property
        def control(self) -> FigletWidget:
            return self.widget


    def __init__(
        self,
        content: RenderableType | SupportsVisual = "",
        *,
        font: ALL_FONTS = "standard",
        justify: JUSTIFY_OPTIONS = "center", 
        color1: str | None = None,
        color2: str | None = None,
        animation_quality: int = 30,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """A custom widget for turning text into ASCII art using PyFiglet.

        This class is designed to be an easy drop in replacement for the Static widget.
        The only new argument is 'font', which has a default set to one of the smallest fonts.
        You can replace any Static widget with this and it should work (aside from the size).

        The widget will try to adjust its render area to fit inside of its parent container.
        The easiest way to use this widget is to place it inside of a container.
        Resize the parent container, and then call the `update()` method.

        Args:
            content: A Rich renderable, or string containing console markup.
            font (PyFiglet): Font to use for the ASCII art. Default is "calvin_s".
            justify (PyFiglet): Justification for the text. Default is "center".
            color1 (Gradient): Set color for the figlet - also First color for the gradient
            color2 (Gradient): Second color for the gradient. Unused if None.
            animation_quality: How many colors the animation gradient should have.
            expand: Expand content if required to fill container.
            shrink: Shrink content if required to fill container.
            markup: True if markup should be parsed and rendered.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
            disabled: Whether the static is disabled or not.

        Included fonts:
        - calvin_s
        - chunky
        - cybermedium
        - small_slant
        - small
        - smblock
        - smbraille
        - standard
        - stick_letters
        - tmplr

        Remember you can download more fonts. To download the extended fonts pack:
        pip install textual-pyfiglet[fonts]
        """

        super().__init__(
            name=name, id=id, classes=classes, disabled=disabled, markup=markup
        )
        try:
            string = str(content)
        except Exception as e:
            self.log.error(f"FigletWidget Error converting input to string: {e}")
            raise e

        self.set_reactive(FigletWidget.figlet_input, string)
        self.set_reactive(FigletWidget.font, font)                  
        self.set_reactive(FigletWidget.justify, justify)                
        self.color1 = color1    
        self.color2 = color2
        self.expand = expand        #! are these usable?
        self.shrink = shrink

        self._content = content                  #! explain why these are here.
        self._visual: Visual | None = None       #! They are not used by anything?

        self.set_reactive(FigletWidget.target_render_width, 200)
        self.set_reactive(FigletWidget.fig_width_reported, 0)     
        self.set_reactive(FigletWidget.fig_height_reported, 0)  

        self.modified_by_fig_width_reported = False
        self.modified_by_fig_height_reported = False
        self.render_width_modified = False
  
        #! NOTE: Figlet also has a "direction" argument. Add here?         

        #~ COLORS / GRADIENT ~#

        if color1 and not color2:
            self.color = Color.parse(color1)
        elif color1 and color2:
            self.gradient = self.make_gradient(color1, color2, animation_quality)
        else:
            self.color = None
            self.gradient = None

        if self.color is None and self.gradient is None:                  # if no style,
            # self.line_color = Style()                           # # set to blank / default style
            self.set_reactive(FigletWidget.line_color, Style())   # # set to blank / default style
        if self.color is not None and self.gradient is None:                      # if only color is set,
            self.line_colors = deque([Style(color=self.color.rich_color)])   # # set to the color
        elif self.color is not None and self.gradient is not None:                            # if both are set:
            self.line_colors = deque([Style(color=color.rich_color) for color in self.gradient.colors])  # sets both
            self.set_interval(interval=0.08, callback=self.refresh, repeat=0)   # this makes the gradient animate            
            #! NOTE- the 'interval' variable above should be one of the args for the widget.

        #~ SIZE / STYLE ~#

        if self.styles.width:
            self.stored_width_style = self.styles.width     # the storing is necessary,
        if self.styles.height:                              # have to control size very manually  
            self.stored_height_style = self.styles.height   # because of the LineAPI usage

        width = self.styles.width

        starting_width = 200
        if width:
            if width.is_auto or width.is_fraction or width.is_percent:
                # In auto, fraction, or percent, 
                self.log("Detected width is auto, fraction, or percent. \n"
                         "Setting starting width to 200.")
                starting_width = 200
            elif width.cells:
                self.log(f"Detected width is set to {width.cells} cells. \n"
                         f"Setting starting width to {width.cells}")
                starting_width = width.cells


        self.figlet = Figlet(           #~ <-- Create the PyFiglet object
            font=font,
            justify=justify,
            width=starting_width, 
        )            

    def on_compose(self):

        self.log(
            f"WIDTH SETTING: {self.styles.width} \n"
            f"HEIGHT SETTING: {self.styles.height} \n"
            f"Parent: {self.parent} \n"
        )    

    #####################
    #~ RENDERING LOGIC ~#
    #####################
    
    def render_figlet(self, figlet_input: str) -> list[str]:
        self.log(Text.from_markup("[bold yellow]render_figlet triggered"))

        try:
            figlet_render = self.figlet.renderText(figlet_input)
        except FigletError as e:
            self.log.error(f"Pyfiglet returned an error when attempting to render: {e}")
            raise e
        except Exception as e:
            self.log.error(f"Unexpected error occured when rendering figlet: {e}")
            raise e
        else:
            figlet_lines = figlet_render.splitlines()   # convert into list of lines

            # Add lines only if the line is not all spaces:
            non_blank_lines = [line for line in figlet_lines if not all(c == ' ' for c in line)]
            if non_blank_lines == []:  # if the figlet output is blank, return empty list
                self.log.error("Figlet output was blank. Returning empty list.")
                return ['']

            if self.stored_width_style.is_auto:  # if the width is auto, we need to trim the lines
                startpoints = []
                for line in non_blank_lines:
                    for c in line:
                        if c != ' ':                 # find first character that is not space
                            startpoints.append(line.index(c))           # get the index
                            break              
                figstart = min(startpoints)   # lowest number in this list is the start of the figlet
                shortened_fig = [line[figstart:].rstrip() for line in non_blank_lines]   # cuts before and after
                return shortened_fig
            else:
                return non_blank_lines
            
    # def watch_line_color(self, value: Style) -> None:
    #     pass

    # def render(self) -> Content:
    #     return Content(self.figlet_output)
    
    # def render_lines(self, crop: Region) -> list[Strip]:
    #     if self.gradient:
    #         self.line_colors.rotate()
    #     return super().render_lines(crop)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""
        if y == 0:
            self.log(Text.from_markup("[bold blue]render_line triggered for line 0"))
            self.log(Rule())
        if y >= self.fig_height_reported:           # if the line is out of range, return blank
            return Strip.blank(self.size.width)
        try:
            self.figlet_lines[y]
        except IndexError as e:
            self.log.error(f"render_line failed for line {y} | {e}")
            return Strip.blank(self.size.width)
        else:
            # segments = [Segment(self.figlet_lines[y], style=self.line_colors[y])]
            segments = [Segment(self.figlet_lines[y], style=self.line_color)]
            return Strip(segments)  
        

    def on_resize(self, caused_by_terminal_resize: bool = False) -> None:

        if self.size.width == 0:        # <- this prevents crashing on boot.
            self.log(Text.from_markup("[bold red]on_resize triggered, but size is 0. Returning."))
            return 
        
        if not self.size_fully_initialized:
            self.size_fully_initialized = True

        assert isinstance(self.parent, Widget)  # this is for type hinting.
               
        if self.styles.width and self.styles.height and not caused_by_terminal_resize:

            self.log(
                f"on_resize triggered: \n"
                f"self.size: {self.size} \n"
                f"self.styles.width.unit: {self.styles.width.unit} \n"
                f"self.styles.height.unit: {self.styles.height.unit} \n"
                f"stored_width_style: {self.stored_width_style} \n"
                f"stored_height_style: {self.stored_height_style} \n"
                f"Parent width: {self.parent.size.width} \n"  
                # (Ignore because parent is type hinted as DOMNode, which does not have a size)
                f"fig_width_reported: {self.fig_width_reported} \n"
                f"fig_height_reported: {self.fig_height_reported} \n"
                f"modified_by_fig_width_reported: {self.modified_by_fig_width_reported} \n"
                f"modified_by_fig_height_reported: {self.modified_by_fig_height_reported} \n"
            )
            # The only reason this should ever be in Auto mode is because it was JUST changed to auto.
            # (Or the Figlet Widget was just initialized in auto mode.)
            # The render cycle will change it back to cells automatically.
            # However, if it does get set to Auto manually, it will mess up the size.
            # Thus, check if both the new style and the stored style are Auto.
            # If so, immediately trigger a re-render to reset everything.
            if (self.styles.width.is_auto and self.stored_width_style.is_auto) or \
            (self.styles.height.is_auto and self.stored_height_style.is_auto):
                self.log(Text.from_markup(
                    "[bold red]Detected auto on both stored and new. Triggering re-render."))
                # self.update()
                self.target_render_width = self.parent.size.width 
                return

            new_width_to_store = self._choose_style_to_store(
                used_style_object = self.styles.width, 
                stored_style_object=  self.stored_width_style,
                modified_flag = self.modified_by_fig_width_reported,
                width_or_height_reported= self.fig_width_reported,
                width_or_height = "width"
            )
            if new_width_to_store and new_width_to_store is not True:  # 'not true' is just so
                self.log(Text.from_markup(                             # pylance doesn't complain
                    f"[green]New width to store: [bold red]{new_width_to_store}"
                ))
                self.stored_width_style = new_width_to_store
                
            elif new_width_to_store is False:               # this means not only is there nothing to update,
                self.modified_by_fig_width_reported = False     # we also have to change the flag back.
                self.log(Text.from_markup(
                "[bold purple]Width was modified by self. \n"
                "[italic]modified_by_fig_width_reported[/italic] "
                f"set back to [red]{self.modified_by_fig_width_reported}."
            ))
            else:
                self.log("_choose_style_to_store returned None for width. Passing.")          

            new_height_to_store = self._choose_style_to_store(
                used_style_object = self.styles.height, 
                stored_style_object=  self.stored_height_style,
                modified_flag = self.modified_by_fig_height_reported,
                width_or_height_reported= self.fig_height_reported,
                width_or_height = "height"
            )
            if new_height_to_store and new_height_to_store is not True:
                self.log(Text.from_markup(
                    f"[green]New height to store: [bold red]{new_height_to_store}"
                ))
                self.stored_height_style = new_height_to_store

            elif new_height_to_store is False:
                self.modified_by_fig_height_reported = False
                self.log(Text.from_markup(
                "[bold purple]Height was modified by self. \n"
                "[italic]modified_by_fig_height_reported[/italic] "
                f"set back to [red]{self.modified_by_fig_height_reported}."
            ))            
            else:
                self.log("_choose_style_to_store returned None for height. Passing.")                                        

        # Now that we know our updated stored width, proceed with changing the Figlet.
        # In auto mode, the Figlet's render target is set to the size of whatever
        # container is the parent of the FigletWidget.
        if self.stored_width_style.is_auto:  
            self.log(Text.from_markup(
                "[bold red]Width in Auto mode. Setting render target width to parent width "
                f"of {self.parent.size.width}"))                   
            self.target_render_width = self.parent.size.width    
        # if not in auto, the Figlet's render target is the size of the figlet.
        else:     
            self.log(Text.from_markup(
                "[bold red]Width is NOT Auto mode. Setting render target width to "
                f"size of self at: {self.size.width}"))             
            self.target_render_width = self.size.width 
           
        self.post_message(self.Updated(self))

    def _choose_style_to_store(
            self,
            used_style_object: Scalar,
            stored_style_object: Scalar,
            modified_flag: bool,           # modified_by_fig_width_reported (or height)
            width_or_height_reported,      # self.fig_width_reported or self.fig_height_reported
            width_or_height: str           # this is just for logging
        ) -> Scalar | bool | None:

        # This can only be set to unit.CELLS for one of two reasons. Either
        # the style itself is a number, or we are in auto mode and it was set by self.

        # If we detect it is set to one of the others: Unit.PERCENT, unit.FRACTION, or unit.AUTO:
        # That must be because it was just set to that by the user(app code).
        # So dealing with those is simple - we can just immediately update the stored style.
        # However, things get trickier when the used setting is cells and the stored setting is auto.
        # There we need to track whether it was updated by the class(self), or by the user/app making
        # changes to the widget size.

        # Remember that when set to auto - the FigletWidget will get the rendered width and then 
        # immediately set the width as an integer - so this will only be in AUTO
        # for a split moment before being set back to an integer

        if width_or_height == "width":
            width_or_height_reported += 1

        if used_style_object.is_cells:
            if stored_style_object.is_auto:
                self.log(f"Used {width_or_height} is cells, but stored {width_or_height} is auto. \n"
                         f"Used style: {used_style_object} \n"
                         f"Used style unit: {used_style_object.unit}")
                # so we need to figure out if the cells was changed.

                if used_style_object.cells == width_or_height_reported:
                    # the used size is the same as the reported size
                    # That is correct. Now check if it was recently set to that.
                    if modified_flag:
                        # The size was just updated by the class. Set the flag back.
                        self.log(Text.from_markup(
                            f"[green]Used {width_or_height} is the same as reported {width_or_height} "
                            "(correct), and recently set by FigletWidget. Setting the flag back."
                        ))
                        return False
                    else:
                        # The size was not updated. That must mean nothing changed.
                        self.log(Text.from_markup(
                            f"[green]Used {width_or_height} is the same as reported {width_or_height} "
                            "(correct), but nothing was modified. "
                            "Flag is already False - nothing to set back."
                        ))                        
                        return  # so just pass / return None.
                else:
                    self.log(f"Used {width_or_height} is NOT the same as reported {width_or_height}. Investigating...")
                    # Used is cell mode - stored is auto mode. Yet the current size doesn't match the reported. 
                    if modified_flag:
                        # If the flag passed in is True, it means the class just modified this setting.
                        # Thus, do not update the stored style.
                        self.log(f"The {width_or_height} modified flag is set to {modified_flag}")
                        return False   # False tells it to set the flag back.
                    else:
                        # Used is cell mode, stored is auto mode, and the current size
                        # doesnt' match the reported. Yet the flag has not been set.
                        # this must mean the user just input a number manually.
                        # Update the stored style
                        self.log("Flag is false... the number must have been manually changed to cells. "
                                 f"Returning the new {width_or_height} style object.") 
                        return used_style_object

            # if both new and stored are cells, just update anyway even if they're the same.
            elif stored_style_object.is_cells or \
                stored_style_object.is_fraction or stored_style_object.is_percent:
                self.log(f"New {width_or_height} is cells, and stored {width_or_height} "
                         f"is cells, fraction, or percent. Returning new {width_or_height}. \n")
                return used_style_object   

        # Any other unit, just update the stored width, even if they're the same:
        elif used_style_object.is_auto or \
        used_style_object.is_fraction or used_style_object.is_percent:
            self.log(f"New {width_or_height} is auto, fraction, or percent. "
                     f"Returning new {width_or_height}. \n")
            return used_style_object   

    ##############
    #~ WATCHERS ~#
    ##############

    def watch_font(self, old_value: str, new_value: str) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch_font triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))

        if old_value == new_value:
            self.log("Font has not changed. Returning.")
            return

        try:
            self.figlet.setFont(font=new_value)
        except Exception as e:
            self.log.error(f"Error setting font: {e}")

        self.watch_figlet_input(self.figlet_input, self.figlet_input)   # trigger reactive

    def watch_justify(self, old_value: str, new_value: str) -> None:

        self.log(Text.from_markup(f"[bold yellow]watch_justify triggered.[/bold yellow]\n"
                f"old_value: {old_value} | new_value: {new_value}"))
                
        if old_value == new_value:
            self.log("Justify has not changed. Returning.")
            return

        try:
            self.figlet.justify = new_value
        except Exception as e:
            self.log.error(f"Error setting justify: {e}")

        self.watch_figlet_input(self.figlet_input, self.figlet_input)   # trigger reactive

    def watch_figlet_input(self, old_value, new_value: str) -> None:

        self.log(Text.from_markup(
            "[bold yellow]watch_figlet_input triggered. \n"
            f"[green]Outer widget style width: {self.styles.width} \n"
            f"Outer widget style height: {self.styles.height} \n"
            f"[bold blue]target_render_width: {self.target_render_width}"
            )
        )
        if self.figlet_lines and old_value == new_value and not self.render_width_modified:
            self.log("New figlet input is the same as old. Re-using the rendered figlet.")
            self.fig_width_reported = self.fig_width_reported
            self.fig_height_reported = self.fig_height_reported
            return            
        elif new_value == '':
            self.log("Figlet input is empty.")
            self.figlet_lines = ['']
            self.mutate_reactive(FigletWidget.figlet_lines) 
        else:
            self.figlet_lines = self.render_figlet(new_value)     # <- where the render happens
            self.mutate_reactive(FigletWidget.figlet_lines)

        if self.render_width_modified:
            self.log(Text.from_markup(
                "[bold red]Detected render_width_modified after rendering. Resetting back to False."
            ))
            self.render_width_modified = False

        # If there's a new render, get the new reported sizes.
        try:
            fig_width_reported = max(len(line) for line in self.figlet_lines)
            fig_height_reported = len(self.figlet_lines)                 
        except ValueError:
            self.log.error(f"Error calculating figlet width. Figlet lines: {self.figlet_lines}")
        else:
            self.log(f"Render successful. \nfig_width_reported: {fig_width_reported}\n"
                     f"fig_height_reported: {fig_height_reported}")
            self.fig_width_reported = fig_width_reported
            self.fig_height_reported = fig_height_reported   


    def watch_target_render_width(self, old_value: int, new_value: int) -> None:

        self.log(Text.from_markup(
            f"[bold yellow]watch_target_render_width triggered.[/bold yellow] \n"
            f"old_value: {old_value} | new_value: {new_value}"
        ))
        if new_value != self.figlet.width:
            self.log(Text.from_markup(f"[italic red]Detected target_render_width changed. "
                f"Changing figlet width from {old_value} to {new_value}." ))
            self.render_width_modified = True
            self.figlet.width = new_value
        else:
            self.log(Text.from_markup("watch_target_render_width: [green]New value of "
                f"{new_value} is the same as current setting. Passing."))
            
        self.watch_figlet_input(self.figlet_input, self.figlet_input)   # trigger reactive


    def watch_fig_width_reported(self, old_value: int, new_value: int) -> None:

        if self.styles.width and self.size_fully_initialized:  

            self.log(Text.from_markup(
                "[bold yellow]watch_fig_width_reported triggered[/bold yellow] \n"
                f"old_value: [yellow]{old_value}[/yellow] | new_value: [yellow]{new_value}[/yellow]\n"
                f"self.target_render_width: [yellow]{self.target_render_width}[/yellow] \n"
                f"stored_width_style: [cyan]{self.stored_width_style}[/cyan] \n"
                f"Current width style: {self.styles.width} \n"
                f"Current width cells: {self.styles.width.cells} \n"
            ))              
 
            if self.stored_width_style.is_auto:
                self.log(Text.from_markup(
                    "[italic]Detected width is [cyan]auto[/cyan]. Changing widget width to fig_width_reported."
                ))
                new_value += 1  # add 1 to the new value. Widget needs to be 1 cell larger than the figlet.
         
                if new_value != self.styles.width.cells:
                    self.modified_by_fig_width_reported = True     
                    self.log(Text.from_markup(
                        "[italic red]Detected fig_width_reported is different than used width. Changing "
                        f"width from {self.styles.width} to [/italic red][yellow]{new_value}[/yellow]. \n"
                        f"self.modified_by_fig_width_reported set to {self.modified_by_fig_width_reported}"
                    ))                   
                    self.styles.width = new_value         
                else:
                    self.log("New reported value equals current width setting. Passing.")
            else:
                self.log(Text.from_markup(
                    "watch_fig_width_reported: Detected width is [italic cyan]not auto[/italic cyan]. Passing."
                ))
        else:
            self.log("Size not fully initialized yet...")                 


    def watch_fig_height_reported(self, old_value: int, new_value: int) -> None:

        if self.styles.height and self.size_fully_initialized:  

            self.log(Text.from_markup(
                "[bold yellow]watch_fig_height_reported triggered[/bold yellow] \n"
                f"old_value: [yellow]{old_value}[/yellow] | new_value: [yellow]{new_value}[/yellow]\n"
                f"self.target_render_height: [yellow]{self.target_render_width}[/yellow] \n"
                f"stored_height_style: [cyan]{self.stored_height_style}[/cyan] \n"
                f"Current height style: {self.styles.height} \n"
                f"Current height cells: {self.styles.height.cells} \n"
            ))              
 
            if self.stored_height_style.is_auto:
                self.log(Text.from_markup(
                    "[italic]Detected height is [cyan]auto[/cyan]. Changing widget height to fig_height_reported."
                ))
         
                if new_value != self.styles.height.cells:
                    self.modified_by_fig_height_reported = True     
                    self.log(Text.from_markup(
                        "[italic red]Detected fig_height_reported is different than used height. Changing "
                        f"height from {self.styles.height} to [/italic red][yellow]{new_value}[/yellow]. \n"
                        f"self.modified_by_fig_height_reported set to {self.modified_by_fig_height_reported}"
                    ))                   
                    self.styles.height = new_value         
                else:
                    self.log("New reported value equals current height setting. Passing.")
            else:
                self.log(Text.from_markup(
                    "watch_fig_height_reported: Detected height is [italic cyan]not auto[/italic cyan]. Passing."
                ))
        else:
            self.log("Size not fully initialized yet...")                   

    #####################
    #~ UTILITY METHODS ~#
    #####################

    # (type ignore is because of overriding update in incompatible manner)
    def update(self, new_text: str | None = None) -> None:  # type: ignore
        '''Update the PyFiglet area with the new text.    
        Note that this over-rides the standard update method in the Static widget.   
        Unlike the Static widget, this method does not take a Rich renderable.   
        It can only take a text string. Figlet needs a normal string to work properly.

        Args:
            new_text: The text to update the PyFiglet widget with. Default is None.'''
        
        if new_text is not None:
            self.figlet_input = new_text
        else:
            self.figlet_input = self.figlet_input   # triggers reactive.
            # If the input is the same, it will run through the checks but it
            # won't waste resources re-rendering the figlet.


    def set_font(self, font: str) -> None:
        """Set the font for the PyFiglet widget.   
        The widget will update with the new font automatically.
        
        Pass in the name of the font as a string:
        ie 'calvin_s', 'small', etc.
        
        Args:
            font: The name of the font to set."""
        
        self.font = font


    def set_justify(self, justify: str) -> None:
        """Set the justification for the PyFiglet widget.   
        The widget will update with the new justification automatically.
        
        Pass in the justification as a string:   
        options are: 'left', 'center', 'right', 'auto'
        
        Args:
            justify: The justification to set."""
        
        self.justify = justify

    def get_fonts_list(self) -> list[str]:
        """Scans the fonts folder.   
        Returns a list of all font filenames (without extensions).
        
        Args:
            get_all: If True, returns all fonts. If False, returns only the base fonts."""

        return list(get_args(ALL_FONTS))     # Extract list from the Literal


    # def get_figlet_as_string(self) -> None:
    #     """Return the PyFiglet text as a string."""
    #     # return self.figlet_output
    #     pass
    
    # def copy_figlet_to_clipboard(self) -> None:
    #     """Copy the PyFiglet text to the clipboard."""

    #     figlet_as_string = self.get_figlet_as_string()
    #     self.log(f"Copying PyFiglet text to clipboard: {figlet_as_string}")

    #     self.app.copy_to_clipboard(figlet_as_string)

    def make_gradient(self, color1: str, color2: str, quality: int) -> Gradient:
        "Use color names, ie. 'red', 'blue'"

        parsed_color1 = Color.parse(color1)
        parsed_color2 = Color.parse(color2)

        stop1 = (0.0, parsed_color1)
        stop2 = (0.5, parsed_color2)
        stop3 = (1.0, parsed_color1)
        return Gradient(stop1, stop2, stop3, quality=quality)
    
