#!/bin/bash
echo "=== Checking Frontend Setup ==="
echo ""

# Check Node.js version
echo "Node.js version:"
node --version
echo ""

# Check npm version
echo "npm version:"
npm --version
echo ""

# Check if package.json exists
if [ -f "package.json" ]; then
    echo "✓ package.json found"
else
    echo "✗ package.json not found"
fi

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo "✓ node_modules exists"
    echo "Number of packages: $(ls node_modules | wc -l)"
else
    echo "✗ node_modules not found"
    echo "Installing dependencies..."
    npm install
fi

# Check Docusaurus config
if [ -f "docusaurus.config.js" ]; then
    echo "✓ docusaurus.config.js found"
else
    echo "✗ docusaurus.config.js not found"
fi

# Check src directory
if [ -d "src" ]; then
    echo "✓ src directory exists"
else
    echo "✗ src directory not found"
fi

echo ""
echo "=== Starting Frontend ==="
echo "Opening browser at: http://localhost:3000"
echo ""
npm start