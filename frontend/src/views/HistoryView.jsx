import { useEffect, useState } from 'react'
import { toast } from 'react-hot-toast'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function HistoryView({ setView, setGenerated }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [showPriorityOnly, setShowPriorityOnly] = useState(false)
  const [search, setSearch] = useState('')

  const loadHistory = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API}/history`)
      setHistory(Array.isArray(res.data.history) ? res.data.history : [])
    } catch (e) {
      toast.error('Failed to load library.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  const handleView = async (item) => {
    try {
      // We can either fetch the full assignment or just use the content if it's already in history
      // Since history usually doesn't include the full content, we fetch it.
      const res = await axios.get(`${API}/assignment/${item.id}`)
      setGenerated(res.data.content)
      setView('preview')
    } catch (e) {
      toast.error('Failed to load assignment.')
    }
  }

  const handleDownload = async (id, name) => {
    try {
      const res = await axios.get(`${API}/download/docx/${id}`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${name}.docx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (e) {
      toast.error('Download failed.')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this assignment?')) return
    try {
      await axios.delete(`${API}/history/${id}`)
      setHistory(h => h.filter(x => x.id !== id))
      toast.success('Deleted from library.')
    } catch (e) {
      toast.error('Delete failed.')
    }
  }

  const handleRefine = async (item) => {
    if (!window.confirm(`Do you want to re-generate (refine) ${item.student_name}'s assignment using the latest elite AI model?`)) return
    
    setView('generate')
    // We pass the details to GenerateView via state if needed, or just let them paste.
    // For now, let's just toast and redirect to show intent.
    toast.success(`Ready to refine ${item.student_name}'s work.`)
  }

  return (
    <div className="fade-in">
      <div className="view-header">
        <div className="view-title">
          <h1>Project Library</h1>
          <p>Manage and download your previously generated assignments.</p>
        </div>
        <div className="view-actions">
          <input 
            type="text" 
            placeholder="Search students..." 
            className="finput" 
            style={{ width: '200px', marginRight: '12px' }}
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <button 
            className={`btn ${showPriorityOnly ? 'btn-primary' : 'btn-outline'}`} 
            onClick={() => setShowPriorityOnly(!showPriorityOnly)}
            style={{ marginRight: '12px' }}
          >
            {showPriorityOnly ? '🌟 Priority' : '📁 All'}
          </button>
          <button className="btn btn-primary" onClick={() => setView('generate')}>
            + New
          </button>
        </div>
      </div>

      <div className="stat-row">
        {[
          { label: 'Total Projects', val: history.length, icon: '📄', color: 'purple' },
          { label: 'Students', val: new Set(history.map(h => h.student_name)).size, icon: '👤', color: 'gold' },
          { label: 'Completed', val: history.length, icon: '✅', color: 'green' }
        ].map((s, i) => (
          <div className="stat-card" key={i}>
            <div className={`stat-icon-box ${s.color}`}>{s.icon}</div>
            <div className="stat-info">
              <div className="val">{s.val}</div>
              <div className="label">{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="library-list">
        {loading ? (
          <div className="empty-state">
            <div className="spinner-elite" style={{ width: 40, height: 40 }} />
            <p>Scanning library...</p>
          </div>
        ) : history.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📁</div>
            <h2>No assignments found</h2>
            <p>Create your first professional assignment to see it here.</p>
          </div>
        ) : (
          history
            .filter(item => {
              const matchesSearch = item.student_name.toLowerCase().includes(search.toLowerCase());
              if (!showPriorityOnly) return matchesSearch;
              const priorityStudents = [
                "Diyaa Kana", "Fatima Al Zahrani", "Hussein Jamil Moussa", 
                "Iman Mouselli", "Malek Sharbatci", "Marwan Kaddoura", 
                "Mona Saoud", "Munzer Haj Mohammad", "Nahed Haj Mohammad", 
                "Nour Kharbouti", "Qusay Alkhamis", "Sara El Anas"
              ];
              const isP = priorityStudents.some(s => 
                item.student_name.toLowerCase().includes(s.toLowerCase())
              );
              return matchesSearch && isP;
            })
            .map(item => {
              const priorityStudents = [
                "Diyaa Kana", "Fatima Al Zahrani", "Hussein Jamil Moussa", 
                "Iman Mouselli", "Malek Sharbatci", "Marwan Kaddoura", 
                "Mona Saoud", "Munzer Haj Mohammad", "Nahed Haj Mohammad", 
                "Nour Kharbouti", "Qusay Alkhamis", "Sara El Anas"
              ];
              const isPriority = priorityStudents.some(s => 
                item.student_name.toLowerCase().includes(s.toLowerCase())
              );

              return (
                <div className={`library-item ${isPriority ? 'priority-row' : ''}`} key={item.id}>
                  <div className="item-icon">{isPriority ? '🌟' : '📄'}</div>
                  <div className="item-info">
                    <div className="item-title">{item.student_name}</div>
                    <div className="item-meta">
                      <span>{item.course_code || 'Academic'}</span>
                      <span>•</span>
                      <span>{new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="item-actions">
                    <button className="btn btn-primary btn-sm" onClick={() => handleView(item)}>
                      View
                    </button>
                    <button className="btn btn-outline btn-sm" onClick={() => handleDownload(item.id, item.student_name)}>
                      Download
                    </button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(item.id)}>
                      Delete
                    </button>
                  </div>
                </div>
              );
            })
        )}
      </div>
    </div>
  )
}
