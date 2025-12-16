"""
Physical AI & Humanoid Robotics Textbook - Standalone RAG Server V5 Enhanced
Better context retrieval and more intelligent responses
Handles both JSON and form-encoded data with RAG chat support
"""

from fastapi import FastAPI, HTTPException, status, Depends, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
import uvicorn
import os
import logging
import json
from urllib.parse import parse_qs
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
import re
from difflib import SequenceMatcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple configuration
SECRET_KEY = os.getenv("SECRET_KEY", "test_secret_key_123")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory user store for demo (replace with database in production)
users = {}
user_sessions = {}

# Enhanced knowledge base with better structure
KNOWLEDGE_BASE = [
    {
        "content": """Physical AI refers to artificial intelligence systems that interact with the physical world through robots or other physical embodiments. It combines AI/ML for decision-making, robotics for physical interaction, sensors for perception, and actuators for movement.

Definition:
Physical AI is embodied artificial intelligence that operates in the physical world, as opposed to purely digital AI systems. These systems can sense their environment, make decisions, and take physical actions.

Key Components:
- AI/ML Algorithms: Neural networks, reinforcement learning, computer vision for perception and decision-making
- Robotics Hardware: Joints, motors, end-effectors, mobile platforms for physical interaction
- Sensor Systems: Cameras, LiDAR, IMUs, tactile sensors for perceiving the environment
- Actuation: Motors, hydraulics, pneumatics, artificial muscles for movement

Real-world Examples:
- Humanoid robots like Boston Dynamics' Atlas performing complex parkour
- Self-driving cars (Tesla Autopilot, Waymo) navigating city streets
- Industrial robots in manufacturing plants assembling products
- Delivery drones with autonomous navigation in urban areas
- Surgical robots like the da Vinci system performing precise operations
- Smart home robots that clean and assist with daily tasks""",
        "source": "Chapter 1: Introduction to Physical AI",
        "keywords": ["physical ai", "embodied ai", "robotics", "sensors", "actuators", "artificial intelligence", "embodiment"],
        "topic": "physical_ai"
    },
    {
        "content": """ROS2 (Robot Operating System 2) is a flexible framework for writing robot software. It provides the tools, libraries, and conventions to simplify complex robot applications.

What is ROS2?
ROS2 is not an operating system but a middleware framework that provides communication between different processes (nodes) in a robotic system. It's the successor to ROS1 with improved real-time performance, security, and support for multiple platforms.

Core Concepts:
- Nodes: Independent processes that perform computation (e.g., sensor processing, motor control)
- Topics: Named buses for exchanging messages between nodes using publish/subscribe pattern
- Services: Request/response communication pattern for synchronous operations
- Actions: Asynchronous goal-oriented tasks with feedback
- Parameters: Configuration values for nodes that can be dynamically updated
- DDS (Data Distribution Service): Underlying communication middleware for reliable data exchange

Complete Python Publisher Example:
```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class PhysicalAIPublisher(Node):
    def __init__(self):
        super().__init__('physical_ai_talker')
        # Create publisher on 'ai_topics' topic
        self.publisher_ = self.create_publisher(String, 'ai_topics', 10)
        timer_period = 2.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Physical AI Lesson {self.count}: Understanding Embodiment'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    physical_ai_node = PhysicalAIPublisher()
    rclpy.spin(physical_ai_node)

    # Cleanup
    physical_ai_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Benefits for Physical AI:
- Distributed system architecture allowing modular development
- Language independence (Python, C++, Java, Rust support)
- Real-time capabilities essential for robot control
- Extensive tooling including RViz for visualization
- Large ecosystem of packages for common robotics tasks""",
        "source": "Chapter 2: ROS2 Fundamentals",
        "keywords": ["ros2", "robot operating system", "nodes", "topics", "services", "actions", "dds", "publisher", "subscriber", "middleware"],
        "topic": "ros2"
    },
    {
        "content": """Gazebo is a powerful 3D simulation environment for robotics development. It provides realistic physics simulation, sensor modeling, and robot visualization.

Introduction to Gazebo:
Gazebo enables developers to test robot algorithms in simulation before deploying to physical hardware, saving time and resources while ensuring safety.

Key Features:
- Physics Engine: ODE (Open Dynamics Engine) for accurate dynamics simulation
- 3D Rendering: High-quality OpenGL-based visualization
- Sensor Simulation: Realistic models for cameras, LiDAR, IMUs, contact sensors
- Robot Models: Support for URDF (Unified Robot Description Format) and SDF formats
- Plugin System: Custom sensors, actuators, and world elements
- ROS Integration: Direct connection to ROS2 nodes for hardware-in-the-loop testing

Complete Robot Model Example (URDF):
```xml
<?xml version="1.0"?>
<robot name="physical_ai_robot">
  <!-- Base Link -->
  <link name="base_link">
    <inertial>
      <mass value="10"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>

    <visual>
      <geometry>
        <cylinder radius="0.3" length="0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0.5 1 1"/>
      </material>
    </visual>

    <collision>
      <geometry>
        <cylinder radius="0.3" length="0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Wheels -->
  <link name="wheel_left">
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
  </link>

  <joint name="wheel_left_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left"/>
    <axis xyz="0 0 1"/>
  </joint>
</robot>
```

Applications in Physical AI:
- Algorithm development before hardware deployment
- Testing in safe, repeatable conditions
- Educational demonstrations and visualization
- Competition robotics (RoboCup, DARPA challenges)
- Multi-robot simulation for swarm intelligence""",
        "source": "Chapter 3: Simulation with Gazebo",
        "keywords": ["gazebo", "simulation", "physics", "urdf", "sdf", "plugins", "ros", "ode", "3d", "visualization"],
        "topic": "gazebo"
    },
    {
        "content": """Humanoid robotics focuses on creating robots with human-like body structures and capabilities. These robots face unique challenges in locomotion, manipulation, and human-robot interaction.

What are Humanoid Robots?
Humanoid robots are designed to resemble the human body structure, typically with a torso, two arms, two legs, and a head. This design allows them to operate in environments built for humans and use tools designed for people.

Major Locomotion Challenges:
- Bipedal Walking: Maintaining balance during dynamic movement using zero moment point (ZMP)
- Gait Planning: Creating smooth, energy-efficient walking patterns
- Terrain Adaptation: Walking on stairs, slopes, uneven surfaces, and soft ground
- Fall Recovery: Detecting falls and executing recovery maneuvers
- Energy Efficiency: Minimizing power consumption during movement

Key Technical Components:
- Leg Kinematics: 6 degrees of freedom (DOF) legs with hip, knee, ankle joints
- Torso Control: Upper body stabilization and dynamic balance
- Arm Manipulation: Dual arms with 5-7 DOF each for object manipulation
- Sensor Fusion: Combining IMU, cameras, force/torque sensors for state estimation
- Actuation: Electric motors, hydraulic systems, or artificial muscles

Pioneering Humanoid Robots:
- Atlas (Boston Dynamics): Advanced parkour, backflips, and rough terrain mobility
- ASIMO (Honda): Early pioneer in humanoid robotics, could run and interact with humans
- Pepper (SoftBank): Social humanoid designed for human interaction and customer service
- HRP Series (AIST): Research platforms for locomotion and human-robot interaction
- Optimus (Tesla): Under development for industrial and household tasks
- Valkyrie (NASA): Designed for disaster response and space missions

Control Methods:
- Zero Moment Point (ZMP): Mathematical criterion for bipedal stability
- Inverse Kinematics: Computing joint angles for desired end-effector positions
- Model Predictive Control (MPC): Real-time optimization of movements
- Learning from Demonstration: Teaching robots through human examples
- Reinforcement Learning: Learning locomotion policies through trial and error""",
        "source": "Chapter 4: Humanoid Robotics",
        "keywords": ["humanoid", "bipedal", "locomotion", "zmp", "kinematics", "atlas", "asimo", "walking", "balance", "manipulation"],
        "topic": "humanoid_robotics"
    },
    {
        "content": """AI in robotics enables machines to perceive, reason, learn, and act in the physical world. This involves various AI techniques specifically tailored for robotic applications.

Machine Learning Applications in Robotics:
- Supervised Learning: Object detection and recognition, pose estimation, semantic segmentation
- Reinforcement Learning: Learning through trial and error, robot control policies, game playing
- Unsupervised Learning: Clustering sensor data, anomaly detection, dimensionality reduction
- Deep Learning: CNNs for vision tasks, RNNs/LSTMs for sequences, Transformers for language

Computer Vision for Robotics:
- Object Recognition: Identifying and locating objects in 3D space
- SLAM (Simultaneous Localization and Mapping): Building maps while tracking position
- Visual Odometry: Estimating camera/robot motion from video sequences
- Face Recognition: Identifying humans for social interaction
- Semantic Segmentation: Pixel-level understanding of scene content

Advanced Path Planning:
- A* Algorithm: Optimal pathfinding on grids with heuristics
- RRT (Rapidly-exploring Random Trees): Planning in high-dimensional spaces
- RRT*: Optimally efficient variant of RRT with path optimization
- PRM (Probabilistic Roadmaps): Pre-computed path networks for fast replanning
- D* Algorithm: Dynamic path planning for unknown environments

Reinforcement Learning Example:
```python
import gym
import numpy as np
from stable_baselines3 import PPO

# Create a robotics environment
env = gym.make('FetchReach-v1')

# Create PPO agent
model = PPO('MlpPolicy', env, verbose=1)

# Train the agent
model.learn(total_timesteps=100000)

# Test the trained agent
obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, dones, info = env.step(action)
    env.render()
    if dones:
        obs = env.reset()
```

Future Directions:
- Embodied AI: Systems that learn through physical interaction with the world
- Federated Learning: Collaborative learning across multiple robots
- Neuromorphic Computing: Brain-inspired hardware for efficient AI processing
- Edge AI: On-robot processing for privacy, speed, and offline operation
- Quantum Computing: Potential for solving complex optimization problems""",
        "source": "Chapter 5: AI in Robotics",
        "keywords": ["machine learning", "computer vision", "path planning", "slam", "reinforcement learning", "deep learning", "neural networks", "optimization"],
        "topic": "ai_robotics"
    }
]

# Security
security = HTTPBearer()


async def parse_request_data(request: Request) -> Dict[str, Any]:
    """Parse request data from JSON or form-encoded format"""
    content_type = request.headers.get('content-type', '').lower()

    # Get raw body
    body = await request.body()

    # Try to parse as JSON first
    if 'application/json' in content_type:
        try:
            return json.loads(body.decode())
        except:
            pass

    # Try form data
    if 'application/x-www-form-urlencoded' in content_type:
        try:
            parsed = parse_qs(body.decode())
            return {k: v[0] if v else '' for k, v in parsed.items()}
        except:
            pass

    # Default: try JSON anyway
    try:
        return json.loads(body.decode())
    except:
        return {}


def enhance_query(query: str) -> str:
    """Enhance query with related terms"""
    enhancements = {
        'robot': ['robotics', 'robotic'],
        'ai': ['artificial intelligence', 'intelligence'],
        'learn': ['learning', 'algorithm'],
        'move': ['movement', 'motion', 'locomotion'],
        'see': ['vision', 'perception', 'camera'],
        'path': ['planning', 'navigation', 'trajectory'],
        'human': ['humanoid', 'human-like']
    }

    words = query.lower().split()
    enhanced = query.lower()

    for word in words:
        if word in enhancements:
            for syn in enhancements[word]:
                if syn not in enhanced:
                    enhanced += f' {syn}'

    return enhanced


def retrieve_relevant_context(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Enhanced retrieval with better scoring"""
    query_lower = enhance_query(query.lower())
    query_words = set(query_lower.split())

    scored_docs = []

    for doc in KNOWLEDGE_BASE:
        score = 0

        # Keyword matching with weights
        doc_keywords = set(k.lower() for k in doc.get('keywords', []))
        keyword_matches = query_words.intersection(doc_keywords)
        score += len(keyword_matches) * 100  # High weight for keyword matches

        # Topic matching
        if 'topic' in doc:
            for word in query_words:
                if doc['topic'] == word:
                    score += 200  # Very high weight for exact topic match

        # Title/source matching
        source_lower = doc['source'].lower()
        if any(word in source_lower for word in query_words):
            score += 50

        # Content similarity
        content_lower = doc['content'].lower()

        # Exact phrase matches
        if query_lower in content_lower:
            score += 150

        # Word matching in content
        content_words = set(content_lower.split())
        word_matches = query_words.intersection(content_words)
        score += len(word_matches) * 10

        # Sequence matching for similar substrings
        for word in query_words:
            if len(word) > 3:
                for content_word in content_words:
                    if len(content_word) > 3:
                        similarity = SequenceMatcher(None, word, content_word).ratio()
                        if similarity > 0.8:
                            score += int(similarity * 30)

        # Bonus for definitions when asked
        if any(q in query_lower for q in ['what is', 'define', 'explain']):
            if any(p in content_lower for p in ['definition:', 'refers to', 'is a', 'are:']):
                score += 80

        if score > 0:
            scored_docs.append((score, doc))

    # Sort by score and return top results
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:max_results]]


def generate_smart_response(query: str, context: List[Dict[str, Any]], user: str) -> Dict[str, Any]:
    """Generate more intelligent and contextual responses"""
    if not context:
        # Better fallback when no context found
        return {
            "response": f"I don't have information about '{query}' in the Physical AI textbook. The textbook covers these main topics:\n\n📚 **Available Topics:**\n- **Physical AI**: Introduction to embodied artificial intelligence\n- **ROS2**: Robot Operating System fundamentals and programming\n- **Gazebo**: 3D simulation for robotics\n- **Humanoid Robotics**: Bipedal robots and locomotion\n- **AI in Robotics**: Machine learning and computer vision applications\n\nTry asking about any of these topics, for example:\n- \"What is Physical AI?\"\n- \"How do I use ROS2?\"\n- \"Explain Gazebo simulation\"\n- \"Tell me about humanoid robots\"",
            "sources": [],
            "related_concepts": ["Physical AI", "Robotics", "AI/ML"],
            "suggestions": [
                "What is Physical AI?",
                "Explain ROS2 concepts",
                "How does Gazebo work?",
                "Humanoid robot challenges"
            ],
            "rag_used": False,
            "ai_used": True
        }

    query_lower = query.lower()

    # Handle different question types
    if any(q in query_lower for q in ['what is', 'define', 'tell me about', 'explain']):
        # Definition/Explanation queries
        topic = extract_topic(query)
        response = build_definition_response(topic, context)

    elif any(q in query_lower for q in ['how to', 'how do', 'example', 'code']):
        # Tutorial/Example queries
        response = build_tutorial_response(query, context)

    elif any(q in query_lower for q in ['why', 'when', 'compare', 'difference']):
        # Analytical queries
        response = build_analytical_response(query, context)

    elif any(q in query_lower for q in ['list', 'components', 'features', 'types']):
        # List-based queries
        response = build_list_response(query, context)

    else:
        # General informational response
        response = build_general_response(query, context)

    # Add sources and related info
    sources = [doc["source"] for doc in context]
    related_concepts = extract_related_concepts(query, context)
    suggestions = generate_smart_suggestions(query, context)

    return {
        "response": response,
        "sources": sources,
        "related_concepts": related_concepts,
        "suggestions": suggestions,
        "rag_used": True,
        "ai_used": False
    }


def extract_topic(query: str) -> str:
    """Extract the main topic from a query"""
    # Remove question words
    clean_query = re.sub(r'\b(what is|define|tell me about|explain|describe)\b', '', query, flags=re.IGNORECASE).strip()

    # Split and get first few words
    words = clean_query.split()[:3]
    return ' '.join(words)


def build_definition_response(topic: str, context: List[Dict[str, Any]]) -> str:
    """Build a response for definition-type queries"""
    response = f"## {topic.title()}\n\n"

    for i, doc in enumerate(context[:2], 1):
        # Extract definition-like sentences
        content = doc["content"]
        lines = content.split('\n')

        definition_found = False
        for line in lines:
            if any(pattern in line.lower() for pattern in [
                'refers to', 'is a', 'are:', 'definition:', 'what is',
                'provides', 'enables', 'combines'
            ]):
                response += f"**{doc['source']}**:\n{line.strip()}\n\n"
                definition_found = True
                break

        if not definition_found:
            # Use first paragraph as definition
            paragraphs = content.split('\n\n')
            if paragraphs:
                first_para = paragraphs[0]
                sentences = first_para.split('.')[:2]
                response += f"**{doc['source']}**:\n{'.'.join(sentences)}.\n\n"

    # Add key points if available
    if len(context) > 0:
        response += "### Key Points:\n"
        for doc in context[:1]:
            content = doc["content"]
            # Look for bullet points or lists
            if 'Key Components:' in content:
                parts = content.split('Key Components:')
                if len(parts) > 1:
                    key_comp = parts[1].split('\n\n')[0]
                    response += key_comp.strip()

    return response


def build_tutorial_response(query: str, context: List[Dict[str, Any]]) -> str:
    """Build a response with code examples"""
    response = f"## Tutorial: {query.title()}\n\n"

    # Find code examples
    code_examples = []
    for doc in context:
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', doc["content"], re.DOTALL)
        for code in code_blocks:
            code_examples.append({
                "code": code.strip(),
                "source": doc["source"]
            })

    if code_examples:
        response += "### Code Example:\n\n"
        for example in code_examples[:2]:
            response += f"From {example['source']}:\n\n```python\n{example['code']}\n```\n\n"
    else:
        # Provide step-by-step guidance
        response += "### Steps to implement:\n\n"
        for i, doc in enumerate(context[:3], 1):
            response += f"{i}. **{doc['source']}**:\n"
            # Extract first actionable sentences
            sentences = doc["content"].split('.')[1:3]
            response += '. '.join(sentences) + '\n\n'

    return response


def build_analytical_response(query: str, context: List[Dict[str, Any]]) -> str:
    """Build an analytical/comparative response"""
    response = f"## Analysis: {query.title()}\n\n"

    # Extract comparisons or explanations
    for i, doc in enumerate(context, 1):
        response += f"### {i}. {doc['source']}\n\n"

        # Look for comparison content
        content = doc["content"]

        if 'challenges:' in content.lower() or 'benefits:' in content.lower():
            # Extract challenges/benefits section
            parts = re.split(r'\n(challenges|benefits):', content, flags=re.IGNORECASE)
            for j in range(1, len(parts), 2):
                if j + 1 < len(parts):
                    section_title = parts[j]
                    section_content = parts[j+1].split('\n\n')[0]
                    response += f"**{section.title()}**:\n{section_content.strip()}\n\n"
        else:
            # Use first informative paragraph
            paragraphs = content.split('\n\n')
            if paragraphs:
                response += paragraphs[0] + "\n\n"

    return response


def build_list_response(query: str, context: List[Dict[str, Any]]) -> str:
    """Build a list-based response"""
    response = f"## {query.title()}\n\n"

    # Extract lists from context
    all_items = []

    for doc in context:
        content = doc["content"]

        # Look for bullet points or numbered lists
        lines = content.split('\n')
        in_list = False

        for line in lines:
            if line.strip().startswith('-') or line.strip().startswith('*'):
                all_items.append(f"- {line.strip()[1:].strip()}")
                in_list = True
            elif re.match(r'^\d+\.', line.strip()):
                all_items.append(line.strip())
                in_list = True
            elif in_list and not line.strip():
                in_list = False
            elif in_list:
                all_items.append(f"- {line.strip()}")

        # If no explicit lists, extract key phrases
        if not all_items:
            # Look for "Key Components" or similar
            if 'Key Components:' in content:
                parts = content.split('Key Components:')
                if len(parts) > 1:
                    items = parts[1].split('\n\n')[0]
                    for item in re.findall(r'- \*\*(.*?)\*\*: (.*)', items):
                        all_items.append(f"**{item[0]}**: {item[1]}")

    # Compile the response
    if all_items:
        response += '\n'.join(all_items[:10])  # Limit to 10 items
    else:
        # Fallback: summarize key points from each document
        for i, doc in enumerate(context, 1):
            response += f"{i}. **From {doc['source']}**:\n"
            sentences = doc["content"].split('.')[:2]
            response += '. '.join(sentences) + '\n\n'

    return response


def build_general_response(query: str, context: List[Dict[str, Any]]) -> str:
    """Build a general informational response"""
    response = f"## Information about {query}\n\n"

    # Provide overview from context
    for i, doc in enumerate(context[:3], 1):
        response += f"### {i}. {doc['source']}\n\n"

        # Use the most relevant paragraph
        content = doc["content"]
        paragraphs = content.split('\n\n')

        # Find paragraph with most query words
        query_words = set(query.lower().split())
        best_para = paragraphs[0] if paragraphs else ""
        best_score = 0

        for para in paragraphs:
            para_words = set(para.lower().split())
            score = len(query_words.intersection(para_words))
            if score > best_score:
                best_score = score
                best_para = para

        response += best_para.strip() + "\n\n"

    return response


def extract_related_concepts(query: str, context: List[Dict[str, Any]]) -> List[str]:
    """Extract related concepts from context"""
    concepts = set()
    query_words = set(query.lower().split())

    for doc in context:
        # Get keywords not in query
        for keyword in doc.get('keywords', []):
            if keyword.lower() not in query_words:
                concepts.add(keyword)

        # Extract key terms from content
        content = doc["content"]
        # Look for capitalized terms or technical terms
        for word in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content):
            if len(word) > 3 and word.lower() not in query_words:
                concepts.add(word)

    return list(concepts)[:5]


def generate_smart_suggestions(query: str, context: List[Dict[str, Any]]) -> List[str]:
    """Generate intelligent follow-up suggestions"""
    suggestions = []
    query_lower = query.lower()

    # Context-based suggestions
    if 'physical ai' in query_lower:
        suggestions.extend([
            "What are the components of Physical AI?",
            "Real-world examples of Physical AI",
            "How does Physical AI differ from traditional AI?"
        ])

    elif 'ros2' in query_lower:
        suggestions.extend([
            "How to create a ROS2 node?",
            "What are ROS2 topics?",
            "ROS2 vs ROS1 differences"
        ])

    elif 'gazebo' in query_lower:
        suggestions.extend([
            "How to create a robot model in Gazebo?",
            "Gazebo vs real world testing",
            "Adding sensors to Gazebo simulation"
        ])

    elif 'humanoid' in query_lower:
        suggestions.extend([
            "Challenges in humanoid robotics",
            "Atlas robot capabilities",
            "Bipedal walking algorithms"
        ])

    elif any(word in query_lower for word in ['ai', 'machine learning', 'reinforcement']):
        suggestions.extend([
            "Machine learning in robotics",
            "Computer vision for robots",
            "Path planning algorithms"
        ])

    # Add context-specific suggestions
    if context:
        for doc in context[:2]:
            # Look for headings or key topics
            lines = doc["content"].split('\n')
            for line in lines:
                if line.strip().startswith('#') or line.strip().startswith('###'):
                    topic = line.strip('#').strip()
                    if topic and len(suggestions) < 5:
                        suggestions.append(f"Tell me more about {topic}")

    # Default suggestions if none generated
    if not suggestions:
        suggestions = [
            "What is Physical AI?",
            "Explain ROS2 fundamentals",
            "How does Gazebo simulation work?",
            "Humanoid robot examples"
        ]

    return suggestions[:4]


# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Physical AI RAG Server V5 Enhanced...")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="Physical AI Textbook API",
    description="API for Physical AI & Humanoid Robotics Textbook with Enhanced RAG",
    version="5.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return username
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request):
    """Register a new user"""
    data = await parse_request_data(request)

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )

    if username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Hash password (truncate to 72 bytes for bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    users[username] = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password
    }

    logger.info(f"User {username} registered successfully")
    return {"message": "User registered successfully"}


@app.post("/api/v1/auth/login")
async def login(request: Request):
    """Login user"""
    data = await parse_request_data(request)

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )

    user = users.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    password_bytes = password.encode('utf-8')[:72]
    if not bcrypt.checkpw(password_bytes, user['hashed_password'].encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create token
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"User {username} logged in successfully")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@app.get("/api/v1/auth/me")
async def get_current_user(current_user: str = Depends(verify_token)):
    """Get current user info"""
    user = users.get(current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "username": user["username"],
        "email": user.get("email")
    }


@app.post("/api/v1/chat")
async def chat_message(request: Request, current_user: str = Depends(verify_token)):
    """Handle chat messages with Enhanced RAG"""
    data = await parse_request_data(request)
    message = data.get('message', '')

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )

    # Retrieve relevant context with enhanced algorithm
    context = retrieve_relevant_context(message, max_results=3)

    # Generate smart response
    response = generate_smart_response(message, context, current_user)

    # Add metadata
    response["timestamp"] = datetime.utcnow().isoformat()
    response["user"] = current_user

    logger.info(f"Generated enhanced RAG response for {current_user}: {message[:50]}...")
    return response


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API V5 Enhanced",
        "features": [
            "Enhanced RAG with better context retrieval",
            "Smart response generation",
            "Code examples and tutorials",
            "Physical AI knowledge base"
        ],
        "endpoints": {
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login",
            "chat": "/api/v1/chat",
            "user": "/api/v1/auth/me"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "knowledge_base_size": len(KNOWLEDGE_BASE),
        "version": "5.0.0-enhanced"
    }


if __name__ == "__main__":
    uvicorn.run(
        "standalone_rag_v5_enhanced:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )