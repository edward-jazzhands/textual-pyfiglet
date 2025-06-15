"""Module for the FigletWidget class."""

# ~ Type Checking (Pyright and MyPy) - Strict Mode
# ~ Linting - Ruff
# ~ Formatting - Black - max 110 characters / line

# STANDARD LIBRARY IMPORTS
from __future__ import annotations
from typing import cast
from typing_extensions import Literal, get_args

# Textual and Rich imports
from textual.css.scalar import Scalar
from textual.widget import Widget
from textual.reactive import reactive

# Textual third-party library imports
from textual_coloromatic import Coloromatic

# Local imports:
from rich_pyfiglet.pyfiglet import Figlet, FigletError, figlet_format
from rich_pyfiglet.pyfiglet.fonts import ALL_FONTS  # not the actual fonts, just the names.

# CONSTANTS:
JUSTIFY_OPTIONS = Literal["left", "center", "right"]
COLOR_MODE = Literal["color", "gradient", "none"]
ANIMATION_TYPE = Literal["gradient", "smooth_strobe", "fast_strobe"]


class FigletWidget(Coloromatic):

    DEFAULT_CSS = "FigletWidget {width: auto; height: auto;}"

    ###################################
    # ~ Public API Class Attributes ~ #
    ###################################
    fonts_list: list[str] = list(get_args(ALL_FONTS))
    """A list of all the available fonts in the Pyfiglet package."""

    ############################
    # ~ Public API Reactives ~ #
    ############################
    text_input: reactive[str] = reactive[str]("", always_update=True)
    """The text to render in the Figlet widget. You can set this directly, or use
    the update() method to set it."""

    font: reactive[ALL_FONTS] = reactive[ALL_FONTS]("ansi_regular", always_update=True)
    """The font to use for the Figlet widget. The reactive attribute takes a string
    literal type in order to provide auto-completion and type hinting. The font must be
    one of the available fonts in the Pyfiglet package. You can also use the set_font()
    method to set the font using a string. This is useful for passing in a variable."""

    justify: reactive[JUSTIFY_OPTIONS] = reactive[JUSTIFY_OPTIONS]("center", always_update=True)
    """The justification to use for the Figlet widget. The reactive attribute takes a string
    literal type in order to provide auto-completion and type hinting. You can also use
    the set_justify() method to set the justification using a string. This is useful for
    passing in a variable."""

    def __init__(
        self,
        text: str = "",
        *,
        font: ALL_FONTS = "standard",
        justify: JUSTIFY_OPTIONS = "center",
        colors: list[str] = [],
        animate: bool = False,
        animation_type: ANIMATION_TYPE = "gradient",
        gradient_quality: int | str = "auto",
        horizontal: bool = False,
        reverse: bool = False,
        fps: float | str = "auto",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Create a FigletWidget.

        Args:
            text: Text to render in the Figlet widget.
            font (PyFiglet): Font to use for the ASCII art. Default is 'standard'.
            justify (PyFiglet): Justification for the text. Default is 'center'.
            colors: List of colors to use for the gradient. This is a list of strings that can be
                parsed by a Textual `Color` object that allows passing in any number of colors you want.
                It also supports passing in Textual CSS variables ($primary, $secondary, $accent, etc).
                If using CSS variables, they will update automatically to match the theme whenever
                the theme is changed.
            animate: Whether to animate the gradient.
            animation_type: Can be 'gradient', 'smooth_strobe', or 'fast_strobe'. The default is 'gradient'.
                - 'gradient' will animate the current gradient it in the direction you specify
                (using the horizontal and reverse settings).
                - 'smooth_strobe' will create a gradient and animate through the colors.
                - 'fast_strobe' will hard switch to the next color in the list.
                It does not make a gradient, and gradient_quality will be ignored.
            gradient_quality: The quality of the gradient. This means how many colors the gradient has
                in it. This is either 'auto' or an integer between 3 and 100. The higher the
                number, the smoother the gradient will be. By default, in auto mode,
                this will be calculated depending on the current animation type.
                - In gradient mode, if vertical, it will be calculated based on the height of the widget.
                If horizontal, it will be calculated based on the width of the widget.
                - In smooth_strobe mode, it will be set to (number of colors * 10).
                - In fast_strobe mode, this setting is ignored.
            horizontal: Whether the gradient should be horizontal or vertical.
                Note that this will have no effect if the animation mode is 'smooth_strobe' or 'fast_strobe'
                because they do not use a direction.
            reverse: Whether the animation should run in reverse.
                If horizontal is False, this will switch between up and down. If horizontal is True, this
                will switch between left and right.
                Note that this will have no effect if the animation mode is 'smooth_strobe' or 'fast_strobe'
                because they do not use a direction.
            fps: The Frames per second for the animation.
                This is a float so that you can set it to values such as 0.5 if you desire. The default
                is 'auto', which will set the FPS to 12 for 'gradient', 12 for 'smooth_strobe', and 1
                for 'fast_strobe'.
            name: Name of widget.
            id: ID of Widget.
            classes: Space separated list of class names.
        """

        try:
            string = str(text)
        except Exception as e:
            raise e

        super().__init__(
            name=name,
            id=id,
            classes=classes,
            colors=colors,
            animate=animate,
            animation_type=animation_type,
            gradient_quality=gradient_quality,
            horizontal=horizontal,
            reverse=reverse,
            fps=fps,
        )

        self.figlet = Figlet()
        self._previous_height: int = 0

        self.font = font
        self.justify = justify
        self.text_input = string

    #################
    # ~ Public API ~#
    #################

    def update(self, text: str) -> None:  # type: ignore[override]
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
            justify: The justification to set. Can be 'left', 'center', or 'right'."""

        self.justify = cast(JUSTIFY_OPTIONS, justify)  # the validate methods handle this afterwards.

    def set_font(self, font: str) -> None:
        """Set the font of the PyFiglet widget.
        This method, unlike setting the reactive property, allows passing in a string
        instead of a string literal type. This is useful for passing in a variable.
        But unlike the reactive property, this does not provide any auto-completion
        for the available fonts. To get auto-completion for available fonts,
        set `self.font` directly with a raw string literal type.

        Args:
            font: The font to set. Must be one of the available fonts."""

        self.font = cast(ALL_FONTS, font)

    def get_figlet_as_string(self) -> str:
        """Return the PyFiglet render as a string."""

        return self.figlet_render

    @classmethod
    def figlet_quick(
        cls, text: str, font: ALL_FONTS = "standard", width: int = 80, justify: JUSTIFY_OPTIONS = "left"
    ) -> str:
        """This is a standalone class method. It just provides quick access to the figlet_format
        function in the pyfiglet package.
        It also adds type hinting / auto-completion for the fonts list."""
        return str(figlet_format(text=text, font=font, width=width, justify=justify))

    #################
    # ~ Validators ~#
    #################

    def validate_text_input(self, text: str) -> str:

        # must use assert here - Pylance does not like using an isinstance check.
        assert isinstance(text, str), "Figlet input must be a string."

        # if not isinstance(text, str):       # Pylance:
        #     raise ValueError("Figlet input must be a string.")
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

    ###############
    # ~ Watchers ~#
    ###############

    #! OVERRIDE
    def watch_text_input(self, text: str) -> None:

        # Normal run-time
        if text == "":
            self._animation_lines = [""]
            self.mutate_reactive(FigletWidget._animation_lines)
        else:
            self._animation_lines = self.render_figlet(text)  # ~ <- where the rendering happens
            self.mutate_reactive(FigletWidget._animation_lines)

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

    ######################
    # ~ RENDERING LOGIC ~#
    ######################

    def on_resize(self) -> None:
        self.refresh_size()

    #! OVERRIDE
    def refresh_size(self) -> None:

        if (
            self.size.width == 0 or self.size.height == 0
        ) and not self.app._dom_ready:  # type: ignore[unused-ignore]
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

        self.text_input = self.text_input  # trigger the reactive to update the figlet.

        # This will make it recalculate the gradient only when the height changes:
        if self.size.height != self._previous_height:
            self._previous_height = self.size.height
            self._color_mode = self._color_mode

        if self.animation_type == "gradient" and self.horizontal:
            self._color_mode = self._color_mode

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
