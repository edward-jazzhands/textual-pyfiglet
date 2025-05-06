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
from textual_pyfiglet.pyfiglet import Figlet, FigletError, figlet_format  # type: ignore
from textual_pyfiglet.pyfiglet.fonts import ALL_FONTS  # not the actual fonts, just the names.

#! NOTE ON TYPE IGNORE:
# The original Pyfiglet package (Which is contained inside Textual-Pyfiglet as a subpackage),
# is not type hinted. In fact it was written long before type hinting was a thing.
# In the future it is a goal to add type hinting to the entire Pyfiglet subpackage.
# This is the only ignore in the entire Textual-Pyfiglet part of the codebase.

# LITERALS:
JUSTIFY_OPTIONS = Literal["left", "center", "right", "auto"]
COLOR_MODE = Literal["color", "gradient", "none"]


class FigletWidget(Widget):

    DEFAULT_CSS = "FigletWidget {width: auto; height: auto;}"

    # - Reactive Properties - #
    _figlet_input: reactive[str] = reactive[str]("", always_update=True)
    _color1: reactive[str | None] = reactive[str | None]("")
    _color2: reactive[str | None] = reactive[str | None]("")
    _animated: reactive[bool] = reactive[bool](False, always_update=True)
    _font: reactive[ALL_FONTS] = reactive[ALL_FONTS]("ansi_regular")
    _justify: reactive[JUSTIFY_OPTIONS] = reactive[JUSTIFY_OPTIONS]("auto")
    _color_mode: reactive[COLOR_MODE] = reactive[COLOR_MODE]("none", always_update=True)
    _animation_interval: reactive[float] = reactive[float](0.08)
    _gradient_quality: reactive[str | int] = reactive[str | int]("auto")
    _fig_height_reported: reactive[int] = reactive[int](0)
    _figlet_lines: reactive[list[str]] = reactive(list, layout=True)

    # - Non-Reactive Properties - #
    fonts_list: list[str] = list(get_args(ALL_FONTS))

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

            self.fig_width = widget.figlet.width
            """This is the width of the Pyfiglet object. It's the internal width setting
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
        animation_quality: str | int = "auto",
        animation_interval: float = 0.08,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Create a FigletWidget.

        Args:
            content: A Rich renderable, or string containing console markup.
            font (PyFiglet): Font to use for the ASCII art. Default is "standard".
            justify (PyFiglet): Justification for the text. Default is "auto".
                (The auto mode will switch to right if the direction is right-to-left.)
            color1 (Gradient): Set color for the figlet - also First color for the gradient
            color2 (Gradient): Second color for the gradient. Unused if None.
            animate: Whether to animate the gradient.
            animation_quality: How many colors the animation gradient should have.
                Default is "auto", which will set the quality to the number of lines in the widget.
            animation_interval: How long to wait between frames of the animation, in seconds.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
        """
        super().__init__(name=name, id=id, classes=classes)

        self.figlet = Figlet()  # ~ <-- Create the PyFiglet object
        self.id

        # NOTE: The FigletWidget has to wait to be fully mounted before
        # it can know its maximum width and set the render size.
        # This is because in modes 'auto', 'percent', and 'fraction', PyFiglet needs to
        # know the maximum width of the widget to render the text properly.

        # When the widget receives its first on_resize event (The first time it learns
        # what its proper size will be), it will set the render size.
        # If auto mode, the max render size is the width of whatever container is the
        # parent of the FigletWidget. If not auto, the max render size is the width of
        # the widget itself.

        try:
            string = str(text)
        except Exception as e:
            self.log.error(f"FigletWidget Error converting input to string: {e}")
            raise e

        self.set_reactive(FigletWidget._figlet_input, string)
        self.set_reactive(FigletWidget._font, font)
        self.set_reactive(FigletWidget._justify, justify)
        if color1 is not None:
            self.set_reactive(FigletWidget._color1, color1)
        if color2 is not None:
            self.set_reactive(FigletWidget._color2, color2)
        self.set_reactive(FigletWidget._animated, animate)
        self.set_reactive(FigletWidget._animation_interval, animation_interval)
        self.set_reactive(FigletWidget._gradient_quality, animation_quality)

        self.line_colors: deque[Style] = deque()
        self.color = None
        self.gradient = None
        self.interval_timer: Timer | None = None

        #! NOTE: Figlet also has a "direction" argument. Add here?

        # ~ COLORS / GRADIENT ~#

        if not color1 and not color2:  # if no style,
            self.set_reactive(FigletWidget._color_mode, "none")  # set to none
        elif color1 and not color2:  # only color 1
            self.set_reactive(FigletWidget._color_mode, "color")  # set to color
        elif color1 and color2:
            self.set_reactive(FigletWidget._color_mode, "gradient")  # set to gradient
        else:
            raise Exception("If you're seeing this error, something is wrong with the color mode.")

    def on_mount(self):

        if self.animated:
            self.interval_timer = self.set_interval(interval=self._animation_interval, callback=self.refresh)

    #################
    # ~ Public API ~#
    #################

    def update(self, new_text: str) -> None:
        """Update the PyFiglet area with the new text.
        Note that this over-rides the standard update method in the Static widget.
        Unlike the Static widget, this method does not take a Rich renderable.
        It can only take a text string. Figlet needs a normal string to work properly.

        Args:
            new_text: The text to update the PyFiglet widget with. Default is None."""

        self.figlet_input = new_text

    @property
    def figlet_input(self) -> str:
        """Getter for the figlet input text."""
        return self._figlet_input

    @figlet_input.setter
    def figlet_input(self, text: str) -> None:
        """Setter for the figlet input text.
        The widget will update with the new text automatically.
        Args:
            text: The text to set. Must be a string."""

        assert isinstance(text, str), "Figlet input must be a string."

        self._figlet_input = text

    @property
    def font(self) -> ALL_FONTS:
        """Getter for the font setting."""
        return self._font

    @font.setter
    def font(self, font: str) -> None:
        """Setter for the font setting with validation.
        Can be any font name from the PyFiglet package."""

        if font not in self.fonts_list:
            raise ValueError(f"Invalid font: {font} \nMust be one of the available fonts.")
        self._font = cast(ALL_FONTS, font)  # Cast to ALL_FONTS for type safety

    @property
    def justify(self) -> str:
        """Getter for the justification setting."""
        return self._justify

    @justify.setter
    def justify(self, value: str) -> None:
        """Setter for the justification setting with validation.
        Can be 'left', 'center', 'right', or 'auto'."""

        if value not in ("left", "center", "right", "auto"):
            raise ValueError(
                f"Invalid justification: {value} \nMust be 'left', 'center', 'right', or 'auto'."
            )
        self._justify = value

        # NOTE: I also had to go into the Pyfiglet source code to create a setter method for
        # justify to allow changing it in real-time. (It previously only had a getter method).

    @property
    def animated(self) -> bool:
        """Getter for the animated state of the PyFiglet widget."""
        return self._animated

    @animated.setter
    def animated(self, value: bool) -> None:
        """Setter for the animated state of the PyFiglet widget.
        The widget will update with the new animated state automatically.
        Args:
            value: The animated state to set. Must be a boolean."""

        self._animated = value

    def toggle_animated(self) -> None:
        """Toggle the animated state of the PyFiglet widget.
        The widget will update with the new animated state automatically."""

        self._animated = not self._animated

    @property
    def color1(self) -> str | None:
        """Getter for the first color setting."""
        return self._color1

    @color1.setter
    def color1(self, color: str | None) -> None:
        """Setter for the first color setting.
        The widget will update with the new color automatically.
        Args:
            color: The first color to set."""

        # if color is not None:
        #     try:
        #         Color.parse(color)  # Check if the color is valid
        #     except Exception as e:
        #         self.log.error(f"Error parsing color: {e}")
        #         raise e

        self._color1 = color

    @property
    def color2(self) -> str | None:
        """Getter for the first color setting."""
        return self._color2

    @color2.setter
    def color2(self, color: str | None) -> None:
        """Setter for the first color setting.
        The widget will update with the new color automatically.
        Args:
            color: The first color to set."""

        # if color is not None:
        #     try:
        #         Color.parse(color)  # Check if the color is valid
        #     except Exception as e:
        #         self.log.error(f"Error parsing color: {e}")
        #         raise e

        self._color2 = color

    @property
    def gradient_quality(self) -> str | int:
        """Getter for the gradient quality setting."""
        return self._gradient_quality

    @gradient_quality.setter
    def gradient_quality(self, quality: str | int) -> None:
        """Setter for the gradient quality setting.
        The widget will update with the new gradient quality automatically.
        Args:
            quality: The gradient quality to set. Can be 'auto' or an integer."""

        if quality == "auto":
            self._gradient_quality = len(self._figlet_lines) * 2
        elif isinstance(quality, int):
            if 3 <= quality <= 100:
                self._gradient_quality = quality
            else:
                raise ValueError("Gradient quality must be between 3 and 100.")
        else:
            raise Exception("Invalid gradient quality. Must be 'auto' or an integer between 1 and 100.")

    @property
    def animation_interval(self) -> float:
        """Getter for the animation interval setting."""
        return self._animation_interval

    @animation_interval.setter
    def animation_interval(self, interval: float) -> None:
        """Setter for the animation interval setting.
        The widget will update with the new animation interval automatically.
        Args:
            interval: The animation interval to set. Must be a float between 0.01 and 1.0."""

        if not 0.01 <= interval <= 1.0:
            raise Exception("Animation interval must be greater than 0.01 and less than 1.0.")
        self._animation_interval = interval

    def get_figlet_as_string(self) -> str:
        """Return the PyFiglet render as a string."""

        return self.figlet_render

    @classmethod
    def figlet_quick(
        cls, text: str, font: ALL_FONTS = "standard", width: int = 80, justify: JUSTIFY_OPTIONS = "auto"
    ):
        """This is a standalone class method. It just provides quick access to the figlet_format
        function in the pyfiglet package.
        It also adds type hinting / auto-completion for the fonts list."""
        return figlet_format(text=text, font=font, width=width, justify=justify)

    ##############
    # ~ WATCHERS ~#
    ##############

    def watch__figlet_input(self, new_value: str) -> None:

        if new_value == "":
            self._figlet_lines = [""]
            self.mutate_reactive(FigletWidget._figlet_lines)
        else:
            self._figlet_lines = self.render_figlet(new_value)  # ~ <- where the render happens
            self.mutate_reactive(FigletWidget._figlet_lines)

        self.post_message(self.Updated(self))

    def watch__color_mode(self, new_value: COLOR_MODE) -> None:

        if new_value == "none":
            self.line_colors = deque([Style()])
            self.gradient = None  # reset the gradient if it was set

        elif new_value == "color":
            try:
                if self.color1:
                    my_color_obj = Color.parse(self.color1)  # An invalid color will raise a ColorParseError
                elif self.color2:
                    my_color_obj = Color.parse(self.color2)
                else:
                    raise Exception("Color mode is set to color, but no colors are set.")
            except Exception as e:
                self.log.error(f"Error parsing color: {e}")
                raise e
            else:
                self.line_colors = deque([Style(color=my_color_obj.rich_color)])
                self.gradient = None  # reset the gradient if it was set

        elif new_value == "gradient":
            if self._gradient_quality == "auto":
                animation_quality = len(self._figlet_lines) * 2
            elif isinstance(self._gradient_quality, int):
                animation_quality = self._gradient_quality
            else:
                raise Exception("Invalid animation quality. Must be 'auto' or an integer.")

            try:
                assert self.color1 and self.color2, "Color mode is set to gradient, but colors are not set."
                self.gradient = self.make_gradient(self.color1, self.color2, animation_quality)
            except Exception as e:
                self.log.error(f"Error creating gradient: {e}")
                raise e
            self.line_colors = deque(
                [Style(color=color.rich_color) for color in self.gradient.colors]
            )  # sets both

        else:
            raise Exception(f"Invalid color mode: {new_value}")

    def watch__color1(self, new_value: str) -> None:

        # These two methods (watch__color1 and watch__color2) only exist to set the
        # color mode. This allows it to use *either* color1 or color2 to set the mode.
        # It will still go into color mode regardless of which color is set.

        assert isinstance(new_value, str)

        if not new_value and not self.color2:
            self._color_mode = "none"
        elif (not new_value and self.color2) or (new_value and not self.color2):
            self._color_mode = "color"
        elif new_value and self.color2:
            self._color_mode = "gradient"

    def watch__color2(self, new_value: str) -> None:

        assert isinstance(new_value, str)

        if not new_value and not self.color1:
            self._color_mode = "none"
        if (not new_value and self.color1) or (new_value and not self.color1):
            self._color_mode = "color"
        elif new_value and self.color1:
            self._color_mode = "gradient"

    def watch__animated(self, new_value: bool) -> None:

        if self.gradient:
            if new_value:
                if self.interval_timer:
                    self.interval_timer.resume()
                else:
                    self.interval_timer = self.set_interval(
                        interval=self._animation_interval, callback=self.refresh
                    )
            else:
                if self.interval_timer:
                    self.interval_timer.stop()
                    self.interval_timer = None

    def watch__font(self, new_value: str) -> None:

        try:
            self.figlet.setFont(font=new_value)
        except Exception as e:
            self.log.error(f"Error setting font: {e}")
            raise e

        self.watch__figlet_input(self._figlet_input)  # trigger reactive

    def watch__justify(self, new_value: str) -> None:

        try:
            self.figlet.justify = new_value
        except Exception as e:
            self.log.error(f"Error setting justify: {e}")
            raise e

        self.watch__figlet_input(self._figlet_input)  # trigger reactive

    def watch__animation_interval(self) -> None:
        self.animated = False  # stop the animation if it was running
        self.animated = True  # restarts the animation with the new interval

    def watch__gradient_quality(self) -> None:

        self._color_mode = self._color_mode  #! This logic chain could really use explaining.

    def watch__fig_height_reported(self) -> None:

        self._color_mode = self._color_mode  # trigger the reactive

    #####################
    # ~ RENDERING LOGIC ~#
    #####################

    def make_gradient(self, color1: str, color2: str, quality: int) -> Gradient:
        "Use color names, ie. 'red', 'blue'"

        try:
            parsed_color1 = Color.parse(color1)
            parsed_color2 = Color.parse(color2)
        except Exception as e:
            self.log.error(f"Error parsing color: {e}")
            raise e

        stop1 = (0.0, parsed_color1)  # 3 stops so that it fades in and out.
        stop2 = (0.5, parsed_color2)
        stop3 = (1.0, parsed_color1)
        return Gradient(stop1, stop2, stop3, quality=quality)

    def on_resize(self) -> None:
        self.refresh_size()

    def refresh_size(self):

        if self.size.width == 0 or self.size.height == 0:  # <- this prevents crashing on boot.
            return

        assert isinstance(self.parent, Widget)  # This is for type hinting.
        assert isinstance(self.styles.width, Scalar)  # These should always pass if it reaches here.

        if self.styles.width.is_auto:
            self.call_after_refresh(self._set_size, "auto")
        # if not in auto, the Figlet's render target is the size of the figlet.
        else:
            self.call_after_refresh(self._set_size, "not_auto")

    def _set_size(self, mode: str) -> None:
        "Used internally by refresh_size()"

        assert isinstance(self.parent, Widget)  # For type hinting.

        if mode == "auto":
            self.figlet.width = self.parent.size.width
        elif mode == "not_auto":
            self.figlet.width = self.size.width
        else:
            raise Exception(f"Invalid mode: {mode}. Must be 'auto' or 'not_auto'.")

        self._figlet_input = self._figlet_input  # trigger the reactive to update the figlet.

    # These two functions below are the secret sauce to making the auto sizing work.
    # They are both over-rides, and they are called by the Textual framework
    # to determine the size of the widget.
    def get_content_width(self, container: Size, viewport: Size) -> int:

        if self._figlet_lines:
            self.fig_width_reported = len(max(self._figlet_lines, key=len))
            return self.fig_width_reported
        else:
            return 0

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:

        if self._figlet_lines:
            self.fig_height_reported = len(self._figlet_lines)
            return self.fig_height_reported
        else:
            return 0

    def render_figlet(self, figlet_input: str) -> list[str]:

        try:
            self.figlet_render = str(self.figlet.renderText(figlet_input))  # * <- Actual render happens here.
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
        if self.gradient and self.animated:
            self.line_colors.rotate()
        return super().render_lines(crop)

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        if y >= len(self._figlet_lines):  # if the line is out of range, return blank
            return Strip.blank(self.size.width)
        try:
            self._figlet_lines[y]
        except IndexError:
            return Strip.blank(self.size.width)
        else:
            color_index = y % len(self.line_colors)
            segments = [Segment(self._figlet_lines[y], style=self.line_colors[color_index])]
            return Strip(segments)
