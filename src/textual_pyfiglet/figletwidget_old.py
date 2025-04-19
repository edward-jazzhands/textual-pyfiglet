"""Module for the FigletWidget class.

Import FigletWidget into your project to use it."""

# STANDARD LIBRARY IMPORTS
from __future__ import annotations
import os
import importlib.util
from collections import deque
# import datetime

# Textual and Rich imports
from textual.app import ComposeResult
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
from textual.reactive import reactive
# from textual.content import Content
# from textual.events import Resize
# Textual-Pyfiglet imports:
from textual_pyfiglet.pyfiglet import Figlet, FigletError

from rich.text import Text

# Line API stuff
# from rich.segment import Segment      #! why tf is this stuff here again?
# from rich.style import Style
# from textual.strip import Strip
# from textual.widget import Widget

class _InnerFiglet(Static):
    """The Inner Figlet contains the actual PyFiglet class.   
    This nested layout is necessary for things to work properly.   
    This is a private class. Don't use it directly.   
    #? There's a full write-up here: ~[ notes/inner_figlet.md ]~ """

    # The inner figlet should always try to be the same size as the outer widget.
    DEFAULT_CSS = "_InnerFiglet {width: 100%; height: 100%;}"

    figlet_input:  reactive[str] = reactive('', always_update=True)     # changed by outer widget
    font:          reactive[str] = reactive('standard')                 # changed by outer widget
    justify:       reactive[str] = reactive('center')                   # changed by outer widget

    figlet_lines: reactive[list[str]] = reactive(list, layout=True) 

    line_color: reactive[Style] = reactive(Style)   # part of reactive/gradient system (why?)
    line_colors: deque[Style] = deque()       

    target_width: reactive[int] = reactive(200, always_update=True)
    "Used to control the figlet's internal render setting."
    # The above reactive is set to always update because the target width is not the same as the figlet's
    # actual render setting. Even if the target width has not changed, it needs to confirm
    # it is the same as the inner render setting and then post a log message.
    # This is probably not necessary but it helps with my sanity.

    fig_width_reported:  reactive[int] = reactive(0, always_update=True)  # width of figlet_lines
    fig_height_reported: reactive[int] = reactive(0, always_update=True)  # height of figlet_lines
    # The reason the above two reactives are set to always update is that the check to see
    # if it matches the target is done in the outer figlet. So even if the number has not changed
    # in the inner figlet, it needs to trigger the outer watcher to ensure it matches the outer target.
    # This only applies to auto mode.

    # Side note: I had to go into the pyfiglet source code to create a setter method for justify
    # to allow changing it in real-time. (It previously only had a getter method).

    def __init__(
        self,
        outer_widget: FigletWidget,      # (could use .parent, but this gives better type hinting)
        figlet_input: str,        
        font:str,
        justify:str,        
        color: Color | None = None,
        gradient: Gradient | None = None,
        **kwargs
    ) -> None:
        """Private class for the FigletWidget."""
        super().__init__(**kwargs)

        #? NOTE ON CODE BELOW
        # In textual, a child widget is only mounted if the parent widget is already mounted.
        # This means that we know what size the parent widget is when we create the child widget.
        # This allows us to do stuff like set a hard size for what this widget (the child) should be.
        # This is important because the PyFiglet class needs to know what size it should be to render properly.

        self.outer_widget = outer_widget   
        width = outer_widget.styles.width

        starting_width = 200
        if width:
            if width.is_auto or width.is_fraction or width.is_percent:
                # In auto, fraction, or percent, 
                self.log("INNER Detected outer width is auto, fraction, or percent. \n"
                         "Setting starting width to 200.")
                starting_width = 200
            elif width.cells:
                self.log(f"INNER Detected width is set to {width.cells} cells. \n"
                         f"Setting starting width to {width.cells}")
                starting_width = width.cells

        self.log(Text.from_markup(f"[green]STARTING WIDTH: [bold blue]{starting_width}"))

        self.figlet = Figlet(           #~ <-- Create the PyFiglet object
            font=font,
            justify=justify,
            width=starting_width, 
        )  

        # self.font = font
        self.set_reactive(_InnerFiglet.figlet_input, figlet_input)  # Remember: If a reactive is not set
        self.set_reactive(_InnerFiglet.font, font)                  # using this method, its watchers will get
        self.set_reactive(_InnerFiglet.justify, justify)            # called on init. 
        self.set_reactive(_InnerFiglet.fig_width_reported, 0)       # all of these need to be set but not called.
        self.set_reactive(_InnerFiglet.fig_height_reported, 0)      # removing any of these makes the app crash.
        self.color = color
        self.gradient = gradient

        if color is None and gradient is None:                  # if no style,
            # self.line_color = Style()                           # # set to blank / default style
            self.set_reactive(_InnerFiglet.line_color, Style())   # # set to blank / default style
        if color is not None and gradient is None:                      # if only color is set,
            self.line_colors = deque([Style(color=color.rich_color)])   # # set to the color
        elif color is not None and gradient is not None:                            # if both are set:
            self.line_colors = deque([Style(color=color.rich_color) for color in gradient.colors])  # sets both
            self.set_interval(interval=0.08, callback=self.refresh, repeat=0)   # this makes the gradient animate

            #! NOTE- the 'interval' variable above should be one of the args for the widget.

    
    def watch_target_width(self, old_value: int, new_value: int) -> None:

        self.log(Text.from_markup(
            f"[bold yellow]watch_target_width triggered.[/bold yellow] \n"
            f"old_value: {old_value} | new_value: {new_value}"
        ))
        if new_value != self.figlet.width:
            self.log(Text.from_markup(f"[italic red]Detected target(inner) width change. "
                f"Changing figlet width from {old_value} to {new_value}." ))
            self.figlet.width = new_value
            self.watch_figlet_input(self.figlet_input, self.figlet_input)
        else:
            self.log(Text.from_markup("watch_target_width: [green]New value of "
                f"{new_value} is the same as current setting. Passing."))
            
        self.watch_figlet_input(self.figlet_input, self.figlet_input)   # trigger reactive

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
            f"[green]Outer widget style width: {self.outer_widget.styles.width} \n"
            f"Outer widget style height: {self.outer_widget.styles.height} \n"
            f"[bold blue]inner target_width: {self.target_width}"
            )
        )
        if self.figlet_lines and old_value == new_value:
            self.log("New figlet input is the same as old. Re-using the rendered figlet.")
            self.fig_width_reported = self.fig_width_reported
            self.fig_height_reported = self.fig_height_reported
            return            
        elif new_value == '':
            self.log("Figlet input is empty.")
            self.figlet_lines = ['']
            self.mutate_reactive(_InnerFiglet.figlet_lines) 
        else:
            self.figlet_lines = self.render_figlet(new_value)     # <- where the render happens
            self.mutate_reactive(_InnerFiglet.figlet_lines)

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


    def watch_fig_width_reported(self, old_value: int, new_value: int) -> None:
        self.log(Text.from_markup(
            "[bold yellow]watch_fig_width_reported triggered[/bold yellow] \n"
            f"old_value: [yellow]{old_value}[/yellow] | new_value: [yellow]{new_value}[/yellow]\n"
            f"self.target_width: [yellow]{self.target_width}[/yellow] \n"
            f"outer_widget stored_width_style: [cyan]{self.outer_widget.stored_width_style}[/cyan]"
        ))
        if self.outer_widget.stored_width_style.is_auto:
            self.log(Text.from_markup(
                "[italic]Detected width is [cyan]auto[/cyan]. Changing outer widget width to fig_width_reported."
            ))
            # self.outer_widget.styles.width = new_value+1  # need this +1 to give it some breathing room
            self.outer_widget.target_outer_width = new_value+1
        else:
            self.log(Text.from_markup(
                "watch_fig_width_reported: Detected width is [italic cyan]not auto[/italic cyan]. Passing."
            ))

    def watch_fig_height_reported(self, old_value: int, new_value: int) -> None:
        self.log(Text.from_markup(
            "[bold yellow]watch_fig_height_reported triggered[/bold yellow] \n"
            f"old_value: [yellow]{old_value}[/yellow] | new_value: [yellow]{new_value}[/yellow] \n"
            f"outer_widget stored_height_style: [cyan]{self.outer_widget.stored_height_style}[/cyan]"
        ))
        if self.outer_widget.stored_height_style.is_auto:
            self.log(Text.from_markup(
                "[italic]Detected height is [cyan]auto[/cyan]. Changing outer widget height to fig_height_reported."
            ))
            # self.outer_widget.styles.height = new_value
            self.outer_widget.target_outer_height = new_value
        else:
            self.log(Text.from_markup(
                "watch_fig_height_reported: Detected height is [italic cyan]not auto[/italic cyan]. Passing."
            ))            
        
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

            if self.outer_widget.stored_width_style.is_auto:  # if the width is auto, we need to trim the lines
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

class FigletWidget(Static):
    """Adds PyFiglet ability to the Static widget.
    
    See init docstring for more info."""

    DEFAULT_CSS = """
    FigletWidget {
        width: auto;
        height: auto;
        padding: 0;
    }
    """

    if importlib.util.find_spec("textual_pyfiglet_fonts") is not None:
        extended_fonts_installed = True
    else:
        extended_fonts_installed = False

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

    stored_width_style: Scalar = Scalar(1.0, Unit.AUTO, Unit.AUTO)
    stored_height_style: Scalar = Scalar(1.0, Unit.AUTO, Unit.AUTO)

    target_outer_width: reactive[int] = reactive(0, always_update=True)
    target_outer_height: reactive[int] = reactive(0, always_update=True)

    size_fully_initialized = False  # Set to true the first time it gets a resize event greater than 0

    figlet_input:  reactive[str] = reactive('', always_update=True) 
    font:          reactive[str] = reactive('standard')             
    justify:       reactive[str] = reactive('center')               

    class Updated(Message):
        """This is here to provide a message to the app that the widget has been updated.
        You might need this to trigger something else in your app resizing, adjusting, etc.
        The size of FIG fonts can vary greatly, so this might help you adjust other widgets.
        
        available properties:
        - outer_width (width of the outer widget)
        - outer_height (height of the outer widget)
        - inner_width (width of the inner widget)
        - inner_height (height of the inner widget)
        - fig_width (width setting of the Pyfiglet object)
        - fig_width_reported (reported width of the rendered ASCII)
        - fig_height_reported (reported height of the rendered ASCII)
        - widget/control (the FigletWidget that was updated)
        """

        def __init__(self, widget: FigletWidget) -> None:
            super().__init__()
            self.widget = widget
            '''The FigletWidget that was updated.'''
            
            self.outer_width = widget.size.width
            "The width of the outer widget. This is the size of the widget as it appears to Textual."
            self.outer_height = widget.size.height
            "The height of the outer widget. This is the size of the widget as it appears to Textual."

            self.inner_target_width = widget._inner_figlet.target_width
            "The target width of the widget. This is the width that the widget is trying to achieve."
            self.fig_width = widget._inner_figlet.figlet.width
            """This is the width of the Pyfiglet object. It's the internal width setting
            Used by the Pyfiglet object to render the text. It's not the same as the widget width."""

            self.fig_width_reported = widget._inner_figlet.fig_width_reported
            "This is the actual width of the figlet ASCII after rendering."
            self.fig_height_reported = widget._inner_figlet.fig_height_reported
            "This is the actual height of the figlet ASCII after rendering."

        @property
        def control(self) -> FigletWidget:
            return self.widget


    def __init__(
        self,
        content: RenderableType | SupportsVisual = "",
        *,
        font: str = "standard",
        justify: str = "center",
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
        self.stored_text = str(content)
        self.font = font
        self.justify = justify
        self.color1 = color1
        self.color2 = color2
        self.expand = expand        #! are these usable?
        self.shrink = shrink

        self._content = content                  #! explain why these are here.
        self._visual: Visual | None = None       #! They are not used by anything?

        self.set_reactive(FigletWidget.target_outer_width, 0)
        self.set_reactive(FigletWidget.target_outer_height, 0)
        # self.modified_by_inner_figlet = False     # flag used by _choose_style_to_store
        self.modified_by_target_outer_width = False
        self.modified_by_target_outer_height = False

        #! NOTE: Figlet also has a "direction" argument. Add here?         

        if color1 and not color2:
            self.color = Color.parse(color1)
        elif color1 and color2:
            self.gradient = self.make_gradient(color1, color2, animation_quality)
        else:
            self.color = None
            self.gradient = None

        if self.styles.width:
            self.stored_width_style = self.styles.width     # the storing is necessary,
        if self.styles.height:                              # have to control size very manually  
            self.stored_height_style = self.styles.height   # because of the LineAPI usage in Inner Figlet.

    def on_compose(self):

        self.log(
            f"OUTER WIDTH SETTING: {self.styles.width} \n"
            f"OUTER HEIGHT SETTING: {self.styles.height} \n"
            f"Parent: {self.parent}"
        )
        self.log(self.app.console)

    def compose(self) -> ComposeResult:

        self._inner_figlet = _InnerFiglet(
            figlet_input=self.stored_text, 
            outer_widget=self,   
            id='inner_figlet',      
            font=self.font,
            justify=self.justify,
            color = self.color,
            gradient = self.gradient,
        )
        yield self._inner_figlet


    def on_resize(self):

        if self.size.width == 0:        # <- this prevents crashing on boot.
            self.log(Text.from_markup("[bold red]on_resize triggered, but size is 0. Returning."))
            return 
        
        if not self.size_fully_initialized:
            self.size_fully_initialized = True
               
        if self.styles.width and self.styles.height:

            self.log(
                f"on_resize triggered in outer widget: \n"
                f"self.size: {self.size} \n"
                f"self.styles.width.unit: {self.styles.width.unit} \n"
                f"self.styles.height.unit: {self.styles.height.unit} \n"
                f"stored_width_style: {self.stored_width_style} \n"
                f"stored_height_style: {self.stored_height_style} \n"
                f"target_outer_width: {self.target_outer_width} \n"
                f"target_outer_height: {self.target_outer_height} \n"
                f"Parent width: {self.parent.size.width} \n"  #type: ignore
                # (Ignore because parent is type hinted as DOMNode, which does not have a size) 
                f"modified_by_target_outer_width: {self.modified_by_target_outer_width} \n"
                f"modified_by_target_outer_height: {self.modified_by_target_outer_height} \n"
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
                self._inner_figlet.target_width = self.parent.size.width #type: ignore
                return

            new_width_to_store = self._choose_style_to_store(
                used_style_object = self.styles.width, 
                stored_style_object=  self.stored_width_style,
                modified_flag = self.modified_by_target_outer_width,
                target_size = self.target_outer_width,
                width_or_height = "width"
            )
            if new_width_to_store and new_width_to_store is not True:  # 'not true' is just so
                self.log(Text.from_markup(                             # pylance doesn't complain
                    f"[green]New width to store: [bold red]{new_width_to_store}"
                ))
                self.stored_width_style = new_width_to_store
                self.set_reactive(FigletWidget.target_outer_width, 0)  # this is so we know its not in use.
                
            elif new_width_to_store is False:               # this means not only is there nothing to update,
                self.modified_by_target_outer_width = False     # we also have to change the flag back.
                self.log(Text.from_markup(
                "[bold purple]Width was modified by Inner Figlet. \n"
                "[italic]modified_by_target_outer_width[/italic] "
                f"set back to [red]{self.modified_by_target_outer_width}."
            ))
            else:
                self.log("_choose_style_to_store returned None for width. Passing.")          

            new_height_to_store = self._choose_style_to_store(
                used_style_object = self.styles.height, 
                stored_style_object=  self.stored_height_style,
                modified_flag = self.modified_by_target_outer_height,
                target_size = self.target_outer_height,
                width_or_height = "height"
            )
            if new_height_to_store and new_height_to_store is not True:
                self.log(Text.from_markup(
                    f"[green]New height to store: [bold red]{new_height_to_store}"
                ))
                self.stored_height_style = new_height_to_store
                self.set_reactive(FigletWidget.target_outer_height, 0)

            elif new_height_to_store is False:
                self.modified_by_target_outer_height = False
                self.log(Text.from_markup(
                "[bold purple]Height was modified by Inner Figlet. \n"
                "[italic]modified_by_target_outer_height[/italic] "
                f"set back to [red]{self.modified_by_target_outer_height}."
            ))            
            else:
                self.log("_choose_style_to_store returned None for height. Passing.")                                        

        # Now that we know our updated stored width, proceed with changing the Inner Figlet.
        # In auto mode, the InnerFiglet's render target is set to the size of whatever
        # container is the parent of the FigletWidget.
        if self.stored_width_style.is_auto:  
            self.log(Text.from_markup(
                "[bold red]Auto mode. Setting target width to parent width "
                f"of {self.parent.size.width}"))      #type: ignore  
            self._inner_figlet.target_width = self.parent.size.width    #type: ignore
        # if not in auto, the InnerFiglet's render target is the size of the outer figlet.
        else:     
            self.log(Text.from_markup(
                "[bold red]NOT Auto mode. Setting target width to "
                f"size of self at: {self.size.width}"))             
            self._inner_figlet.target_width = self.size.width 
           
        self.post_message(self.Updated(self))

    def _choose_style_to_store(
            self,
            used_style_object: Scalar,
            stored_style_object: Scalar,
            modified_flag: bool,           # modified_by_target_outer_width (or height)
            target_size: int,              # target_outer_width (or height)
            width_or_height: str           # this is just for logging
        ) -> Scalar | bool | None:

        # This can only be set to unit.CELLS for one of two reasons. Either
        # the style itself is a number, or we are in auto mode and it was set by the InnerFiglet.

        # If we detect it is set to one of the others: Unit.PERCENT, unit.FRACTION, or unit.AUTO:
        # That must be because it was just set to that by the user(app code).
        # So dealing with those is simple - we can just immediately update the stored style.
        # However, things get trickier when the used setting is cells and the stored setting is auto.
        # There we need to track whether it was updated by the Inner Figlet, or by the user/app making
        # changes to the widget size.

        # Remember that when set to auto - the InnerFiglet will get the rendered width and then 
        # immediately set the target outer width as an integer - so this will only be in AUTO
        # for a split moment before being set back to an integer

        if used_style_object.is_cells:
            if stored_style_object.is_auto:
                self.log(f"Used {width_or_height} is cells, but stored {width_or_height} is auto. \n"
                         f"Used style: {used_style_object} \n"
                         f"Used style unit: {used_style_object.unit}")
                # so we need to figure out if the cells was changed.

                if used_style_object.cells == target_size:
                    # the used size is the same as the outer target size
                    # That is correct. Now check if it was recently set to that.
                    if modified_flag:
                        # The target size was just updated by the inner figlet. Set the flag back.
                        self.log(Text.from_markup(
                            "[green]Used style is the same as target size (correct), and recently set by target. "
                            "Setting the flag back."
                        ))
                        return False
                    else:
                        # The target size was not updated. That must mean nothing changed.
                        self.log(Text.from_markup(
                            "[green]Used style is the same as target size (correct), but target wasn't modified. "
                            "Flag is already False - nothing to set back."
                        ))                        
                        return  # so just pass / return None.
                else:
                    self.log("Used style is NOT the same as target size. Investigating...")
                    # Used is cell mode - stored is auto mode. Yet the current size doesn't match the target. 
                    if modified_flag:
                        # If the flag passed in is True, it means the Inner Figlet just modified this setting.
                        # Thus, do not update the stored style.
                        self.log(f"The {width_or_height} modified flag is set to {modified_flag}")
                        return False   # False tells it to set the flag back.
                    else:
                        # Used is cell mode, stored is auto mode, and the current size
                        # doesnt' match the target. Yet the flag has not been set.
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
                   

    def watch_target_outer_width(self, old_value: int, new_value: int) -> None:
        "This will only be triggered by the InnerFiglet if the stored_width_style is auto."

        self.log(Text.from_markup(
            "[bold yellow]watch_target_outer_width triggered:[/bold yellow]\n"
            f"Old value: [yellow]{old_value}[/yellow] | New value: [yellow]{new_value}[/yellow] \n"
            f"self.modified_by_target_outer_width: {self.modified_by_target_outer_width}"
        ))
        if self.modified_by_target_outer_width:
            self.log.error("Warning: modified_by_target_outer_width should not be True going in")
        if not self.stored_width_style.is_auto:
            self.log.error("Warning: stored_width_style should be auto going in")

        if self.styles.width and self.size_fully_initialized:
            self.log(
                f"Current width style: {self.styles.width} \n"
                f"Stored width style: {self.stored_width_style} \n"
                f"Current width cells: {self.styles.width.cells} \n"
                f"Current width value: {self.styles.width.value} \n"
                f"Actual width: {self.size.width}"
            )            
            if new_value != self.styles.width.cells:
                self.modified_by_target_outer_width = True     
                self.log(Text.from_markup(
                    "[italic red]Detected target (outer) width is different than used width. Changing "
                    f"width from {self.styles.width} to new target of [/italic red][yellow]{new_value}[/yellow]. \n"
                    f"self.modified_by_target_outer_width set to {self.modified_by_target_outer_width}"
                ))                   
                self.styles.width = new_value         
            else:
                self.log("New target (outer) value equals current width setting. Passing.")
        else:
            self.log("Size not fully initialized yet...")                  

    def watch_target_outer_height(self, old_value: int, new_value: int) -> None:
        "This will only be triggered by the InnerFiglet if the stored_height_style is auto."

        self.log(Text.from_markup(
            "[bold yellow]watch_target_outer_height triggered:[/bold yellow] \n"
            f"Old value: [yellow]{old_value}[/yellow] | New value: [yellow]{new_value}[/yellow] \n"
            f"self.modified_by_target_outer_height: {self.modified_by_target_outer_height}"
        ))
        if self.modified_by_target_outer_height:
            self.log.error("Warning: modified_by_target_outer_height should not be True going in")
        if not self.stored_height_style.is_auto:
            self.log.error("Warning: stored_width_style should be auto going in")

        if self.styles.height and self.size_fully_initialized:
            self.log(
                f"Current height style: {self.styles.height} \n"
                f"Stored height style: {self.stored_height_style} \n"
                f"Current height cells: {self.styles.height.cells} \n"
                f"Current height value: {self.styles.height.value} \n"
                f"Actual height: {self.size.height}"
                )                 
            if new_value != self.styles.height.cells:
                self.modified_by_target_outer_height = True     
                self.log(Text.from_markup(
                    "[italic red]Detected target (outer) height is different than used height. Changing "
                    f"height from {self.styles.height} to new target of [/italic red][yellow]{new_value}[/yellow]. \n"
                    f"self.modified_by_target_outer_height set to {self.modified_by_target_outer_height}"
                ))                 
                self.styles.height = new_value           
            else:
                self.log("New target (outer) value equals current height setting. Passing.")
        else:
            self.log("Size not fully initialized yet...")         


    # (type ignore is because of overriding update in incompatible manner)
    def update(self, new_text: str | None = None) -> None:  # type: ignore
        '''Update the PyFiglet area with the new text.    
        Note that this over-rides the standard update method in the Static widget.   
        Unlike the Static widget, this method does not take a Rich renderable.   
        It can only take a text string. Figlet needs a normal string to work properly.

        Args:
            new_text: The text to update the PyFiglet widget with. Default is None.'''
        
        if new_text is not None:
            self.stored_text = new_text

        self._inner_figlet.figlet_input = self.stored_text


    def set_font(self, font: str) -> None:
        """Set the font for the PyFiglet widget.   
        The widget will update with the new font automatically.
        
        Pass in the name of the font as a string:
        ie 'calvin_s', 'small', etc.
        
        Args:
            font: The name of the font to set."""
        
        self._inner_figlet.font = font


    def set_justify(self, justify: str) -> None:
        """Set the justification for the PyFiglet widget.   
        The widget will update with the new justification automatically.
        
        Pass in the justification as a string:   
        options are: 'left', 'center', 'right', 'auto'
        
        Args:
            justify: The justification to set."""
        
        self._inner_figlet.justify = justify

    def get_fonts_list(self, get_all: bool = True) -> list[str]:
        """Scans the fonts folder.   
        Returns a list of all font filenames (without extensions).
        
        Args:
            get_all: If True, returns all fonts. If False, returns only the base fonts."""

        if not get_all:
            return self.base_fonts
        
        fonts_list = []
        fonts_list.extend(self.base_fonts)

        if self.extended_fonts_installed:
            import textual_pyfiglet_fonts

            # get the path of the fonts package:
            fonts_module_path = os.path.dirname(textual_pyfiglet_fonts.__file__) 

            # add extended fonts to the list:
            for font_file in os.listdir(fonts_module_path):
                if os.path.isdir(os.path.join(fonts_module_path, font_file)):
                    continue        # skip directories
                if font_file.endswith('.flf') or font_file.endswith('.tlf'):
                    fonts_list.append(os.path.splitext(font_file)[0])
                
        return fonts_list


    # def get_figlet_as_string(self) -> None:
    #     """Return the PyFiglet text as a string."""
    #     # return self._inner_figlet.figlet_output
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
    
