/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'An Interactive Technical Textbook',
  favicon: 'img/favicon.svg',
  url: 'https://physical-ai-robotics.org',
  baseUrl: '/',
  organizationName: 'Physical AI',
  projectName: 'physical-ai-robotics-textbook',

  onBrokenLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/physical-ai/physical-ai-robotics-textbook/tree/main/',
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/physical-ai/physical-ai-robotics-textbook/tree/main/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Chapters',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left'
        },
        {
          to: '/rag-monitor',
          label: 'RAG Monitor',
          position: 'left'
        },
        {
          href: 'https://github.com/physical-ai/physical-ai-robotics-textbook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Chapter 1: Physical AI Foundations',
              to: '/docs/category/chapter-1-physical-ai-foundations',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/physical-ai/physical-ai-robotics-textbook',
            },
            {
              label: 'Discord',
              href: 'https://discord.gg/physical-ai',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              to: '/blog',
            },
            {
              label: 'About',
              to: '/docs/introduction',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Zakia Bashir.`,
    },
    prism: {
      theme: require('prism-react-renderer').themes.github,
      darkTheme: require('prism-react-renderer').themes.dracula,
      additionalLanguages: ['python', 'bash', 'json', 'yaml', 'docker'],
    },
    mermaid: {
      theme: {
        light: 'base',
        dark: 'base',
      },
      options: {
        themeVariables: {
          primaryColor: '#3b82f6',
          primaryTextColor: '#1f2937',
          primaryBorderColor: '#e5e7eb',
          lineColor: '#6b7280',
          sectionBkgColor: '#f9fafb',
          altSectionBkgColor: '#f3f4f6',
          gridColor: '#e5e7eb',
          secondaryColor: '#10b981',
          tertiaryColor: '#f59e0b',
        },
      },
    },
  },

plugins: [
    '@docusaurus/plugin-ideal-image',
    '@docusaurus/theme-mermaid',
  ],
// 
//   // Webpack configuration to handle localStorage issues
//   webpack: {
//     jsLoader: (isServer) => ({
//       loader: require.resolve('swc-loader'),
//       options: {
//         jsc: {
//           target: isServer ? 'es2022' : 'es2020',
//           parser: {
//             syntax: 'typescript',
//             tsx: true,
//           },
//           transform: {
//             react: {
//               runtime: 'automatic',
//             },
//           },
//         },
//       },
//     }),
//   },

  // Configure static site generation
  staticDirectories: ['static'],

  // Client modules configuration
  clientModules: [
    require.resolve('./src/theme/MDXComponents.js'),
  ],
};

module.exports = config;