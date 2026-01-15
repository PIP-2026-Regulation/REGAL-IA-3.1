import React, { useState, useEffect } from 'react'
import './ParametersModal.css'

function ParametersModal({ isOpen, onClose, darkMode, onToggleDarkMode }) {
  const [colorTheme, setColorTheme] = useState(() => {
    return localStorage.getItem('colorTheme') || 'blue'
  })

  const colorThemes = [
    { id: 'blue', name: 'Blue', primary: '#93c5fd', primaryDark: '#60a5fa', primaryLight: '#bfdbfe' },
    { id: 'purple', name: 'Purple', primary: '#c4b5fd', primaryDark: '#a78bfa', primaryLight: '#ddd6fe' },
    { id: 'green', name: 'Green', primary: '#86efac', primaryDark: '#4ade80', primaryLight: '#bbf7d0' },
    { id: 'orange', name: 'Orange', primary: '#fdba74', primaryDark: '#fb923c', primaryLight: '#fed7aa' },
    { id: 'red', name: 'Red', primary: '#fca5a5', primaryDark: '#f87171', primaryLight: '#fecaca' },
    { id: 'teal', name: 'Teal', primary: '#5eead4', primaryDark: '#2dd4bf', primaryLight: '#99f6e4' }
  ]

  useEffect(() => {
    const theme = colorThemes.find(t => t.id === colorTheme)
    if (theme) {
      document.documentElement.style.setProperty('--primary-color', theme.primary)
      document.documentElement.style.setProperty('--primary-dark', theme.primaryDark)
      document.documentElement.style.setProperty('--primary-light', theme.primaryLight)
      localStorage.setItem('colorTheme', colorTheme)
    }
  }, [colorTheme])

  const handleColorThemeChange = (themeId) => {
    setColorTheme(themeId)
  }

  if (!isOpen) return null

  return (
    <>
      <div className="modal-overlay" onClick={onClose} />
      <div className="parameters-modal">
        <div className="modal-header">
          <h2>⚙️ Parameters</h2>
          <button onClick={onClose} className="modal-close-btn">✕</button>
        </div>

        <div className="modal-content">
          <div className="parameter-section">
            <h3>Appearance</h3>
            <div className="parameter-item">
              <div className="parameter-info">
                <span className="parameter-label">Theme</span>
                <span className="parameter-description">
                  Switch between light and dark mode
                </span>
              </div>
              <button
                onClick={onToggleDarkMode}
                className="theme-toggle-btn"
              >
                {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
              </button>
            </div>

            <div className="parameter-item color-theme-item">
              <div className="parameter-info">
                <span className="parameter-label">Color Theme</span>
                <span className="parameter-description">
                  Choose your preferred color scheme
                </span>
              </div>
              <div className="color-theme-grid">
                {colorThemes.map(theme => (
                  <button
                    key={theme.id}
                    className={`color-theme-btn ${colorTheme === theme.id ? 'active' : ''}`}
                    onClick={() => handleColorThemeChange(theme.id)}
                    title={theme.name}
                    style={{ backgroundColor: theme.primary }}
                  >
                    {colorTheme === theme.id && '✓'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="parameter-section">
            <h3>About</h3>
            <div className="parameter-item about-section">
              <div className="about-content">
                <h4>EU AI Act Compliance Advisor</h4>
                <p>
                  This tool helps you assess your AI system's compliance with the EU AI Act regulation.
                  It provides preliminary guidance based on your system description.
                </p>
                <p className="disclaimer">
                  ⚠️ <strong>Disclaimer:</strong> This tool provides preliminary guidance only.
                  It is not a substitute for legal advice.
                </p>
                <div className="github-link">
                  <a
                    href="https://github.com/PIP-2026-Regulation"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="github-btn"
                  >
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                    </svg>
                    View on GitHub
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default ParametersModal
