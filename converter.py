"""Core image conversion functionality with enhanced stream handling."""

from typing import Tuple, Protocol, Optional, BinaryIO, TextIO, Union, Any, runtime_checkable
import sys
import io

from .color import ANSIColor, ANSI_ESCAPE_CLOSE
from .symbols import Symbols
from .config import Config, COLORS, REVERSE
from .text_image import FragmentInfo, FragmentWriter


@runtime_checkable
class PixelImage(Protocol):
    """Protocol for image objects that can be converted to ASCII."""
    
    def dimensions(self) -> Tuple[int, int]:
        """Get the image dimensions (width, height)."""
        ...
    
    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """Get the RGBA value of a pixel."""
        ...


class StreamFragmentWriter:
    """Implements FragmentWriter for file-like objects with advanced stream type detection."""
    
    def __init__(self, stream: Union[TextIO, BinaryIO]):
        """Initialize with intelligent stream type detection."""
        self.stream = stream
        # Enhanced stream type detection using introspection
        self.is_text_io = isinstance(stream, io.TextIOBase) or hasattr(stream, 'encoding')
        # Maintain backward compatibility with existing codebase
        self.is_binary = not self.is_text_io
    
    def background(self, bg: ANSIColor) -> bool:
        """Set the background color with protocol-aware data handling."""
        if bg.is_transparent:
            return False
        self.write_bytes(bg.as_background())
        return True
    
    def write_fragment(self, info: FragmentInfo) -> None:
        """Write a fragment to the stream with automatic format conversion."""
        self.write_bytes(info.sym)
    
    def write_colored_fragment(
        self, info: FragmentInfo, 
        bg: Optional[ANSIColor] = None, 
        fg: Optional[ANSIColor] = None
    ) -> None:
        """Write a colored fragment to the stream with protocol-aware formatting."""
        if bg:
            self.write_bytes(bg.as_background())
        if fg:
            self.write_bytes(fg.as_foreground())
            
        self.write_bytes(info.sym)
        
        if bg or fg:
            self.write_bytes(ANSI_ESCAPE_CLOSE)
    
    def write_bytes(self, data: Union[bytes, str]) -> None:
        """Write raw data to the stream with intelligent type conversion.
        
        This implementation dynamically adapts to the stream's protocol requirements
        by determining the appropriate data type at write-time rather than initialization.
        """
        if self.is_text_io:
            # Text stream protocol implementation
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            self.stream.write(data)
        else:
            # Binary stream protocol implementation
            if isinstance(data, str):
                data = data.encode('utf-8')
            self.stream.write(data)


def convert_image_to_ascii(
    config: Config, 
    image: PixelImage, 
    output: Union[FragmentWriter, TextIO, BinaryIO]
) -> None:
    """
    Convert an image to ASCII art and write it to the output.
    
    Args:
        config: Configuration for the conversion
        image: Image to convert
        output: Output to write to
    """
    # Robust protocol verification with runtime checking
    if not isinstance(output, FragmentWriter):
        output = StreamFragmentWriter(output)
        
    width, height = image.dimensions()
    
    ansi_close = False
    if config.background:
        if not config.reversed:
            ansi_close = output.background(config.background)
    
    colored = config.use_colors
    
    for y in range(height):
        for x in range(width):
            pixel = image.get_pixel(x, y)
            
            if colored:
                r, g, b, a = pixel
                sym, sym_index = config.symbols.sym_and_index(pixel)
                fg = ANSIColor(r, g, b, a)
                
                fi = FragmentInfo(sym=sym, sym_index=sym_index, fg=fg)
                
                fg_color = fg if not fg.is_transparent else None
                bg_color = config.background
                
                if ansi_close and config.reversed:
                    # Swap background and foreground
                    fg_color, bg_color = bg_color, fg_color
                    
                output.write_colored_fragment(fi, bg_color, fg_color)
            else:
                sym, sym_index = config.symbols.sym_and_index(pixel)
                r, g, b, a = pixel
                output.write_fragment(FragmentInfo(
                    sym=sym, 
                    sym_index=sym_index,
                    fg=ANSIColor(r, g, b, a)
                ))
                
        # Write newline with consistent stream type handling
        output.write_bytes('\n')
    
    if ansi_close:
        output.write_bytes(ANSI_ESCAPE_CLOSE)