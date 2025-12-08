---
slug: getting-started-with-ros2
title: Getting Started with ROS 2 for Robotics
authors: [zakia-bashir]
tags: [tutorial, ros2, robotics, beginner]
---

ROS 2 (Robot Operating System 2) is the foundation of modern robotics development. In this post, we'll guide you through setting up ROS 2 and understanding its core concepts.

<!-- truncate -->

## What is ROS 2?

ROS 2 is a set of software libraries and tools that help you build robot applications. It provides:

- **Communication infrastructure** for distributed systems
- **Hardware abstraction** to work with different sensors and actuators
- **Package management** and build tools
- **Visualization and debugging** tools

## Installing ROS 2

### Ubuntu/Linux
```bash
# Set locale
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS 2 apt repository
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 Humble
sudo apt update
sudo apt install ros-humble-desktop
```

### Windows
1. Download the latest ROS 2 installer from the [official website](https://docs.ros.org/en/humble/Installation/Windows-Install-Binary.html)
2. Run the installer and follow the wizard
3. Open a Command Prompt and source the setup file:
```cmd
call C:\dev\ros2\humble\local_setup.bat
```

## Core Concepts

### 1. Nodes
Nodes are the smallest executable units in ROS 2. Each node performs a specific task:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class MyRobotNode(Node):
    def __init__(self):
        super().__init__('my_robot_node')
        self.get_logger().info('Robot node started!')

def main():
    rclpy.init()
    node = MyRobotNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 2. Topics
Topics are named buses for exchanging messages:

```python
# Publisher
self.publisher = self.create_publisher(String, 'robot_status', 10)

# Subscriber
self.subscription = self.create_subscription(
    String,
    'commands',
    self.command_callback,
    10
)
```

### 3. Services
Services provide request-response communication:

```python
# Service Server
self.srv = self.create_service(
    AddTwoInts,
    'add_two_ints',
    self.add_two_ints_callback
)
```

## Useful Commands

```bash
# List all running nodes
ros2 node list

# View node information
ros2 node info /my_robot_node

# List topics
ros2 topic list

# View topic data
ros2 topic echo /robot_status

# Check topic frequency
ros2 topic hz /robot_status

# Call a service
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 5, b: 3}"
```

## Next Steps

1. **Practice with turtlesim**: A simple simulator for learning ROS 2
2. **Explore URDF**: Learn to describe robot models
3. **Try Gazebo**: Advanced robot simulation
4. **Build a project**: Create your own robot application

## Resources

- [Official ROS 2 Documentation](https://docs.ros.org/en/humble/)
- [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [ROS 2 Answers](https://answers.ros.org/)

Happy robot building! 🤖

---

*Need help? Check out our [Chapter 2: Core Robotics Systems](/docs/chapter-2/lesson-1) in the textbook!*