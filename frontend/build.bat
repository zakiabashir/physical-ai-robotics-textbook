@echo off
echo Starting build process...

:: Create a simple build script that works around localStorage issue
echo Mocking localStorage for Node.js environment...
echo const localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {}, clear: () => {} }; > temp-localstorage-patch.js
echo global.localStorage = localStorage; >> temp-localstorage-patch.js

:: Run the build with the patch
set NODE_OPTIONS=--require temp-localstorage-patch.js --max-old-space-size=4096
npm run build

:: Clean up
del temp-localstorage-patch.js

echo Build complete!