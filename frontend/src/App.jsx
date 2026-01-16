import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'
import ComplianceReport from './components/ComplianceReport'
import ChatHistory from './components/ChatHistory'
import ExportPanel from './components/ExportPanel'
import ParametersModal from './components/ParametersModal'
import TypewriterText from './components/TypewriterText'
import CoverPage from './components/CoverPage'

const API_BASE_URL = '/api'

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [progress, setProgress] = useState(null)
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [chatHistory, setChatHistory] = useState(() => {
    const saved = localStorage.getItem('chatHistory')
    return saved ? JSON.parse(saved) : []
  })
  const [currentChatIndex, setCurrentChatIndex] = useState(null)
  const [showExportPanel, setShowExportPanel] = useState(false)
  const [finalReport, setFinalReport] = useState(null)
  const [showParametersModal, setShowParametersModal] = useState(false)
  const [showChatMenu, setShowChatMenu] = useState(false)
  const [isRenaming, setIsRenaming] = useState(false)
  const [renameValue, setRenameValue] = useState('')
  const [typingMessageIndex, setTypingMessageIndex] = useState(null)
  const messagesEndRef = useRef(null)
  const chatMenuRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
    document.body.classList.toggle('dark-mode', darkMode)
  }, [darkMode])

  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory))
  }, [chatHistory])

  useEffect(() => {
    // Load saved color theme
    const savedColorTheme = localStorage.getItem('colorTheme') || 'blue'
    const colorThemes = {
      blue: { primary: '#93c5fd', primaryDark: '#60a5fa', primaryLight: '#bfdbfe' },
      purple: { primary: '#c4b5fd', primaryDark: '#a78bfa', primaryLight: '#ddd6fe' },
      green: { primary: '#86efac', primaryDark: '#4ade80', primaryLight: '#bbf7d0' },
      orange: { primary: '#fdba74', primaryDark: '#fb923c', primaryLight: '#fed7aa' },
      red: { primary: '#fca5a5', primaryDark: '#f87171', primaryLight: '#fecaca' },
      teal: { primary: '#5eead4', primaryDark: '#2dd4bf', primaryLight: '#99f6e4' }
    }
    const theme = colorThemes[savedColorTheme]
    if (theme) {
      document.documentElement.style.setProperty('--primary-color', theme.primary)
      document.documentElement.style.setProperty('--primary-dark', theme.primaryDark)
      document.documentElement.style.setProperty('--primary-light', theme.primaryLight)
    }

    startNewChat()
  }, [])

  const startNewChat = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/session/new`)
      const newSessionId = response.data.session_id
      setSessionId(newSessionId)

      const initialMessages = []

      setMessages(initialMessages)
      setProgress(null)
      setFinalReport(null)
      setShowExportPanel(false)

      const newChat = {
        id: newSessionId,
        title: 'New Assessment',
        timestamp: new Date().toISOString(),
        messages: initialMessages
      }

      setChatHistory(prev => [newChat, ...prev])
      setCurrentChatIndex(0)
    } catch (error) {
      console.error('Failed to create session:', error)
      setMessages([{
        role: 'error',
        content: 'Failed to initialize the application. Please refresh the page.',
        timestamp: new Date().toISOString()
      }])
    }
  }

  const loadChat = (index) => {
    const chat = chatHistory[index]
    setCurrentChatIndex(index)
    setSessionId(chat.id)
    setMessages(chat.messages)
    setTypingMessageIndex(null)

    const lastMessage = chat.messages[chat.messages.length - 1]
    if (lastMessage && lastMessage.is_done) {
      setFinalReport(lastMessage.content)
    } else {
      setFinalReport(null)
    }

    setShowExportPanel(false)
  }

  const updateCurrentChat = (newMessages) => {
    if (currentChatIndex === null) return

    setChatHistory(prev => {
      const updated = [...prev]
      const currentChat = updated[currentChatIndex]

      // Only update title if it's still "New Assessment" (hasn't been renamed or set)
      const shouldUpdateTitle = currentChat.title === 'New Assessment'

      updated[currentChatIndex] = {
        ...currentChat,
        messages: newMessages,
        title: shouldUpdateTitle ? extractChatTitle(newMessages) : currentChat.title
      }
      return updated
    })
  }

  const extractChatTitle = (msgs) => {
    const userMsg = msgs.find(m => m.role === 'user')
    if (userMsg) {
      return userMsg.content.substring(0, 50) + (userMsg.content.length > 50 ? '...' : '')
    }
    return 'New Assessment'
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || !sessionId || isLoading) return

    const userMessage = inputValue.trim()
    setInputValue('')

    // Reset textarea height immediately
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    const newMessages = [...messages, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }]

    setMessages(newMessages)
    updateCurrentChat(newMessages)
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        content: userMessage,
        session_id: sessionId
      })

      const updatedMessages = [...newMessages, {
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date().toISOString(),
        is_done: response.data.is_done
      }]

      setMessages(updatedMessages)
      updateCurrentChat(updatedMessages)
      setProgress(response.data.progress)
      setTypingMessageIndex(updatedMessages.length - 1)

      if (response.data.is_done) {
        setFinalReport(response.data.message)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessages = [...newMessages, {
        role: 'error',
        content: `Error: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toISOString()
      }]
      setMessages(errorMessages)
      updateCurrentChat(errorMessages)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(e)
    }
  }

  const deleteChat = (index) => {
    const newHistory = chatHistory.filter((_, i) => i !== index)
    setChatHistory(newHistory)

    if (currentChatIndex === index) {
      // If deleting current chat, load the next available chat or start new one
      if (newHistory.length > 0) {
        const newIndex = Math.min(index, newHistory.length - 1)
        setCurrentChatIndex(newIndex)
        const chat = newHistory[newIndex]
        setSessionId(chat.id)
        setMessages(chat.messages)
        const lastMessage = chat.messages[chat.messages.length - 1]
        if (lastMessage && lastMessage.is_done) {
          setFinalReport(lastMessage.content)
        } else {
          setFinalReport(null)
        }
      } else {
        // No chats left, start a new one
        startNewChat()
      }
    } else if (currentChatIndex > index) {
      setCurrentChatIndex(currentChatIndex - 1)
    }
  }

  const cleanMessageContent = (content) => {
    return content
      .replace(/^\[Q\d+\/\d+\]🎯?\s*/gm, '')
      .replace(/^\[Q\d+\/\d+\]\s*/gm, '')
      .replace(/^✅\s*Description received\.?\s*/gim, '')
      .replace(/^Q\d+\s*:\s*/gm, '')
  }

  const handleRenameChat = () => {
    if (currentChatIndex === null) return
    const currentTitle = chatHistory[currentChatIndex].title
    setRenameValue(currentTitle)
    setIsRenaming(true)
    setShowChatMenu(false)
  }

  const confirmRename = () => {
    if (currentChatIndex === null || !renameValue.trim()) return

    setChatHistory(prev => {
      const updated = [...prev]
      updated[currentChatIndex] = {
        ...updated[currentChatIndex],
        title: renameValue.trim()
      }
      return updated
    })

    setIsRenaming(false)
    setRenameValue('')
  }

  const cancelRename = () => {
    setIsRenaming(false)
    setRenameValue('')
  }

  const handleDeleteCurrentChat = () => {
    if (currentChatIndex !== null) {
      setShowChatMenu(false)
      deleteChat(currentChatIndex)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(cleanMessageContent(text)).then(() => {
      // You can add a toast notification here if desired
    })
  }

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (chatMenuRef.current && !chatMenuRef.current.contains(event.target)) {
        setShowChatMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      <ChatHistory
        isOpen={sidebarOpen}
        chatHistory={chatHistory}
        currentChatIndex={currentChatIndex}
        onSelectChat={loadChat}
        onNewChat={startNewChat}
        onDeleteChat={deleteChat}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onOpenParameters={() => setShowParametersModal(true)}
      />

      <ParametersModal
        isOpen={showParametersModal}
        onClose={() => setShowParametersModal(false)}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
      />

      <div className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <main className="chat-container">
          {finalReport && showExportPanel ? (
            <ExportPanel
              report={finalReport}
              onClose={() => setShowExportPanel(false)}
            />
          ) : finalReport && !showExportPanel ? (
            <ComplianceReport
              report={finalReport}
              onExport={() => setShowExportPanel(true)}
            />
          ) : (
            <>
              {messages.filter(m => m.role === 'user').length > 0 && (
                <>
                  {/* Top Bar */}
                  <div className="chat-top-bar">
                    <div className="chat-top-left">
                      {isRenaming ? (
                        <div className="rename-input-container">
                          <input
                            type="text"
                            value={renameValue}
                            onChange={(e) => setRenameValue(e.target.value)}
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') confirmRename()
                              if (e.key === 'Escape') cancelRename()
                            }}
                            className="rename-input"
                            autoFocus
                          />
                          <button onClick={confirmRename} className="rename-confirm-btn">✓</button>
                          <button onClick={cancelRename} className="rename-cancel-btn">✕</button>
                        </div>
                      ) : (
                        <span className="model-name">Regal-IA</span>
                      )}
                    </div>
                    <div className="chat-top-right">
                      <div className="chat-menu-container" ref={chatMenuRef}>
                        <button
                          className="chat-menu-btn"
                          onClick={() => setShowChatMenu(!showChatMenu)}
                        >
                          ⋯
                        </button>
                        {showChatMenu && (
                          <div className="chat-menu-dropdown">
                            <button onClick={handleRenameChat} className="menu-item">
                              ✏️ Rename conversation
                            </button>
                            <button onClick={handleDeleteCurrentChat} className="menu-item delete-item">
                              🗑️ Delete conversation
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </>
              )}

              <div className="messages">
                {progress && messages.filter(m => m.role === 'user').length > 0 && (
                  <div className="progress-badge-fixed">
                    Q{progress.questions_asked + 1}
                  </div>
                )}
                {messages.filter(m => m.role === 'user').length === 0 ? (
                  <CoverPage />
                ) : (
                  <>
                    {messages.map((msg, index) => (
                      <div key={index} className={`message ${msg.role}`}>
                        <div className="message-content">
                          {msg.role === 'assistant' && index === typingMessageIndex ? (
                            <TypewriterText
                              content={cleanMessageContent(msg.content)}
                              speed={10}
                              onComplete={() => setTypingMessageIndex(null)}
                            />
                          ) : (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {cleanMessageContent(msg.content)}
                            </ReactMarkdown>
                          )}
                        </div>
                        {msg.role === 'assistant' && (
                          <button
                            className="copy-message-btn"
                            onClick={() => copyToClipboard(msg.content)}
                            title="Copy message"
                          >
                            <img src="/copy-icon.svg" alt="Copy" className="copy-icon" />
                          </button>
                        )}
                      </div>
                    ))}
                    {isLoading && (
                      <div className="message assistant loading">
                        <div className="message-content">
                          <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="input-wrapper">
                <form onSubmit={sendMessage} className="input-container">
                  <textarea
                    ref={textareaRef}
                    value={inputValue}
                    onChange={(e) => {
                      setInputValue(e.target.value)
                      e.target.style.height = 'auto'
                      if (e.target.value.trim()) {
                        e.target.style.height = e.target.scrollHeight + 'px'
                      } else {
                        e.target.style.height = 'auto'
                      }
                    }}
                    onKeyPress={handleKeyPress}
                    placeholder="Describe your AI system here..."
                    disabled={isLoading || !sessionId}
                    rows={1}
                    className="message-input"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !inputValue.trim() || !sessionId}
                    className="send-button"
                  >
                    ↑
                  </button>
                </form>
                <p className="disclaimer-text">
                  ⚠️ <em>This tool provides preliminary guidance only. Not a substitute for legal advice.</em>
                </p>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
