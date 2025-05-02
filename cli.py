#!/usr/bin/env python3
"""Command-line interface for AARTY."""

import sys
import argparse
from pathlib import Path
from typing import Optional, List, Tuple, Union, Any
import io

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow library is required. Install with 'pip install pillow'", file=sys.stderr)
    sys.exit(1)

from .color import ANSIColor
from .symbols import Symbols
from .config import Config, COLORS, REVERSE
from .converter import convert_image_to_ascii, PixelImage


class PILImageAdapter(PixelImage):
    """Adapter for PIL Image to PixelImage protocol."""
    
    def __init__(self, image: Image.Image):
        """Initialize with a PIL Image."""
        self.image = image.convert('RGBA')
    
    def dimensions(self) -> Tuple[int, int]:
        """Get the image dimensions."""
        return self.image.size
    
    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """Get the RGBA value of a pixel."""
        return self.image.getpixel((x, y))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments with conflict resolution."""
    parser = argparse.ArgumentParser(
        description="AARTY: Convert images to ASCII art for terminal display"
    )
    
    parser.add_argument(
        "path", nargs="?", type=str,
        help="Path to the image file (reads from stdin if not provided)"
    )
    
    parser.add_argument(
        "-c", "--symbols", type=str, default=" .,-~!;:=*&%$@#",
        help="Characters to use for drawing (lighter to darker)"
    )
    
    parser.add_argument(
        "-s", "--scale", type=int, default=4,
        help="Output scale (1 is original size)"
    )
    
    parser.add_argument(
        "-w", "--width", type=int,
        help="Output width in columns (overrides scale)"
    )
    
    # MODIFIED: Changed shorthand from -h to -H to avoid conflict
    parser.add_argument(
        "-H", "--height", type=int,
        help="Output height in rows (overrides scale)"
    )
    
    parser.add_argument(
        "-b", "--background", type=str,
        help="Background color (r,g,b format)"
    )
    
    parser.add_argument(
        "-r", "--reverse", action="store_true",
        help="Reverse foreground and background colors"
    )
    
    parser.add_argument(
        "-u", "--color", action="store_true",
        help="Use colors in output"
    )
    
    parser.add_argument(
        "--filter", type=str, choices=["nearest", "bilinear", "bicubic", "lanczos"],
        default="nearest", help="Resampling filter for resizing"
    )
    
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"AARTY v{__import__('aarty').__version__}"
    )
    
    return parser.parse_args()
    
def parse_color(color_str: str) -> Optional[Tuple[int, int, int]]:
    if not color_str:
        return None
        
    try:
        if ',' in color_str:
            r, g, b = map(int, color_str.split(','))
            return (r, g, b)
            
        if color_str.startswith('#') and len(color_str) == 7:
            r = int(color_str[1:3], 16)
            g = int(color_str[3:5], 16)
            b = int(color_str[5:7], 16)
            return (r, g, b)
            
    except (ValueError, IndexError):
        print(f"Error: Invalid color format '{color_str}'. Use r,g,b or #RRGGBB", file=sys.stderr)
        
    return None


def get_resize_filter(filter_name: str) -> int:
    """Get the PIL resize filter constant."""
    filters = {
        "nearest": Image.NEAREST,
        "bilinear": Image.BILINEAR,
        "bicubic": Image.BICUBIC,
        "lanczos": Image.LANCZOS,
    }
    return filters.get(filter_name, Image.NEAREST)


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Create configuration
    flags = 0
    if args.color:
        flags |= COLORS
    if args.reverse:
        flags |= REVERSE
        
    config = Config(
        symbols=Symbols(list(args.symbols)),
        flags=flags
    )
    
    if args.background:
        bg_color = parse_color(args.background)
        if bg_color:
            config.background = ANSIColor(*bg_color)
    
    # Load image
    try:
        if args.path:
            image = Image.open(args.path)
        else:
            # Read from stdin
            image = Image.open(io.BytesIO(sys.stdin.buffer.read()))
    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        return 1
    
    # Resize image
    width, height = image.size
    
    if args.width:
        width = args.width
    if args.height:
        height = args.height
        
    if args.scale > 1:
        width = width // args.scale
        height = height // args.scale
    
    resized_image = image.resize(
        (width, height), 
        resample=get_resize_filter(args.filter)
    )
    
    # Convert to ASCII
    image_adapter = PILImageAdapter(resized_image)
    convert_image_to_ascii(config, image_adapter, sys.stdout)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
