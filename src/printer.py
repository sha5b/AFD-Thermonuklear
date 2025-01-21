import serial
import serial.tools.list_ports
from typing import Dict, Optional
import time

class M08FPrinter:
    # M08F printer USB identifiers
    VENDOR_ID = "0483"  # STMicroelectronics
    PRODUCT_ID = "5740"  # M08F Printer

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

    def __init__(self, config: Dict):
        self.config = config
        port = self.find_printer_port()
        if not port:
            raise serial.SerialException("M08F printer not found. Please check connection.")
            
        self.serial = serial.Serial(
            port=port,
            baudrate=config['printer']['baudrate'],
            timeout=1
        )
        
    def print_text(self, text: str) -> bool:
        """Print text to the M08F printer."""
        try:
            # Format text for printer
            formatted_text = self._format_text(text)
            
            # Send to printer
            self.serial.write(formatted_text.encode())
            
            # Wait based on print speed
            delay = 60.0 / self.config['printer']['print_speed']
            time.sleep(delay)
            
            return True
        except serial.SerialException as e:
            print(f"Printer error: {str(e)}")
            return False
            
    def _format_text(self, text: str) -> str:
        """Format text for M08F printer."""
        # Add printer-specific formatting
        formatted = text.replace('\n', '\r\n')
        formatted += '\r\n\r\n'  # Add extra newlines between tweets
        return formatted
        
    def close(self):
        """Close the serial connection."""
        if self.serial.is_open:
            self.serial.close()
