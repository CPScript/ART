"""Configuration for ASCII art rendering."""

from typing import Optional, Tuple, Union, Any
from dataclasses import dataclass, field

from .symbols import Symbols, EMPTY_SET
from .color import ANSIColor

# Constants for flags
COLORS = 0b1
REVERSE = 0b10


@dataclass
class Config:
    """
    Configuration for ASCII art rendering.
    
    This class holds all parameters that affect the rendering of an image
    to ASCII art, including the symbol set, color options, and flags.
    """
    symbols: Symbols
    background: Optional[ANSIColor] = None
    flags: int = 0
    
    @classmethod
    def new(cls, symbols: Symbols) -> 'Config':
        """Create a new configuration with the given symbol set."""
        return cls(symbols=symbols)
    
    def with_flags(self, flags: int) -> 'Config':
        """Return a new configuration with the specified flags."""
        return Config(
            symbols=self.symbols,
            background=self.background,
            flags=flags
        )
    
    def with_background(self, color: Union[ANSIColor, Tuple[int, int, int]]) -> 'Config':
        """Return a new configuration with the specified background color."""
        if isinstance(color, tuple):
            color = ANSIColor(*color)
        return Config(
            symbols=self.symbols,
            background=color,
            flags=self.flags
        )
    
    @classmethod
    def new_with_background(cls, symbols: Symbols, background: ANSIColor) -> 'Config':
        """Create a new configuration with both symbols and background set."""
        return cls(symbols=symbols, background=background)
    
    @property
    def reversed(self) -> bool:
        """Check if the REVERSE flag is set."""
        return bool(self.flags & REVERSE)
    
    @property
    def use_colors(self) -> bool:
        """Check if the COLORS flag is set."""
        return bool(self.flags & COLORS)
    
    def calc_buf_size(self, width: int, height: int) -> int:
        """
        Calculate the buffer size needed for the ASCII art.
        
        This is used for allocating buffers for efficient rendering.
        """
        size = width * height
        
        if self.use_colors:
            # Account for ANSI color codes
            size *= 25  # Approximation for color codes overhead
            
        return size