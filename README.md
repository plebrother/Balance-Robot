# WhatdoUmean - Electronics_Design_Project_2_Balance_Robot

A self-balancing two-wheeled robot built using an ESP32 and MPU6050, with communication handled via a Raspberry Pi. Developed as part of Imperial College London’s EE2 Electronics Design Project.

---

## Overview

This robot maintains upright balance using real-time feedback from an IMU (MPU6050) and PID control running on an ESP32. It is remotely controllable and expandable for additional functionality.

---

## Key Features
- Real-time balancing using PID control
- Stepper motor drive system
- MPU6050 gyroscope and accelerometer integration
- Communication interface via Raspberry Pi
- Remote or manual control options
- Expandable design for sensor and vision-based features

---

## Potential High-Level Features
These are optional features to demonstrate scalability and technical depth:
- Object transport while balancing
- Waypoint navigation using magnetic or optical sensors
- Web-based GUI or joystick control through the Raspberry Pi
- Voice command interface via the Raspberry Pi
- Obstacle avoidance using ultrasonic or infrared sensors
- Follow-mode or assistance function (e.g., person tracking)
- Real-time visualisation or camera feed from onboard Pi

---

## Hardware Used
- ESP32 microcontroller
- MPU6050 IMU sensor
- Stepper motors with motor drivers
- Raspberry Pi (for high-level control and communication)
- Power distribution circuitry and robot chassis

---

## Software Stack
- Arduino/C++ for embedded control
- Python 3 for Raspberry Pi scripts
- Serial/Bluetooth/Wi-Fi (to be confirmed) for communication
- GitHub for collaboration and version control

