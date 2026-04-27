import { Brain, Headphones, Calendar, BarChart3 } from 'lucide-react'

const AgentIndicator = ({ agent, emotion }) => {
  const agentConfig = {
    orchestrator: {
      icon: Brain,
      label: 'Orchestrator',
      color: 'bg-gray-500',
      emoji: '🤖'
    },
    support: {
      icon: Headphones,
      label: 'Support',
      color: 'bg-blue-500',
      emoji: '🎧'
    },
    booking: {
      icon: Calendar,
      label: 'Booking',
      color: 'bg-green-500',
      emoji: '📅'
    },
    general: {
      icon: Brain,
      label: 'General',
      color: 'bg-purple-500',
      emoji: '💬'
    },
    analytics: {
      icon: BarChart3,
      label: 'Analytics',
      color: 'bg-orange-500',
      emoji: '📊'
    }
  }

  const emotionEmojis = {
    happy: '😊',
    sad: '😢',
    angry: '😠',
    neutral: '😐',
    excited: '🤩',
    frustrated: '😤',
    confused: '😕',
    satisfied: '😌'
  }

  const config = agentConfig[agent] || agentConfig.general
  const Icon = config.icon
  const emotionEmoji = emotionEmojis[emotion] || emotionEmojis.neutral

  return (
    <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
      <span className="text-lg">{emotionEmoji}</span>
      <div className={`w-2 h-2 rounded-full ${config.color} animate-pulse`} />
      <Icon className="w-4 h-4" />
      <span className="text-sm font-medium">{config.label}</span>
    </div>
  )
}

export default AgentIndicator
