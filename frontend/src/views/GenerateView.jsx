import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import axios from 'axios'

const API = '/api'

const STEPS = [
  'Analyzing assignment instructions...',
  'Detecting course & part requirements...',
  'Researching business context...',
  'Constructing deep academic solution...',
  'Finalizing professional document...'
]

export default function GenerateView({ apiKey, onGenerated }) {
  const [studentName, setStudentName] = useState('')
  const [instructions, setInstructions] = useState('')
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(0)
  
  // New State for Dynamic Selection
  const [assignmentTypes, setAssignmentTypes] = useState([])
  const [selectedType, setSelectedType] = useState('custom_assignment')
  const [businessName, setBusinessName] = useState('')
  const [businessWebsite, setBusinessWebsite] = useState('')

  useEffect(() => {
    // Fetch assignment types on mount
    axios.get(`${API}/assignment-types`).then(res => {
      setAssignmentTypes(res.data.types)
    }).catch(err => console.error("Failed to fetch assignment types", err))
  }, [])

  const handleSubmit = async () => {
    if (!studentName.trim() || !instructions.trim()) {
      toast.error('Please enter the name and assignment instructions.')
      return
    }

    setLoading(true)
    let s = 0
    const iv = setInterval(() => {
      s = (s + 1) % STEPS.length
      setStep(s)
    }, 2000)

    try {
      const res = await axios.post(`${API}/generate`, {
        student_name: studentName,
        assignment_type: selectedType,
        business_name: businessName,
        business_website: businessWebsite,
        additional_requirements: instructions,
        openai_api_key: apiKey,
      }, { timeout: 300000 })

      clearInterval(iv)
      toast.success('Assignment Generated!')
      onGenerated(res.data)
    } catch (e) {
      clearInterval(iv)
      toast.error('Generation failed. Check your API key.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="magic-view fade-in">
      {loading && (
        <div className="progress-overlay">
          <div className="progress-card-inner">
            <div className="spinner-elite" />
            <h2 style={{ marginBottom: 8 }}>AI Analysis in Progress</h2>
            <p style={{ color: '#64748B' }}>{STEPS[step]}</p>
          </div>
        </div>
      )}

      <div className="magic-header">
        <h1>Assignment Forge</h1>
        <p>Paste the instructions given by your instructor. AI will analyze and generate the full solution.</p>
      </div>

      <div className="magic-card">
        <div className="magic-input-group">
          <label>Student Name</label>
          <select 
            className="magic-select"
            value={studentName}
            onChange={e => setStudentName(e.target.value)}
          >
            <option value="">Select a Student...</option>
            <option value="Diyaa Kana">Diyaa Kana</option>
            <option value="Fatima Al Zahrani">Fatima Al Zahrani</option>
            <option value="Hussein Jamil Moussa">Hussein Jamil Moussa</option>
            <option value="Iman Mouselli">Iman Mouselli</option>
            <option value="Malek Sharbatci">Malek Sharbatci</option>
            <option value="Marwan Kaddoura">Marwan Kaddoura</option>
            <option value="Mona Saoud">Mona Saoud</option>
            <option value="Munzer Haj Mohammad">Munzer Haj Mohammad</option>
            <option value="Nahed Haj Mohammad">Nahed Haj Mohammad</option>
            <option value="Nour Kharbouti">Nour Kharbouti</option>
            <option value="Qusay Alkhamis">Qusay Alkhamis</option>
            <option value="Sara El Anas">Sara El Anas</option>
          </select>
        </div>

        <div className="magic-input-group">
          <label>Assignment Template</label>
          <select 
            className="magic-select"
            value={selectedType}
            onChange={e => setSelectedType(e.target.value)}
          >
            <option value="custom_assignment">Custom AI Analysis (Generic)</option>
            {assignmentTypes.map(t => (
              <option key={t.id} value={t.id}>{t.course} - {t.number}: {t.label}</option>
            ))}
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div className="magic-input-group">
            <label>Business Name (Optional)</label>
            <input 
              className="magic-input"
              placeholder="e.g. Acme Corp"
              value={businessName}
              onChange={e => setBusinessName(e.target.value)}
            />
          </div>
          <div className="magic-input-group">
            <label>Business Website (Optional)</label>
            <input 
              className="magic-input"
              placeholder="https://..."
              value={businessWebsite}
              onChange={e => setBusinessWebsite(e.target.value)}
            />
          </div>
        </div>

        <div className="magic-input-group">
          <label>Additional Instructions & Context</label>
          <textarea 
            placeholder="Paste specific guidelines or additional context here..." 
            value={instructions}
            onChange={e => setInstructions(e.target.value)}
            style={{ height: '200px' }}
          />
        </div>

        <button className="magic-btn" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Analyzing & Solving...' : '⚡ Generate Professional Assignment'}
        </button>
      </div>
    </div>
  )
}
