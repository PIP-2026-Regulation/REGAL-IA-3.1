import React, { useState, useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './ComplianceReport.css'

function ComplianceReport({ report, onExport }) {
  const [activeSection, setActiveSection] = useState('overview')

  // Parse the report into sections
  const sections = useMemo(() => {
    const parsed = {
      title: '',
      riskClassification: '',
      violations: '',
      articles: '',
      penalties: '',
      roadmap: '',
      recommendations: ''
    }

    // Extract title
    const titleMatch = report.match(/📊\s*FINAL\s+COMPLIANCE\s+ASSESSMENT\s*\n+([^\n]+)/i)
    if (titleMatch) {
      parsed.title = titleMatch[1].trim()
    }

    // Extract sections by headers
    const riskMatch = report.match(/1\.\s*RISK\s+CLASSIFICATION\s*([\s\S]*?)(?=2\.|$)/i)
    if (riskMatch) parsed.riskClassification = riskMatch[1].trim()

    const violationsMatch = report.match(/2\.\s*IDENTIFIED\s+VIOLATIONS\s*&\s*CONCERNS\s*([\s\S]*?)(?=3\.|$)/i)
    if (violationsMatch) parsed.violations = violationsMatch[1].trim()

    const articlesMatch = report.match(/3\.\s*APPLICABLE\s+ARTICLES\s*([\s\S]*?)(?=4\.|$)/i)
    if (articlesMatch) parsed.articles = articlesMatch[1].trim()

    const penaltiesMatch = report.match(/4\.\s*PENALTIES\s*(?:\(Article\s+99\))?\s*([\s\S]*?)(?=5\.|$)/i)
    if (penaltiesMatch) parsed.penalties = penaltiesMatch[1].trim()

    const roadmapMatch = report.match(/5\.\s*COMPLIANCE\s+ROADMAP\s*([\s\S]*?)(?=6\.|$)/i)
    if (roadmapMatch) parsed.roadmap = roadmapMatch[1].trim()

    const recsMatch = report.match(/6\.\s*TECHNICAL\s+RECOMMENDATIONS\s*([\s\S]*?)(?=Note:|Type 'reset'|$)/i)
    if (recsMatch) parsed.recommendations = recsMatch[1].trim()

    return parsed
  }, [report])

  const getRiskLevel = () => {
    const match = sections.riskClassification.match(/Risk\s+Level:\s*\*{0,2}\s*([A-Z\-\s]+?)(?:\s*\*{0,2}\s*(?:Confidence|$))/i)
    return match ? match[1].trim().toUpperCase() : 'UNKNOWN'
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'PROHIBITED': return '#dc3545'
      case 'HIGH-RISK': return '#ff6b6b'
      case 'LIMITED': return '#ffc107'
      case 'MINIMAL': return '#28a745'
      default: return '#6c757d'
    }
  }

  const riskLevel = getRiskLevel()

  return (
    <div className="compliance-report">
      <div className="report-navigation">
        <button
          className={activeSection === 'overview' ? 'active' : ''}
          onClick={() => setActiveSection('overview')}
        >
          Overview
        </button>
        <button
          className={activeSection === 'risk' ? 'active' : ''}
          onClick={() => setActiveSection('risk')}
        >
          Risk Classification
        </button>
        <button
          className={activeSection === 'violations' ? 'active' : ''}
          onClick={() => setActiveSection('violations')}
        >
          Violations & Concerns
        </button>
        <button
          className={activeSection === 'articles' ? 'active' : ''}
          onClick={() => setActiveSection('articles')}
        >
          Applicable Articles
        </button>
        <button
          className={activeSection === 'penalties' ? 'active' : ''}
          onClick={() => setActiveSection('penalties')}
        >
          Penalties
        </button>
        <button
          className={activeSection === 'roadmap' ? 'active' : ''}
          onClick={() => setActiveSection('roadmap')}
        >
          Compliance Roadmap
        </button>
        <button
          className={activeSection === 'recommendations' ? 'active' : ''}
          onClick={() => setActiveSection('recommendations')}
        >
          Recommendations
        </button>
      </div>

      <div className="report-content">
        <button
          onClick={onExport}
          className="floating-export-btn"
        >
          📥 Export
        </button>
        {activeSection === 'overview' && (
          <div className="section-content">
            <h2>Assessment Overview</h2>
            <div className="overview-grid">
              <div className="overview-card">
                <h3>🎯 Risk Level</h3>
                <div className="overview-value" style={{ color: getRiskColor(riskLevel) }}>
                  <strong>{riskLevel}</strong>
                </div>
              </div>
              <div className="overview-card">
                <h3>⚠️ Violations</h3>
                <div className="overview-value">
                  {(sections.violations.match(/Article\s+\d+/g) || []).length}
                </div>
              </div>
              <div className="overview-card">
                <h3>📋 Applicable Articles</h3>
                <div className="overview-value">
                  {(sections.articles.match(/Article\s+\d+/g) || []).length}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeSection === 'risk' && (
          <div className="section-content">
            <h2>1. Risk Classification</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {sections.riskClassification
                .replace(/\*\*\s*Risk Level:\*\*/g, '\n\n- **Risk Level:**')
                .replace(/\*\*\s*Confidence:\*\*/g, '\n\n- **Confidence:**')
                .replace(/\*\*\s*Rationale:\*\*/g, '\n\n- **Rationale:**')}
            </ReactMarkdown>
          </div>
        )}

        {activeSection === 'violations' && (
          <div className="section-content">
            <h2>2. Identified Violations & Concerns</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {sections.violations}
            </ReactMarkdown>
          </div>
        )}

        {activeSection === 'articles' && (
          <div className="section-content">
            <h2>3. Applicable Articles</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {sections.articles}
            </ReactMarkdown>
          </div>
        )}

        {activeSection === 'penalties' && (
          <div className="section-content">
            <h2>4. Penalties (Article 99)</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {sections.penalties}
            </ReactMarkdown>
          </div>
        )}

        {activeSection === 'roadmap' && (
          <div className="section-content">
            <h2>5. Compliance Roadmap</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {sections.roadmap}
            </ReactMarkdown>
          </div>
        )}

        {activeSection === 'recommendations' && (
          <div className="section-content">
            <h2>6. Technical Recommendations</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {sections.recommendations}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}

export default ComplianceReport
