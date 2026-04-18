# STM32 Bluetooth-Controlled Autonomous Rover 🚗

## 📌 Project Overview
A full-stack embedded system project featuring a custom-built, dual-mode smart vehicle. The system integrates a custom Altium PCB shield, an STM32F401RE microcontroller, and a Python-based desktop interface. It supports real-time switching between manual Bluetooth control and an autonomous line-following mode driven by a PID algorithm with encoder feedback.

## 🚀 Key Features
* **Dual-Mode Navigation:** Seamless switching between manual control and autonomous line-following via Bluetooth.
* **Precision Control:** Implemented a PID control algorithm utilizing encoder feedback to ensure smooth and continuous movement on complex track trajectories.
* **Custom Hardware:** Designed a dedicated PCB shield to efficiently integrate the MCU with motor drivers, sensors, and communication modules.
* **Desktop Interface:** Developed a Python-based GUI (`visualize.py`) for real-time bidirectional communication, telemetry visualization, and mode switching.

## 🛠️ Hardware Components
* **MCU:** STM32F401RE Nucleo-64
* **Motor Driver:** TB6612FNG
* **Sensors:** IR Sensor Array (Line detection), N20 DC Motor Encoders
* **Communication:** HC-05 Bluetooth Module

## 📂 Repository Structure

```text
.
├── Firmware/                 # STM32CubeIDE project directory
│   ├── Core/                 # Main application code (Src/Inc) and Startup scripts
│   ├── STM32F401RETX_FLASH.ld# Flash Linker script
│   ├── STM32F401RETX_RAM.ld  # RAM Linker script
│   └── Src_XePrj.ioc         # STM32CubeMX configuration file
├── PCB/                      # Altium Designer hardware design files
│   ├── PCB1.PcbDoc           # PCB Layout
│   ├── PCB_Project.PrjPcb    # Altium Project file
│   └── Sheet1.SchDoc         # Schematic Document
└── visualize.py              # Python desktop interface for Bluetooth control
