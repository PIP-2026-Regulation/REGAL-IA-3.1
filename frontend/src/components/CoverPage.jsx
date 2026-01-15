import React from 'react'
import './CoverPage.css'

function CoverPage() {
  const guidelines = [
    {
      icon: '🎯',
      title: 'Primary purpose and functionality',
      description: 'What does your AI system do?'
    },
    {
      icon: '👥',
      title: 'Target users and deployment context',
      description: 'Who will use it and where?'
    },
    {
      icon: '📊',
      title: 'Data processed',
      description: 'What type of data does it handle?'
    },
    {
      icon: '🤖',
      title: 'AI/ML techniques used',
      description: 'What technologies power your system?'
    },
    {
      icon: '⚙️',
      title: 'Decision-making autonomy level',
      description: 'How autonomous are the decisions?'
    },
    {
      icon: '🔒',
      title: 'Safeguards and human oversight',
      description: 'What controls are in place?'
    }
  ]

  return (
    <div className="cover-page">
      <div className="cover-content">
        <div className="cover-header">
          <div className="cover-logo">
            <img src="/logo.png" alt="Regal-IA" className="cover-logo-image" />
          </div>
          <h1 className="cover-title">Welcome to Regal-IA</h1>
        </div>
        <p className="cover-subtitle">
          Please describe your AI system in detail. Include:
        </p>

        <div className="guidelines-grid">
          {guidelines.map((item, index) => (
            <div key={index} className="guideline-card">
              <div className="guideline-icon">{item.icon}</div>
              <div className="guideline-content">
                <h3 className="guideline-title">{item.title}</h3>
                <p className="guideline-description">{item.description}</p>
              </div>
            </div>
          ))}
        </div>

        <p className="cover-footer">
          Be specific to enable accurate EU AI Act compliance assessment
        </p>
      </div>
    </div>
  )
}

export default CoverPage
