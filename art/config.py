from typing import Optional, Tuple, Union, Any
from dataclasses import dataclass, field

from .symbols import Symbols, EMPTY_SET
from .color import ANSIColor

# Constants for flags
COLORS = 0b1
REVERSE = 0b10


@dataclass
class Config:
    symbols: Symbols
    background: Optional[ANSIColor] = None
    flags: int = 0
    
    @classmethod
    def new(cls, symbols: Symbols) -> 'Config':
        return cls(symbols=symbols)
    
    def with_flags(self, flags: int) -> 'Config':
        return Config(
            symbols=self.symbols,
            background=self.background,
            flags=flags
        )
    
    def with_background(self, color: Union[ANSIColor, Tuple[int, int, int]]) -> 'Config':
        if isinstance(color, tuple):
            color = ANSIColor(*color)
        return Config(
            symbols=self.symbols,
            background=color,
            flags=self.flags
        )
    
    @classmethod
    def new_with_background(cls, symbols: Symbols, background: ANSIColor) -> 'Config':
        return cls(symbols=symbols, background=background)
    
    @property
    def reversed(self) -> bool:
        return bool(self.flags & REVERSE)
    
    @property
    def use_colors(self) -> bool:
        return bool(self.flags & COLORS)
    
    def calc_buf_size(self, width: int, height: int) -> int:
        size = width * height
        
        if self.use_colors:
            size *= 25
            
        return size