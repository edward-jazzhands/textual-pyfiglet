# Textual-Pyfiglet<br>Documentation and Guide

## Installation

```sh
pip install textual-pyfiglet
```

Or using uv:

```sh
uv add textual-pyfiglet
```

## Demo app

You can instantly try out the demo app using uv or pipx:

```sh
uvx textual-pyfiglet
```

```sh
pipx run textual-pyfiglet
```

Or if you have it downloaded into your python environment, run it using the entry script:

```sh
textual-pyfiglet
```

For uv users, after adding it to your environment:

```sh
uv run textual-pyfiglet
```

## Getting Started

Import into your project with:

```py
from textual_pyfiglet import FigletWidget
```

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

## Live updating

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

## Changing font / justification

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

This section is not complete yet (The color/animation system is still under development, but you can see it action in the demo app).

## API Reference

You can find the full API reference on the [reference page](reference.md).
