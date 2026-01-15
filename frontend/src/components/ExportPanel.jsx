import React, { useState } from 'react'
import './ExportPanel.css'

function ExportPanel({ report, onClose }) {
  const [selectedFormat, setSelectedFormat] = useState('pdf')
  const [isExporting, setIsExporting] = useState(false)

  const exportFormats = [
    { id: 'pdf', name: 'PDF Document', icon: '📄', description: 'Professional PDF report' },
    { id: 'docx', name: 'Word Document', icon: '📝', description: 'Editable DOCX file' },
    { id: 'md', name: 'Markdown', icon: '📋', description: 'Plain markdown text' },
    { id: 'html', name: 'HTML Page', icon: '🌐', description: 'Standalone HTML file' },
    { id: 'json', name: 'JSON Data', icon: '💾', description: 'Structured JSON data' },
  ]

  const handleExport = () => {
    setIsExporting(true)

    // Simulate export process
    setTimeout(() => {
      switch (selectedFormat) {
        case 'pdf':
          exportAsPDF()
          break
        case 'docx':
          exportAsDOCX()
          break
        case 'md':
          exportAsMarkdown()
          break
        case 'html':
          exportAsHTML()
          break
        case 'json':
          exportAsJSON()
          break
      }
      setIsExporting(false)
    }, 1000)
  }

  const exportAsPDF = () => {
    // TODO: Implement PDF export using jsPDF or similar
    alert('PDF export will be implemented. For now, please use Print to PDF from your browser.')
    window.print()
  }

  const exportAsDOCX = () => {
    // TODO: Implement DOCX export using docx library
    alert('DOCX export coming soon!')
  }

  const exportAsMarkdown = () => {
    const blob = new Blob([report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `eu-ai-act-compliance-report-${Date.now()}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const exportAsHTML = () => {
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EU AI Act Compliance Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }
        h1, h2, h3 { color: #003399; }
        pre { background: #f5f5f5; padding: 1rem; border-radius: 4px; }
    </style>
</head>
<body>
    <pre>${report}</pre>
</body>
</html>
    `
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `eu-ai-act-compliance-report-${Date.now()}.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  const exportAsJSON = () => {
    const jsonData = {
      timestamp: new Date().toISOString(),
      report: report,
      metadata: {
        tool: 'EU AI Act Compliance Advisor',
        version: '1.0.0'
      }
    }
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `eu-ai-act-compliance-report-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="export-panel">
      <div className="export-content">
        <p className="export-description">
          Choose your preferred export format for the compliance assessment report.
        </p>

        <div className="format-grid">
          {exportFormats.map(format => (
            <div
              key={format.id}
              className={`format-card ${selectedFormat === format.id ? 'selected' : ''}`}
              onClick={() => setSelectedFormat(format.id)}
            >
              <div className="format-icon">{format.icon}</div>
              <div className="format-info">
                <div className="format-name">{format.name}</div>
                <div className="format-description">{format.description}</div>
              </div>
              <div className="format-check">
                {selectedFormat === format.id && '✓'}
              </div>
            </div>
          ))}
        </div>

        <div className="export-actions">
          <button onClick={onClose} className="cancel-btn">
            Cancel
          </button>
          <button
            onClick={handleExport}
            className="export-confirm-btn"
            disabled={isExporting}
          >
            {isExporting ? 'Exporting...' : `Export as ${exportFormats.find(f => f.id === selectedFormat)?.name}`}
          </button>
        </div>

        <div className="export-note">
          <strong>Note:</strong> The exported report contains your AI system's compliance assessment.
          Keep this document for your records and share with your legal team.
        </div>
      </div>
    </div>
  )
}

export default ExportPanel
