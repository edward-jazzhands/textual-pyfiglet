"validators.py"

from __future__ import annotations
import re

from textual.validation import Validator, ValidationResult  # , Number
from textual.color import Color, ColorParseError


class ColorValidator(Validator):

    def __init__(self, theme_variables: dict[str, str]) -> None:
        super().__init__()
        self.theme_variables = theme_variables

    def validate(self, value: str) -> ValidationResult:

        if value == "":
            return self.success()

        if value.startswith("$"):
            try:
                value = self.theme_variables[value[1:]]
            except KeyError:
                return self.failure(f"Color variable {value} not found in theme variables.")

        try:
            Color.parse(value)
        except ColorParseError:
            return self.failure("Invalid color format. Must be a valid color name or hex code.")
        else:
            return self.success()


class QualityValidator(Validator):

    def validate(self, value: str) -> ValidationResult:

        if value == "":
            return self.success()
        try:
            value_int = int(value)
        except ValueError:
            return self.failure(
                "Invalid quality format. Must be empty (for auto), or an integer between 3-100."
            )
        else:
            if 3 <= value_int <= 100:
                return self.success()
            else:
                return self.failure(
                    "Invalid quality format. Must be empty (for auto), or an integer between 3-100."
                )


class FPSValidator(Validator):

    def validate(self, value: str) -> ValidationResult:

        if value == "":
            return self.success()
        try:
            value_float = float(value)
        except ValueError:
            return self.failure(
                "Invalid FPS format. Must be empty (for auto), or a float greater than 0 with max 100."
            )
        else:
            if 0 < value_float <= 100:
                return self.success()
            else:
                return self.failure(
                    "Invalid FPS format. Must be empty (for auto), or a float greater than 0 with max 100."
                )


class SizeValidator(Validator):

    patterns = [
        r"^[1-9][0-9]{0,2}$",  # Number between 1-999
        r"^(100|[1-9]?[0-9])%$",  # Percentage
        r"^\d*\.?\d+fr$",  # Float followed by 'fr'
    ]

    def validate(self, value: str) -> ValidationResult:

        if any(re.match(pattern, value) for pattern in self.patterns):
            return self.success()
        elif value == "":
            return self.success()
        else:
            return self.failure(
                "Invalid size format. Must be a number between 1-999, a percentage, "
                "a float followed by 'fr', or 'auto'."
            )
