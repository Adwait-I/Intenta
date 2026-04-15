/**
 * INTENTA — Local Auth Service
 * Replaces Firebase. All auth is local JWT via the FastAPI backend.
 * Token is stored in memory (no localStorage) for XSS safety.
 * Call `initAuth()` on app start to rehydrate from sessionStorage (web only).
 */

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// ── In-memory token store ────────────────────────────────────────────────────
// Using a closure keeps the token out of global scope / window object.
let _token: string | null = null;
let _userEmail: string | null = null;
let _userRole: string | null = null;
let _authChangeListeners: Array<(user: LocalUser | null) => void> = [];

export interface LocalUser {
  email: string;
  role: string;
}

// ── Internal helpers ─────────────────────────────────────────────────────────

function _notifyListeners(user: LocalUser | null) {
  _authChangeListeners.forEach(fn => fn(user));
}

function _setSession(token: string, email: string, role: string) {
  _token = token;
  _userEmail = email;
  _userRole = role;
  // Persist across page refresh (session only — cleared when tab closes)
  try {
    sessionStorage.setItem('intenta_token', token);
    sessionStorage.setItem('intenta_email', email);
    sessionStorage.setItem('intenta_role', role);
  } catch {
    // sessionStorage unavailable (SSR / native) — memory-only is fine
  }
  _notifyListeners({ email, role });
}

function _clearSession() {
  _token = null;
  _userEmail = null;
  _userRole = null;
  try {
    sessionStorage.removeItem('intenta_token');
    sessionStorage.removeItem('intenta_email');
    sessionStorage.removeItem('intenta_role');
  } catch { /* noop */ }
  _notifyListeners(null);
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Call once on app startup to rehydrate session from sessionStorage.
 */
export function initAuth() {
  try {
    const token = sessionStorage.getItem('intenta_token');
    const email = sessionStorage.getItem('intenta_email');
    const role = sessionStorage.getItem('intenta_role');
    if (token && email && role) {
      _token = token;
      _userEmail = email;
      _userRole = role;
      _notifyListeners({ email, role });
    } else {
      _notifyListeners(null);
    }
  } catch {
    _notifyListeners(null);
  }
}

export function getToken(): string | null {
  return _token;
}

export function getCurrentUser(): LocalUser | null {
  if (!_userEmail || !_userRole) return null;
  return { email: _userEmail, role: _userRole };
}

export function onAuthStateChanged(listener: (user: LocalUser | null) => void): () => void {
  _authChangeListeners.push(listener);
  // Immediately emit current state
  listener(getCurrentUser());
  return () => {
    _authChangeListeners = _authChangeListeners.filter(fn => fn !== listener);
  };
}

// ── Signup ────────────────────────────────────────────────────────────────────

export async function signUp(email: string, password: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Signup failed' }));
    throw new Error(body.detail || 'Signup failed');
  }
}

// ── Login ─────────────────────────────────────────────────────────────────────

export async function signIn(email: string, password: string): Promise<LocalUser> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(body.detail || 'Login failed');
  }

  const data = await res.json();
  _setSession(data.access_token, data.email, data.role);
  return { email: data.email, role: data.role };
}

// ── Logout ────────────────────────────────────────────────────────────────────

export function signOut(): void {
  _clearSession();
}

// ── Auth header helper (used by api.ts) ───────────────────────────────────────

export function getAuthHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}
