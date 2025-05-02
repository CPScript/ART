"""Text image representation for rendered ASCII art."""

from typing import List, Optional, Tuple, Dict, Any, Protocol, runtime_checkable, Union
import io
from dataclasses import dataclass, field

from .color import ANSIColor, TRANSPARENT, ANSI_ESCAPE_CLOSE
from .symbols import Symbols
from .config import Config


@dataclass
class FragmentInfo:
    """Information about a fragment (pixel) in the ASCII art."""
    sym: str
    sym_index: int
    fg: ANSIColor = field(default_factory=lambda: TRANSPARENT)


@dataclass
class IndexedFragment:
    """
    Fragment represented by its index in the symbol set.
    
    Reduces memory usage compared to storing the actual character.
    """
    sym_index: int
    fg: ANSIColor = field(default_factory=lambda: TRANSPARENT)
    
    @classmethod
    def new(cls, sym_index: int) -> 'IndexedFragment':
        """Create a new indexed fragment."""
        return cls(sym_index=sym_index)
    
    def with_foreground(self, fg: ANSIColor) -> 'IndexedFragment':
        """Return a new fragment with the specified foreground color."""
        return IndexedFragment(sym_index=self.sym_index, fg=fg)
    
    @classmethod
    def new_with_foreground(cls, sym_index: int, fg: ANSIColor) -> 'IndexedFragment':
        """Create a new fragment with both index and foreground set."""
        return cls(sym_index=sym_index, fg=fg)


@dataclass
class Fragment:
    """Represents a pixel in terminal context."""
    ch: str
    fg: ANSIColor = field(default_factory=lambda: TRANSPARENT)
    
    @classmethod
    def new(cls, ch: str) -> 'Fragment':
        """Create a new fragment."""
        return cls(ch=ch)
    
    @property
    def sym(self) -> str:
        """Get the character."""
        return self.ch
    
    def with_foreground(self, fg: ANSIColor) -> 'Fragment':
        """Return a new fragment with the specified foreground color."""
        return Fragment(ch=self.ch, fg=fg)
    
    @classmethod
    def new_with_foreground(cls, ch: str, fg: ANSIColor) -> 'Fragment':
        """Create a new fragment with both character and foreground set."""
        return cls(ch=ch, fg=fg)
    
    @property
    def foreground(self) -> ANSIColor:
        """Get the fragment foreground."""
        return self.fg


@runtime_checkable
class FragmentWriter(Protocol):
    """Protocol for writing fragments to a buffer."""
    
    def background(self, bg: ANSIColor) -> bool:
        """Set the background color and return whether to send ANSI close code."""
        ...
    
    def write_fragment(self, info: FragmentInfo) -> None:
        """Write a fragment to the buffer."""
        ...
    
    def write_colored_fragment(
        self, info: FragmentInfo, 
        bg: Optional[ANSIColor] = None, 
        fg: Optional[ANSIColor] = None
    ) -> None:
        """Write a colored fragment to the buffer."""
        ...
    
    def write_bytes(self, bytes_data: Union[bytes, str]) -> None:
        """Write raw bytes to the buffer."""
        ...


class TextImage:
    """
    Represents a complete ASCII art image.
    
    This class stores the fragments that make up the image and provides
    methods for accessing and manipulating them.
    """
    
    def __init__(self, config: Config, width: int, height: int):
        """Initialize a text image with the given dimensions."""
        self.config = config
        self.fragments: List[IndexedFragment] = []
        self.row_len = width
        self.height = height
    
    def fragment_at(self, x: int, y: int) -> Optional[Fragment]:
        """Get the fragment at the specified coordinates."""
        idx = y * self.row_len + x
        return self.get(idx)
    
    def get(self, idx: int) -> Optional[Fragment]:
        """Get the fragment at the specified index."""
        if idx < len(self.fragments):
            return self._get_unchecked(idx)
        return None
    
    def _get_unchecked(self, idx: int) -> Fragment:
        """Get the fragment without bounds checking."""
        fragment = self.fragments[idx]
        return Fragment(
            ch=self.config.symbols.get(fragment.sym_index),
            fg=fragment.fg
        )
    
    def _fragment_at_unchecked(self, x: int, y: int) -> Fragment:
        """Get the fragment at coordinates without bounds checking."""
        return self._get_unchecked(y * self.row_len + x)
    
    def insert(self, idx: int, fragment: IndexedFragment) -> None:
        """Insert a fragment at the specified index."""
        if idx >= len(self.fragments):
            # Extend the list if necessary
            self.fragments.extend([IndexedFragment(0)] * (idx - len(self.fragments) + 1))
        self.fragments[idx] = fragment
    
    def put(self, x: int, y: int, fragment: IndexedFragment) -> None:
        """Insert a fragment at the specified coordinates."""
        self.insert(y * self.row_len + x, fragment)
    
    def __len__(self) -> int:
        """Get the number of fragments."""
        return len(self.fragments)
    
    def is_empty(self) -> bool:
        """Check if the image is empty."""
        return len(self.fragments) == 0
    
    def __str__(self) -> str:
        """Render the image as a string."""
        result = io.StringIO()
        
        if self.config.use_colors:
            self._color_fmt(result)
        else:
            self._fmt(result)
            
        return result.getvalue()
    
    def _fmt(self, buffer: io.StringIO) -> None:
        """Format the image without colors."""
        i = 0
        for frag in self.fragments:
            if i == self.row_len:
                i = 0
                buffer.write('\n')
            buffer.write(self.config.symbols.get(frag.sym_index))
            i += 1
    
    def _color_fmt(self, buffer: io.StringIO) -> None:
        """Format the image with colors."""
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
    
    # Implementation of FragmentWriter protocol
    def background(self, bg: ANSIColor) -> bool:
        """Set the background color."""
        return True
    
    def write_fragment(self, info: FragmentInfo) -> None:
        """Write a fragment to the buffer."""
        self.fragments.append(IndexedFragment(
            sym_index=info.sym_index,
            fg=info.fg
        ))
    
    def write_colored_fragment(
        self, info: FragmentInfo, 
        bg: Optional[ANSIColor] = None, 
        fg: Optional[ANSIColor] = None
    ) -> None:
        """Write a colored fragment to the buffer."""
        self.write_fragment(info)
    
    def write_bytes(self, bytes_data: Union[bytes, str]) -> None:
        """Write raw bytes to the buffer (ignored)."""
        pass
