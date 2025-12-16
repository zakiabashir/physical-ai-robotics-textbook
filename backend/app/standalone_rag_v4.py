"""
Physical AI & Humanoid Robotics Textbook - Standalone RAG Server V4
Handles both JSON and form-encoded data with RAG chat support
Uses embedded knowledge base for responses
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple configuration
SECRET_KEY = os.getenv("SECRET_KEY", "test_secret_key_123")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory user store for demo (replace with database in production)
users = {}
user_sessions = {}

# Embedded knowledge base for Physical AI
KNOWLEDGE_BASE = [
    {
        "content": """Physical AI refers to artificial intelligence systems that interact with the physical world through robots or other physical embodiments. It combines AI/ML for decision-making, robotics for physical interaction, sensors for perception, and actuators for movement.

Key Components:
- **AI/ML Algorithms**: Neural networks, reinforcement learning, computer vision
- **Robotics Hardware**: Joints, motors, end-effectors, mobile platforms
- **Sensor Systems**: Cameras, LiDAR, IMUs, tactile sensors
- **Actuation**: Motors, hydraulics, pneumatics, artificial muscles

Examples:
- Humanoid robots like Boston Dynamics' Atlas
- Self-driving cars (Tesla Autopilot, Waymo)
- Industrial robots in manufacturing
- Delivery drones with autonomous navigation
- Surgical robots like the da Vinci system""",
        "source": "Chapter 1: Introduction to Physical AI",
        "keywords": ["physical ai", "embodied ai", "robotics", "sensors", "actuators"]
    },
    {
        "content": """ROS2 (Robot Operating System 2) is a flexible framework for writing robot software. It provides the tools, libraries, and conventions to simplify complex robot applications.

Key Concepts:
- **Nodes**: Independent processes that perform computation
- **Topics**: Named buses for exchanging messages between nodes
- **Services**: Request/response communication pattern
- **Actions**: Asynchronous goal-oriented tasks
- **Parameters**: Configuration values for nodes
- **DDS**: Data Distribution Service for communication

Code Example - Publisher Node:
```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        timer_period = 1.0
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    talker = Talker()
    rclpy.spin(talker)
    talker.destroy_node()
    rclpy.shutdown()
```

Benefits:
- Distributed system architecture
- Language independence (Python, C++, Java)
- Real-time capabilities
- Extensive tooling and visualization""",
        "source": "Chapter 2: ROS2 Fundamentals",
        "keywords": ["ros2", "nodes", "topics", "services", "dds", "publisher", "subscriber"]
    },
    {
        "content": """Gazebo is a 3D simulation environment for robotics development. It provides realistic physics simulation, sensor modeling, and robot visualization.

Key Features:
- **Physics Engine**: ODE for accurate dynamics
- **3D Rendering**: OpenGL-based visualization
- **Sensor Simulation**: Cameras, LiDAR, IMUs, contact sensors
- **Robot Models**: URDF and SDF file formats
- **Plugin System**: Custom sensors and actuators
- **ROS Integration**: Direct connection to ROS nodes

Creating a Simple Robot Model:
```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <link name="base_link">
    <inertial>
      <mass value="1"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </collision>
  </link>
</robot>
```

Use Cases:
- Algorithm development before hardware deployment
- Testing in safe, repeatable conditions
- Educational demonstrations
- Competition robotics (RoboCup, etc.)""",
        "source": "Chapter 3: Simulation with Gazebo",
        "keywords": ["gazebo", "simulation", "physics", "urdf", "sdf", "plugins", "ros"]
    },
    {
        "content": """Humanoid robotics focuses on creating robots with human-like body structures and capabilities. These robots face unique challenges in locomotion, manipulation, and human-robot interaction.

Locomotion Challenges:
- **Bipedal Walking**: Maintaining balance during dynamic movement
- **Gait Planning**: Smooth, energy-efficient walking patterns
- **Terrain Adaptation**: Walking on stairs, slopes, uneven surfaces
- **Fall Recovery**: Detecting and recovering from falls

Key Components:
- **Leg Kinematics**: 6-DOF legs with hip, knee, ankle joints
- **Torso Control**: Upper body stabilization and balance
- **Arm Manipulation**: Dual arms with 5-7 DOF each
- **Sensor Fusion**: IMU, cameras, force/torque sensors

Notable Humanoid Robots:
- **Atlas** (Boston Dynamics): Advanced parkour and mobility
- **ASIMO** (Honda): Early pioneer in humanoid robotics
- **Pepper** (SoftBank): Social humanoid for human interaction
- **HRP Series** (AIST): Research platforms for locomotion
- **Optimus** (Tesla): Under development for industrial use

Control Methods:
- **Zero Moment Point (ZMP)**: Stability criterion for bipedal walking
- **Inverse Kinematics**: Computing joint angles for desired positions
- **Model Predictive Control**: Real-time optimization of movements
- **Learning from Demonstration**: Teaching robots through human examples""",
        "source": "Chapter 4: Humanoid Robotics",
        "keywords": ["humanoid", "bipedal", "locomotion", "zmp", "kinematics", "atlas", "asimo"]
    },
    {
        "content": """AI in robotics enables machines to perceive, reason, learn, and act in the physical world. This involves various AI techniques tailored for robotic applications.

Machine Learning in Robotics:
- **Supervised Learning**: Object detection, pose estimation
- **Reinforcement Learning**: Learning through trial and error
- **Unsupervised Learning**: Clustering, anomaly detection
- **Deep Learning**: CNNs for vision, RNNs for sequences

Computer Vision Applications:
- **Object Recognition**: Identifying and locating objects
- **SLAM**: Simultaneous Localization and Mapping
- **Visual Odometry**: Estimating camera motion
- **Face Recognition**: Human-robot interaction

Path Planning Algorithms:
- **A* Algorithm**: Grid-based pathfinding
- **RRT (Rapidly-exploring Random Trees)**: High-dimensional planning
- **PRM (Probabilistic Roadmaps)**: Pre-computed path networks
- **Dijkstra's**: Shortest path in graphs

Learning from Demonstration:
```python
# Example of imitation learning
import numpy as np

def learn_from_demonstrations(demos):
    """Learn policy from expert demonstrations"""
    # Collect state-action pairs from demonstrations
    states = []
    actions = []

    for demo in demos:
        states.extend(demo['states'])
        actions.extend(demo['actions'])

    # Train a simple neural network policy
    policy = train_policy_network(states, actions)
    return policy
```

Future Directions:
- **Embodied AI**: AI that learns through physical interaction
- **Federated Learning**: Collaborative learning across robots
- **Neuromorphic Computing**: Brain-inspired hardware
- **Edge AI**: On-robot processing for privacy and speed""",
        "source": "Chapter 5: AI in Robotics",
        "keywords": ["machine learning", "computer vision", "path planning", "slam", "reinforcement learning", "deep learning"]
    }
]

# Security
security = HTTPBearer()


async def parse_request_data(request: Request) -> Dict[str, Any]:
    """Parse request data from JSON or form-encoded format"""
    content_type = request.headers.get('content-type', '').lower()

    # Get raw body
    body = await request.body()

    # Log what we received
    logger.info(f"Content-Type: {content_type}")
    logger.info(f"Raw body length: {len(body)}")

    # Try to parse as JSON first
    if 'application/json' in content_type:
        try:
            data = json.loads(body.decode('utf-8'))
            logger.info(f"Parsed as JSON: {data}")
            return data
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")

    # Try to parse as form data
    if 'application/x-www-form-urlencoded' in content_type:
        try:
            # Parse URL-encoded form data
            form_data = body.decode('utf-8')
            parsed = parse_qs(form_data)
            # Convert from {key: [value]} to {key: value}
            data = {k: v[0] if v else '' for k, v in parsed.items()}
            logger.info(f"Parsed as form data: {data}")
            return data
        except Exception as e:
            logger.error(f"Failed to parse form data: {e}")

    # If content-type is not set or unrecognized, try both
    if not content_type:
        # Try JSON first
        try:
            data = json.loads(body.decode('utf-8'))
            logger.info(f"Parsed as JSON (no content-type): {data}")
            return data
        except:
            pass

        # Then try form data
        try:
            form_data = body.decode('utf-8')
            if '=' in form_data and '&' in form_data:
                parsed = parse_qs(form_data)
                data = {k: v[0] if v else '' for k, v in parsed.items()}
                logger.info(f"Parsed as form data (no content-type): {data}")
                return data
        except:
            pass

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Unable to parse request. Content-Type: {content_type}"
    )


def retrieve_relevant_context(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Retrieve relevant context from knowledge base"""
    query_lower = query.lower()
    scored_docs = []

    for doc in KNOWLEDGE_BASE:
        score = 0

        # Check keyword matches
        for keyword in doc.get("keywords", []):
            if keyword.lower() in query_lower:
                score += 10

        # Check content matches
        query_words = set(query_lower.split())
        content_words = set(doc["content"].lower().split())

        # Jaccard similarity
        intersection = query_words.intersection(content_words)
        union = query_words.union(content_words)
        jaccard = len(intersection) / len(union) if union else 0
        score += jaccard * 100

        # Bonus for exact phrase matches
        if query_lower in doc["content"].lower():
            score += 50

        if score > 0:
            scored_docs.append((score, doc))

    # Sort by score (descending) and return top results
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:max_results]]


def generate_rag_response(query: str, context: List[Dict[str, Any]], user: str) -> Dict[str, Any]:
    """Generate response using RAG (Retrieval-Augmented Generation)"""
    if not context:
        # Fallback response when no relevant context found
        return {
            "response": f"I don't have specific information about '{query}' in the Physical AI textbook. However, I can tell you that Physical AI combines artificial intelligence with robotics to create intelligent systems that interact with the physical world.\n\nWould you like to know about specific topics like:\n- Introduction to Physical AI\n- ROS2 fundamentals\n- Gazebo simulation\n- Humanoid robotics\n- AI techniques in robotics",
            "sources": [],
            "related_concepts": ["Physical AI", "Robotics", "AI/ML"],
            "suggestions": [
                "What is Physical AI?",
                "Tell me about ROS2",
                "How does Gazebo work?",
                "Explain humanoid robots"
            ]
        }

    # Build context string
    context_text = "\n\n".join([f"From {doc['source']}:\n{doc['content']}" for doc in context])

    # Generate contextual response
    query_lower = query.lower()

    # Check for specific question patterns
    if "what is" in query_lower or "define" in query_lower:
        # Extract the topic
        topic = extract_topic_from_query(query)
        relevant_content = find_definition(topic, context)

        response = f"Based on the Physical AI textbook:\n\n{relevant_content}"

    elif "how" in query_lower or "example" in query_lower or "code" in query_lower:
        # Look for practical examples or code
        relevant_content = find_examples(query, context)

        response = f"Here's a practical example from the textbook:\n\n{relevant_content}"

    elif "components" in query_lower or "parts" in query_lower or "features" in query_lower:
        # Look for component information
        relevant_content = find_components(query, context)

        response = f"The key components are:\n\n{relevant_content}"

    else:
        # General response
        response = f"Hello {user}! Based on the Physical AI textbook, here's what I found:\n\n"

        # Summarize key points from context
        for i, doc in enumerate(context[:2], 1):
            # Extract first few sentences
            sentences = doc["content"].split('.')[:3]
            summary = '.'.join(sentences).strip()
            response += f"{i}. {summary}\n\n"

        response += "\nWould you like me to elaborate on any specific aspect?"

    # Extract sources
    sources = [doc["source"] for doc in context]

    # Generate related concepts
    related_concepts = []
    for doc in context:
        related_concepts.extend(doc.get("keywords", [])[:2])
    related_concepts = list(set(related_concepts))[:5]

    # Generate suggestions
    suggestions = generate_suggestions(query_lower)

    return {
        "response": response,
        "sources": sources,
        "related_concepts": related_concepts,
        "suggestions": suggestions,
        "rag_used": True,
        "ai_used": False
    }


def extract_topic_from_query(query: str) -> str:
    """Extract the main topic from a 'what is' query"""
    patterns = [
        r"what is (?:a )?([^?]+)",
        r"define ([^?]+)",
        r"tell me about ([^?]+)",
        r"explain ([^?]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            return match.group(1).strip()

    return query.strip()


def find_definition(topic: str, context: List[Dict[str, Any]]) -> str:
    """Find definition of topic in context"""
    topic_lower = topic.lower()

    for doc in context:
        content = doc["content"].lower()

        # Look for topic definition patterns
        if topic_lower in content:
            lines = doc["content"].split('\n')
            for i, line in enumerate(lines):
                if topic_lower in line.lower() and ('is' in line.lower() or ':' in line):
                    # Return this line and next 2-3 lines
                    definition = '\n'.join(lines[i:i+4])
                    return f"{doc['source']}:\n{definition}"

    # Fallback: return first relevant paragraph
    if context:
        return f"{context[0]['source']}:\n{context[0]['content'][:500]}..."

    return "Definition not found in the current context."


def find_examples(query: str, context: List[Dict[str, Any]]) -> str:
    """Find code examples or practical examples in context"""
    examples = []

    for doc in context:
        # Look for code blocks
        code_match = re.search(r'```[\w]*\n(.*?)```', doc["content"], re.DOTALL)
        if code_match:
            examples.append(f"{doc['source']} - Code Example:\n{code_match.group(1)}")

        # Look for bullet points with examples
        lines = doc["content"].split('\n')
        for i, line in enumerate(lines):
            if 'example' in line.lower() or 'e.g.' in line.lower():
                example_text = '\n'.join(lines[i:i+4])
                examples.append(f"{doc['source']}:\n{example_text}")

    return '\n\n'.join(examples) if examples else context[0]["content"][:500]


def find_components(query: str, context: List[Dict[str, Any]]) -> str:
    """Find component information in context"""
    components = []

    for doc in context:
        # Look for bullet lists or component sections
        lines = doc["content"].split('\n')
        in_component_section = False

        for line in lines:
            if 'component' in line.lower() or 'key' in line.lower() or 'feature' in line.lower():
                in_component_section = True

            if in_component_section and line.strip().startswith('-'):
                components.append(line.strip())
            elif in_component_section and line.strip() == '':
                break

    return '\n'.join(components[:10]) if components else context[0]["content"][:300]


def generate_suggestions(query: str) -> List[str]:
    """Generate suggested follow-up questions"""
    suggestions = []

    # Topic-based suggestions
    if "physical ai" in query:
        suggestions.extend([
            "What are the components of Physical AI?",
            "How does Physical AI differ from traditional AI?",
            "What are real-world applications of Physical AI?"
        ])

    if "ros2" in query:
        suggestions.extend([
            "How do I create a ROS2 publisher?",
            "What are ROS2 topics?",
            "How to use ROS2 services?"
        ])

    if "gazebo" in query:
        suggestions.extend([
            "How to create a robot model in Gazebo?",
            "What sensors can I simulate in Gazebo?",
            "How to connect Gazebo to ROS2?"
        ])

    if "humanoid" in query:
        suggestions.extend([
            "What is Zero Moment Point (ZMP)?",
            "How do humanoid robots maintain balance?",
            "What are the challenges in bipedal locomotion?"
        ])

    # Default suggestions
    if not suggestions:
        suggestions = [
            "Tell me more about this topic",
            "What are the practical applications?",
            "Can you show me a code example?",
            "How does this relate to other topics?"
        ]

    return suggestions[:4]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Physical AI Textbook Standalone RAG Server V4...")
    logger.info(f"Knowledge base loaded with {len(KNOWLEDGE_BASE)} documents")
    yield
    # Shutdown
    logger.info("Shutting down Physical AI Textbook Standalone RAG Server V4...")


# Create FastAPI application
app = FastAPI(
    title="Physical AI Textbook API - Standalone RAG V4",
    description="Backend API for the Physical AI & Humanoid Robotics interactive textbook",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
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
    """Register a new user - accepts JSON or form data"""
    # Parse the request data
    data = await parse_request_data(request)

    # Extract fields
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Validate required fields
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )

    # Check if user already exists
    if username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Hash password using bcrypt directly (truncate to 72 bytes max for bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    # Store user
    users[username] = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }

    logger.info(f"User {username} registered successfully")
    return {"message": "User created successfully"}


@app.post("/api/v1/auth/login")
async def login(request: Request):
    """Login user and return access token - accepts JSON or form data"""
    # Parse the request data
    data = await parse_request_data(request)

    # Extract fields
    username = data.get('username')
    password = data.get('password')

    # Validate required fields
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )

    # Verify user exists
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password
    stored_password = users[username]["password"]
    password_bytes = password.encode('utf-8')[:72]

    if not bcrypt.checkpw(password_bytes, stored_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    # Store session
    user_sessions[username] = {
        "token": access_token,
        "expires_at": (datetime.utcnow() + access_token_expires).isoformat()
    }

    logger.info(f"User {username} logged in successfully")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@app.post("/api/v1/auth/google")
async def google_login(request: Request):
    """Login with Google OAuth - placeholder for future implementation"""
    data = await parse_request_data(request)

    # For now, return a message that Google Sign-In is coming soon
    return {
        "message": "Google Sign-In is coming soon! Please use email/password to sign in for now.",
        "status": "not_implemented"
    }


@app.get("/api/v1/auth/me")
async def get_current_user(current_user: str = Depends(verify_token)):
    """Get current user information"""
    user = users.get(current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "username": user["username"],
        "email": user.get("email"),
        "created_at": user["created_at"]
    }


@app.post("/api/v1/auth/logout")
async def logout(current_user: str = Depends(verify_token)):
    """Logout user"""
    if current_user in user_sessions:
        del user_sessions[current_user]

    logger.info(f"User {current_user} logged out successfully")
    return {"message": "Successfully logged out"}


@app.post("/api/v1/chat")
async def chat_message(request: Request, current_user: str = Depends(verify_token)):
    """Handle chat messages with RAG"""
    # Parse the request data
    data = await parse_request_data(request)
    message = data.get('message', '')

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )

    # Retrieve relevant context from knowledge base
    context = retrieve_relevant_context(message, max_results=3)

    # Generate response using RAG
    response = generate_rag_response(message, context, current_user)

    # Add timestamp
    response["timestamp"] = datetime.utcnow().isoformat()
    response["user"] = current_user

    logger.info(f"Generated RAG response for user {current_user}")
    return response


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API - Standalone RAG V4",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "User authentication with flexible request parsing",
            "RAG-powered chat with embedded knowledge base",
            "Google OAuth (placeholder)",
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - optimized for speed"""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Physical AI Textbook API - Standalone RAG V4",
        "version": "0.1.0",
        "description": "Backend API for interactive Physical AI textbook with RAG",
        "features": [
            "User authentication with flexible request parsing",
            "RAG (Retrieval-Augmented Generation) chat responses",
            "Embedded knowledge base from Physical AI textbook",
        ]
    }


@app.post("/api/v1/auth/test")
async def test_auth():
    """Test endpoint to verify auth is working"""
    return {"message": "Auth endpoints are working!"}


if __name__ == "__main__":
    uvicorn.run(
        "app.standalone_rag_v4:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False,
    )