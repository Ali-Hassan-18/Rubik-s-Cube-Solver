import React, { useState, useCallback, useMemo } from 'react';
import CubeInput from './components/CubeInput';
import ImageUpload from './components/ImageUpload';
import SolutionDisplay from './components/SolutionDisplay';
import './App.css';

// ── Premium 3D Solver Logo ──────────────────────────────────────────────────
const SolverLogo = ({ size = 40 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" className="premium-logo-svg">
    <rect x="10" y="10" width="80" height="80" rx="18" stroke="currentColor" strokeWidth="6"/>
    <path d="M10 36.6H90M10 63.3H90M36.6 10V90M63.3 10V90" stroke="currentColor" strokeWidth="4" strokeLinecap="round"/>
    <rect x="36.6" y="36.6" width="26.8" height="26.8" fill="currentColor" fillOpacity="0.15" rx="4"/>
  </svg>
);

function App() {
  const [isStarted, setIsStarted] = useState(false);
  const [difficulty, setDifficulty] = useState(null);
  const [solution, setSolution] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('manual');
  const [darkMode, setDarkMode] = useState(false);

  const moveList = useMemo(() => {
    if (!solution?.solution) return [];
    return solution.solution.trim().split(/\s+/);
  }, [solution]);

  const handleSolve = useCallback((cubeState) => {
    setLoading(true);
    setError(null);
    fetch('/api/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state: cubeState, difficulty }),
    })
      .then((res) => res.json())
      .then((data) => data.success ? setSolution(data) : setError(data.error))
      .catch((err) => setError('Solver Error: ' + err.message))
      .finally(() => setLoading(false));
  }, [difficulty]);

  // ── Theme Toggle Component (Shared) ────────────────────────────────────────
  const ThemeToggle = () => (
    <button 
      className="theme-toggle-btn" 
      onClick={() => setDarkMode(!darkMode)}
      aria-label="Toggle Theme"
    >
      {darkMode ? "☀️" : "🌙"}
    </button>
  );

  // 1. Landing Page
  if (!isStarted) {
    return (
      <div className={`landing-hero ${darkMode ? 'dark' : ''}`}>
        <div className="landing-overlay"></div>
        
        <div className="landing-actions">
          <ThemeToggle />
        </div>

        <div className="hero-content">
          <div className="hero-visual">
            <SolverLogo size={115} />
          </div>
          <h1 className="hero-title">RUBIK'S CUBE <span className="accent-glow">SOLVER</span></h1>
          <p className="hero-tagline">
            A masterclass in precision: a premium, simplified interface powered by 
            high-performance Kociemba algorithms.
          </p>
          <button className="start-btn-3d" onClick={() => setIsStarted(true)}>
            START SOLVING
          </button>
          <div className="hero-footer-tags">
             <span>✨ AI Detection</span>
             <span>🚀 Optimal Paths</span>
             <span>🎨 Bespoke UI</span>
          </div>
        </div>
      </div>
    );
  }

  // 2. Level Selection Page
  if (isStarted && !difficulty) {
    return (
      <div className={`level-hero ${darkMode ? 'dark' : ''}`}>
        <div className="landing-overlay"></div>
        
        <div className="landing-actions">
          <ThemeToggle />
        </div>

        <div className="level-content">
          <h2 className="level-title">Select Your <span className="accent-glow">Experience</span></h2>
          <p className="level-tagline">
            Tailor the solving steps to match your current skill level.
          </p>
          
          <div className="level-cards">
            <div className="level-card" onClick={() => setDifficulty('beginner')}>
              <h3>Beginner</h3>
              <p>Step-by-step guidance with fundamental moves. Perfect for learning.</p>
            </div>
            <div className="level-card" onClick={() => setDifficulty('advanced')}>
              <h3>Advanced</h3>
              <p>Optimal, high-speed mathematical paths for professionals.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 3. Main Workspace Interface
  return (
    <div className={`app-root${darkMode ? ' dark' : ''}`}>
      <nav className="top-nav">
        <div className="nav-brand" onClick={() => { setIsStarted(false); setDifficulty(null); setSolution(null); }}>
          <SolverLogo size={32} />
          <div className="brand-text">
            <span className="brand-main">Rubik's Solver</span>
            <span className="brand-sub">Professional Workspace</span>
          </div>
        </div>
        <div className="nav-actions">
          <ThemeToggle />
        </div>
      </nav>

      {solution && (
        <div className="notation-bar">
          <div className="notation-scroll">
            {moveList.map((m, i) => <span key={i} className="move-token">{m}</span>)}
          </div>
        </div>
      )}

      <div className="app-layout">
        <aside className="sidebar">
          <section className="sidebar-group">
            <label className="sidebar-label">INPUT METHOD</label>
            <div className="mode-tabs">
              <button className={`mode-tab ${mode === 'manual' ? 'active' : ''}`} onClick={() => setMode('manual')}>Manual Grid</button>
              <button className={`mode-tab ${mode === 'image' ? 'active' : ''}`} onClick={() => setMode('image')}>Camera Scan</button>
            </div>
          </section>

          <section className="sidebar-group">
            <label className="sidebar-label">ANALYTICS</label>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-value">{moveList.length || '--'}</span>
                <span className="stat-name">Moves</span>
              </div>
              <div className="stat-card">
                <span className="stat-value" style={{ fontSize: '1.2rem' }}>
                  {difficulty ? difficulty.charAt(0).toUpperCase() + difficulty.slice(1) : '--'}
                </span>
                <span className="stat-name">Level</span>
              </div>
            </div>
          </section>

          <button className="reset-btn" onClick={() => setSolution(null)}>Reset Analysis</button>
        </aside>

        <main className="main-viewport">
          <div className={`panel-3d ${loading ? 'loading' : ''}`}>
            {loading && (
              <div className="glass-loader">
                <div className="spinner" />
                <p>Computing mathematical path...</p>
              </div>
            )}
            {mode === 'manual' ? <CubeInput onSolve={handleSolve} /> : <ImageUpload onDetect={handleSolve} />}
          </div>

          {solution && (
            <div className="panel-3d solution-card">
              <SolutionDisplay solution={solution} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
