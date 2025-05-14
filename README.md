![textual-pyfiglet-banner](https://github.com/user-attachments/assets/62b1ff88-46e5-4c7e-a6ae-3fb4074048ee)

# Textual-Pyfiglet

![badge](https://img.shields.io/badge/linted-Ruff-blue?style=for-the-badge&logo=ruff)
![badge](https://img.shields.io/badge/formatted-black-black?style=for-the-badge)
![badge](https://img.shields.io/badge/type_checked-MyPy-blue?style=for-the-badge&logo=python)
![badge](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![badge](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fedward-jazzhands%2Ftextual-pyfiglet%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&style=for-the-badge)

Textual-PyFiglet is an implementation of [PyFiglet](https://github.com/pwaller/pyfiglet) for [Textual](https://github.com/Textualize/textual).

It provides a `FigletWidget` which makes it easy to add ASCII banners with colors and animating gradients.

*This library is the sister library of [Rich-Pyfiglet](https://github.com/edward-jazzhands/rich-pyfiglet).*

## Features

- Color system built on Textual's color system. Thus, it can display any color in the truecolor/16-bit spectrum,
and can take common formats such as hex code and RGB, or just a huge variety of named colors.
- Make a gradient automatically between any two colors.
- Animation system that's dead simple to use. Just make your gradient and toggle it on/off. It can also be started
or stopped in real-time.
- The auto-size mode will re-size the widget with the new rendered ASCII output in real-time. It can also wrap
to the parent container and be made to resize with your terminal.
- Text can be typed or updated in real time - This can be connected to user input or modified programmatically.
- Animation settings can be modified to get different effects. Set a low amount of colors and a low speed for a
very old-school retro look, set it to a high amount of colors and a high speed for a very smooth animation, or
experiment with a blend of these settings.
- The fonts are type-hinted to give you auto-completion in your code editor, eliminating the need to manually
check what fonts are available.
- Included demo app to showcase the features.

https://github.com/user-attachments/assets/c80edaa6-022d-4044-a8fc-d131e785baf9

## Demo App

If you have uv or Pipx, you can immediately try the demo app:

```sh
uvx textual-pyfiglet 
```

```sh
pipx textual-pyfiglet
```

## Documentation

### [Click here for documentation](https://edward-jazzhands.github.io/libraries/textual-pyfiglet/)

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
