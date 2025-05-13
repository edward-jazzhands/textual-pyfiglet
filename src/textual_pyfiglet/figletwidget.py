"""Module for the FigletWidget class."""

# ~ Type Checking (Pyright and MyPy) - Strict Mode
# ~ Linting - Ruff
# ~ Formatting - Black - max 110 characters / line

# STANDARD LIBRARY IMPORTS
from __future__ import annotations

from typing import cast
from typing_extensions import Literal, get_args
from collections import deque

# Textual and Rich imports
from textual.strip import Strip
from textual.color import Gradient, Color
from textual.css.scalar import Scalar
from textual.geometry import Size, Region
from textual.message import Message

# from textual.widgets import Static
from textual.widget import Widget
from textual.reactive import reactive
from textual.timer import Timer
from rich.segment import Segment
from rich.style import Style

# Textual-Pyfiglet imports:
from rich_pyfiglet.pyfiglet import (
    Figlet,
    FigletError,
    figlet_format,  # type: ignore[unused-ignore]
)
from rich_pyfiglet.pyfiglet.fonts import ALL_FONTS  # not the actual fonts, just the names.

#! NOTE ON TYPE IGNORE:
# The original Pyfiglet package (Which is contained inside Rich-Pyfiglet as a subpackage),
# is not type hinted. In fact it was written long before type hinting was a thing.
# In the future it is a goal to add type hinting to the entire Pyfiglet subpackage.
# This is the only ignore in the entire Textual-Pyfiglet part of the codebase.
# Also, the [unused-ignore] tag is because Pyright and MyPy disagree on whether the
# ignore statement is necessary. Its a hack to make MyPy ignore the ignore.

# LITERALS:
JUSTIFY_OPTIONS = Literal["left", "center", "right", "auto"]
COLOR_MODE = Literal["color", "gradient", "none"]


class FigletWidget(Widget):

    DEFAULT_CSS = "FigletWidget {width: auto; height: auto;}"

    ###################################
    # ~ Public API Class Attributes ~ #
    ###################################
    fonts_list: list[str] = list(get_args(ALL_FONTS))

    ############################
    # ~ Public API Reactives ~ #
    ############################
    text_input: reactive[str] = reactive[str]("", always_update=True)
    """The text to render in the Figlet widget. You can set this directly, or use
    the update() method to set it."""

    color1: reactive[str | None] = reactive[str | None](None, always_update=True)
    """The first color to use for the gradient. This is either a string that can be parsed by a
    Textual Color object, or `None`."""

    color2: reactive[str | None] = reactive[str | None](None, always_update=True)
    """The second color to use for the gradient. This is either a string that can be parsed by a
    Textual Color object, or `None`."""

    animated: reactive[bool] = reactive[bool](False, always_update=True)
    """Whether to animate the gradient. This is a boolean value. If True, the gradient will
    animate."""

    font: reactive[ALL_FONTS] = reactive[ALL_FONTS]("ansi_regular", always_update=True)
    """The font to use for the Figlet widget. The reactive attribute takes a string
    literal type in order to provide auto-completion and type hinting. The font must be
    one of the available fonts in the Pyfiglet package. You can also use the set_font()
    method to set the font using a string. This is useful for passing in a variable."""

    justify: reactive[JUSTIFY_OPTIONS] = reactive[JUSTIFY_OPTIONS]("auto", always_update=True)
    """The justification to use for the Figlet widget. The reactive attribute takes a string
    literal type in order to provide auto-completion and type hinting. The justification
    must be one of the available justifications in the Pyfiglet package. You can also use
    the set_justify() method to set the justification using a string. This is useful for
    passing in a variable."""

    animation_interval: reactive[float] = reactive[float](0.08, always_update=True)
    """The interval between frames of the animation. This is a float value that represents
    the time in seconds. The default is 0.08 seconds."""

    gradient_quality: reactive[str | int] = reactive[str | int]("auto", always_update=True)
    """The quality of the gradient. This is either a string that can be 'auto' or an integer
    between 3 and 100. The default is 'auto', which will set the quality to the number of
    lines in the widget. If you set this to an integer, it will be used as the number of
    colors in the gradient. The higher the number, the smoother the gradient will be."""

    #########################
    # ! Private Reactives ! #
    #########################
    _figlet_lines: reactive[list[str]] = reactive(list, layout=True)
    _color_mode: reactive[COLOR_MODE] = reactive[COLOR_MODE]("none", always_update=True)

    class Updated(Message):
        """This is here to provide a message to the app that the widget has been updated.
        You might need this to trigger something else in your app resizing, adjusting, etc.
        The size of FIG fonts can vary greatly, so this might help you adjust other widgets.

        available properties:
        - width (width of the widget)
        - height (height of the widget)
        - fig_width (width render setting of the Pyfiglet object)
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

            self.width_setting = widget.figlet.width
            """This is the max width setting of the Pyfiglet object. It's the internal width setting
            used by the Pyfiglet object to render the text. It's not the same as the widget width."""

        @property
        def control(self) -> FigletWidget:
            return self.widget

    def __init__(
        self,
        text: str = "",
        *,
        font: ALL_FONTS = "standard",
        justify: JUSTIFY_OPTIONS = "auto",
        color1: str | None = None,
        color2: str | None = None,
        animate: bool = False,
        gradient_quality: str | int = "auto",
        animation_interval: float = 0.08,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Create a FigletWidget.

        Args:
            text: Text to render in the Figlet widget.
            font (PyFiglet): Font to use for the ASCII art. Default is "standard".
            justify (PyFiglet): Justification for the text. Default is "auto".
                (The auto mode will switch to right if the direction is right-to-left.)
            color1 (Gradient): Set color for the figlet - also First color for the gradient
            color2 (Gradient): Second color for the gradient. Unused if None.
            animate: Whether to animate the gradient.
            gradient_quality: How many colors the animation gradient should have.
                Default is "auto", which will set the quality to the number of lines in the widget.
            animation_interval: How long to wait between frames of the animation, in seconds.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
        """
        # NOTE: The FigletWidget has to wait to be fully mounted before
        # it can know its maximum width and set the render size.
        # This is because in modes 'auto', 'percent', and 'fraction', PyFiglet needs to
        # know the maximum width of the widget to render the text properly.

        # When the widget receives its first on_resize event (The first time it learns
        # what its proper size will be), it will set the render size.
        # If in auto mode, the max render size is the width of whatever is the
        # parent of the FigletWidget in the DOM. If not in auto, the max render size is
        # the width of the widget itself. (So for example if the widget is set to 1fr,
        # when it finally receives its first resize event, it will check its actual width
        # in cells and then set the maximum render size to that number.)

        super().__init__(name=name, id=id, classes=classes)

        self._initialized = False
        self.figlet = Figlet()  # type: ignore[no-untyped-call]

        self._color1_obj: Color | None = None
        self._color2_obj: Color | None = None
        self._line_colors: deque[Style] = deque([Style()])
        self._gradient: Gradient | None = None
        self._interval_timer: Timer | None = None
        self._previous_height: int = 0
        self._size_mode = "auto"  # This is set to auto or not_auto in the refresh_size() method.

        self.set_reactive(FigletWidget._color_mode, "none")
        self.set_reactive(FigletWidget.animated, animate)
        self.set_reactive(FigletWidget.animation_interval, animation_interval)
        self.set_reactive(FigletWidget.gradient_quality, gradient_quality)

        try:
            string = str(text)
        except Exception as e:
            self.log.error(f"FigletWidget Error converting input to string: {e}")
            raise e

        self.set_reactive(FigletWidget.text_input, string)
        self.text_input = string
        self.font = font
        self.justify = justify
        self.color1 = color1
        self.color2 = color2

    #################
    # ~ Public API ~#
    #################

    def update(self, text: str) -> None:
        """Update the PyFiglet area with new text. You can tie this into a user input
        for real-time updating (or set `text_input` directly).
        Args:
            new_text: The text to update the PyFiglet widget with."""

        self.text_input = text

    def set_text(self, text: str) -> None:
        """Alias for the update() method. This is here for convenience.
        Args:
            new_text: The text to update the PyFiglet widget with."""

        self.text_input = text

    def set_justify(self, justify: str) -> None:
        """Set the justification of the PyFiglet widget.
        This method, unlike the setting the reactive property, allows passing in a string
        instead of a string literal type. This is useful for passing in a variable.
        Args:
            justify: The justification to set. Can be 'left', 'center', 'right', or 'auto'."""

        self.justify = cast(JUSTIFY_OPTIONS, justify)  # the validate methods handle this afterwards.

    def set_font(self, font: str) -> None:
        """Set the font of the PyFiglet widget.
        This method, unlike setting the reactive property, allows passing in a string
        instead of a string literal type. This is useful for passing in a variable.
        Args:
            font: The font to set. Must be one of the available fonts."""

        self.font = cast(ALL_FONTS, font)

    def toggle_animated(self) -> None:
        """Toggle the animated state of the PyFiglet widget.
        The widget will update with the new animated state automatically."""

        self.animated = not self.animated

    def get_figlet_as_string(self) -> str:
        """Return the PyFiglet render as a string."""

        return self.figlet_render

    @classmethod
    def figlet_quick(
        cls, text: str, font: ALL_FONTS = "standard", width: int = 80, justify: JUSTIFY_OPTIONS = "auto"
    ) -> str:
        """This is a standalone class method. It just provides quick access to the figlet_format
        function in the pyfiglet package.
        It also adds type hinting / auto-completion for the fonts list."""
        return str(
            figlet_format(text=text, font=font, width=width, justify=justify)  # type: ignore[no-untyped-call]
        )

    #################
    # ~ Validators ~#
    #################

    def validate_text_input(self, text: str) -> str:

        # must use assert here - Pylance does not like using an isinstance check.
        assert isinstance(text, str), "Figlet input must be a string."
        return text

    def validate_font(self, font: ALL_FONTS) -> ALL_FONTS:

        if font in self.fonts_list:
            return font
        else:
            raise ValueError(f"Invalid font: {font} \nMust be one of the available fonts.")

    def validate_justify(self, value: str) -> str:

        if value in ("left", "center", "right", "auto"):
            return value
        else:
            raise ValueError(
                f"Invalid justification: {value} \nMust be 'left', 'center', 'right', or 'auto'."
            )

    def validate_color1(self, color: str | None) -> str | None:

        if color is not None:
            try:
                self._color1_obj = Color.parse(color)  # Check if the color is valid
            except Exception as e:
                self.log.error(f"Error parsing color: {e}")
                raise e
        return color

    def validate_color2(self, color: str | None) -> str | None:

        if color is not None:
            try:
                self._color2_obj = Color.parse(color)  # Check if the color is valid
            except Exception as e:
                self.log.error(f"Error parsing color: {e}")
                raise e
        return color

    def validate_gradient_quality(self, quality: str | int) -> str | int:

        if quality == "auto":
            return quality
        elif isinstance(quality, int):
            if 3 <= quality <= 100:
                return quality
            else:
                raise ValueError("Gradient quality must be between 3 and 100.")
        else:
            raise Exception("Invalid gradient quality. Must be 'auto' or an integer between 1 and 100.")

    def validate_animation_interval(self, interval: float) -> float:

        if 0.01 <= interval <= 1.0:
            return interval
        else:
            raise ValueError("Animation interval must be between 0.01 and 1.0 seconds.")

    ###############
    # ~ Watchers ~#
    ###############

    def watch_text_input(self, text: str) -> None:

        # Initializing check
        if not self._initialized:
            if not self._figlet_lines:
                if text == "":
                    self._figlet_lines = [""]
                    self.mutate_reactive(FigletWidget._figlet_lines)
                else:
                    self._figlet_lines = self.render_figlet(text)  # Initial render
                    self.mutate_reactive(FigletWidget._figlet_lines)
            # If not initialized BUT we have _figlet_lines, that means we have our
            # initial render we need to calculate the sizes. So don't render again:
            return

        # Normal run-time
        if text == "":
            self._figlet_lines = [""]
            self.mutate_reactive(FigletWidget._figlet_lines)
        else:
            self._figlet_lines = self.render_figlet(text)  # ~ <- where the rendering happens
            self.mutate_reactive(FigletWidget._figlet_lines)

        self.post_message(self.Updated(self))

    def watch__color_mode(self, color_mode: COLOR_MODE) -> None:

        if color_mode == "none":
            self._line_colors = deque([Style()])
            self._gradient = None  # reset the gradient if it was set

        elif color_mode == "color":

            color_obj = self._color1_obj or self._color2_obj
            if color_obj is None:
                raise ValueError("Color mode is set to color, but no colors are set.")

            self._line_colors = deque([Style(color=color_obj.rich_color)])
            self._gradient = None  # reset the gradient if it was set

        elif color_mode == "gradient":
            if self.gradient_quality == "auto":
                gradient_quality = len(self._figlet_lines) * 2
            elif isinstance(self.gradient_quality, int):
                gradient_quality = self.gradient_quality
            else:
                raise ValueError("Invalid animation quality. Must be 'auto' or an integer.")

            try:
                assert (
                    self._color1_obj and self._color2_obj
                ), "Color mode is set to gradient, but colors are not set."
                self._gradient = self.make_gradient(self._color1_obj, self._color2_obj, gradient_quality)
            except Exception as e:
                self.log.error(f"Error creating gradient: {e}")
                raise e
            else:
                assert self._gradient is not None, "Gradient was not created. This should not happen."
                self._line_colors = deque([Style(color=color.rich_color) for color in self._gradient.colors])
        else:
            raise ValueError(f"Invalid color mode: {color_mode}")

        if self._initialized:
            self.post_message(self.Updated(self))

    def watch_color1(self, color1: str | None) -> None:

        # These two methods (watch__color1 and watch__color2) only exist to set the
        # color mode. This allows it to use *either* color1 or color2 to set the mode.
        # It will still go into color mode regardless of which color is set.

        # The logic to actually set the color is in the watch__color_mode method.
        # If we simply change from one color to another, the mode will stay the same,
        # ('color' mode), but it will still trigger the watch__color_mode method
        # because it is set to always_update=True.
        # Likewise, if we're changing one color in a gradient, the mode will remain as
        # 'gradient', but it will still trigger the watch__color_mode and update the gradient.

        if color1 and not self._color1_obj:
            raise AssertionError("Color1 is set, but color1_obj is None. This should not happen.")

        if not color1:
            if not self._color2_obj:
                self._color_mode = "none"
            else:
                _color2_obj = self._color2_obj
                self._color_mode = "color"
        else:
            if not self._color2_obj:
                self._color_mode = "color"
            else:
                self._color_mode = "gradient"

    def watch_color2(self, color2: str | None) -> None:

        if color2 and not self._color2_obj:
            raise AssertionError("Color2 is set, but color2_obj is None. This should not happen.")

        if not color2:
            if not self._color1_obj:
                self._color_mode = "none"
            else:
                self._color_mode = "color"
        else:
            if not self._color1_obj:
                self._color_mode = "color"
            else:
                self._color_mode = "gradient"

    def watch_animated(self, animated: bool) -> None:

        if animated:
            if self._interval_timer:
                self._interval_timer.resume()
            else:
                self._interval_timer = self.set_interval(
                    interval=self.animation_interval, callback=self.refresh
                )
        else:
            if self._interval_timer:
                self._interval_timer.stop()
                self._interval_timer = None

        if self._initialized:
            self.post_message(self.Updated(self))

    def watch_font(self, font: str) -> None:

        try:
            self.figlet.setFont(font=font)
        except Exception as e:
            self.log.error(f"Error setting font: {e}")
            raise e

        if self._initialized:
            self.watch_text_input(self.text_input)  # trigger reactive

    def watch_justify(self, justify: str) -> None:

        try:
            self.figlet.justify = justify
        except Exception as e:
            self.log.error(f"Error setting justify: {e}")
            raise e

        if self._initialized:
            self.watch_text_input(self.text_input)  # trigger reactive

    def watch_animation_interval(self) -> None:

        if self.animated:
            self.animated = False  # Stop the animation if it was running.
            self.animated = True  # Restart the animation with the new interval.

    def watch_gradient_quality(self) -> None:

        self._color_mode = self._color_mode  #! This logic chain could really use explaining.

    #####################
    # ~ RENDERING LOGIC ~#
    #####################

    def make_gradient(self, color1_obj: Color, color2_obj: Color, quality: int) -> Gradient:
        "Use color names, ie. 'red', 'blue'"

        stop1 = (0.0, color1_obj)  # 3 stops so that it fades in and out.
        stop2 = (0.5, color2_obj)
        stop3 = (1.0, color1_obj)
        return Gradient(stop1, stop2, stop3, quality=quality)

    def on_resize(self) -> None:
        self.refresh_size()

    def refresh_size(self) -> None:

        if self.size.width == 0 or self.size.height == 0:  # <- this prevents crashing on boot.
            return

        assert isinstance(self.parent, Widget)  # This is for type hinting.
        assert isinstance(self.styles.width, Scalar)  # These should always pass if it reaches here.

        if self.styles.width.is_auto:
            self.size_mode = "auto"
            self.figlet.width = self.parent.size.width
        # if not in auto, the Figlet's render target is the size of the figlet.
        else:
            self.size_mode = "not_auto"
            self.figlet.width = self.size.width

        if not self._initialized:
            self._initialized = True
            self.call_after_refresh(lambda: setattr(self, "animated", self.animated))

        self.text_input = self.text_input  # trigger the reactive to update the figlet.

        # This will make it recalculate the gradient only when the height changes:
        if self.size.height != self._previous_height:
            self._previous_height = self.size.height
            self._color_mode = self._color_mode

    # These two functions below are the secret sauce to making the auto sizing work.
    # They are both over-rides, and they are called by the Textual framework
    # to determine the size of the widget.
    def get_content_width(self, container: Size, viewport: Size) -> int:

        if self._figlet_lines:
            return len(max(self._figlet_lines, key=len))
        else:
            return 0

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:

        if self._figlet_lines:
            return len(self._figlet_lines)
        else:
            return 0

    def render_figlet(self, text_input: str) -> list[str]:

        try:
            self.figlet_render = str(self.figlet.renderText(text_input))  # * <- Actual render happens here.
        except FigletError as e:
            self.log.error(f"Pyfiglet returned an error when attempting to render: {e}")
            raise e
        except Exception as e:
            self.log.error(f"Unexpected error occured when rendering figlet: {e}")
            raise e
        else:
            render_lines: list[str] = self.figlet_render.splitlines()  # convert into list of lines

            while True:
                lines_cleaned: list[str] = []
                for i, line in enumerate(render_lines):
                    if i == 0 and all(c == " " for c in line):  # if first line and blank
                        pass
                    elif i == len(render_lines) - 1 and all(c == " " for c in line):  # if last line and blank
                        pass
                    else:
                        lines_cleaned.append(line)

                if lines_cleaned == render_lines:  # if there's no changes,
                    break  # loop is done
                else:  # If lines_cleaned is different, that means there was
                    render_lines = (
                        lines_cleaned  # a change. So set render_lines to lines_cleaned and restart loop.
                    )

            if lines_cleaned == []:  # if the figlet output is blank, return empty list
                return [""]

            if (
                self.styles.width and self.styles.width.is_auto
            ):  # if the width is auto, we need to trim the lines
                startpoints: list[int] = []
                for line in lines_cleaned:
                    for c in line:
                        if c != " ":  # find first character that is not space
                            startpoints.append(line.index(c))  # get the index
                            break
                figstart = min(startpoints)  # lowest number in this list is the start of the figlet
                shortened_fig = [line[figstart:].rstrip() for line in lines_cleaned]  # cuts before and after
                return shortened_fig
            else:
                return lines_cleaned

    def render_lines(self, crop: Region) -> list[Strip]:
        if self._gradient and self.animated:
            self._line_colors.rotate()
        return super().render_lines(crop)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        if y >= len(self._figlet_lines):  # if the line is out of range, return blank
            return Strip.blank(self.size.width)
        try:
            self._figlet_lines[y]  # Safety net. Technically I think should not be needed.
        except IndexError:
            return Strip.blank(self.size.width)
        else:
            color_index = y % len(self._line_colors)  # This makes it rotate through the colors.
            segments = [Segment(self._figlet_lines[y], style=self._line_colors[color_index])]
            return Strip(segments)
