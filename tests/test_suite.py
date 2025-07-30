from typing import cast
from pathlib import Path
from textual.pilot import Pilot
from textual_pyfiglet.demo import TextualPyFigletDemo

DEMO_DIR = Path(__file__).parent.parent / "src" / "textual_pyfiglet" / "demo"
TERINAL_SIZE = (110, 36)

async def test_launch():  
    """Test launching the TextualPyFigletDemo app."""
    app = TextualPyFigletDemo()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.exit(None) 

def test_snapshot_pattern_nostyle(snap_compare):

    async def run_before(pilot: Pilot[None]) -> None:
        pilot.app.action_focus_next()
        await pilot.wait_for_animation()

    assert snap_compare(
        DEMO_DIR / "main.py",
        terminal_size=TERINAL_SIZE,
        run_before=run_before,
    )

def test_snapshot_slidecontainer_closed(snap_compare):

    async def run_before(pilot: Pilot[None]) -> None:
        demo_app = cast(TextualPyFigletDemo, pilot.app)
        demo_app.action_toggle_menu()
        demo_app.action_focus_next()
        await pilot.wait_for_animation()

    assert snap_compare(
        DEMO_DIR / "main.py",
        terminal_size=TERINAL_SIZE,
        run_before=run_before,
    ) 

def test_snapshot_set_font_slant(snap_compare):

    async def run_before(pilot: Pilot[None]) -> None:
        demo_app = cast(TextualPyFigletDemo, pilot.app)
        demo_app.figlet_widget.font = "slant"
        demo_app.action_focus_next()
        await pilot.wait_for_animation()

    assert snap_compare(
        DEMO_DIR / "main.py",
        terminal_size=TERINAL_SIZE,
        run_before=run_before,
    )     

def test_snapshot_colors_basic(snap_compare):

    async def run_before(pilot: Pilot[None]) -> None:
        demo_app = cast(TextualPyFigletDemo, pilot.app)
        demo_app.figlet_widget.set_color_list(["red", "blue"])
        demo_app.action_focus_next()
        await pilot.pause()

    assert snap_compare(
        DEMO_DIR / "main.py",
        terminal_size=TERINAL_SIZE,
        run_before=run_before,
    )    

def test_snapshot_colors_horizontal(snap_compare):

    async def run_before(pilot: Pilot[None]) -> None:
        demo_app = cast(TextualPyFigletDemo, pilot.app)
        demo_app.figlet_widget.horizontal = True
        demo_app.figlet_widget.set_color_list(["red", "blue"])
        demo_app.action_focus_next()
        await pilot.pause()

    assert snap_compare(
        DEMO_DIR / "main.py",
        terminal_size=TERINAL_SIZE,
        run_before=run_before,
    )        