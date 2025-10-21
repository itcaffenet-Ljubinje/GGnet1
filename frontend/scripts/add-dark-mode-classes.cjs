/**
 * Script to add dark: prefix to text-gray-* classes in all components
 * This ensures all text is properly styled for dark mode
 */

const fs = require('fs');
const path = require('path');

// Text color mappings for dark mode
const textMappings = {
  'text-gray-900': 'dark:text-gray-100',
  'text-gray-800': 'dark:text-gray-200',
  'text-gray-700': 'dark:text-gray-300',
  'text-gray-600': 'dark:text-gray-400',
  'text-gray-500': 'dark:text-gray-400',
  'text-gray-400': 'dark:text-gray-500',
  'text-gray-300': 'dark:text-gray-600',
  'text-gray-200': 'dark:text-gray-700',
  'text-gray-100': 'dark:text-gray-800',
};

// Background color mappings
const bgMappings = {
  'bg-white': 'dark:bg-gray-800',
  'bg-gray-50': 'dark:bg-gray-800',
  'bg-gray-100': 'dark:bg-gray-700',
  'bg-gray-200': 'dark:bg-gray-600',
};

// Border color mappings
const borderMappings = {
  'border-gray-200': 'dark:border-gray-700',
  'border-gray-300': 'dark:border-gray-600',
  'border-gray-400': 'dark:border-gray-500',
};

function processFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;

  // Process text colors
  Object.entries(textMappings).forEach(([light, dark]) => {
    const regex = new RegExp(`(className="[^"]*?)${light}([^"]*")`, 'g');
    if (regex.test(content)) {
      content = content.replace(regex, `$1${light} ${dark}$2`);
      modified = true;
    }
  });

  // Process background colors
  Object.entries(bgMappings).forEach(([light, dark]) => {
    const regex = new RegExp(`(className="[^"]*?)${light}([^"]*")`, 'g');
    if (regex.test(content)) {
      content = content.replace(regex, `$1${light} ${dark}$2`);
      modified = true;
    }
  });

  // Process border colors
  Object.entries(borderMappings).forEach(([light, dark]) => {
    const regex = new RegExp(`(className="[^"]*?)${light}([^"]*")`, 'g');
    if (regex.test(content)) {
      content = content.replace(regex, `$1${light} ${dark}$2`);
      modified = true;
    }
  });

  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✓ Updated: ${filePath}`);
    return true;
  }
  return false;
}

function processDirectory(dirPath) {
  const files = fs.readdirSync(dirPath);
  let totalModified = 0;

  files.forEach(file => {
    const filePath = path.join(dirPath, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      totalModified += processDirectory(filePath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      if (processFile(filePath)) {
        totalModified++;
      }
    }
  });

  return totalModified;
}

// Process all component files
const srcDir = path.join(__dirname, '../src');
console.log('Adding dark mode classes to all components...\n');
const totalModified = processDirectory(srcDir);
console.log(`\n✓ Done! Modified ${totalModified} files.`);

