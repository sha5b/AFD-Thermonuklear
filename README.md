# AFD-Thermonuklear

A thermal printer system for printing tweets with advanced formatting and emoji support. This project uses the Phomemo M08F thermal printer (a portable 80mm thermal printer) to create nicely formatted printouts of tweets with different font sizes and layouts.

## Printer Information

The Phomemo M08F is a high-quality thermal printer with the following specifications:
- Print Width: 80mm (effective print width: 72mm/576 dots)
- Resolution: 203 DPI
- Print Speed: Adjustable (1-5 levels)
- Connection: USB
- VID/PID: 0483/5740 (STMicroelectronics)
- Compatible OS: Windows/Mac/Linux

## Features

- **Advanced Text Formatting**
  - Username: Compact 32pt font for clean identification
  - Title: Large 48pt font for emphasis
  - Content: Medium 42pt font for readability
  - Hashtags: Right-aligned 36pt font for style
- **Emoji Support** using Segoe UI Emoji font
- **Smart Text Wrapping** to fit printer width
- **High Print Quality** with maximum density setting
- **Configurable Settings** via YAML config file

## Requirements

- Windows 11 (for printer drivers)
- Python 3.x
- M08F Thermal Printer
- Required Python packages (install via `pip install -r requirements.txt`):
  - PySerial
  - PyWin32
  - Pillow
  - PyYAML
  - keyboard

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AFD-Thermonuklear.git
   cd AFD-Thermonuklear
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the printer settings in `config.yaml`:
   ```yaml
   printer:
     print_speed: 2  # 1 (slow) to 5 (fast)
     feed_lines: 3   # Paper feed after printing
   ```

4. Prepare your tweets in `tweets.csv` with the following format:
   ```csv
   username,title,content,tags,date,printed
   user123,Tweet Title,Tweet content here,#tag1 #tag2,2024-01-01,false
   ```

## Usage

Run the main script:
```bash
python src/main.py
```

The program will:
1. Initialize the printer with optimal settings
2. Print a startup message
3. Continuously select and print random unprinted tweets
4. Mark printed tweets in the CSV file

Press ESC to exit the program.

## File Structure

- `src/`
  - `main.py` - Main program entry point
  - `printer.py` - M08F printer interface and formatting
  - `tweet_reader.py` - CSV tweet file handling
  - `buffer.py` - Print buffer management
  - `twitter.py` - Twitter API integration (if used)
- `config.yaml` - Configuration settings
- `tweets.csv` - Tweet database
- `requirements.txt` - Python dependencies

## Print Format

Each tweet is printed with the following layout:

```
@username                              (32pt)

Title in large text                    (48pt)


Content with proper wrapping           (42pt)
and support for emojis 😊

                      #hashtags #here  (36pt, right-aligned)
```

## Configuration Options

### Printer Settings (config.yaml)

```yaml
printer:
  # Print speed (1-5)
  # 1: Slowest, highest quality
  # 5: Fastest, may reduce quality
  print_speed: 2

  # Number of lines to feed after printing
  feed_lines: 3
```

## Error Handling

The system includes robust error handling for common issues:
- Printer connection failures
- Invalid tweet formats
- File access errors
- Print buffer overflows

Error messages are clearly displayed with potential solutions.

## Development

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Include docstrings for functions and classes
- Maintain error handling patterns

## Troubleshooting

### Common Issues

1. **Printer Not Found**
   - Check USB connection
   - Verify printer power
   - Confirm correct VID/PID in printer.py

2. **Garbled Text**
   - Ensure UTF-8 encoding in CSV file
   - Verify font availability
   - Check print density settings

3. **Print Quality**
   - Adjust print_speed in config.yaml
   - Ensure high print density setting
   - Clean printer head if necessary

### Debug Mode

Add `debug: true` to config.yaml for additional logging:
```yaml
printer:
  debug: true
  print_speed: 2
  feed_lines: 3
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thermal printer protocol documentation
- PIL library for image processing
- PyWin32 for Windows integration
