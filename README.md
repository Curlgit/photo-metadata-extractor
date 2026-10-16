📸 photo-metadata-extractor

A lightweight image metadata inspection tool for Termux and Android.

Photo Metadata Inspector is a Python-based utility designed to inspect image properties and available EXIF metadata through a simple terminal interface. It is intended for educational use, metadata exploration, and personal image analysis.

---

✨ Features

- 🖼️ Image Information — view image format, file size, and resolution.
- 📷 Camera Details — inspect camera manufacturer and model when available.
- 📅 Date & Software Metadata — view recorded date and software information.
- 📍 GPS Metadata Check — check whether GPS metadata appears to be present.
- 📄 JSON Report — save the latest inspection report locally.
- 📱 Termux Support — designed for Android terminal environments.
- ⚡ Lightweight Interface — simple menu-based workflow.

📋 Requirements

Before installing, make sure you have:

- Android device with Termux
- Python 3
- Git
- Pillow (Python Imaging Library)
- Internet access for package installation

**🚀 Installation Guide**

Step 1 — Update Termux

**Update your package list before installing dependencies**
```bash
pkg update && pkg upgrade -y
```
**Step 2 — Install Git**
```bash
pkg install git -y
```
**Step 3 — Clone the Repository**
```bash
git clone https://github.com/Curlgit/photo-metadata-extractor.git
```
**Step 4 — Enter the Project Directory**
```bash
cd photo-metadata-extractor
```
**Step 5 — Run the Installer**

**6 Make the installation script executable**
```bash
chmod +x install.sh
```
**7 Start the installer using Bash**
```bash
bash install.sh
```
Step 8
**Run tool**
```bash
python'photo incementa stacker.py'
```
The installer attempts to set up Python, Git, the required build dependencies, and Pillow. It also installs "requests", as included in the installation script.

🧰 Pillow Build Error Fix

If Pillow installation fails with a long compilation error, missing JPEG headers, or a build dependency error, try the following commands.

Step 1 — Install Build Dependencies
```bash
pkg install python ndk-sysroot clang make libjpeg-turbo -y
```
Step 2 — Install Pillow Without Cache
```bash
python -m pip install --no-cache-dir Pillow
```
Step 3 — Verify Pillow
```bash
python -c "from PIL import Image; print('Pillow OK')"
```
Expected output:

Pillow OK

If the installation still fails, try Termux's packaged version:
```bash
pkg install python-pillow
```
«💡 The commands above are troubleshooting steps, not a guarantee that every Pillow build error will be fixed. If an error persists, check the exact error message and your Termux environment.»

🔐 Enable Android Storage Access

To allow Termux to access shared Android storage, run:
```bash
termux-setup-storage
```
Accept the Android permission prompt when it appears.

▶️ Start the Program

The main Python filename for this project is:

"photo incementa stacker.py"

Run it with:
```bash
python "photo incementa stacker.py"
```
If you rename the Python file, update the command to match its exact filename.

🖼️ Example Image Paths

When prompted for an image path, enter the full path to an existing image on your device.

Example 1 — Camera Folder
```bash
/storage/emulated/0/DCIM/Camera/IMG_2026-10-16-10-34-38-732.jpg
```
Example 2 — Pictures Folder
```bash
/storage/emulated/0/Pictures/MyPhoto.jpg
```
Example 3 — Downloaded Image
```bash
/storage/emulated/0/Download/sample-image.jpg
```
These are examples only. Replace the filenames with the actual images stored on your phone.

🛠️ Troubleshooting

❌ "No module named PIL"

Install Pillow:
```bash
pkg install python-pillow
```
If you need to use pip instead:
```bash
python -m pip install --no-cache-dir Pillow
```
❌ "No such file or directory"

Check your current directory:
```bash
pwd

List the files:

ls -la
```
Move into the correct project directory and confirm that the Python filename matches the run command.

❌ "Permission denied"

Run:
```bash
chmod +x install.sh
bash install.sh
```
❌ Image path not found

Enable storage access:
```bash
termux-setup-storage
```
Then check that the image exists and the path is correct.

❌ "git: command not found"

Install Git:
```bash
pkg install git -y
```
❌ "pip" installation error

Update pip:
```bash
python -m pip install --upgrade pip
```
If Termux reports an environment restriction or a package-build issue, prefer the corresponding Termux package when available.

📂 Report Location

The latest JSON report is saved at:

~/.photo_metadata_inspector/last_report.json

The report contains the metadata collected by the program. Fields may be unavailable if the image does not contain the relevant metadata.

🔏 Privacy Notes

- Inspect only images you are authorized to access.
- Metadata can contain personal information, including dates and location details.
- Review reports before sharing them publicly.
- Removing metadata from a report does not modify the original image.

**⚠️ Disclaimer
This tool is developed for educational and entertainment purposes only. Use it only with images you are authorized to inspect. The developer is not responsible for illegal activity, unauthorized use, or misuse of this tool**

👨‍💻 Project Information

- Project: Photo Metadata Inspector
- Language: Python
- Platform: Termux / Android
- Metadata Library: Pillow
- Report Format: JSON


---

Photo Metadata Inspector — Simple. Lightweight. Informative.
