from textual.app import App
from textual import on
from textual.widgets import Static, Button, RadioSet, RadioButton, Checkbox, Input
from textual.containers import Container

from textual_slidecontainer import SlideContainer
from textual_pyfiglet.figletwidget import FigletWidget

class TextualApp(App[None]):


    BINDINGS = [
        ("t", "toggle_slide", "Toggle Slide Container")
    ]

    DEFAULT_CSS = """
    #my_container {
        width: 1fr; height: 1fr;
        align: left middle; content-align: center middle;
        padding: 3;
    }
    #my_static { 
        border: solid $primary; 
        width: 1fr; 
        content-align: center middle; 
    }
    SlideContainer {
        width: 30; height: 85%;
        background: $panel; align: center top;
        border: outer $panel-darken-1;

    }
    Button { margin: 0 1; }
    .menubar { background: transparent; }
    """

    def compose(self):

       # The container will start closed / hidden:
        with SlideContainer(slide_direction="left", start_open=False):
            yield Static("SlideContainer", id="my_static")
            with RadioSet(classes="menubar"):
                yield RadioButton("Option 1", id="option1")
                yield RadioButton("Option 2", id="option2")
                yield RadioButton("Option 3", id="option3")
                yield RadioButton("Option 4", id="option4")
                yield RadioButton("Option 5", id="option5")
            yield Input(placeholder="Type something here...", id="input_field", classes="menubar")
            yield Checkbox("Checkbox One", id="checkbox_one", classes="menubar")
            yield Checkbox("Checkbox Two", id="checkbox_two", classes="menubar")
            yield Checkbox("Checkbox Three", id="checkbox_three", classes="menubar")

            
        # yield Footer()        

        with Container(id="my_container"):
            self.figlet_widget = FigletWidget(
                "Textual - SlideContainer",
                font="ansi_shadow",
                horizontal=True,
                justify="left",
                colors=["yellow", "crimson"],
                # animate=True,
                # gradient_quality=50,
                # fps=4,
            )
            yield self.figlet_widget
 

    @on(Button.Pressed, "#toggle_slide")
    def action_toggle_slide(self) -> None:
        self.query_one(SlideContainer).toggle()

TextualApp().run()