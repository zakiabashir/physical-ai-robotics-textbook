/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'introduction',
    {
      type: 'category',
      label: 'Chapter 1: Physical AI Foundations',
      collapsible: true,
      collapsed: true,
      items: [
        'chapter-1/lesson-1',
        'chapter-1/lesson-2',
        'chapter-1/lesson-3',
      ],
    },
    {
      type: 'category',
      label: 'Chapter 2: Core Robotics Systems',
      collapsible: true,
      collapsed: true,
      items: [
        'chapter-2/lesson-1',
        'chapter-2/lesson-2',
        'chapter-2/lesson-3',
      ],
    },
    {
      type: 'category',
      label: 'Chapter 3: AI-Robot Intelligence',
      collapsible: true,
      collapsed: true,
      items: [
        'chapter-3/lesson-1',
        'chapter-3/lesson-2',
        'chapter-3/lesson-3',
      ],
    },
    {
      type: 'category',
      label: 'Chapter 4: Humanoid Robotics Capstone',
      collapsible: true,
      collapsed: true,
      items: [
        'chapter-4/lesson-1',
        'chapter-4/lesson-2',
        'chapter-4/lesson-3',
        'chapter-4/lesson-4',
      ],
    },
  ],
};

module.exports = sidebars;