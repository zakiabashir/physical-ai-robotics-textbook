import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/ur/blog',
    component: ComponentCreator('/ur/blog', '742'),
    exact: true
  },
  {
    path: '/ur/blog/archive',
    component: ComponentCreator('/ur/blog/archive', '1c5'),
    exact: true
  },
  {
    path: '/ur/blog/authors',
    component: ComponentCreator('/ur/blog/authors', '186'),
    exact: true
  },
  {
    path: '/ur/blog/future-of-humanoid-robots',
    component: ComponentCreator('/ur/blog/future-of-humanoid-robots', 'a62'),
    exact: true
  },
  {
    path: '/ur/blog/getting-started-with-ros2',
    component: ComponentCreator('/ur/blog/getting-started-with-ros2', '428'),
    exact: true
  },
  {
    path: '/ur/blog/tags',
    component: ComponentCreator('/ur/blog/tags', '14b'),
    exact: true
  },
  {
    path: '/ur/blog/tags/ai',
    component: ComponentCreator('/ur/blog/tags/ai', '3f4'),
    exact: true
  },
  {
    path: '/ur/blog/tags/announcement',
    component: ComponentCreator('/ur/blog/tags/announcement', '3d6'),
    exact: true
  },
  {
    path: '/ur/blog/tags/beginner',
    component: ComponentCreator('/ur/blog/tags/beginner', 'd52'),
    exact: true
  },
  {
    path: '/ur/blog/tags/future',
    component: ComponentCreator('/ur/blog/tags/future', 'd3c'),
    exact: true
  },
  {
    path: '/ur/blog/tags/humanoid-robots',
    component: ComponentCreator('/ur/blog/tags/humanoid-robots', '97c'),
    exact: true
  },
  {
    path: '/ur/blog/tags/physical-ai',
    component: ComponentCreator('/ur/blog/tags/physical-ai', 'e1e'),
    exact: true
  },
  {
    path: '/ur/blog/tags/robotics',
    component: ComponentCreator('/ur/blog/tags/robotics', 'f37'),
    exact: true
  },
  {
    path: '/ur/blog/tags/ros-2',
    component: ComponentCreator('/ur/blog/tags/ros-2', '9b0'),
    exact: true
  },
  {
    path: '/ur/blog/tags/society',
    component: ComponentCreator('/ur/blog/tags/society', '65c'),
    exact: true
  },
  {
    path: '/ur/blog/tags/tutorial',
    component: ComponentCreator('/ur/blog/tags/tutorial', '51e'),
    exact: true
  },
  {
    path: '/ur/blog/welcome-to-physical-ai',
    component: ComponentCreator('/ur/blog/welcome-to-physical-ai', '241'),
    exact: true
  },
  {
    path: '/ur/RAGMonitor',
    component: ComponentCreator('/ur/RAGMonitor', '392'),
    exact: true
  },
  {
    path: '/ur/docs',
    component: ComponentCreator('/ur/docs', '964'),
    routes: [
      {
        path: '/ur/docs',
        component: ComponentCreator('/ur/docs', '0bf'),
        routes: [
          {
            path: '/ur/docs',
            component: ComponentCreator('/ur/docs', '643'),
            routes: [
              {
                path: '/ur/docs/chapter-1/lesson-1',
                component: ComponentCreator('/ur/docs/chapter-1/lesson-1', 'ff1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-1/lesson-1-example',
                component: ComponentCreator('/ur/docs/chapter-1/lesson-1-example', '592'),
                exact: true
              },
              {
                path: '/ur/docs/chapter-1/lesson-2',
                component: ComponentCreator('/ur/docs/chapter-1/lesson-2', '304'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-1/lesson-3',
                component: ComponentCreator('/ur/docs/chapter-1/lesson-3', 'd15'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-2/lesson-1',
                component: ComponentCreator('/ur/docs/chapter-2/lesson-1', '7ea'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-2/lesson-2',
                component: ComponentCreator('/ur/docs/chapter-2/lesson-2', 'aa0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-2/lesson-3',
                component: ComponentCreator('/ur/docs/chapter-2/lesson-3', '70c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-3/lesson-1',
                component: ComponentCreator('/ur/docs/chapter-3/lesson-1', 'f92'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-3/lesson-2',
                component: ComponentCreator('/ur/docs/chapter-3/lesson-2', '5e9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-3/lesson-3',
                component: ComponentCreator('/ur/docs/chapter-3/lesson-3', 'bbe'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-4/lesson-1',
                component: ComponentCreator('/ur/docs/chapter-4/lesson-1', '65c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-4/lesson-2',
                component: ComponentCreator('/ur/docs/chapter-4/lesson-2', '985'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-4/lesson-3',
                component: ComponentCreator('/ur/docs/chapter-4/lesson-3', 'ac9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/chapter-4/lesson-4',
                component: ComponentCreator('/ur/docs/chapter-4/lesson-4', 'ba7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/ur/docs/introduction',
                component: ComponentCreator('/ur/docs/introduction', 'a5b'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/ur/',
    component: ComponentCreator('/ur/', '3b1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
