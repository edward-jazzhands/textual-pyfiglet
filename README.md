```
   __            __              __                    
  / /____  _  __/ /___  ______ _/ /                    
 / __/ _ \| |/_/ __/ / / / __ `/ /_____                
/ /_/  __/>  </ /_/ /_/ / /_/ / /_____/                
\__/\___/_/|_|\__/\__,_/\__,_/_/                       
                 _____       __     __                 
    ____  __  __/ __(_)___ _/ /__  / /_                
   / __ \/ / / / /_/ / __ `/ / _ \/ __/                
  / /_/ / /_/ / __/ / /_/ / /  __/ /_                  
 / .___/\__, /_/ /_/\__, /_/\___/\__/                  
/_/    /____/      /____/                              
```

Base package - includes 10 fonts (71kb):   
```
pip install textual-pyfiglet
```
Install with extended fonts collection - 519 fonts (1.6mb):   
```
pip install textual-pyfiglet[fonts]
```
------------------------------------------

Textual-PyFiglet is an implementation of [PyFiglet](https://github.com/pwaller/pyfiglet) for [Textual](https://github.com/Textualize/textual).

It provides a `FigletWidget` which is designed to be easy to use inside of Textual.

![Demo GIF](https://raw.githubusercontent.com/edward-jazzhands/textual-pyfiglet/refs/heads/main/demo.gif)

# Key features


### Textual-PyFiglet is a fork of PyFiglet:

The original PyFiglet has zero dependencies, since it's a full re-write of FIGlet in Python. Thus by forking, Textual-PyFiglet also has zero dependencies (aside from Textual of course). PyFiglet is bundled inside as a sub-package.

I made sure to preserve the full git history of PyFiglet, as well as its original CLI and demo (see Demo Program below).

### Minimized:

PyFiglet wheel: **1.1 MB**.  -->   Textual-PyFiglet wheel: **71 KB**.

99% of the size of PyFiglet is just the massive fonts collection, 519 in total. In the base textual-pyfiglet package I've included only 10 of the best minimal fonts. I've also made it very easy to download the full collection for those who still want it (use extended fonts install, shown at the top)

### Widget easily drops into your Textual app:

The widget is based on `Static` and is designed to mimick its behavior. That means it can drop-in replace any Static widget, and it should just work without even adding or changing arguments (using default font). Assuming you're accounting for the size of the text somehow.

You can dynamically set the size (ie 1fr, 100%) as you would with any Textual widget. It will respond automatically to any widget resize events, and re-draw the figlet.

### Real-time updating:

This real-time updating can be seen in the included demo, as well as the OG online generator:   
https://patorjk.com/software/taag/

It's easy to implement in your own Textual app. See below.

### Extended fonts collection moved to separate package:

If you want the whole collection, simply use:   
`pip install textual-pyfiglet[fonts]`

You can install the whole thing straight from that command, or use it to add the fonts to an existing install. The fonts package is about 1.5 MB (compressed). 

The included 10 fonts I hand-picked were chosen for being small, minimalist, and professional looking. For people that don't want to think about fonts, these 10 will probably be all you need.

You can also easily add more fonts by just downloading individual font files the oldschool way, and plopping them in the fonts folder (inside the Pyfiglet folder, which will be in /lib/python/site-packages/textual-pyfiglet)

A good website to download individual fonts:
http://www.jave.de/figlet/fonts/overview.html

# Usage

### Demo program, CLI:
Run the demo program with either:   
`textual-pyfiglet`   
Or:   
`python -m textual_pyfiglet`

PyFiglet also has its own CLI which has been kept available. (Which has its own built-in demo program.) You can access the PyFiglet CLI with:   
`python -m textual_pyfiglet.pyfiglet`

Try it out to see the options. For instance, try running this code:   
`python -m textual_pyfiglet.pyfiglet Hey guys, whats up?`   

# How to use:

FigletWidget is designed to be used like a normal Static widget.

You can simply create one with the  Textual syntax:

```python
from textual_pyfiglet import FigletWidget

def compose(self):
   yield FigletWidget("Label of Things", id="figlet1")
```

In this case it will use the default font, Calvin_s. You can also specify a font in the constructor:

```python
yield FigletWidget("Label of Things", id="figlet1" font="small")
```

## Resizing

The FigletWidget will auto-update the rendering area whenever it gets resized.   
Internally it uses Textual's `on_resize` method. So it should work automatically.
Just set the widget to the size you want, and PyFiglet will render what it can in that space.

## Change the font:

The widget will update automatically when this is run:
```python
self.query("#figlet1").set_font(new_font)
```
| Base fonts  |                |
|-------------|----------------|
| calvin_s    | smblock
| chunky      | smbraille 
| cybermedium | standard
| small_slant | stick_letters
| small       | tmplr

If the extended fonts pack is not installed, the widget will do a quick check every launch to see if its been downloaded. So you can install it afterwards any time you feel like it.

## Live updating / Passing text

To update the FigletWidget with new text, simply pass it in the update method:

```python
self.query_one("#figlet1").update(text)
```

For instance, if you have a TextArea widget where a user can enter text, you can do this:

```python
@on(TextArea.Changed)
def text_changed(self):
   text = self.query_one("#text_input").text
   self.query_one("#figlet1").update(text)
```
The FigletWidget will then auto-update with every key-stroke.   
Note that you cannot pass in a Rich renderable, like the normal Static widget - the text has to be a normal string for PyFiglet to work.

You can access two lists of installed fonts through methods in the FigletWidget:

```python
figlet1 = self.query_one("#figlet1")
all_fonts = figlet1.get_fonts_list(get_all=True)
base_fonts = figlet1.get_fonts_list(get_all=False)  # only get standard 10
```

-----------------------------------
## Thanks and Copyright

Both Textual-Pyfiglet and the original PyFiglet are under MIT License. See LICENSE file.

FIGlet fonts have existed for a long time. There's a bunch of good generators on the internet. Just google "figlet online".
Several of those were very helpful for me so big thanks to anyone that has made a FIGlet generator of some kind.

Thanks to original creators of FIGlet:   
https://www.figlet.org

Thanks to the PyFiglet team:   
https://github.com/pwaller/pyfiglet
 
Thanks to Textual:   
https://github.com/Textualize/textual   

And finally, thanks to the many hundreds of people that contributed to the fonts collection.