from __future__ import annotations
from typing import get_args, Literal
import os

# import time
# import click
# from collections import deque

from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text
from rich.style import Style

# from rich.segment import Segment
from rich.measure import Measurement
from rich.color import Color, blend_rgb
from textual_pyfiglet.pyfiglet import Figlet
from textual_pyfiglet.pyfiglet.fonts import ALL_FONTS


GRADIENT_DIRECTIONS = Literal["none", "horizontal", "vertical"]
ANIMATION_TYPE = Literal["smooth", "switch"]
# smooth: Will create gradients between each color in the list
# switch: Will simply hard switch to the next color in the list
#   Note that gradients will not be used/created in this mode.


class RichFiglet:

    def __init__(
        self,
        text: str,
        font: ALL_FONTS = "standard",
        width: int | None = None,
        colors: list[str] | None = None,
        gradient_dir: GRADIENT_DIRECTIONS = "none",
        quality: int | None = None,
        animate: bool = False,
        animation_type: ANIMATION_TYPE = "smooth",
        speed: float = 0.2,
        remove_blank_lines: bool = False,
    ):
        """Create a RichFiglet object.

        Args:
            text: The text to render.
            font: The font to use. Defaults to "standard".
            colors: A list of colors to use for gradients or animations. Each color can be a name, hex code,
                or RGB triplet. If None, no gradient or animation will be applied. For available named colors,
                see: https://rich.readthedocs.io/en/stable/appendix/colors.html
            gradient_dir: The direction of the gradient. Can be "none", "horizontal", or "vertical".
                Used in combination with animation types to create different effects.
                See the Rich-Pyfiglet documentation for examples:
                #! INSERT LINK HERE
            quality: The number of steps to blend between two colors. Defaults to None, which enables
                auto mode. Auto mode sets the quality based on the width or height of the rendered banner.
                One exception: if animate=True, gradient_dir="none", and animation_type="smooth",
                auto mode will default to 10 steps per gradient.
            animate: Whether to animate the text. Requires at least two colors. Defaults to False.
            animation_type: The animation interpolation mode. Can be "smooth" or "switch". Defaults to "smooth".
                - "smooth": Colors blend gradually (e.g. via linear gradient).
                - "switch": Hard cuts between colors with no interpolation.
                Note: switch mode does not use gradients.
                If animation_type is "smooth" and gradient_dir is "none", the result is a pulsing effect
                that changes the entire banner's color simultaneously.
            speed: Time between animation steps in seconds. Defaults to 0.2. Higher values slow the animation;
                lower values speed it up. Ignored if animate=False.
            remove_blank_lines: When True, all blank lines from the inside of the rendered ASCII art
                will be removed. Some fonts have gaps between the lines- this will remove them and
                compress the banner down to the minimum size.
        """

        if not text:
            raise ValueError("Text cannot be empty. Please provide a valid text string.")
        if font not in get_args(ALL_FONTS):
            raise ValueError(f"Font {font} is not in the fonts folder.")
        if gradient_dir not in ["none", "horizontal", "vertical"]:
            raise ValueError("Gradient direction must be 'none', 'vertical', or 'horizontal'.")
        if animate and (colors is None or len(colors) < 2):
            raise ValueError("At least two colors are required for animation.")
        if quality and (colors is None or len(colors) < 2):
            raise ValueError("At least two colors are required to set a gradient quality.")
        if quality and quality < 2:
            raise ValueError("Gradient Quality must be 2 or higher.")
        if animation_type not in ["smooth", "switch"]:
            raise ValueError("Animation type must be either 'smooth' or 'switch'.")

        if width:
            # Pyright complains if I use 'if isinstance(width, int)' here.
            assert isinstance(width, int), "Width must be an integer."
            if width < 1:
                raise ValueError("Width must be greater than 0.")
            self.width = width
        else:
            terminal_width = self.get_terminal_width()
            if terminal_width:
                self.width = terminal_width
            else:
                self.width = 80  # Fallback width

        self.text = text
        self.font = font
        self.colors = colors
        self.gradient_dir = gradient_dir
        self.animate = animate
        self.quality = quality
        self.speed = speed
        self.remove_blank_lines = remove_blank_lines

        # Parse and Set colors if provided
        self.colors = None
        self.gradient = None

        # This will raise an error if any color is invalid
        parsed_colors: list[Color] = []
        if colors:
            for color in colors:
                color_obj = self.parse_color(color)
                parsed_colors.append(color_obj)

        self.figlet = Figlet(font=font, width=self.width)  # Create the Figlet object
        self.render = self.figlet.renderText(text)
        rendered_lines = self.render.splitlines()

        # Remove leading and trailing blank lines LOOPER
        while True:
            lines_cleaned: list[str] = []
            for i, line in enumerate(rendered_lines):
                if remove_blank_lines:
                    if all(c == " " for c in line):  # if line is blank, skip it
                        pass
                    else:
                        lines_cleaned.append(line)  # Only append the lines we want to keep.
                else:
                    if i == 0 and all(c == " " for c in line):  # if first line, and blank
                        pass
                    elif i == len(rendered_lines) - 1 and all(c == " " for c in line):  # if last line
                        pass
                    else:
                        lines_cleaned.append(line)

            if lines_cleaned == rendered_lines:  # if there's no changes,
                break
            else:
                rendered_lines = lines_cleaned
                # If lines_cleaned is different, that means there was
                # a change. So set render_lines to lines_cleaned and restart loop.

        self.rendered_lines = rendered_lines
        self.reported_width = len(max(rendered_lines, key=len))

        if gradient_dir == "vertical":
            quality = quality if quality else len(rendered_lines)
        elif gradient_dir == "horizontal":
            quality = quality if quality else len(max(rendered_lines, key=len))
        else:
            quality = None

        if len(parsed_colors) == 1:
            self.color = parsed_colors[0]
        elif len(parsed_colors) > 1:
            self.color = None
            if animation_type == "smooth":

                self.gradient = self.make_gradient(parsed_colors[0], parsed_colors[1], quality)
                for i in range(2, len(parsed_colors)):
                    self.gradient += self.make_gradient(parsed_colors[i - 1], parsed_colors[i], quality)
            else:
                # self.gradient = parsed_colors
                pass

        # if color1_obj and color2_obj:
        #     gradient1 = self.make_gradient(color1_obj, color2_obj, quality)
        #     gradient2 = self.make_gradient(color2_obj, color1_obj, quality)
        #     self.gradient = gradient1 + gradient2

        # NOTE: The gradient function blends two colors. So to make a looping animation,
        # we need to blend color1 to color2, and then color2 back to color1.
        # Then add both gradients together to make a looping gradient.

        # if not animate:
        #     for i, line in enumerate(lines_cleaned):
        #         rich_text = Text(line, style=Style(color=gradient[i]))
        #         console.print(rich_text)
        # else:
        #     if gradient_dir == "horizontal":
        #         self.horizontal_animation(lines_cleaned, gradient, speed)
        #     elif gradient_dir == "vertical":
        #         self.vertical_animation(lines_cleaned, gradient, speed)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:

        # yield Segment("test")
        if self.color:
            yield Text(self.render, style=Style(color=self.color))
        elif self.gradient:
            # if not animate:
            if self.gradient_dir == "vertical":
                for i, line in enumerate(self.rendered_lines):
                    yield Text(line, style=Style(color=self.gradient[i]))
            elif self.gradient_dir == "horizontal":
                pass

            # if self.gradient_dir == "horizontal":
            #     self.horizontal_animation(self.rendered_lines, self.gradient, self.speed)
            # elif self.gradient_dir == "vertical":
            #     self.vertical_animation(self.rendered_lines, self.gradient, self.speed)
        # If neither color nor gradient, that must mean its plain/no style:
        else:
            yield Text(self.render)

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        return Measurement(self.reported_width, options.max_width)

    def get_terminal_width(
        self,
    ) -> int | None:
        """Get the terminal size."""
        try:
            size = os.get_terminal_size()
            return size.columns
        except Exception:
            pass

    def parse_color(self, color: str) -> Color:
        try:
            color2_obj = Color.parse(color)  # Check if the color is valid
        except Exception as e:
            raise e
        else:
            return color2_obj

    def make_gradient(self, color1: Color, color2: Color, steps: int = 10) -> list[Color]:
        """
        Generate a smooth gradient between two colors.

        Args:
            color1: Starting color (can be name, hex, rgb)
            color2: Ending color (can be name, hex, rgb)
            steps: Number of colors in the gradient

        Returns:
            List of Color objects representing the gradient
        """
        if steps <= 1:
            raise ValueError("Number of steps must be greater than 1.")

        triplet1 = color1.get_truecolor()
        triplet2 = color2.get_truecolor()

        gradient: list[Color] = []
        for i in range(steps):
            cross_fade = i / (steps - 1)
            blended_triplet = blend_rgb(triplet1, triplet2, cross_fade)
            blended_color = Color.from_triplet(blended_triplet)
            gradient.append(blended_color)

        return gradient
        # Explanation:
        # the function blend_rgb takes two RGB triplets and a cross-fade value (0 to 1)
        # the cross-fade value determines how much of each color to mix. You can think
        # of it as a percentage: 0.5 is a perfect 50/50 mix of the two colors.
        # 0.2 would be 20% of the first color and 80% of the second color, and so on.

        # So when we divide i by the amount of steps (minus 1), we get a series of values
        # starting at 0 and ending at 1. For example, if steps is 5, the values would be:
        # 0.0, 0.25, 0.5, 0.75, 1.0 (notice dividing by 4, to make 5 steps).

    # def horizontal_animation(self, figlet: list[str], colors: list[Color], speed: float):

    #     with Live(refresh_per_second=1 / speed, console=console) as live:
    #         position = 0
    #         while True:
    #             combined_text = Text()
    #             for i, line in enumerate(figlet):
    #                 text = Text(line)
    #                 for j in range(len(line)):
    #                     # Same index positions across all lines get the same color
    #                     color_index = (j + position) % len(colors)
    #                     text.stylize(Style(color=colors[color_index]), j, j + 1)
    #                 combined_text.append(text)  # Add the line to our combined text

    #                 if i < len(figlet) - 1:  # Add a newline if this isn't the last line
    #                     combined_text.append("\n")

    #             panel = Panel(combined_text, box=MINIMAL, expand=False, padding=(0, 0))
    #             live.update(panel)
    #             position += 1
    #             time.sleep(speed)

    # def vertical_animation(self, figlet: list[str], colors: list[Color], speed: float):

    #     with Live(refresh_per_second=1 / speed, console=console) as live:
    #         position = 0
    #         while True:
    #             text = Text()
    #             for i, line in enumerate(figlet):
    #                 color_index = (i + position) % len(colors)
    #                 if i > 0:
    #                     text.append("\n")  # Add newline except for first line
    #                 text.append(line, style=Style(color=colors[color_index]))

    #             panel = Panel(text, box=MINIMAL, expand=False)
    #             live.update(panel)
    #             position += 1
    #             time.sleep(speed)

    # def horizontal_and_vertical_animation(self, figlet: list[str], colors: list[Color], speed: float):

    #     with Live(refresh_per_second=20, console=console) as live:
    #         position = 0
    #         while True:
    #             text = Text()
    #             for line_i, line in enumerate(figlet):
    #                 if line_i > 0:
    #                     text.append("\n")  # Add newline except for first line
    #                 for char_i, char in enumerate(line):
    #                     diagonal_pos = (char_i + line_i + position) % len(colors)
    #                     text.append(char, style=f"{colors[diagonal_pos]}")

    #             panel = Panel(text, box=MINIMAL, expand=False, padding=(0, 0))
    #             live.update(panel)
    #             position += 1
    #             time.sleep(speed)
