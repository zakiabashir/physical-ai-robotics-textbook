import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/blog',
    component: ComponentCreator('/blog', 'fcc'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive', '182'),
    exact: true
  },
  {
    path: '/blog/authors',
    component: ComponentCreator('/blog/authors', '0b7'),
    exact: true
  },
  {
    path: '/blog/future-of-humanoid-robots',
    component: ComponentCreator('/blog/future-of-humanoid-robots', '0ab'),
    exact: true
  },
  {
    path: '/blog/getting-started-with-ros2',
    component: ComponentCreator('/blog/getting-started-with-ros2', 'a5b'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags', '287'),
    exact: true
  },
  {
    path: '/blog/tags/ai',
    component: ComponentCreator('/blog/tags/ai', '7e9'),
    exact: true
  },
  {
    path: '/blog/tags/announcement',
    component: ComponentCreator('/blog/tags/announcement', '05c'),
    exact: true
  },
  {
    path: '/blog/tags/beginner',
    component: ComponentCreator('/blog/tags/beginner', '1c9'),
    exact: true
  },
  {
    path: '/blog/tags/future',
    component: ComponentCreator('/blog/tags/future', '83f'),
    exact: true
  },
  {
    path: '/blog/tags/humanoid-robots',
    component: ComponentCreator('/blog/tags/humanoid-robots', '257'),
    exact: true
  },
  {
    path: '/blog/tags/physical-ai',
    component: ComponentCreator('/blog/tags/physical-ai', '275'),
    exact: true
  },
  {
    path: '/blog/tags/robotics',
    component: ComponentCreator('/blog/tags/robotics', '7f5'),
    exact: true
  },
  {
    path: '/blog/tags/ros-2',
    component: ComponentCreator('/blog/tags/ros-2', 'be4'),
    exact: true
  },
  {
    path: '/blog/tags/society',
    component: ComponentCreator('/blog/tags/society', 'bb3'),
    exact: true
  },
  {
    path: '/blog/tags/tutorial',
    component: ComponentCreator('/blog/tags/tutorial', 'c13'),
    exact: true
  },
  {
    path: '/blog/welcome-to-physical-ai',
    component: ComponentCreator('/blog/welcome-to-physical-ai', '161'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', 'd19'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '924'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '401'),
            routes: [
              {
                path: '/docs/chapter-1/lesson-1',
                component: ComponentCreator('/docs/chapter-1/lesson-1', '31f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-1/lesson-1-example',
                component: ComponentCreator('/docs/chapter-1/lesson-1-example', '308'),
                exact: true
              },
              {
                path: '/docs/chapter-1/lesson-2',
                component: ComponentCreator('/docs/chapter-1/lesson-2', '40c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-1/lesson-3',
                component: ComponentCreator('/docs/chapter-1/lesson-3', 'a56'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-2/lesson-1',
                component: ComponentCreator('/docs/chapter-2/lesson-1', '0a1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-2/lesson-2',
                component: ComponentCreator('/docs/chapter-2/lesson-2', '506'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-2/lesson-3',
                component: ComponentCreator('/docs/chapter-2/lesson-3', '4c5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-3/lesson-1',
                component: ComponentCreator('/docs/chapter-3/lesson-1', 'dc4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-3/lesson-2',
                component: ComponentCreator('/docs/chapter-3/lesson-2', 'def'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-3/lesson-3',
                component: ComponentCreator('/docs/chapter-3/lesson-3', '13f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-4/lesson-1',
                component: ComponentCreator('/docs/chapter-4/lesson-1', '5f9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-4/lesson-2',
                component: ComponentCreator('/docs/chapter-4/lesson-2', '768'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-4/lesson-3',
                component: ComponentCreator('/docs/chapter-4/lesson-3', '7f3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-4/lesson-4',
                component: ComponentCreator('/docs/chapter-4/lesson-4', 'f64'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/introduction',
                component: ComponentCreator('/docs/introduction', 'f7d'),
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
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
