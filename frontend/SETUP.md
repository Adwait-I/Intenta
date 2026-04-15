# INTENTA Frontend - Setup & Running Guide

## Prerequisites
- Ensure the backend API is running (see backend README)
- Node.js and npm installed
- Expo CLI (optional, `npx expo` works)

## Setup Complete ✓

The frontend has been configured with:
- ✓ Dependencies installed (`node_modules/`)
- ✓ Asset files created (`assets/icon.png`, `splash.png`, etc.)
- ✓ Environment configuration (`.env` file)
- ✓ TypeScript configuration
- ✓ Babel configuration for React Native

## Running the App

### Option 1: Expo Web (Fastest for testing)
```bash
npm run web
```
Opens in browser at http://localhost:19006

### Option 2: iOS Simulator (macOS only)
```bash
npm run ios
```
Requires Xcode and iOS Simulator installed

### Option 3: Android Emulator
```bash
npm run android
```
Requires Android Studio and Android Emulator

### Option 4: Expo Go (Mobile device)
```bash
npm start
```
Then scan QR code with Expo Go app on your phone

## Important Notes

1. **Backend Connection**: The app expects the backend API at `http://localhost:8000`
   - Ensure Docker containers are running
   - Edit `.env` file to change API_BASE_URL if needed

2. **First Time Setup**: Run `npm install` if dependencies weren't loaded
   - This project uses Expo which manages React Native setup

3. **Troubleshooting**:
   - Clear cache: `npm start -- --clear`
   - Reset modules: `rm -rf node_modules && npm install`
   - Check backend health: Visit http://localhost:8000/health

## Project Structure
```
frontend/
├── App.tsx                 # Entry point
├── src/
│   ├── screens/           # App screens (Landing, Input, Output)
│   ├── components/        # Reusable UI components
│   ├── navigation/        # Stack navigator setup
│   ├── services/          # API client
│   └── theme/            # Design tokens & styles
├── assets/               # App icons, splash screen
└── package.json         # Dependencies
```

## API Endpoints Used
- `POST /generate` - Main design generation
- `GET /health` - Backend health check

## Development Notes
- Hot reload is enabled by default with Expo
- Modify code and save to see changes instantly
- Console logs visible in Expo CLI output
