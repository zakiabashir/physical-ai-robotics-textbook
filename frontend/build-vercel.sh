#!/bin/bash

# Build script for Vercel deployment
# This script handles the localStorage issue that occurs with Node.js v25

echo "Starting build process for Vercel..."

# Create localStorage file for Node.js v25+
echo '{}' > localStorage.json

# Export Node options to handle localStorage
export NODE_OPTIONS="--localstorage-file=./localStorage.json --max-old-space-size=4096"

# Run the build
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build completed successfully!"
    echo "Build artifacts are in: ./build"
else
    echo "Build failed!"
    exit 1
fi