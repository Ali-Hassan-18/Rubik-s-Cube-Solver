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

// Sequence configuration steps matching backend compiler pipeline arrays
const SCAN_STEPS = [
  { id: 'U', name: 'UP (Top Face)' },
  { id: 'R', name: 'RIGHT (Right Face)' },
  { id: 'F', name: 'FRONT (Front Face)' },
  { id: 'D', name: 'DOWN (Bottom Face)' },
  { id: 'L', name: 'LEFT (Left Face)' },
  { id: 'B', name: 'BACK (Rear Face)' }
];

// Automatically switches between your live deployed backend or local server fallback
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

function App() {
  const [isStarted, setIsStarted] = useState(false);
  const [solution, setSolution] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('manual');
  const [darkMode, setDarkMode] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  
  // Mobile responsive sidebar drawer state tracking
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const moveList = useMemo(() => {
    if (!solution?.solution) return [];
    return solution.solution.trim().split(/\s+/);
  }, [solution]);

  const handleSolve = useCallback((cubeState) => {
    setLoading(true);
    setError(null);
    
    fetch(`${API_BASE_URL}/api/solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state: cubeState }),
    })
      .then((res) => res.json())
      .then((data) => data.success ? setSolution(data) : setError(data.error))
      .catch((err) => setError('Solver Error: ' + err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleFaceScan = useCallback(async (fileObject) => {
    if (!fileObject) return;
    
    setLoading(true);
    setError(null);
    
    const activeFace = SCAN_STEPS[currentStepIndex].id;
    const formData = new FormData();
    formData.append('file', fileObject);
    formData.append('face', activeFace);

    try {
      const response = await fetch(`${API_BASE_URL}/api/upload-face`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!data.success) {
        setError(data.error);
        return;
      }

      if (data.all_sides_complete) {
        setSolution(data);
        setCurrentStepIndex(0); 
      } else {
        setCurrentStepIndex((prev) => prev + 1);
      }
    } catch (err) {
      setError('Connection to computer vision engine failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [currentStepIndex]);

  const resetAnalysisState = () => {
    setSolution(null);
    setError(null);
    setCurrentStepIndex(0);
    setIsSidebarOpen(false);
    fetch(`${API_BASE_URL}/api/reset-scan`, { method: 'POST' }).catch(() => {});
  };

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  const ThemeToggle = () => (
    <button 
      className="theme-toggle-btn" 
      onClick={() => setDarkMode(!darkMode)}
      aria-label="Toggle Theme"
    >
      {darkMode ? "☀️" : "🌙"}
    </button>
  );

  if (!isStarted) {
    return (
      <div className={`landing-hero ${darkMode ? 'dark' : ''}`}>
        <div className="landing-overlay"></div>
        <div className="landing-actions"><ThemeToggle /></div>
        <div className="hero-content">
          <div className="hero-visual"><SolverLogo size={115} /></div>
          <h1 className="hero-title">RUBIK'S CUBE <span className="accent-glow">SOLVER</span></h1>
          <p className="hero-tagline">
            A masterclass in precision: a premium interface powered by 
            high-performance Kociemba mathematical optimization algorithms.
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

  return (
    <div className={`app-root${darkMode ? ' dark' : ''}`}>
      <nav className="top-nav">
        <div className="nav-left-group">
          {/* Mobile Side Menu Trigger Button */}
          <button 
            className={`hamburger-menu ${isSidebarOpen ? 'open' : ''}`} 
            onClick={toggleSidebar}
            aria-label="Toggle Controls Menu"
          >
            <span className="burger-bar"></span>
            <span className="burger-bar"></span>
            <span className="burger-bar"></span>
          </button>

          <div className="nav-brand" onClick={() => { setIsStarted(false); resetAnalysisState(); }}>
            <SolverLogo size={32} />
            <div className="brand-text">
              <span className="brand-main">Rubik's Solver</span>
              <span className="brand-sub">Professional Workspace</span>
            </div>
          </div>
        </div>

        <div className="nav-actions">
          <button className="back-btn" onClick={() => { setIsStarted(false); resetAnalysisState(); }}>← Back</button>
          <ThemeToggle />
        </div>
      </nav>

      <div className="app-layout">
        {/* Mobile Dismissal Overlay Curtain */}
        {isSidebarOpen && <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)} />}

        <aside className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
          <section className="sidebar-group">
            <label className="sidebar-label">INPUT METHOD</label>
            <div className="mode-tabs">
              <button 
                className={`mode-tab ${mode === 'manual' ? 'active' : ''}`} 
                onClick={() => { setMode('manual'); setIsSidebarOpen(false); }}
              >
                Manual Grid
              </button>
              <button 
                className={`mode-tab ${mode === 'image' ? 'active' : ''}`} 
                onClick={() => { setMode('image'); setIsSidebarOpen(false); }}
              >
                Camera Scan
              </button>
            </div>
          </section>

          {mode === 'image' && !solution && (
            <section className="sidebar-group scan-progress-section">
              <label className="sidebar-label">SCANNING PROGRESS</label>
              <div className="scan-steps-indicator">
                <p className="active-step-banner">Current Target: <b>{SCAN_STEPS[currentStepIndex].id}</b></p>
                <progress max="6" value={currentStepIndex} className="premium-progress-bar" />
                <span className="step-fraction-sub">{currentStepIndex}/6 Sides Processed</span>
              </div>
            </section>
          )}

          <section className="sidebar-group">
            <label className="sidebar-label">ANALYTICS</label>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-value">{moveList.length || '--'}</span>
                <span className="stat-name">Moves</span>
              </div>
            </div>
          </section>

          <button className="reset-btn" onClick={resetAnalysisState}>Reset Analysis</button>
        </aside>

        <main className="main-viewport">
          {error && <div className="error-toast-banner">⚠️ {error}</div>}
          
          <div className={`panel-3d ${loading ? 'loading' : ''}`}>
            {loading && (
              <div className="glass-loader">
                <div className="spinner" />
                <p>Analyzing Matrix configurations...</p>
              </div>
            )}
            
            {mode === 'manual' ? (
              <CubeInput onSolve={handleSolve} />
            ) : (
              <div className="guided-scan-container" style={{ textAlign: 'center', width: '100%' }}>
                <h3 className="guided-step-title" style={{ color: '#4f46e5', marginBottom: '15px' }}>
                  Please Upload Side: <span className="highlight-step" style={{ background: '#e0e7ff', padding: '4px 10px', borderRadius: '6px' }}>{SCAN_STEPS[currentStepIndex].name}</span>
                </h3>
                <ImageUpload onDetect={handleFaceScan} loading={loading} />
              </div>
            )}
          </div>

          {solution && (
            <>
              <div className="panel-3d solution-card">
                <SolutionDisplay solution={solution} />
              </div>
              <div className="notation-bar">
                <div className="notation-scroll">
                  {moveList.map((m, i) => <span key={i} className="move-token">{m}</span>)}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;