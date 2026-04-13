/**
 * INTENTA — Firebase Configuration
 */
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyD0UD6KzC3-etz8XN0F10CR9ejH8sVHFbA",
  authDomain: "intenta-e0b93.firebaseapp.com",
  projectId: "intenta-e0b93",
  storageBucket: "intenta-e0b93.firebasestorage.app",
  messagingSenderId: "594905123595",
  appId: "1:594905123595:web:93518fcf78969163f9f00e",
  measurementId: "G-91E73C1MPJ"
};

// Initialize Firebase only once
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();

// Export the auth service
export const auth = getAuth(app);
