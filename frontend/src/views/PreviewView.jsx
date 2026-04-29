import { useState } from 'react'
import axios from 'axios'
import { toast } from 'react-hot-toast'

const API = 'http://localhost:8000'

export default function PreviewView({ generated }) {
  const [exporting, setExporting] = useState(false)

  if (!generated) return null

  const handleExport = async (format) => {
    setExporting(true)
    try {
      const res = await axios.post(`${API}/export/${format}`, generated, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Assignment_${generated.student_name}.${format === 'docx' ? 'docx' : 'pdf'}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch {
      toast.error('Export failed.')
    } finally {
      setExporting(false)
    }
  }

  const renderContent = (item, idx) => {
    const text = item.text || ''
    const label = item.label || ''
    
    // Image Placeholder
    const imgMatch = text.match(/image\[\[(.*?)\]\]/)
    if (imgMatch) {
      return (
        <div key={idx} style={{
          border: '2px dashed #CBD5E1',
          background: '#F8FAFC',
          padding: '40px',
          textAlign: 'center',
          margin: '20px 0',
          borderRadius: '8px',
          color: '#64748B',
          fontSize: '13px'
        }}>
          📷 Visual Evidence Placeholder [[{imgMatch[1]}]]
        </div>
      )
    }

    if (item.type === 'paragraph') {
      return (
        <div key={idx} style={{ marginBottom: '15px' }}>
          {label && <strong style={{ display: 'block', color: '#1E293B', marginBottom: '4px' }}>{label}:</strong>}
          <p style={{ textAlign: 'justify', fontSize: '11pt', color: '#334155', lineHeight: '1.6' }}>{text}</p>
        </div>
      )
    }

    if (item.type === 'field') {
      return (
        <div key={idx} style={{ display: 'flex', gap: '10px', marginBottom: '10px', borderBottom: '1px solid #F1F5F9', paddingBottom: '4px' }}>
          <span style={{ fontWeight: 700, minWidth: '150px', color: '#475569' }}>{label}:</span>
          <span style={{ color: '#0F172A' }}>{item.value}</span>
        </div>
      )
    }

    if (item.type === 'bullet_list' || item.type === 'numbered_list') {
      const ListTag = item.type === 'numbered_list' ? 'ol' : 'ul'
      return (
        <div key={idx} style={{ marginBottom: '20px' }}>
          {label && <strong style={{ color: '#1E293B' }}>{label}</strong>}
          <ListTag style={{ marginTop: '8px', paddingLeft: '20px', color: '#334155' }}>
            {item.items?.map((li, i) => <li key={i} style={{ marginBottom: '6px' }}>{li}</li>)}
          </ListTag>
        </div>
      )
    }

    if (item.type === 'grid_table' || item.type === 'key_value_table') {
      const headers = item.headers || (item.type === 'key_value_table' ? ['Characteristic', 'Description'] : [])
      const rows = item.rows || []
      return (
        <div key={idx} style={{ margin: '20px 0' }}>
          {label && <div style={{ fontWeight: 800, marginBottom: '8px', fontSize: '12pt', color: '#4F46E5' }}>{label}</div>}
          <table className="academic-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#1A1A2E', color: 'white' }}>
                {headers.map((h, i) => <th key={i} style={{ padding: '10px', textAlign: 'left', fontSize: '10pt' }}>{h.toUpperCase()}</th>)}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #E2E8F0' }}>
                  {Object.values(row).map((cell, j) => <td key={j} style={{ padding: '10px', fontSize: '10pt', verticalAlign: 'top' }}>{cell}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }

    if (item.type === 'pros_cons_table') {
      return (
        <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', margin: '20px 0' }}>
          <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', padding: '15px', borderRadius: '8px' }}>
            <h4 style={{ color: '#15803D', marginTop: 0 }}>Strategic Advantages (Pros)</h4>
            <ul style={{ paddingLeft: '20px', fontSize: '10pt' }}>
              {item.pros?.map((p, i) => <li key={i}>{p}</li>)}
            </ul>
          </div>
          <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', padding: '15px', borderRadius: '8px' }}>
            <h4 style={{ color: '#B91C1C', marginTop: 0 }}>Potential Limitations (Cons)</h4>
            <ul style={{ paddingLeft: '20px', fontSize: '10pt' }}>
              {item.cons?.map((c, i) => <li key={i}>{c}</li>)}
            </ul>
          </div>
        </div>
      )
    }

    if (item.type === 'influencer_table') {
      return (
        <div key={idx} style={{ overflowX: 'auto', margin: '20px 0' }}>
          <table className="academic-table">
            <thead>
              <tr style={{ background: '#4F46E5', color: 'white' }}>
                <th>Influencer</th>
                <th>Platform</th>
                <th>Handle</th>
                <th>Followers</th>
                <th>Niche</th>
                <th>Engagement</th>
                <th>Fit Score</th>
              </tr>
            </thead>
            <tbody>
              {item.influencers?.map((inf, i) => (
                <tr key={i}>
                  <td><strong>{inf.name}</strong></td>
                  <td>{inf.platform}</td>
                  <td>{inf.handle}</td>
                  <td>{inf.followers}</td>
                  <td>{inf.niche}</td>
                  <td>{inf.engagement}</td>
                  <td style={{ fontWeight: 800, color: '#4F46E5' }}>{inf.fit_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }

    if (item.type === 'outreach_message') {
      return (
        <div key={idx} style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '20px', borderRadius: '8px', margin: '20px 0' }}>
          <div style={{ fontSize: '12px', color: '#64748B', marginBottom: '10px' }}>PROPOSED OUTREACH MESSAGE ({item.platform})</div>
          <div style={{ fontWeight: 700, marginBottom: '8px' }}>Subject: {item.subject}</div>
          <div style={{ whiteSpace: 'pre-wrap', fontSize: '11pt', color: '#1E293B', fontStyle: 'italic', borderLeft: '4px solid #4F46E5', paddingLeft: '15px' }}>
            {item.message}
          </div>
        </div>
      )
    }

    return <p key={idx} style={{ marginBottom: '15px', textAlign: 'justify', fontSize: '11pt' }}>{text}</p>
  }

  return (
    <div className="preview-container fade-in">
      <div className="preview-toolbar">
        <div>
          <div style={{ fontWeight: 800, fontSize: '18px' }}>Live Document Preview</div>
          <div style={{ color: '#64748B', fontSize: '12px' }}>Review and export in your preferred format</div>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-outline" onClick={() => handleExport('docx')} disabled={exporting}>
            Export Word
          </button>
          <button className="btn btn-primary" onClick={() => handleExport('pdf')} disabled={exporting}>
            Export PDF
          </button>
        </div>
      </div>

      <div className="document-scroller">
        <div className="document-paper">
          <div className="assignment-cover">
            <h1 className="assignment-title">{generated.title}</h1>
            <div className="assignment-meta">
              <span className="meta-label">Student</span>
              <span className="meta-value">{generated.student_name}</span>
              <span className="meta-label">Course</span>
              <span className="meta-value">{generated.course}</span>
              <span className="meta-label">Assignment</span>
              <span className="meta-value">{generated.assignment_number}</span>
            </div>
          </div>

          {generated.sections?.map((section, sIdx) => (
            <div key={sIdx} className="section-card">
              <h1 style={{ fontSize: '20pt', fontWeight: 800, color: '#4F46E5', marginBottom: '20px', borderBottom: '1px solid #E2E8F0' }}>
                {section.heading}
              </h1>
              {section.content?.map((item, iIdx) => renderContent(item, iIdx))}
            </div>
          ))}

          <div style={{ marginTop: '60px', borderTop: '2px solid #000', paddingTop: '20px', textAlign: 'center', fontWeight: 700 }}>
            End of Assignment - {generated.student_name}
          </div>
        </div>
      </div>
    </div>
  )
}
