"""Simple test server for integration testing"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Physical AI Textbook API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Physical AI Textbook API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Physical AI Textbook API"}

@app.get("/api/v1/content/navigation")
async def get_navigation():
    return {
        "chapters": [
            {"id": "chapter-1", "title": "Introduction to Physical AI", "lessons": ["lesson-1", "lesson-2", "lesson-3"]},
            {"id": "chapter-2", "title": "Robot Operating System (ROS)", "lessons": ["lesson-1", "lesson-2", "lesson-3"]},
            {"id": "chapter-3", "title": "Simulation Environments", "lessons": ["lesson-1", "lesson-2", "lesson-3"]},
            {"id": "chapter-4", "title": "Humanoid Robotics", "lessons": ["lesson-1", "lesson-2", "lesson-3", "lesson-4"]},
        ]
    }

@app.get("/api/v1/content/chapters")
async def get_chapters():
    return {
        "chapters": [
            {"id": "chapter-1", "title": "Introduction to Physical AI", "description": "Learn the fundamentals of Physical AI"},
            {"id": "chapter-2", "title": "Robot Operating System (ROS)", "description": "Master ROS 2 for robotics"},
            {"id": "chapter-3", "title": "Simulation Environments", "description": "Explore Gazebo and Isaac Sim"},
            {"id": "chapter-4", "title": "Humanoid Robotics", "description": "Advanced humanoid robot control"},
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)