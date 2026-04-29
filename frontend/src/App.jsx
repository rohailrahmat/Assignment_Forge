import { useState, useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import GenerateView from './views/GenerateView'
import HistoryView from './views/HistoryView'
import PreviewView from './views/PreviewView'
import { Sparkles, Library, FileText, Settings, Moon, Sun, KeyRound } from 'lucide-react'

export default function App() {
  const [view, setView] = useState('generate')
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('af_apikey') || '')
  const [generated, setGenerated] = useState(null)
  const [historyCount, setHistoryCount] = useState(0)
  const [theme, setTheme] = useState(() => localStorage.getItem('af_theme') || 'dark')
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    localStorage.setItem('af_apikey', apiKey)
  }, [apiKey])

  useEffect(() => {
    localStorage.setItem('af_theme', theme)
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const handleGenerated = (data) => {
    setGenerated(data)
    setHistoryCount(c => c + 1)
    setView('preview')
  }

  const viewProps = { 
    apiKey, 
    onGenerated: handleGenerated, 
    generated, 
    setView, 
    historyCount,
    setGenerated
  }

  return (
    <div className="app-shell">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#0F172A',
            color: '#E2E8F0',
            border: '1px solid rgba(148, 163, 184, 0.25)',
          },
        }}
      />
      
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">✦</div>
          <div>
            <span className="logo-text">AssignmentForge</span>
            <div className="logo-sub">Studio</div>
          </div>
        </div>

        <div className="sidebar-pill">Premium Academic Workflow</div>

        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${view === 'generate' ? 'active' : ''}`}
            onClick={() => setView('generate')}
          >
            <Sparkles size={16} /> New Assignment
          </button>
          
          <button 
            className={`nav-item ${view === 'history' ? 'active' : ''}`}
            onClick={() => setView('history')}
          >
            <Library size={16} /> Library
            {historyCount > 0 && <span className="nav-badge">{historyCount}</span>}
          </button>

          {generated && (
            <button 
              className={`nav-item ${view === 'preview' ? 'active' : ''}`}
              onClick={() => setView('preview')}
            >
              <FileText size={16} /> Live Preview
            </button>
          )}
        </nav>

        <div style={{ marginTop: 'auto' }}>
          <button className="nav-item settings-btn" onClick={() => setShowSettings(true)}>
            <Settings size={16} /> Settings
          </button>
        </div>
      </aside>

      <main className="main-content">
        {view === 'generate' && <GenerateView {...viewProps} />}
        {view === 'history'  && <HistoryView  {...viewProps} />}
        {view === 'preview'  && <PreviewView  {...viewProps} />}
      </main>

      {showSettings && (
        <div className="settings-overlay" onClick={() => setShowSettings(false)}>
          <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
            <div className="settings-title-row">
              <h3>App Settings</h3>
              <button className="btn btn-outline btn-sm" onClick={() => setShowSettings(false)}>Close</button>
            </div>

            <div className="settings-block">
              <div className="settings-label">Theme Mode</div>
              <div className="theme-toggle">
                <button
                  className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
                  onClick={() => setTheme('dark')}
                >
                  <Moon size={14} /> Dark
                </button>
                <button
                  className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
                  onClick={() => setTheme('light')}
                >
                  <Sun size={14} /> Light
                </button>
              </div>
            </div>

            <div className="settings-block">
              <div className="settings-label"><KeyRound size={14} /> API Key</div>
              <input
                className="api-key-input"
                type="password"
                placeholder="sk-..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
              <div className="settings-note">
                {apiKey ? 'Connected and ready' : 'Add key for live AI generation'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
