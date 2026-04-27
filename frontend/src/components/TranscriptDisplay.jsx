import { useEffect, useRef } from 'react'
import { User, Bot, Sparkles } from 'lucide-react'

const TranscriptDisplay = ({ messages }) => {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const getAgentColor = (agent) => {
    const colors = {
      support: 'bg-blue-100 text-blue-800',
      booking: 'bg-green-100 text-green-800',
      general: 'bg-purple-100 text-purple-800',
      analytics: 'bg-orange-100 text-orange-800',
      orchestrator: 'bg-gray-100 text-gray-800'
    }
    return colors[agent] || colors.general
  }

  const getEmotionEmoji = (emotion) => {
    const emojis = {
      happy: '😊',
      sad: '😔',
      angry: '😠',
      frustrated: '😤',
      confused: '😕',
      excited: '🎉',
      neutral: '😐'
    }
    return emojis[emotion] || '😐'
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400">
        <Sparkles className="w-16 h-16 mb-4" />
        <p className="text-lg font-medium">Start a conversation</p>
        <p className="text-sm mt-2">Click the microphone or type a message</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex gap-3 ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          {message.role === 'assistant' && (
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
            </div>
          )}

          <div
            className={`max-w-[70%] rounded-2xl px-4 py-3 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200'
            }`}
          >
            {message.role === 'assistant' && message.agent && (
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${getAgentColor(message.agent)}`}>
                  {message.agent.charAt(0).toUpperCase() + message.agent.slice(1)} Agent
                </span>
                {message.emotion && (
                  <span className="text-sm">{getEmotionEmoji(message.emotion)}</span>
                )}
              </div>
            )}
            <p className={`text-sm ${message.role === 'user' ? 'text-white' : 'text-gray-800'}`}>
              {message.content}
            </p>
            <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-400'}`}>
              {message.timestamp.toLocaleTimeString()}
            </p>
          </div>

          {message.role === 'user' && (
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-600 to-gray-800 flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
            </div>
          )}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  )
}

export default TranscriptDisplay
