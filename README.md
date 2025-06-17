![textual-pyfiglet-banner-transparent](https://github.com/user-attachments/assets/4391ddc7-98a6-474b-8c45-603567d9dad0)

# Textual-Pyfiglet

![badge](https://img.shields.io/badge/linted-Ruff-blue?style=for-the-badge&logo=ruff)
![badge](https://img.shields.io/badge/formatted-black-black?style=for-the-badge)
![badge](https://img.shields.io/badge/type_checked-MyPy-blue?style=for-the-badge&logo=python)
![badge](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

Textual-PyFiglet is an implementation of [PyFiglet](https://github.com/pwaller/pyfiglet) for [Textual](https://github.com/Textualize/textual).

It provides a `FigletWidget` which makes it easy to add ASCII banners with colors and animating gradients.

*This library is related to [Rich-Pyfiglet](https://github.com/edward-jazzhands/rich-pyfiglet), as well as utilizes [Textual-Coloromatic](https://github.com/edward-jazzhands/textual-coloromatic) to provide the Color/animation abilities.*

## Features

- Full integration of Pyfiglet into Textual. Change the text or the font in real time - This can be connected to user input or modified programmatically.
- Color system built on Textual's color system. Thus, it can display any color in the truecolor/16-bit spectrum,
and can take common formats such as hex code and RGB, or just a huge variety of named colors.
- Make a gradient automatically between any two colors.
- Animation system that's simple to use. Just make your gradient and toggle it on/off. It can also be started
or stopped in real-time.
- The auto-size mode will re-size the widget with the new rendered ASCII output in real-time. It can also wrap
to the parent container and be made to resize with your terminal.
- Animation settings can be modified to get different effects. Set a low amount of colors and a low speed for a
very old-school retro look, set it to a high amount of colors and a high speed for a very smooth animation.
- The fonts are type-hinted to give you auto-completion in your code editor, eliminating the need to manually
check what fonts are available.
- Included demo app to showcase the features.

## Demo App

If you have uv or Pipx, you can immediately try the demo app:

```sh
uvx textual-pyfiglet 
```

```sh
pipx run textual-pyfiglet
```

## Documentation

### [Click here for documentation](https://edward-jazzhands.github.io/libraries/textual-pyfiglet/)

## Video

https://github.com/user-attachments/assets/ab172ed2-88b0-4759-815f-0d00488d3a6e

## Questions, issues, suggestions?

Feel free to post an issue.

## Thanks and Copyright

Both Textual-Pyfiglet and the original PyFiglet are under MIT License. See LICENSE file.

FIGlet fonts have existed for a long time, and many people have contributed over the years.

Original creators of FIGlet:  
[https://www.figlet.org](https://www.figlet.org)

The PyFiglet creators:  
[https://github.com/pwaller/pyfiglet](https://github.com/pwaller/pyfiglet)

Textual:  
[https://github.com/Textualize/textual](https://github.com/Textualize/textual)

And finally, thanks to the many hundreds of people that contributed to the fonts collection.
