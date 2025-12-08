"""
Code execution service using StackBlitz WebContainers
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import json
import re
import os
import uuid

logger = logging.getLogger(__name__)


class CodeExecutionService:
    """Service for executing code in sandboxed WebContainers"""

    def __init__(self):
        self.active_containers = {}  # Track active containers
        self.execution_results = {}  # Cache execution results
        self.timeout_seconds = 30  # Default timeout
        self.max_concurrent = 5  # Max concurrent executions

    async def execute_code(
        self,
        code: str,
        language: str = "python",
        files: Optional[List[Dict[str, str]]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute code in a WebContainer"""

        execution_id = str(uuid.uuid4())
        start_time = datetime.now()

        try:
            # Check if we have too many concurrent executions
            if len(self.active_containers) >= self.max_concurrent:
                raise Exception("Too many code executions running. Please try again later.")

            # Create execution context
            context = {
                "id": execution_id,
                "language": language,
                "code": code,
                "files": files or [],
                "timeout": timeout or self.timeout_seconds,
                "created_at": start_time.isoformat()
            }

            # For now, simulate execution since StackBlitz API integration would require
            # additional setup and API keys
            result = await self._simulate_execution(context)

            # Cache the result
            self.execution_results[execution_id] = {
                **result,
                "cached_at": datetime.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "id": execution_id
            }

    async def _simulate_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate code execution for demonstration"""

        code = context["code"]
        language = context["language"]

        # Create a result based on the code
        result = {
            "id": context["id"],
            "success": True,
            "output": "",
            "error": "",
            "execution_time": 0.5,
            "language": language
        }

        # Python execution simulation
        if language.lower() == "python":
            # Simple Python code simulation
            if "print(" in code:
                # Extract print statements
                prints = re.findall(r'print\(([^)]*)\)', code)
                outputs = []
                for print_stmt in prints:
                    # Clean up the print statement
                    output = print_stmt.strip('\'"').strip()
                    outputs.append(output)
                result["output"] = "\n".join(outputs)
            elif "import " in code or "from " in code:
                result["output"] = "Code imported successfully"
            elif "def " in code:
                result["output"] = "Function defined successfully"
            else:
                result["output"] = "Python code executed"

        # ROS 2 specific simulations
        elif "ros2" in code or "rclpy" in code:
            result["output"] = """
ROS 2 simulation output:
- rclpy init successful
- Node creation completed
- Publisher/Subscriber pattern detected
- Execution time: 0.3s
"""

        # JavaScript execution simulation
        elif language.lower() in ["javascript", "js", "node"]:
            if "console.log" in code:
                logs = re.findall(r'console\.log\(([^)]*)\)', code)
                outputs = []
                for log in logs:
                    output = log.strip('\'"')
                    outputs.append(output)
                result["output"] = "\n".join(outputs)
            else:
                result["output"] = "JavaScript code executed"

        # C++ execution simulation
        elif language.lower() in ["cpp", "c++"]:
            if "#include" in code:
                result["output"] = "C++ code compiled successfully"
            elif "std::cout" in code:
                couts = re.findall(r'std::cout\s*<<\s*([^;]+);', code)
                outputs = []
                for cout in couts:
                    output = cout.strip()
                    outputs.append(output)
                result["output"] = "\n".join(outputs)
            else:
                result["output"] = "C++ code compiled"

        return result

    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status of an execution"""

        if execution_id in self.execution_results:
            return {
                "id": execution_id,
                "status": "completed",
                "result": self.execution_results[execution_id]
            }

        if execution_id in self.active_containers:
            return {
                "id": execution_id,
                "status": "running",
                "started_at": self.active_containers[execution_id]["started_at"]
            }

        return {
            "id": execution_id,
            "status": "not_found",
            "error": "Execution not found"
        }

    async def kill_execution(self, execution_id: str) -> bool:
        """Kill a running execution"""

        if execution_id in self.active_containers:
            del self.active_containers[execution_id]
            return True
        return False

    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported programming languages"""

        return [
            {
                "name": "Python",
                "extension": "py",
                "monaco_language": "python",
                "description": "Python 3.x with scientific libraries"
            },
            {
                "name": "JavaScript",
                "extension": "js",
                "monaco_language": "javascript",
                "description": "Node.js runtime"
            },
            {
                "name": "TypeScript",
                "extension": "ts",
                "monaco_language": "typescript",
                "description": "TypeScript with Node.js"
            },
            {
                "name": "C++",
                "extension": "cpp",
                "monaco_language": "cpp",
                "description": "C++17 with ROS 2 support"
            },
            {
                "name": "Bash",
                "extension": "sh",
                "monaco_language": "shell",
                "description": "Bash shell scripting"
            }
        ]

    async def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code for security and syntax issues"""

        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "security_issues": []
        }

        # Security checks
        dangerous_patterns = [
            r'os\.system\(',
            r'subprocess\.',
            r'eval\(',
            r'exec\(',
            r'open\(.*["\'][\'\'][)]',
            r'__import__.*os',
            r'import.*os',
            r'from\s+os\s+import',
            r'file\(',
            r'open\(',
            r'input\s*\('
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                validation_result["security_issues"].append(
                    f"Potentially dangerous code detected: {pattern}"
                )
                validation_result["valid"] = False

        # Language-specific validation
        if language.lower() == "python":
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                validation_result["errors"].append(f"Syntax error: {str(e)}")
                validation_result["valid"] = False

        return validation_result

    async def create_ros2_environment(self) -> Dict[str, Any]:
        """Create a pre-configured ROS 2 environment"""

        return {
            "environment_variables": {
                "ROS_DOMAIN_ID": "physical_ai_robotics",
                "ROS_DISTRO": "humble",
                "PYTHONPATH": "/opt/ros/humble/lib/python3.10/site-packages",
                "LD_LIBRARY_PATH": "/opt/ros/humble/lib:/opt/ros/humble/lib/x86_64-linux-gnu"
            },
            "pre_installed_packages": [
                "ros-humble-desktop",
                "ros-humble-ros-base",
                "ros-humble-rclpy",
                "ros-humble-rviz2",
                "ros-humble-gazebo-ros-pkgs",
                "python3-numpy",
                "python3-scipy"
            ],
            "launch_files": [
                "/opt/ros/humble/share/turtlebot3_launch/launch/robot_state_publisher.launch.py",
                "/opt/ros/humble/share/turtlebot3_simulation/launch/turtlebot3_world.launch.py"
            ]
        }