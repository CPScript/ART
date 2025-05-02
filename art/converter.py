from typing import Tuple, Protocol, Optional, BinaryIO, TextIO, Union, Any, runtime_checkable
import sys
import io

from .color import ANSIColor, ANSI_ESCAPE_CLOSE
from .symbols import Symbols
from .config import Config, COLORS, REVERSE
from .text_image import FragmentInfo, FragmentWriter


@runtime_checkable
class PixelImage(Protocol):
    
    def dimensions(self) -> Tuple[int, int]:
        ...
    
    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        ...


class StreamFragmentWriter:
    
    def __init__(self, stream: Union[TextIO, BinaryIO]):
        self.stream = stream
        self.is_text_io = isinstance(stream, io.TextIOBase) or hasattr(stream, 'encoding')
        self.is_binary = not self.is_text_io
    
    def background(self, bg: ANSIColor) -> bool:
        if bg.is_transparent:
            return False
        self.write_bytes(bg.as_background())
        return True
    
    def write_fragment(self, info: FragmentInfo) -> None:
        self.write_bytes(info.sym)
    
    def write_colored_fragment(
        self, info: FragmentInfo, 
        bg: Optional[ANSIColor] = None, 
        fg: Optional[ANSIColor] = None
    ) -> None:
        if bg:
            self.write_bytes(bg.as_background())
        if fg:
            self.write_bytes(fg.as_foreground())
            
        self.write_bytes(info.sym)
        
        if bg or fg:
            self.write_bytes(ANSI_ESCAPE_CLOSE)
    
    def write_bytes(self, data: Union[bytes, str]) -> None:
        if self.is_text_io:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            self.stream.write(data)
        else:
            if isinstance(data, str):
                data = data.encode('utf-8')
            self.stream.write(data)


def convert_image_to_ascii(
    config: Config, 
    image: PixelImage, 
    output: Union[FragmentWriter, TextIO, BinaryIO]
) -> None:
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
                
        output.write_bytes('\n')
    
    if ansi_close:
        output.write_bytes(ANSI_ESCAPE_CLOSE)