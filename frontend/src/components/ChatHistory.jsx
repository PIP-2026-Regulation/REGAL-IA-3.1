import React from 'react'
import './ChatHistory.css'

function ChatHistory({ isOpen, chatHistory, currentChatIndex, onSelectChat, onNewChat, onDeleteChat, onToggle, onOpenParameters }) {
  const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <>
      <div className={`chat-history-sidebar ${isOpen ? 'open' : 'collapsed'}`}>
        {isOpen && (
          <div className="sidebar-header">
            <div className="sidebar-logo">
              <img src="/logo.png" alt="RegalIA Logo" className="logo-image" />
            </div>
            <button onClick={onToggle} className="toggle-btn-open" title="Hide sidebar">
              ☰
            </button>
          </div>
        )}

        {!isOpen && (
          <div className="sidebar-collapsed-header">
            <button onClick={onToggle} className="toggle-btn-collapsed" title="Show sidebar">
              ☰
            </button>
          </div>
        )}

        {isOpen && (
          <div className="sidebar-content">
            <button onClick={onNewChat} className="new-chat-btn-expanded">
              <span className="btn-icon">➕</span>
              <span className="btn-text">New chat</span>
            </button>

            <div className="chat-list">
              {chatHistory.length === 0 ? (
                <div className="empty-state">
                  <p>No chat history yet</p>
                  <p className="empty-hint">Start a new assessment!</p>
                </div>
              ) : (
                chatHistory.map((chat, index) => (
                  <div
                    key={chat.id}
                    className={`chat-item ${currentChatIndex === index ? 'active' : ''}`}
                    onClick={() => onSelectChat(index)}
                  >
                    <div className="chat-item-content">
                      <div className="chat-title">{chat.title}</div>
                      <div className="chat-meta">
                        <span className="chat-date">{formatDate(chat.timestamp)}</span>
                        <span className="chat-messages">{chat.messages.length} msgs</span>
                      </div>
                    </div>
                    <button
                      className="delete-chat-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        onDeleteChat(index)
                      }}
                      title="Delete chat"
                    >
                      🗑️
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {!isOpen && (
          <div className="sidebar-collapsed-content">
            <button onClick={onNewChat} className="icon-btn new-chat-icon" title="New Assessment">
              ➕
            </button>
          </div>
        )}

        <div className="sidebar-footer">
          {isOpen ? (
            <button onClick={onOpenParameters} className="parameters-btn-expanded">
              <span className="btn-icon">⚙️</span>
              <span className="btn-text">Parameters</span>
            </button>
          ) : (
            <button onClick={onOpenParameters} className="icon-btn parameters-icon" title="Parameters">
              ⚙️
            </button>
          )}
        </div>
      </div>
    </>
  )
}

export default ChatHistory
