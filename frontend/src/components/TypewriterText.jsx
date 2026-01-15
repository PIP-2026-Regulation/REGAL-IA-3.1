import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function TypewriterText({ content, speed = 10, onComplete }) {
  const [displayedContent, setDisplayedContent] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (currentIndex < content.length) {
      const timeout = setTimeout(() => {
        setDisplayedContent(prev => prev + content[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, speed)

      return () => clearTimeout(timeout)
    } else if (onComplete && currentIndex === content.length) {
      onComplete()
    }
  }, [currentIndex, content, speed, onComplete])

  // Reset when content changes
  useEffect(() => {
    setDisplayedContent('')
    setCurrentIndex(0)
  }, [content])

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {displayedContent}
    </ReactMarkdown>
  )
}

export default TypewriterText
