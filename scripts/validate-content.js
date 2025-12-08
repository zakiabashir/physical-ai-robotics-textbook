#!/usr/bin/env node

/**
 * Content Validation Script
 *
 * This script validates all MDX lesson files to ensure they contain
 * all required components and follow the proper format.
 */

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const yaml = require('js-yaml');

const REQUIRED_COMPONENTS = [
  'learning_objectives',
  'deep_explanations',
  'code_examples',
  'diagrams',
  'labs_and_activities',
  'summary_and_quiz'
];

const REQUIRED_FRONTMATTER_FIELDS = [
  'title',
  'description',
  'difficulty',
  'estimated_time',
  'prerequisites'
];

function validateFrontmatter(frontmatter, filePath) {
  const errors = [];
  const warnings = [];

  // Check required fields
  for (const field of REQUIRED_FRONTMATTER_FIELDS) {
    if (!frontmatter[field]) {
      errors.push(`Missing required frontmatter field: ${field}`);
    }
  }

  // Validate difficulty
  if (frontmatter.difficulty && !['beginner', 'intermediate', 'advanced'].includes(frontmatter.difficulty)) {
    warnings.push(`Invalid difficulty level: ${frontmatter.difficulty}. Should be: beginner, intermediate, or advanced`);
  }

  // Validate estimated time
  if (frontmatter.estimated_time && (typeof frontmatter.estimated_time !== 'number' || frontmatter.estimated_time < 0)) {
    warnings.push(`Estimated time should be a positive number (minutes)`);
  }

  return { errors, warnings };
}

function validateContent(content, filePath) {
  const errors = [];
  const warnings = [];
  const foundComponents = new Set();

  // Check for each required component
  for (const component of REQUIRED_COMPONENTS) {
    const patterns = [
      new RegExp(`##\\s*${component.replace(/_/g, ' ')}`, 'i'),
      new RegExp(`###\\s*${component.replace(/_/g, ' ')}`, 'i'),
      new RegExp(`**${component.replace(/_/g, ' ')}**`, 'i')
    ];

    const found = patterns.some(pattern => pattern.test(content));
    if (found) {
      foundComponents.add(component);
    }
  }

  // Report missing components
  for (const component of REQUIRED_COMPONENTS) {
    if (!foundComponents.has(component)) {
      errors.push(`Missing required component: ${component.replace(/_/g, ' ')}`);
    }
  }

  // Validate code blocks
  const codeBlocks = content.match(/```(\w+)?\n([\s\S]*?)```/g) || [];
  if (codeBlocks.length === 0) {
    warnings.push('No code blocks found. Lessons should include code examples.');
  }

  // Check for Mermaid diagrams
  const mermaidDiagrams = content.match(/```mermaid\n([\s\S]*?)```/g) || [];
  if (mermaidDiagrams.length === 0) {
    warnings.push('No Mermaid diagrams found. Consider adding diagrams to explain concepts.');
  }

  // Check for activities/labs
  const hasActivity = content.match(/(?:activity|lab|hands-?on)/i);
  if (!hasActivity) {
    warnings.push('No hands-on activities or labs found. Include practical exercises.');
  }

  // Check for quiz/questions
  const hasQuiz = content.match(/(?:quiz|question|exercise)/i);
  if (!hasQuiz) {
    warnings.push('No quiz or assessment questions found. Include knowledge checks.');
  }

  // Check word count (should be substantial)
  const wordCount = content.split(/\s+/).length;
  if (wordCount < 500) {
    warnings.push(`Lesson seems short (${wordCount} words). Consider adding more content.`);
  }

  // Check for broken links (basic check)
  const internalLinks = content.match(/\[([^\]]+)\]\(\/docs\/([^)]+)\)/g) || [];
  for (const link of internalLinks) {
    const match = link.match(/\[([^\]]+)\]\(\/docs\/([^)]+)\)/);
    if (match) {
      const linkPath = path.join(process.cwd(), 'docs', match[2]);
      if (!fs.existsSync(linkPath)) {
        warnings.push(`Broken internal link: ${match[1]} -> ${match[2]}`);
      }
    }
  }

  return { errors, warnings };
}

function validateFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');

    // Extract frontmatter
    const frontmatterMatch = content.match(/^---\n(.*?)\n---/s);
    if (!frontmatterMatch) {
      return {
        filePath,
        valid: false,
        errors: ['No frontmatter found'],
        warnings: []
      };
    }

    const frontmatterText = frontmatterMatch[1];
    let frontmatter;
    try {
      frontmatter = yaml.load(frontmatterText);
    } catch (e) {
      return {
        filePath,
        valid: false,
        errors: [`Invalid YAML frontmatter: ${e.message}`],
        warnings: []
      };
    }

    // Validate frontmatter
    const { errors: fmErrors, warnings: fmWarnings } = validateFrontmatter(frontmatter, filePath);

    // Validate content
    const bodyContent = content.slice(frontmatterMatch[0].length);
    const { errors: contentErrors, warnings: contentWarnings } = validateContent(bodyContent, filePath);

    return {
      filePath,
      valid: fmErrors.length === 0 && contentErrors.length === 0,
      errors: [...fmErrors, ...contentErrors],
      warnings: [...fmWarnings, ...contentWarnings],
      stats: {
        wordCount: bodyContent.split(/\s+/).length,
        codeBlocks: (bodyContent.match(/```(\w+)?\n/g) || []).length,
        diagrams: (bodyContent.match(/```mermaid\n/g) || []).length
      }
    };
  } catch (e) {
    return {
      filePath,
      valid: false,
      errors: [`Failed to read file: ${e.message}`],
      warnings: []
    };
  }
}

function main() {
  const docsDir = path.join(process.cwd(), 'docs');

  if (!fs.existsSync(docsDir)) {
    console.error(chalk.red('Error: docs directory not found'));
    process.exit(1);
  }

  // Find all lesson files
  const lessonFiles = [];
  function findLessons(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        findLessons(fullPath);
      } else if (file.endsWith('.mdx') && file.startsWith('lesson-')) {
        lessonFiles.push(fullPath);
      }
    }
  }

  findLessons(docsDir);

  if (lessonFiles.length === 0) {
    console.error(chalk.red('Error: No lesson files found'));
    process.exit(1);
  }

  console.log(chalk.blue(`Found ${lessonFiles.length} lesson files\n`));

  // Validate all files
  const results = [];
  let totalErrors = 0;
  let totalWarnings = 0;

  for (const filePath of lessonFiles) {
    const result = validateFile(filePath);
    results.push(result);
    totalErrors += result.errors.length;
    totalWarnings += result.warnings.length;

    // Print file results
    const relativePath = path.relative(process.cwd(), filePath);
    if (result.valid) {
      console.log(chalk.green(`✓ ${relativePath}`));
    } else {
      console.log(chalk.red(`✗ ${relativePath}`));
    }

    // Print errors
    for (const error of result.errors) {
      console.log(chalk.red(`  ✗ ${error}`));
    }

    // Print warnings
    for (const warning of result.warnings) {
      console.log(chalk.yellow(`  ⚠ ${warning}`));
    }

    // Print stats
    if (result.stats) {
      console.log(chalk.gray(`  📊 ${result.stats.wordCount} words, ${result.stats.codeBlocks} code blocks, ${result.stats.diagrams} diagrams`));
    }

    console.log('');
  }

  // Print summary
  console.log(chalk.blue('\n=== Validation Summary ==='));
  console.log(`Files checked: ${lessonFiles.length}`);
  console.log(`Valid files: ${results.filter(r => r.valid).length}`);
  console.log(`Errors: ${totalErrors}`);
  console.log(`Warnings: ${totalWarnings}`);

  // Exit with error code if any validation failed
  if (totalErrors > 0) {
    console.log(chalk.red('\n❌ Validation failed. Please fix the errors above.'));
    process.exit(1);
  } else if (totalWarnings > 0) {
    console.log(chalk.yellow('\n⚠️  Validation passed with warnings. Consider addressing them.'));
  } else {
    console.log(chalk.green('\n✅ All files validated successfully!'));
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = { validateFile, validateContent, validateFrontmatter };