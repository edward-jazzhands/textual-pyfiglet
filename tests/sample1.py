# This file is a work in progress
# none of this is usable yet

import pytest
from unittest.mock import Mock, patch
from textual.app import App, ComposeResult
from textual.pilot import Pilot

# Assuming these imports - adjust paths as needed
from textual_pyfiglet.figletwidget import FigletWidget, JUSTIFY_OPTIONS, ALL_FONTS
from rich_pyfiglet.pyfiglet import FigletError


class TestApp(App[None]):
    """Simple test app to hold our widget."""
    
    def compose(self) -> ComposeResult:
        yield FigletWidget(id="test-widget")


@pytest.fixture
async def pilot():
    """Create a pilot for testing."""
    app = TestApp()
    async with app.run_test() as pilot:
        yield pilot


class TestFigletWidgetBasics:
    """Test basic functionality."""
    
    def test_widget_creation_defaults(self):
        """Test widget can be created with default values."""
        widget = FigletWidget()
        assert widget.text_input == ""
        assert widget.font == "standard"
        assert widget.justify == "center"
    
    def test_widget_creation_with_text(self):
        """Test widget creation with initial text."""
        widget = FigletWidget("Hello")
        assert widget.text_input == "Hello"
    
    def test_widget_creation_with_params(self):
        """Test widget creation with various parameters."""
        widget = FigletWidget(
            text="Test", 
            font="big", 
            justify="left"
        )
        assert widget.text_input == "Test"
        assert widget.font == "big"
        assert widget.justify == "left"


class TestPublicAPIMethods:
    """Test the public API methods."""
    
    def test_update_method(self):
        """Test the update() method changes text_input."""
        widget = FigletWidget()
        widget.update("New Text")
        assert widget.text_input == "New Text"
    
    def test_set_text_method(self):
        """Test set_text() alias method."""
        widget = FigletWidget()
        widget.set_text("Alias Test")
        assert widget.text_input == "Alias Test"
    
    def test_set_font_method(self):
        """Test set_font() with string input."""
        widget = FigletWidget()
        widget.set_font("big")
        assert widget.font == "big"
    
    def test_set_justify_method(self):
        """Test set_justify() with string input."""
        widget = FigletWidget()
        widget.set_justify("right")
        assert widget.justify == "right"
    
    def test_figlet_quick_classmethod(self):
        """Test the figlet_quick class method."""
        result = FigletWidget.figlet_quick("Test")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Test" in result or any(c.isalpha() for c in result)  # ASCII art contains letters
    
    def test_figlet_quick_with_params(self):
        """Test figlet_quick with different parameters."""
        result = FigletWidget.figlet_quick("Hi", font="big", justify="center")
        assert isinstance(result, str)
        assert len(result) > 0


class TestValidators:
    """Test the validation methods."""
    
    def test_validate_text_input_valid(self):
        """Test text input validation with valid strings."""
        widget = FigletWidget()
        assert widget.validate_text_input("test") == "test"
        assert widget.validate_text_input("") == ""
        assert widget.validate_text_input("123") == "123"
    
    def test_validate_text_input_invalid(self):
        """Test text input validation with invalid types."""
        widget = FigletWidget()
        with pytest.raises(AssertionError, match="Figlet input must be a string"):
            widget.validate_text_input(123)  # type: ignore
    
    def test_validate_font_valid(self):
        """Test font validation with valid fonts."""
        widget = FigletWidget()
        assert widget.validate_font("standard") == "standard"
        assert widget.validate_font("big") == "big"
    
    def test_validate_font_invalid(self):
        """Test font validation with invalid font."""
        widget = FigletWidget()
        with pytest.raises(ValueError, match="Invalid font"):
            widget.validate_font("nonexistent_font")  # type: ignore
    
    def test_validate_justify_valid(self):
        """Test justify validation with valid options."""
        widget = FigletWidget()
        assert widget.validate_justify("left") == "left"
        assert widget.validate_justify("center") == "center"
        assert widget.validate_justify("right") == "right"
        assert widget.validate_justify("auto") == "auto"
    
    def test_validate_justify_invalid(self):
        """Test justify validation with invalid option."""
        widget = FigletWidget()
        with pytest.raises(ValueError, match="Invalid justification"):
            widget.validate_justify("invalid")


class TestRenderLogic:
    """Test the figlet rendering logic."""
    
    def test_render_figlet_basic(self):
        """Test basic figlet rendering."""
        widget = FigletWidget()
        result = widget.render_figlet("Hi")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(line, str) for line in result)
    
    def test_render_figlet_empty_string(self):
        """Test rendering empty string."""
        widget = FigletWidget()
        result = widget.render_figlet("")
        assert result == [""]
    
    def test_render_figlet_whitespace_cleanup(self):
        """Test that leading/trailing blank lines are removed."""
        widget = FigletWidget()
        result = widget.render_figlet("A")  # Single character should have minimal blank lines
        # Check that we don't have leading/trailing all-space lines
        if len(result) > 1:
            assert not all(c == " " for c in result[0])  # First line shouldn't be all spaces
            assert not all(c == " " for c in result[-1])  # Last line shouldn't be all spaces
    
    @patch('your_module.FigletWidget.figlet')
    def test_render_figlet_error_handling(self, mock_figlet):
        """Test error handling in render_figlet."""
        widget = FigletWidget()
        mock_figlet.renderText.side_effect = FigletError("Test error")
        
        with pytest.raises(FigletError):
            widget.render_figlet("test")
    
    def test_get_figlet_as_string(self):
        """Test get_figlet_as_string method."""
        widget = FigletWidget("Test")
        # Trigger rendering by accessing text_input
        widget.text_input = "Test"
        result = widget.get_figlet_as_string()
        assert isinstance(result, str)


class TestReactiveWatchers:
    """Test the reactive watchers."""
    
    def test_watch_text_input_empty(self):
        """Test watcher behavior with empty text."""
        widget = FigletWidget()
        widget.watch_text_input("")
        assert widget._animation_lines == [""]
    
    def test_watch_text_input_with_text(self):
        """Test watcher behavior with actual text."""
        widget = FigletWidget()
        widget.watch_text_input("Hi")
        assert isinstance(widget._animation_lines, list)
        assert len(widget._animation_lines) > 0
    
    @patch('your_module.FigletWidget.figlet')
    def test_watch_font(self, mock_figlet):
        """Test font watcher."""
        widget = FigletWidget()
        widget._initialized = True  # Simulate initialized state
        widget.watch_font("big")
        mock_figlet.setFont.assert_called_with(font="big")
    
    @patch('your_module.FigletWidget.figlet')
    def test_watch_justify(self, mock_figlet):
        """Test justify watcher."""
        widget = FigletWidget()
        widget._initialized = True  # Simulate initialized state
        widget.watch_justify("left")
        assert mock_figlet.justify == "left"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_fonts_list_available(self):
        """Test that fonts_list is populated."""
        assert hasattr(FigletWidget, 'fonts_list')
        assert isinstance(FigletWidget.fonts_list, list)
        assert len(FigletWidget.fonts_list) > 0
        assert "standard" in FigletWidget.fonts_list
    
    def test_text_conversion_in_init(self):
        """Test that non-string text is converted to string in __init__."""
        widget = FigletWidget(123)  # type: ignore
        assert widget.text_input == "123"
    
    def test_text_conversion_exception_in_init(self):
        """Test exception handling during text conversion in __init__."""
        # Create an object that will raise an exception on str()
        class BadObject:
            def __str__(self):
                raise ValueError("Cannot convert to string")
        
        with pytest.raises(ValueError, match="Cannot convert to string"):
            FigletWidget(BadObject())  # type: ignore


# Parametrized tests for comprehensive coverage
class TestParametrized:
    """Parametrized tests for better coverage."""
    
    @pytest.mark.parametrize("font_name", ["standard", "big", "small"])
    def test_different_fonts(self, font_name):
        """Test rendering with different fonts."""
        widget = FigletWidget("Test", font=font_name)  # type: ignore
        result = widget.render_figlet("Hi")
        assert isinstance(result, list)
        assert len(result) > 0
    
    @pytest.mark.parametrize("justify_option", ["left", "center", "right"])
    def test_different_justifications(self, justify_option):
        """Test rendering with different justifications."""
        widget = FigletWidget("Test", justify=justify_option)  # type: ignore
        result = widget.render_figlet("Hi")
        assert isinstance(result, list)
        assert len(result) > 0
    
    @pytest.mark.parametrize("text_input", ["", "A", "Hello", "123", "Special!@#"])
    def test_various_text_inputs(self, text_input):
        """Test rendering with various text inputs."""
        widget = FigletWidget()
        result = widget.render_figlet(text_input)
        assert isinstance(result, list)
        if text_input == "":
            assert result == [""]
        else:
            assert len(result) > 0


# Integration tests with Textual pilot (if you want to test UI interactions)
class TestWithPilot:
    """Integration tests using Textual pilot."""
    
    async def test_widget_in_app(self, pilot: Pilot):
        """Test widget integration in a Textual app."""
        widget = pilot.app.query_one("#test-widget", FigletWidget)
        assert widget is not None
        
        # Test updating text through the widget
        widget.update("Hello")
        assert widget.text_input == "Hello"
    
    async def test_reactive_updates(self, pilot: Pilot):
        """Test that reactive updates work in app context."""
        widget = pilot.app.query_one("#test-widget", FigletWidget)
        
        # Test that changing reactives triggers updates
        widget.text_input = "Test"
        await pilot.pause()  # Let the reactive system process
        
        assert widget.text_input == "Test"
        assert isinstance(widget._animation_lines, list)