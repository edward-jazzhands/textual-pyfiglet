# Help file

## Width and Height

The Width and Height settings can take four possible input types:

1) Blank - Auto mode. This will resize the widget to be the same size as the inner rendered text, just as a normal Static widget would.
2) Number - Set the width directly with an integer. Corresponds to cell size.
3) Percentage - ie. 100%, 70%, etc. (whole numbers only, max 100%)
4) Frames - ie 1fr, 2fr, 0.5fr (floats are allowed)

## Colors

The color settings are parsed and validated by the `Color` class from `textual.color`.
They can take a named color, or one of the formats allowed by the parse method.

To create a gradient, simply set more than 1 color in the colors popup.

To see the named colors, run *textual colors* using the dev tools package, and
flip over to the 'named colors' tab.

Colors may also be parsed from the following formats:

1) Text beginning with a `#` is parsed as a hexadecimal color code,
    where R, G, B, and A must be hexadecimal digits (0-9A-F):

    - `#RGB`
    - `#RGBA`
    - `#RRGGBB`
    - `#RRGGBBAA`

2) Alternatively, RGB colors can also be specified in the format
    that follows, where R, G, and B must be numbers between 0 and 255
    and A must be a value between 0 and 1:

    - `rgb(R,G,B)`
    - `rgb(R,G,B,A)`

3) The HSL model can also be used, with a syntax similar to the above,
    if H is a value between 0 and 360, S and L are percentages, and A
    is a value between 0 and 1:

    - `hsl(H,S,L)`
    - `hsla(H,S,L,A)`

## Animation Type

Note that the animate switch will be greyed out unless you have at least 2 colors set.

- 'gradient' will animate the current gradient it in the direction you specify
(using the horizontal and reverse settings).
- 'smooth_strobe' will create a gradient and animate through the colors.
- 'fast_strobe' will hard switch to the next color in the list.
It does not make a gradient, and gradient_quality will be ignored.

## Gradient Quality

Gradient quality refers to the number of color "stops" that are in a gradient.
By default, in auto mode (blank), this will be calculated depending on the current
animation type:

- In gradient mode, if vertical, it will be calculated based on the height of the widget.
If horizontal, it will be calculated based on the width of the widget.
- In smooth_strobe mode, it will be set to (number of colors * 10).
- In fast_strobe mode, this setting is ignored.

The color gradient will always loop itself, so if there's not enough colors
to fill the widget, it will loop back around. By setting the quality to be very low,
you can get a retro/8-bit effect. Conversely, by setting the quality to be very high,
you can make the color animation look extremely smooth.

## Animation FPS

Frames per second for the animation. This can be either a float greater than 0 with a
max of 100, or leave blank for auto mode. When in auto mode, it will use 12 FPS for
the 'gradient', 8 FPS for 'smooth_strobe', and drop down to 1 FPS when changed
to 'fast_strobe' mode (to avoid giving people seizures and whatnot).
