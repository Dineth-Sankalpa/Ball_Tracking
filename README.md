# Autonomous Object Tracking Base: ROS 2 Active Tracking System

![ROS 2](https://img.shields.io/badge/ROS_2-Humble-22314E?logo=ros)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)
![C++](https://img.shields.io/badge/C++-17-00599C?logo=c%2B%2B)
![Hardware](https://img.shields.io/badge/Hardware-Raspberry_Pi_4_%7C_Kobuki_Qbot-red)

A robust, depth-aware visual tracking system built on ROS 2 Humble. This project utilizes a Microsoft Kinect v1 (RGB-D) and a Kobuki Qbot mobile base to actively identify, track, and maintain a fixed physical distance from a target object. 

This tracking package serves as the foundational mobility and spatial-awareness layer for a larger **Autonomous 3D Object Scanning and Point Cloud Visualization** architecture.

## 🚀 System Architecture

The system is fully decentralized across three main components, bridged by ROS 2 topics:

1. **`kinect_ros2` (C++):** A low-level hardware bridge utilizing `libfreenect` to publish raw RGB and Depth matrices to the ROS 2 network.
2. **`vision_node` (Python/OpenCV):** Subscribes to the RGB-D streams. Applies HSV color space filtering, extracts the target's centroid using image moments, and samples an aligned 5x5 pixel depth patch to calculate physical distance in millimeters. Features Exponential Moving Average (EMA) smoothing for signal stability.
3. **`control_node` (Python):** A state-machine-driven physics controller. Translates standard ROS 2 error variables into the explicit `[Speed, Radius]` serial byte payload required by the Kobuki differential drive base. 

### Control State Machine
* **State 1 (Active Tracking):** Utilizes proportional control with a 40mm deadband to maintain a strict 500mm distance from the target.
	* **Velocity Ramping:** Applies acceleration smoothing to prevent hardware jerking and motor stalling.
	* **Sensor Memory & Blindspot Evasion:** Remembers the last valid distance so if the target disappears inside the Kinect v1 minimum-range blindspot, the robot can reverse and bring it back into view.
* **State 2 (Searching):** If the visual lock is broken, the robot retains the last known error vector and executes a localized sweep (up to 2 rotations) to reacquire the target.
* **State 3 (Idle):** Safe resting state when no target is present.

## 🛠️ Hardware Requirements
* **Compute:** Raspberry Pi 4 Model B (Running Ubuntu 22.04 Server)
* **Chassis:** Kobuki Qbot Differential Drive Base
* **Sensor:** Microsoft Kinect v1 (Xbox 360) with external power supply

## ⚙️ Installation & Dependencies

### 1. ROS 2 & C++ Hardware Dependencies
Ensure you have ROS 2 Humble installed. Then, install the required image pipeline modules, Python runtime helpers, and the Kinect development libraries:
```bash
sudo apt-get update
sudo apt-get install python-is-python3 python3-opencv ros-humble-cv-bridge ros-humble-image-transport ros-humble-depth-image-proc
sudo apt-get install libfreenect-dev libfreenect-bin
```

### 2. Python Dependencies
The Python nodes require PySerial for hardware communication and a specific version of NumPy to avoid compatibility crashes with `cv_bridge`:

```bash
pip install pyserial "numpy<2"
```

### 3. Hardware Permissions
Standard Linux users do not have access to raw USB and video streams. You must add your user to these groups to allow the drivers to run without `sudo`:

```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G video $USER
sudo usermod -a -G plugdev $USER
```

*(Note: You must log out and log back in, or restart the Raspberry Pi, for these permissions to take effect).*

### 4. Build the Workspace
Clone this repository
```bash
git clone https://github.com/fadlio/kinect_ros2.git
``` 
into the `src` folder of your `colcon` workspace and build:

```bash
cd ~/ros2_ws
colcon build --packages-select kinect_ros2 ball_tracking_pkg
source install/setup.bash
```

## 🎮 Usage
The system is optimized for **headless operation via SSH**, meaning no graphical displays are required on the Raspberry Pi during deployment, saving critical CPU cycles.

**Terminal 1: Launch the Camera Bridge**

```bash
source ~/ros2_ws/install/setup.bash
ros2 run kinect_ros2 kinect_ros2_node
```

**Terminal 2: Launch the Tracking Pipeline**
Ensure the Kobuki base is powered on, then launch the vision and control nodes simultaneously:

```bash
source ~/ros2_ws/install/setup.bash
ros2 launch ball_tracking_pkg tracker_launch.py
```

________