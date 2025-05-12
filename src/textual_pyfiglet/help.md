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

To create a gradient, simply set both color 1 and color 2.

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

## Gradient Quality

Gradient quality refers to the number of color "stops" that are in a gradient.
By default, in auto mode (blank), this will be set to the height of the widget * 2.
Thus, a height of 10 would give you 20 stops - 10 to blend from color1 to color2,
then another 10 to blend back. This creates a smooth alternating gradient.

The color gradient will always loop itself, so if there's not enough colors
to fill the widget, it will loop back around. By setting the quality to be very low,
you can get a retro/8-bit effect. Conversely, by setting the quality to be very high,
you can make the color animation look extremely smooth.

## Animation Speed

This is the rate the animation refreshes in seconds. It must be a float between 0.05 and 1.0.
