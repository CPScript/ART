from typing import List, Optional, Tuple, Dict, Any, Protocol, runtime_checkable, Union
import io
from dataclasses import dataclass, field

from .color import ANSIColor, TRANSPARENT, ANSI_ESCAPE_CLOSE
from .symbols import Symbols
from .config import Config


@dataclass
class FragmentInfo:
    sym: str
    sym_index: int
    fg: ANSIColor = field(default_factory=lambda: TRANSPARENT)


@dataclass
class IndexedFragment:
    sym_index: int
    fg: ANSIColor = field(default_factory=lambda: TRANSPARENT)
    
    @classmethod
    def new(cls, sym_index: int) -> 'IndexedFragment':
        return cls(sym_index=sym_index)
    
    def with_foreground(self, fg: ANSIColor) -> 'IndexedFragment':
        return IndexedFragment(sym_index=self.sym_index, fg=fg)
    
    @classmethod
    def new_with_foreground(cls, sym_index: int, fg: ANSIColor) -> 'IndexedFragment':
        return cls(sym_index=sym_index, fg=fg)


@dataclass
class Fragment:
    ch: str
    fg: ANSIColor = field(default_factory=lambda: TRANSPARENT)
    
    @classmethod
    def new(cls, ch: str) -> 'Fragment':
        return cls(ch=ch)
    
    @property
    def sym(self) -> str:
        return self.ch
    
    def with_foreground(self, fg: ANSIColor) -> 'Fragment':
        return Fragment(ch=self.ch, fg=fg)
    
    @classmethod
    def new_with_foreground(cls, ch: str, fg: ANSIColor) -> 'Fragment':
        return cls(ch=ch, fg=fg)
    
    @property
    def foreground(self) -> ANSIColor:
        return self.fg


@runtime_checkable
class FragmentWriter(Protocol):    
    def background(self, bg: ANSIColor) -> bool:
        ...
    
    def write_fragment(self, info: FragmentInfo) -> None:
        ...
    
    def write_colored_fragment(
        self, info: FragmentInfo, 
        bg: Optional[ANSIColor] = None, 
        fg: Optional[ANSIColor] = None
    ) -> None:
        ...
    
    def write_bytes(self, bytes_data: Union[bytes, str]) -> None:
        ...


class TextImage:
    def __init__(self, config: Config, width: int, height: int):
        self.config = config
        self.fragments: List[IndexedFragment] = []
        self.row_len = width
        self.height = height
    
    def fragment_at(self, x: int, y: int) -> Optional[Fragment]:
        idx = y * self.row_len + x
        return self.get(idx)
    
    def get(self, idx: int) -> Optional[Fragment]:
        if idx < len(self.fragments):
            return self._get_unchecked(idx)
        return None
    
    def _get_unchecked(self, idx: int) -> Fragment:
        fragment = self.fragments[idx]
        return Fragment(
            ch=self.config.symbols.get(fragment.sym_index),
            fg=fragment.fg
        )
    
    def _fragment_at_unchecked(self, x: int, y: int) -> Fragment:
        return self._get_unchecked(y * self.row_len + x)
    
    def insert(self, idx: int, fragment: IndexedFragment) -> None:
        if idx >= len(self.fragments):
            # Extend the list if necessary
            self.fragments.extend([IndexedFragment(0)] * (idx - len(self.fragments) + 1))
        self.fragments[idx] = fragment
    
    def put(self, x: int, y: int, fragment: IndexedFragment) -> None:
        self.insert(y * self.row_len + x, fragment)
    
    def __len__(self) -> int:
        return len(self.fragments)
    
    def is_empty(self) -> bool:
        return len(self.fragments) == 0
    
    def __str__(self) -> str:
        result = io.StringIO()
        
        if self.config.use_colors:
            self._color_fmt(result)
        else:
            self._fmt(result)
            
        return result.getvalue()
    
    def _fmt(self, buffer: io.StringIO) -> None:
        i = 0
        for frag in self.fragments:
            if i == self.row_len:
                i = 0
                buffer.write('\n')
            buffer.write(self.config.symbols.get(frag.sym_index))
            i += 1
    
    def _color_fmt(self, buffer: io.StringIO) -> None:
        has_background = False
        
        if self.config.reversed:
            if self.config.background and not self.config.background.is_transparent:
                buffer.write(str(self.config.background))
                has_background = True
        else:
            if self.config.background:
                buffer.write(self.config.background.as_background())
                has_background = True
        
        i = 0
        for frag in self.fragments:
            if i == self.row_len:
                i = 0
                buffer.write('\n')
            i += 1
            
            sym = self.config.symbols.get(frag.sym_index)
            
            if self.config.reversed:
                buffer.write(f"{frag.fg:-}")
            else:
                buffer.write(f"{frag.fg}")
                
            buffer.write(f"{sym}{ANSI_ESCAPE_CLOSE}")
        
        if has_background:
            buffer.write(ANSI_ESCAPE_CLOSE)
    
    def background(self, bg: ANSIColor) -> bool:
        return True
    
    def write_fragment(self, info: FragmentInfo) -> None:
        self.fragments.append(IndexedFragment(
            sym_index=info.sym_index,
            fg=info.fg
        ))
    
    def write_colored_fragment(
        self, info: FragmentInfo, 
        bg: Optional[ANSIColor] = None, 
        fg: Optional[ANSIColor] = None
    ) -> None:
        self.write_fragment(info)
    
    def write_bytes(self, bytes_data: Union[bytes, str]) -> None:
        pass
