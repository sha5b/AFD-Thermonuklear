import win32file
import win32con
import serial.tools.list_ports
from typing import Dict, Optional
import time
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

class M08FPrinter:
    # M08F printer USB identifiers
    VENDOR_ID = "0483"  # STMicroelectronics
    PRODUCT_ID = "5740"  # M08F Printer
    
    # Printer settings
    MAX_WIDTH = 384  # Standard thermal printer width (48mm = 384 dots)
    BYTES_PER_LINE = 48  # 384 bits = 48 bytes per line
    LINE_HEIGHT = 40  # Increased line height
    FONT_SIZE = 48   # Larger initial font size

    def __init__(self, config: Dict):
        # Find printer port
        port = self.find_printer_port()
        if not port:
            raise Exception("M08F printer not found. Please check connection.")
            
        print(f"Connecting to printer on {port}...")
        
        # Open port directly
        port_path = r'\\.\{}'.format(port)  # Proper raw string for Windows path
        print(f"Opening port: {port_path}")
        self.handle = win32file.CreateFile(
            port_path,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            0,  # No sharing
            None,  # Default security
            win32con.OPEN_EXISTING,
            0,  # No overlapped I/O
            None  # No template file
        )
        
        # Configure port
        dcb = win32file.DCB()
        dcb.BaudRate = 9600
        dcb.ByteSize = 8
        dcb.Parity = 0  # NOPARITY
        dcb.StopBits = 0  # ONESTOPBIT
        win32file.SetCommState(self.handle, dcb)
        
        # Set timeouts (all timeouts in milliseconds)
        timeouts = (500, 500, 500, 500, 1000)  # Add reasonable timeouts
        win32file.SetCommTimeouts(self.handle, timeouts)
        
        self.config = config
        print(f"Connected to printer")
        
        # Initialize printer
        self._initialize_printer()
        
    @classmethod
    def find_printer_port(cls) -> Optional[str]:
        """Find the M08F printer port using VID and PID."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if (hasattr(port, "vid") and hasattr(port, "pid") and
                format(port.vid, "04x").upper() == cls.VENDOR_ID and
                format(port.pid, "04x").upper() == cls.PRODUCT_ID):
                return port.device
        return None
        
    def _initialize_printer(self):
        """Initialize the printer with basic settings."""
        # Reset printer
        self._write(b'\x1B\x40')  # ESC @ - Initialize printer
        time.sleep(0.1)
        
        # Set print density to highest
        self._write(b'\x1B\x37\x07')  # ESC 7 n - Set print density
        
        # Set line spacing
        self._write(b'\x1B\x33\x24')  # ESC 3 n - Set line spacing
        
        # Set print speed based on config (1=slow, 5=fast)
        speed = self.config.get('printer', {}).get('print_speed', 3)
        speed = max(1, min(5, speed))  # Ensure speed is between 1 and 5
        self._write(b'\x1B\x73' + bytes([speed]))  # ESC s n - Set speed
        
        # Set text justification to left (use full width)
        self._write(b'\x1B\x61\x00')  # ESC a 0 - Left justification
        
        time.sleep(0.1)

    def _write(self, data: bytes) -> None:
        """Write raw bytes to printer."""
        print(f"Writing {len(data)} bytes")
        win32file.WriteFile(self.handle, data)
        time.sleep(0.02)  # Even shorter delay for faster printing
        
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Try adding the word to the current line
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                # If current line has words, add it to lines
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # If the word itself is too long, force wrap it
                    lines.append(word)
                    current_line = []
        
        # Add the last line if it exists
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def _text_to_image(self, text: str) -> Image.Image:
        """Convert text to a monochrome image."""
        try:
            # Try to use Arial font with larger size
            font = ImageFont.truetype("arial.ttf", self.FONT_SIZE)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
            
        # Split text into paragraphs
        paragraphs = text.split('\n')
        
        # Process each paragraph and collect all lines
        all_lines = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Get the maximum possible font size that fits the width
                test_size = self.FONT_SIZE
                while test_size > 12:  # Don't go smaller than 12pt
                    try:
                        test_font = ImageFont.truetype("arial.ttf", test_size)
                    except:
                        break
                        
                    # Test with the full width
                    bbox = test_font.getbbox(paragraph)
                    if bbox[2] - bbox[0] <= self.MAX_WIDTH:
                        font = test_font
                        break
                    test_size -= 4
                
                # Wrap text to fit width
                wrapped_lines = self._wrap_text(paragraph, font, self.MAX_WIDTH)
                all_lines.extend(wrapped_lines)
            else:
                all_lines.append('')  # Keep empty lines for spacing
                
        # Calculate total height needed
        height = len(all_lines) * self.LINE_HEIGHT
        
        # Create new image with white background
        img = Image.new('1', (self.MAX_WIDTH, height), 1)  # 1 = white
        draw = ImageDraw.Draw(img)
        
        # Draw each line
        y = 0
        for line in all_lines:
            if line.strip():
                # Left align text (no centering)
                draw.text((0, y), line, font=font, fill=0)  # 0 = black
            y += self.LINE_HEIGHT
            
        return img
        
    def _print_image(self, img: Image.Image) -> None:
        """Print a PIL image."""
        # Convert to monochrome
        img = img.convert('1')  # Convert to 1-bit
        
        # Process image in blocks of 255 lines maximum
        for start_y in range(0, img.height, 255):
            # Calculate lines for this block
            lines_in_block = min(255, img.height - start_y)
            
            # Send block marker exactly as specified in protocol
            self._write(b'\x1D\x76\x30\x00')  # GS v 0 : print raster bit image
            self._write(bytes([self.BYTES_PER_LINE, 0]))  # 48 bytes per line (384 dots)
            self._write(bytes([lines_in_block, 0]))  # Number of lines in this block
            
            # Send image data
            for y in range(start_y, start_y + lines_in_block):
                line_data = bytearray()
                for x in range(0, self.MAX_WIDTH, 8):
                    byte = 0
                    for bit in range(8):
                        if x + bit < self.MAX_WIDTH:
                            if img.getpixel((x + bit, y)) == 0:  # Black pixel
                                byte |= (1 << (7 - bit))
                    line_data.append(byte)
                self._write(bytes(line_data))
            
            time.sleep(0.02)  # Shorter delay between blocks
        
        # Feed paper
        feed_lines = self.config.get('printer', {}).get('feed_lines', 5)
        self._write(bytes([0x1B, 0x64, feed_lines]))  # Feed n lines
        
    def print_text(self, text: Dict) -> bool:
        """Print text to the printer."""
        try:
            # Format the text
            output = f"""@{text['username']}

{text['title']}

"""
            if text['content']:
                output += f"{text['content']}\n\n"
            
            if text['hashtags']:
                output += f"{' '.join(text['hashtags'])}\n"
            
            # Convert text to image and print
            img = self._text_to_image(output)
            self._print_image(img)
            
            return True
        except Exception as e:
            print(f"Printer error: {str(e)}")
            return False
            
    def print_startup_message(self) -> bool:
        """Print the startup message."""
        try:
            message = """FASCISM SEES ITS SALVATION
IN GIVING THESE MASSES
NOT THEIR RIGHT, BUT INSTEAD
A CHANCE TO EXPRESS
THEMSELVES"""
            
            # Convert to image and print
            img = self._text_to_image(message)
            self._print_image(img)
            
            return True
        except Exception as e:
            print(f"Printer error during startup message: {str(e)}")
            return False
            
    def test_print(self) -> bool:
        """Print a test page to verify printer is working."""
        try:
            print("Sending test print...")
            
            test_message = """=== TEST PRINT ===

Testing basic text output...

1. Normal text
2. Multiple
3. Lines
4. Of
5. Text

Test complete!"""
            
            # Convert to image and print
            img = self._text_to_image(test_message)
            self._print_image(img)
            
            return True
        except Exception as e:
            print(f"Printer error during test: {str(e)}")
            return False
            
    def close(self):
        """Close the printer connection."""
        try:
            win32file.CloseHandle(self.handle)
        except:
            pass
