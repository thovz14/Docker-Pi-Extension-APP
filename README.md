# 🐳 DockerPi Extension

A lightweight, user-friendly GUI for managing Docker containers on Raspberry Pi. Built with Python and Tkinter, featuring a modern design with the Fredoka font.

## ✨ Features
* **Modern Dashboard:** Monitor which containers are online or offline at a glance.
* **Container Creator:** Easily deploy new containers with custom names, images, and port mappings.
* **Real-time Status:** Reliable status tracking using Docker's native inspection tools.
* **User-Friendly UI:** Clean interface with rounded buttons and smooth navigation, optimized for desktop users.
* **Pi-Apps Integrated:** Seamless installation and uninstallation via the Pi-Apps store.

## 🚀 Installation
The easiest way to install is through **Pi-Apps**. 

If you want to install it manually for testing, run this command in your terminal:
`wget -qO- https://raw.githubusercontent.com/thovz14/Docker-Pi-Extension-APP/main/install | bash`

## 🛠️ Requirements
* **Hardware:** Raspberry Pi (ARM32 or ARM64).
* **OS:** Raspberry Pi OS or any Ubuntu/Debian-based distribution with a desktop environment.
* **Dependencies:** Docker (installed automatically via the install script).

## 📂 Project Structure
* `dockerpi.py`: The main Python application.
* `install`: Bash script for automated installation and menu shortcut creation.
* `uninstall`: Bash script for clean removal of the app and its dependencies.
* `icon-64.png`: Custom application icon.

## 👤 Author
Developed by **thovz14**.
Special thanks to the Pi-Apps community for their amazing platform.

## ⚖️ License
This project is open-source. Feel free to contribute!
