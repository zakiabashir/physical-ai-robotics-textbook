# Chat Authentication Guide

## Why Chat Shows Generic Responses

The chat assistant requires **authentication** to provide intelligent responses. When not signed in, it shows a welcome message instead of calling the backend API.

## How It Works

### 1. Not Signed In
```
👋 Welcome to the Physical AI & Humanoid Robotics textbook!

Please **sign in** to ask questions about:

📖 Physical AI concepts
🤖 ROS2 programming
🦾 Humanoid robotics
🎯 Learning paths

[🔐 Sign In to Continue] ← Click to authenticate
```

### 2. Signed In
```
Hello {username}! I'm your Physical AI & Humanoid Robotics textbook assistant. I can help you with:

📚 Chapter topics
🤖 ROS2 and Gazebo
🦾 Humanoid robots
🧠 AI concepts
💻 Programming examples

What would you like to learn about?
```

### 3. After Signing In
- Chat calls the backend API with your authentication token
- Backend provides contextual, intelligent responses
- Responses are personalized and topic-specific

## Example Responses When Authenticated

**Q: "what is physical ai?"**
```
Physical AI refers to artificial intelligence systems that interact with the physical world through robots or other physical embodiments. It combines:

- **AI/ML** for decision-making
- **Robotics** for physical interaction
- **Sensors** for perception
- **Actuators** for movement

Examples include humanoid robots like Atlas, self-driving cars, and industrial robots...
```

## How to Sign In

1. Click the chat button (bottom-right)
2. Click "🔐 Sign In to Continue" in the chat
3. Enter your credentials or register
4. Chat will automatically reopen with AI responses

## Token Expiration
- Authentication tokens expire after 30 minutes
- When expired, chat shows sign-in button again
- Click the button to re-authenticate instantly

## Status
- ✅ Backend: Providing intelligent responses
- ✅ Frontend: Clear authentication messaging
- ✅ User Experience: Seamless sign-in flow