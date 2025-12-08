import React from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import clsx from 'clsx';

import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--primary button--lg"
            to="/docs/introduction">
            Start Learning
          </Link>
        </div>
      </div>
    </header>
  );
}

function ChapterCard({ chapter, number }) {
  return (
    <div className={clsx('col col--4', styles.chapterCard)}>
      <div className="card">
        <div className="card__header">
          <Heading as="h3">
            Chapter {number}: {chapter.title}
          </Heading>
        </div>
        <div className="card__body">
          <p>{chapter.description}</p>
          <ul className={styles.chapterFeatures}>
            {chapter.features.map((feature, idx) => (
              <li key={idx}>{feature}</li>
            ))}
          </ul>
        </div>
        <div className="card__footer">
          <Link
            className="button button--primary button--block"
            to={chapter.link}>
            Start Chapter {number}
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();

  const chapters = [
    {
      title: "Physical AI Foundations",
      description: "Introduction to embodied AI and the integration of physical systems with artificial intelligence",
      features: ["Embodied Intelligence", "Perception-Action Loops", "VLA Models"],
      link: "/docs/chapter-1/lesson-1"
    },
    {
      title: "Core Robotics Systems",
      description: "Master ROS 2, Gazebo simulation, and the Unity robotics ecosystem",
      features: ["ROS 2 Fundamentals", "Gazebo Simulation", "Unity Integration"],
      link: "/docs/chapter-2/lesson-1"
    },
    {
      title: "AI-Robot Intelligence",
      description: "Deep dive into NVIDIA Isaac platform and vision-language-action systems",
      features: ["Isaac Platform", "Computer Vision", "VLA Integration"],
      link: "/docs/chapter-3/lesson-1"
    },
    {
      title: "Humanoid Robotics Capstone",
      description: "Complete project building an autonomous humanoid robot system",
      features: ["Biped Locomotion", "Whole-body Control", "Integration Project"],
      link: "/docs/chapter-4/lesson-1"
    }
  ];

  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Interactive textbook for learning Physical AI and Humanoid Robotics">
      <HomepageHeader />
      <main>
        <div className="container margin-vert--lg">
          <div className="row">
            <div className="col col--8 col--offset-2">
              <div className="text--center margin-bottom--xl">
                <Heading as="h2">Welcome to the Future of Robotics Education</Heading>
                <p className={styles.heroDescription}>
                  This interactive textbook combines theory, hands-on coding, and AI-powered assistance
                  to provide a comprehensive learning experience in Physical AI and Humanoid Robotics.
                </p>
              </div>
            </div>
          </div>

          <div className="row margin-vert--lg">
            {chapters.map((chapter, idx) => (
              <ChapterCard key={idx} chapter={chapter} number={idx + 1} />
            ))}
          </div>

          <div className="row margin-vert--xl">
            <div className="col col--6">
              <div className={styles.featureBox}>
                <Heading as="h3">🤖 AI-Powered Learning</Heading>
                <p>
                  Get personalized help from our AI assistant that understands the context of your learning
                  and provides tailored explanations.
                </p>
              </div>
            </div>
            <div className="col col--6">
              <div className={styles.featureBox}>
                <Heading as="h3">💻 Interactive Code</Heading>
                <p>
                  Run and modify Python, ROS 2, and Isaac code directly in your browser with
                  our interactive coding environment.
                </p>
              </div>
            </div>
            <div className="col col--6">
              <div className={styles.featureBox}>
                <Heading as="h3">📊 Progress Tracking</Heading>
                <p>
                  Monitor your learning journey with detailed progress tracking and
                  achievement badges as you complete lessons.
                </p>
              </div>
            </div>
            <div className="col col--6">
              <div className={styles.featureBox}>
                <Heading as="h3">🎯 Hands-on Projects</Heading>
                <p>
                  Apply your knowledge through practical labs and a capstone project
                  building a complete humanoid robot system.
                </p>
              </div>
            </div>
          </div>

          <div className={styles.ctaSection}>
            <div className="text--center">
              <Heading as="h2">Ready to Start Your Journey?</Heading>
              <p className={styles.ctaDescription}>
                Join thousands of students learning the future of robotics and AI.
              </p>
              <Link
                className="button button--primary button--lg"
                to="/docs/introduction">
                Get Started Now
              </Link>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}