# Physical AI & Humanoid Robotics Textbook - Quick Start Guide

## Overview

This is an AI-native, interactive technical textbook for learning Physical AI and Humanoid Robotics. The book combines theory, hands-on labs, and AI assistance to provide a comprehensive learning experience.

## For Readers

### Getting Started

1. **Visit the Textbook**
   - URL: https://physical-ai-robotics.panaversity.org
   - No installation required - works in any modern browser

2. **Optional: Create an Account**
   - Click "Sign Up" in the top right
   - Provide email and complete background survey
   - Benefits: Progress tracking, personalized content, Urdu translation

3. **Navigate the Content**
   - Use the sidebar to browse chapters and lessons
   - Each lesson includes:
     - Learning objectives
     - Interactive theory sections
     - Code examples
     - Hands-on labs
     - Knowledge checks

4. **Get Help While Learning**
   - Select any text and click "Ask Book"
   - Use the chat widget for general questions
   - Get contextual explanations and related content

5. **Complete Activities**
   - Run code examples directly in your browser
   - Complete lab exercises for practical skills
   - Take quizzes to test your understanding

### Course Structure

- **Chapter 1**: Physical AI Foundations (Weeks 1-2)
- **Chapter 2**: Core Robotics Systems (Weeks 3-7)
- **Chapter 3**: AI-Robot Intelligence (Weeks 8-13)
- **Chapter 4**: Humanoid Robotics Capstone

### Features

- **Interactive Code**: Run and modify ROS 2, Gazebo, and Isaac examples
- **AI Assistant**: Get help with any concept instantly
- **Progress Tracking**: Monitor your learning journey
- **Multilingual**: Switch between English and Urdu
- **Offline Mode**: Download content for offline reading

## For Contributors

### Prerequisites

- Node.js 18+ and npm
- Git
- GitHub account
- (Optional) ROS 2 Humble for testing

### Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/panaversity/physical-ai-textbook.git
   cd physical-ai-textbook
   ```

2. **Install Dependencies**
   ```bash
   npm install
   cd backend
   pip install -r requirements.txt
   ```

3. **Start Development**
   ```bash
   # Terminal 1 - Frontend
   npm run start

   # Terminal 2 - Backend (optional, for chatbot)
   cd backend
   uvicorn app.main:app --reload
   ```

4. **Access Local Site**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Adding Content

1. **Create New Lesson**
   ```bash
   mkdir - docs/chapter-X
   # Create lesson-X.mdx file
   ```

2. **Lesson Template**
   ```mdx
   ---
   title: "Lesson Title"
   objectives:
     - "Objective 1"
     - "Objective 2"
   ---

   import { CodeRunner } from '@site/src/components/CodeRunner';
   import { Mermaid } from '@site/src/components/Mermaid';

   ## Theory Section

   Your theory content here...

   ## Code Example

   <CodeRunner language="python">
   {`# Your code here
   print("Hello, ROS 2!")`}
   </CodeRunner>

   ## Diagram

   <Mermaid>
   {`
   graph TD
       A[Start] --> B[Process]
       B --> C[End]
   `}
   </Mermaid>
   ```

3. **Content Guidelines**
   - Each lesson must have 3+ learning objectives
   - Include at least one interactive element
   - All code examples must be tested
   - Add alt text for all images
   - Provide both English and Urdu versions

### Testing

1. **Run Tests**
   ```bash
   npm run test
   cd backend && pytest
   ```

2. **Content Validation**
   ```bash
   npm run validate-content
   ```

3. **Build Check**
   ```bash
   npm run build
   ```

### Submitting Changes

1. Create a feature branch
2. Make your changes
3. Run all tests
4. Submit a pull request
5. Request review from the team

## Technical Requirements

### Minimum Requirements

- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Internet**: Required for chatbot and initial load
- **Screen Resolution**: 1024x768 minimum

### Recommended Setup

- **Browser**: Latest Chrome or Firefox
- **Internet**: 10 Mbps+ for smooth simulations
- **RAM**: 8GB+ for complex simulations
- **OS**: Windows 10, macOS 11, or Ubuntu 20.04+

### Optional Hardware

- **Robot**: TurtleBot3 or similar for Chapter 4
- **GPU**: NVIDIA GPU for local simulation
- **Camera**: For computer vision labs
- **Microphone**: For voice control features

## Troubleshooting

### Common Issues

1. **Code Runner Not Working**
   - Check browser console for errors
   - Disable ad blockers
   - Try refreshing the page

2. **Chatbot Not Responding**
   - Check internet connection
   - Verify API key configuration
   - Check rate limits

3. **Simulations Loading Slowly**
   - Close other browser tabs
   - Check internet speed
   - Try lower quality settings

4. **Translation Issues**
   - Report specific translation errors
   - Suggest improvements via feedback

### Getting Help

- **Email**: support@panaversity.org
- **Discord**: [Community Server Link]
- **GitHub Issues**: [Repository Issues]
- **Documentation**: [Full Documentation Link]

## Next Steps

1. **Start Learning**: Begin with Chapter 1, Lesson 1
2. **Join Community**: Connect with other learners
3. **Provide Feedback**: Help us improve the textbook
4. **Contribute**: Add your expertise to the content

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this textbook in your work, please cite:

```
Physical AI & Humanoid Robotics Textbook (2025)
Panaversity Institute
https://physical-ai-robotics.panaversity.org
```

---

Happy learning! 🤖✨