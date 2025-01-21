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
    
    # Printer physical specs
    DPI = 203  # Printer resolution is 203 dpi
    WIDTH_MM = 190  # Physical width is 210mm
    
    # Printer settings in dots
    MAX_WIDTH = int(WIDTH_MM * DPI / 25.4)  # 1678 dots (210mm at 203dpi)
    BYTES_PER_LINE = (MAX_WIDTH + 7) // 8  # 210 bytes (1678 dots rounded up to nearest byte)
    
    # Font sizes for different elements
    USERNAME_SIZE = 32   # Smaller size for username
    TITLE_SIZE = 48     # Larger size for title
    CONTENT_SIZE = 42   # Medium size for content
    HASHTAG_SIZE = 36   # Slightly smaller for hashtags
    
    MARGIN = 10      # Small margin to maximize usable width
    LINE_HEIGHT = 40  # Line height in dots
    
    def __init__(self, config: Dict):
        # Find printer port
        port = self.find_printer_port()
        if not port:
            raise Exception("M08F printer not found. Please check connection.")
            
        print(f"Connecting to printer on {port}...")
        
        # Open port directly
        port_path = r'\\.\{}'.format(port)
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
        
        # Set timeouts
        timeouts = (500, 500, 500, 500, 1000)
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
        
        # Set print density to highest for better emoji detail
        self._write(b'\x1B\x37\x07')  # ESC 7 n - Set print density (7 = highest)
        
        # Set line spacing
        self._write(b'\x1B\x33\x40')  # ESC 3 n - Set line spacing to 64 dots
        
        # Set print speed based on config (1=slow, 5=fast)
        speed = self.config.get('printer', {}).get('print_speed', 2)  # Slower default speed
        speed = max(1, min(5, speed))  # Ensure speed is between 1 and 5
        self._write(b'\x1B\x73' + bytes([speed]))  # ESC s n - Set speed
        
        time.sleep(0.1)

    def _write(self, data: bytes) -> None:
        """Write raw bytes to printer."""
        win32file.WriteFile(self.handle, data)
        time.sleep(0.02)  # Short delay for stability
        
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont) -> list:
        """Wrap text to fit printer width."""
        max_width = self.MAX_WIDTH - (2 * self.MARGIN)
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
                    wrapped = textwrap.wrap(word, width=20)  # Force wrap long words
                    lines.extend(wrapped[:-1])
                    current_line = [wrapped[-1]] if wrapped else []
        
        # Add the last line if it exists
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font with specified size."""
        try:
            # Try to use Segoe UI Emoji font for emoji support
            try:
                return ImageFont.truetype("seguiemj.ttf", size)  # Windows Emoji font
            except:
                try:
                    return ImageFont.truetype("segoe ui emoji", size)  # Alternative path
                except:
                    try:
                        return ImageFont.truetype("arial.ttf", size)  # Fallback to Arial
                    except:
                        return ImageFont.load_default()
        except:
            return ImageFont.load_default()

    def _simple_text_to_image(self, text: str, align: int = 0, size: int = None) -> Image.Image:
        """Convert simple text to a monochrome image."""
        # Use title size if no size specified
        font = self._get_font(size or self.TITLE_SIZE)
            
        # Split text into paragraphs
        paragraphs = text.split('\n')
        
        # Process each paragraph and collect all lines
        all_lines = []
        line_heights = []  # Store height for each line
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Wrap text to fit width
                wrapped_lines = self._wrap_text(paragraph, font)
                all_lines.extend(wrapped_lines)
                # Calculate line height based on actual text height
                for line in wrapped_lines:
                    bbox = font.getbbox(line)
                    height = bbox[3] - bbox[1]
                    line_heights.append(height + 10)  # Add 10 dots padding
            else:
                all_lines.append('')  # Keep empty lines for spacing
                line_heights.append(20)  # Height for empty lines
                
        # Calculate total height needed
        total_height = sum(line_heights)
        
        # Create new image with white background
        img = Image.new('1', (self.MAX_WIDTH, total_height), 1)  # 1 = white
        draw = ImageDraw.Draw(img)
        
        # Draw each line
        y = 0
        for line, height in zip(all_lines, line_heights):
            if line.strip():
                # Get the line's width
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                
                # Calculate x position based on alignment
                if align == 1:  # Center
                    x = (self.MAX_WIDTH - text_width) // 2
                elif align == 2:  # Right
                    x = self.MAX_WIDTH - text_width - self.MARGIN
                else:  # Left
                    x = self.MARGIN
                
                # Draw the text
                draw.text((x, y), line, font=font, fill=0)  # 0 = black
            y += height
                
        return img
        
    def _tweet_to_image(self, text: Dict) -> Image.Image:
        """Convert tweet to a monochrome image with different font sizes."""
        # Get fonts for different elements
        username_font = self._get_font(self.USERNAME_SIZE)
        title_font = self._get_font(self.TITLE_SIZE)
        content_font = self._get_font(self.CONTENT_SIZE)
        hashtag_font = self._get_font(self.HASHTAG_SIZE)
        
        # Create image with estimated height
        total_height = 300  # Initial estimate
        img = Image.new('1', (self.MAX_WIDTH, total_height), 1)  # 1 = white
        draw = ImageDraw.Draw(img)
        
        # Draw username
        username = f"@{text['username']}"
        bbox = username_font.getbbox(username)
        draw.text((self.MARGIN, 20), username, font=username_font, fill=0)
        current_y = 80  # Space after username
        
        # Draw title
        wrapped_title = self._wrap_text(text['title'], title_font)
        for line in wrapped_title:
            bbox = title_font.getbbox(line)
            draw.text((self.MARGIN, current_y), line, font=title_font, fill=0)
            current_y += bbox[3] - bbox[1] + 10
        current_y += 40  # Extra space after title
        
        # Draw content if present
        if text['content']:
            wrapped_content = self._wrap_text(text['content'], content_font)
            for line in wrapped_content:
                bbox = content_font.getbbox(line)
                draw.text((self.MARGIN, current_y), line, font=content_font, fill=0)
                current_y += bbox[3] - bbox[1] + 10
            current_y += 40  # Extra space after content
        
        # Draw hashtags if present
        if text['hashtags']:
            hashtag_text = ' '.join(text['hashtags'])
            wrapped_hashtags = self._wrap_text(hashtag_text, hashtag_font)
            for line in wrapped_hashtags:
                bbox = hashtag_font.getbbox(line)
                width = bbox[2] - bbox[0]
                # Right align hashtags
                x = self.MAX_WIDTH - width - self.MARGIN
                draw.text((x, current_y), line, font=hashtag_font, fill=0)
                current_y += bbox[3] - bbox[1] + 10
        
        # Crop image to actual height
        return img.crop((0, 0, self.MAX_WIDTH, current_y + 20))
        
    def _print_image(self, img: Image.Image) -> None:
        """Print a PIL image."""
        # Convert to monochrome
        img = img.convert('1')  # Convert to 1-bit
        
        # Process image in blocks of 255 lines maximum
        for start_y in range(0, img.height, 255):
            # Calculate lines for this block
            lines_in_block = min(255, img.height - start_y)
            
            # Send block marker
            self._write(b'\x1D\x76\x30\x00')  # GS v 0 : print raster bit image
            self._write(bytes([self.BYTES_PER_LINE, 0]))  # bytes per line
            self._write(bytes([lines_in_block, 0]))  # lines in this block
            
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
            
            time.sleep(0.02)  # Short delay between blocks
        
        # Feed paper
        feed_lines = self.config.get('printer', {}).get('feed_lines', 3)
        self._write(bytes([0x1B, 0x64, feed_lines]))  # Feed n lines
        
    def print_text(self, text: Dict) -> bool:
        """Print text to the printer."""
        try:
            print("\n=== Printing Tweet ===")
            print(f"From: @{text['username']}")
            print(f"Title: {text['title']}")
            if text['content']:
                print(f"Content: {text['content']}")
            if text['hashtags']:
                print(f"Hashtags: {' '.join(text['hashtags'])}")
            print("===================\n")
            
            # Convert tweet to image and print
            img = self._tweet_to_image(text)
            self._print_image(img)
            
            return True
        except Exception as e:
            print(f"Printer error: {str(e)}")
            return False
            
    def print_startup_message(self) -> bool:
        """Print the startup message."""
        try:
            message = """Fascism sees its salvation in giving these masses not their right, but instead a chance to express themselves."""
            
            # Print centered with larger font
            img = self._simple_text_to_image(message, align=1, size=48)  # Center align with large font
            self._print_image(img)
            
            return True
        except Exception as e:
            print(f"Printer error during startup message: {str(e)}")
            return False
            
    def close(self):
        """Close the printer connection."""
        try:
            win32file.CloseHandle(self.handle)
        except:
            pass
