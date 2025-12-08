@echo off
echo Starting build process...

:: Create a temporary localStorage file
echo {} > localstorage.json

:: Create a simple build script that works around localStorage issue
echo const fs = require('fs'); > temp-localstorage-patch.js
echo const localStorage = { >> temp-localstorage-patch.js
echo   getItem: (key) => { >> temp-localstorage-patch.js
echo     try { >> temp-localstorage-patch.js
echo       const data = JSON.parse(fs.readFileSync('localstorage.json', 'utf8')); >> temp-localstorage-patch.js
echo       return data[key] || null; >> temp-localstorage-patch.js
echo     } catch { return null; } >> temp-localstorage-patch.js
echo   }, >> temp-localstorage-patch.js
echo   setItem: (key, value) => { >> temp-localstorage-patch.js
echo     try { >> temp-localstorage-patch.js
echo       const data = JSON.parse(fs.readFileSync('localstorage.json', 'utf8')); >> temp-localstorage-patch.js
echo       data[key] = value; >> temp-localstorage-patch.js
echo       fs.writeFileSync('localstorage.json', JSON.stringify(data)); >> temp-localstorage-patch.js
echo     } catch { >> temp-localstorage-patch.js
echo       fs.writeFileSync('localstorage.json', JSON.stringify({[key]: value})); >> temp-localstorage-patch.js
echo     } >> temp-localstorage-patch.js
echo   }, >> temp-localstorage-patch.js
echo   removeItem: (key) => { >> temp-localstorage-patch.js
echo     try { >> temp-localstorage-patch.js
echo       const data = JSON.parse(fs.readFileSync('localstorage.json', 'utf8')); >> temp-localstorage-patch.js
echo       delete data[key]; >> temp-localstorage-patch.js
echo       fs.writeFileSync('localstorage.json', JSON.stringify(data)); >> temp-localstorage-patch.js
echo     } catch {} >> temp-localstorage-patch.js
echo   }, >> temp-localstorage-patch.js
echo   clear: () => { >> temp-localstorage-patch.js
echo     try { fs.writeFileSync('localstorage.json', '{}'); } catch {} >> temp-localstorage-patch.js
echo   } >> temp-localstorage-patch.js
echo }; >> temp-localstorage-patch.js
echo global.localStorage = localStorage; >> temp-localstorage-patch.js

:: Set Node options and run the build
set NODE_OPTIONS=--require temp-localstorage-patch.js --max-old-space-size=4096
npm run build

:: Clean up
del temp-localstorage-patch.js
del localstorage.json

echo Build complete!