"""ANSI color functionality for terminal output."""

from dataclasses import dataclass
from typing import Tuple, Optional

# Constants for ANSI escape sequences
ANSI_ESCAPE_CLOSE = "\033[0m"
ANSI_FOREGROUND_ESCAPE = "\033[38;2;"
ANSI_BACKGROUND_ESCAPE = "\033[48;2;"
ANSI_COLOR_CODE_LEN = 12


@dataclass
class ANSIColor:
    """
    Represents an ANSI color for terminal output.
    
    This class handles the conversion of RGB values to ANSI escape codes
    for both foreground and background colors.
    """
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255
    
    def __post_init__(self):
        """Validate color values."""
        for attr in ('r', 'g', 'b', 'a'):
            val = getattr(self, attr)
            if not isinstance(val, int) or not (0 <= val <= 255):
                setattr(self, attr, min(255, max(0, int(val))))
    
    @property
    def is_transparent(self) -> bool:
        """Return True if the color is transparent (alpha < 120)."""
        return self.a < 120
    
    def as_background(self) -> str:
        """Return an ANSI escaped background color."""
        if self.is_transparent:
            return ""
        return f"{ANSI_BACKGROUND_ESCAPE}{self.r};{self.g};{self.b}m"
    
    def as_foreground(self) -> str:
        """Return an ANSI escaped foreground color."""
        if self.is_transparent:
            return ""
        return f"{ANSI_FOREGROUND_ESCAPE}{self.r};{self.g};{self.b}m"
    
    def __str__(self) -> str:
        """String representation for the color."""
        if self.is_transparent:
            return ""
        return f"{ANSI_FOREGROUND_ESCAPE}{self.r};{self.g};{self.b}m"
    
    def __format__(self, format_spec: str) -> str:
        """Format the color according to format_spec."""
        if self.is_transparent:
            return ""
        if '-' in format_spec:
            return self.as_background()
        return self.as_foreground()


# Transparent color singleton
TRANSPARENT = ANSIColor(0, 0, 0, 0)