"""Defines the symbol sets used for ASCII art conversion."""

from typing import List, Tuple, Union, Optional
from dataclasses import dataclass

# Constants
EMPTY_CHAR = ' '


@dataclass
class Symbols:
    """
    Represents a set of characters used to render ASCII art.
    
    The characters are ordered from lightest to darkest, and are selected
    based on the brightness of the pixel being rendered.
    """
    set: List[str] = None
    
    def __post_init__(self):
        """Initialize with empty list if None."""
        if self.set is None:
            self.set = []
    
    @classmethod
    def empty(cls) -> 'Symbols':
        """Create an empty symbol set."""
        return cls([])
    
    def get(self, idx: int) -> str:
        """
        Get the character at the specified index.
        
        If the set is empty, returns EMPTY_CHAR.
        If idx is out of range, returns the last character.
        """
        if self.is_empty():
            return EMPTY_CHAR
        if idx >= len(self.set):
            return self.set[-1]
        return self.set[idx]
    
    def sym_index(self, pixel: Tuple[int, int, int, int]) -> int:
        """
        Calculate the index of the symbol in the set based on the RGBA value.
        
        Args:
            pixel: RGBA tuple (r, g, b, a)
            
        Returns:
            Index into the symbol set
        """
        if self.is_empty():
            return 0
            
        r, g, b, a = pixel
        
        # Calculate brightness index
        length = len(self.set)
        idx = (r + g + b) // 3
        
        if idx == 0:
            return 0
            
        if a < 120:
            idx = a % (idx or 1)
            
        # Map to symbol range
        idx = idx * length // 256
        
        # Ensure valid range
        return min(idx, length - 1)
    
    def sym_and_index(self, pixel: Tuple[int, int, int, int]) -> Tuple[str, int]:
        """Get both the symbol and its index for a given pixel."""
        idx = self.sym_index(pixel)
        return self.get(idx), idx
    
    def __len__(self) -> int:
        """Return the length of the symbol set."""
        return len(self.set)
    
    def is_empty(self) -> bool:
        """Check if the symbol set is empty."""
        return len(self.set) == 0


# Singleton empty set
EMPTY_SET = Symbols.empty()