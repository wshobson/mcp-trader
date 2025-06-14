# Installation Guide

## Prerequisites: TA-Lib C Library

The Python `ta-lib` package requires the TA-Lib C library to be installed on your system before you can install the Python wrapper.

### macOS

Using Homebrew:
```bash
brew install ta-lib
```

Using MacPorts:
```bash
sudo port install ta-lib
```

### Linux (Ubuntu/Debian)

```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

### Linux (CentOS/RHEL/Fedora)

```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

### Windows

1. Download ta-lib-0.4.0-msvc.zip from http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip
2. Unzip to `C:\ta-lib`
3. For 64-bit Python, you may need to build from source using Visual Studio

### Alternative: Using Conda

If you're using Anaconda or Miniconda:
```bash
conda install -c conda-forge ta-lib
```

## Installing MCP Trader

After installing the TA-Lib C library:

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-trader.git
cd mcp-trader

# Install Python dependencies
pip install -r requirements.txt
```

## Troubleshooting

### macOS ARM64 (M1/M2)

If you encounter issues on Apple Silicon:
```bash
export TA_INCLUDE_PATH="$(brew --prefix ta-lib)/include"
export TA_LIBRARY_PATH="$(brew --prefix ta-lib)/lib"
pip install ta-lib
```

### Linux Library Path Issues

If you get library not found errors:
```bash
echo "/usr/local/lib" | sudo tee -a /etc/ld.so.conf
sudo ldconfig
```

### Windows Compilation Issues

For Windows users experiencing compilation errors:
1. Install Visual Studio Build Tools
2. Use pre-compiled wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

## Verification

Test your installation:
```python
import talib
print(talib.get_functions())
```

If this runs without errors, TA-Lib is properly installed.