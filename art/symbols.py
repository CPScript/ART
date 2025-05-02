from typing import List, Tuple, Union, Optional
from dataclasses import dataclass

# Constants
EMPTY_CHAR = ' '


@dataclass
class Symbols:
    set: List[str] = None
    
    def __post_init__(self):
        if self.set is None:
            self.set = []
    
    @classmethod
    def empty(cls) -> 'Symbols':
        return cls([])
    
    def get(self, idx: int) -> str:
        if self.is_empty():
            return EMPTY_CHAR
        if idx >= len(self.set):
            return self.set[-1]
        return self.set[idx]
    
    def sym_index(self, pixel: Tuple[int, int, int, int]) -> int:
        if self.is_empty():
            return 0
            
        r, g, b, a = pixel
        
        length = len(self.set)
        idx = (r + g + b) // 3
        
        if idx == 0:
            return 0
            
        if a < 120:
            idx = a % (idx or 1)
            
        idx = idx * length // 256
        
        return min(idx, length - 1)
    
    def sym_and_index(self, pixel: Tuple[int, int, int, int]) -> Tuple[str, int]:
        idx = self.sym_index(pixel)
        return self.get(idx), idx
    
    def __len__(self) -> int:
        return len(self.set)
    
    def is_empty(self) -> bool:
        return len(self.set) == 0

EMPTY_SET = Symbols.empty()