![textual-pyfiglet-banner](https://github.com/user-attachments/assets/62b1ff88-46e5-4c7e-a6ae-3fb4074048ee)

# Textual-Pyfiglet

## Installation

```sh
pip install textual-pyfiglet
```

Or using uv:

```sh
uv add textual-pyfiglet
```

Try the included demo app! (Using uv or pipx):

```sh
uvx textual-pyfiglet
```

```sh
pipx textual-pyfiglet
```

------------------------------------------

Textual-PyFiglet is an implementation of [PyFiglet](https://github.com/pwaller/pyfiglet) for [Textual](https://github.com/Textualize/textual).

It provides a `FigletWidget` which makes it easy to add ASCII banners with colors and animating gradients.

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

If you want to run the demo app out of a local environment, install it, activate
your environment, and run `textual-pyfiglet`. Or if using uv, run:

```sh
uv run textual-pyfiglet
```

## How to use

The FigletWidget works out of the box with default settings. The most basic usage
does not require any arguments aside from the input text:

```py
from textual_pyfiglet import FigletWidget

def compose(self):
   yield FigletWidget("My Banner")
```

In the above example, it will use the default font: 'standard'.  
You can also specify a font as an argument:

```py
yield FigletWidget("My Banner", font="small")
```

To update the FigletWidget with new text, simply pass it in the `update` method:

```py
self.query_one("#figlet1").update("New text here")
```

For instance, if you have a TextArea widget where a user can enter text, you can do this:

```py
from textual import on

@on(TextArea.Changed)
def text_changed(self):
   text = self.query_one("#text_input").text
   self.query_one("#figlet1").update(text)
```

The FigletWidget will then auto-update with every key-stroke.  

You can set the font directly using the `set_font` method. This method is type hinted
to give you auto-completion for the fonts:

```py
self.query("#figlet1").set_font("small")
```

Likewise to set the justification:

```py
self.query("#figlet1").set_justify("left")
```

## Colors, Gradients, and Animation

This section is not complete yet.

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
