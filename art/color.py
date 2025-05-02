from dataclasses import dataclass
from typing import Tuple, Optional

ANSI_ESCAPE_CLOSE = "\033[0m"
ANSI_FOREGROUND_ESCAPE = "\033[38;2;"
ANSI_BACKGROUND_ESCAPE = "\033[48;2;"
ANSI_COLOR_CODE_LEN = 12


@dataclass
class ANSIColor:
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255
    
    def __post_init__(self):
        for attr in ('r', 'g', 'b', 'a'):
            val = getattr(self, attr)
            if not isinstance(val, int) or not (0 <= val <= 255):
                setattr(self, attr, min(255, max(0, int(val))))
    
    @property
    def is_transparent(self) -> bool:
        return self.a < 120
    
    def as_background(self) -> str:
        if self.is_transparent:
            return ""
        return f"{ANSI_BACKGROUND_ESCAPE}{self.r};{self.g};{self.b}m"
    
    def as_foreground(self) -> str:
        if self.is_transparent:
            return ""
        return f"{ANSI_FOREGROUND_ESCAPE}{self.r};{self.g};{self.b}m"
    
    def __str__(self) -> str:
        if self.is_transparent:
            return ""
        return f"{ANSI_FOREGROUND_ESCAPE}{self.r};{self.g};{self.b}m"
    
    def __format__(self, format_spec: str) -> str:
        if self.is_transparent:
            return ""
        if '-' in format_spec:
            return self.as_background()
        return self.as_foreground()

TRANSPARENT = ANSIColor(0, 0, 0, 0)