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

Base package, includes 10 fonts (41kb):   
`pip install textual-pyfiglet`

Install with extended fonts collection (1.2mb):   
`pip install textual-pyfiglet[fonts]`   

------------------------------------------

Textual-PyFiglet is an implementation of PyFiglet for Textual.

It provides a `FigletWidget` which is designed to be easy to use, and blend in with how Textual works.

## Key features


### Textual-PyFiglet is a fork of PyFiglet:

   The original PyFiglet has zero dependencies, since it's a full re-write of FIGlet in Python. Thus by forking, **Textual-PyFiglet also has zero dependencies** (aside from Textual of course). PyFiglet is bundled inside as a sub-package.

   I also made sure to preserve the full git history of PyFiglet, as well as its original CLI and demo (see Demo Program below).

### Greatly minimized:

   The built distribution of the original **PyFiglet is 1.1 MB**. That's not enormous by any means, but it's about twice the size of the entire Textual wheel (which is 600 KB)

   The wheel for **Textual-PyFiglet is 41 KB**.

   99% of the size of PyFiglet is just the massive fonts collection, about 550 in total. In the base textual-pyfiglet package I've included only 10 of the most basic and common fonts. I've also made it very easy to download the full collection for those who still want it (use extended fonts install, shown at the top)

### Widget easily drops into your Textual app:

   The widget is based on `Static` and is designed to mimick its behavior. That means it can drop-in replace any Static widget, and it should just work without even adding or changing arguments (using default font). Assuming you're accounting for the size of the text somehow.

   It achieves this by simply overriding the `update()` method in Static. When update is called, PyFiglet will convert the input text, and PyFiglet's output is passed to `self.renderable`. So it should drop in nicely if you have any Static widgets that are using these attributes.

   By default, the FigletWidget will automatically set its own size when it updates. (width and height are set to auto). But, **it will also respect any container or widget it's inside of, and wrap the text accordingly.**

   Note that **this behavior can be toggled**. By default it will wrap on resize, but this can be turned off, in which case it will crop.

### Possible to Live-Update the text:

   This same 'live-updating' feature can be seen in the included demo, as well as the OG online generator:   
   https://patorjk.com/software/taag/

   For instance, if using a TextArea widget to enter text, simply update the FigletWidget with each keystroke:

   ```python
   @on(TextArea.Changed)
   def text_changed(self):
      text = self.query_one("#text_input").text
      self.query_one("#figlet").update(text)
   ```

### Extended fonts collection moved to separate package:

   If you want the whole collection, simply use:   
   `pip install textual-pyfiglet[fonts]`

   You can install the whole thing straight from that command, or use it to add the fonts to an existing install. The fonts collection is about 1 MB zipped. Hey, when you're making CLI tools, being light-weight matters. That's why the extended collection has been made optional - Now you decide if you need it.

   You can also easily add more fonts by just downloading individual font files the oldschool way, and plopping them in the fonts folder (inside the Pyfiglet folder)

   A good website to download individual fonts:
   http://www.jave.de/figlet/fonts/overview.html

### Demo program included

   Run the demo program with either:   
   `textual-pyfiglet`   
   Or:   
   `python -m textual_pyfiglet`

   PyFiglet also has its own CLI which has been kept available. You can access the PyFiglet CLI with:   
   `python -m textual_pyfiglet.pyfiglet`

   Try it out to see the options. For instance, try running this code:   
   `python -m textual_pyfiglet.pyfiglet Hey guys, whats up?`   


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