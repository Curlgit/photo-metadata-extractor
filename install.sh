
#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=================================="
echo " Photo Metadata Inspector Setup"
echo "=================================="

echo "[1/4] Updating Termux packages..."
pkg update

echo "[2/4] Installing Python, Git and build tools..."
pkg install python git clang make ndk-sysroot libjpeg-turbo -y

echo "[3/4] Installing Python dependencies..."
python -m pip install --no-cache-dir requests

echo "[4/4] Installing Pillow..."
if ! python -c "from PIL import Image" >/dev/null 2>&1; then
    python -m pip install --no-cache-dir Pillow
fi

echo ""
echo "[+] Checking Pillow..."
if python -c "from PIL import Image; print('Pillow OK')"; then
    echo "[+] Setup completed successfully!"
else
    echo "[!] Pillow installation failed."
    echo "[!] Try: pkg install python-pillow"
    exit 1
fi

echo ""
echo "Run your tool with:"
echo "python 'photo incementa stacker.py'"
