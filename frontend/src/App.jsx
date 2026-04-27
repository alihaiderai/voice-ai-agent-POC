import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Send, Trash2, Activity, Phone, PhoneCall, BarChart3 } from 'lucide-react'
import VoiceVisualizer from './components/VoiceVisualizer'
import TranscriptDisplay from './components/TranscriptDisplay'
import AgentIndicator from './components/AgentIndicator'
import AnalyticsDashboard from './components/AnalyticsDashboard'

function App() {
  const [isConnected, setIsConnected] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [messages, setMessages] = useState([])
  const [currentAgent, setCurrentAgent] = useState('orchestrator')
  const [status, setStatus] = useState('Disconnected')
  const [textInput, setTextInput] = useState('')
  const [showPhoneModal, setShowPhoneModal] = useState(false)
  const [phoneNumber, setPhoneNumber] = useState('+92')
  const [phoneMessage, setPhoneMessage] = useState('Hello! This is a call from our AI voice agent.')
  const [callStatus, setCallStatus] = useState('')
  const [currentEmotion, setCurrentEmotion] = useState('neutral')
  const [activeTab, setActiveTab] = useState('chat') // 'chat' or 'analytics'
  
  const wsRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)

  useEffect(() => {
    connectWebSocket()
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/voice')
    
    ws.onopen = () => {
      setIsConnected(true)
      setStatus('Connected')
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      handleWebSocketMessage(message)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setStatus('Error')
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      setStatus('Disconnected')
      console.log('WebSocket disconnected')
    }
    
    wsRef.current = ws
  }

  const handleWebSocketMessage = (message) => {
    const { type, data, agent, emotion } = message
    
    switch (type) {
      case 'status':
        setStatus(data)
        break
      
      case 'transcript':
        setMessages(prev => [...prev, {
          role: 'user',
          content: data,
          timestamp: new Date()
        }])
        break
      
      case 'response':
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data,
          agent: agent || 'general',
          emotion: emotion || 'neutral',
          timestamp: new Date()
        }])
        setCurrentAgent(agent || 'general')
        setCurrentEmotion(emotion || 'neutral')
        break
      
      case 'audio':
        playAudio(data)
        break
      
      case 'error':
        setStatus(`Error: ${data}`)
        break
    }
  }

  const playAudio = async (base64Audio) => {
    try {
      const audioData = atob(base64Audio)
      const arrayBuffer = new ArrayBuffer(audioData.length)
      const view = new Uint8Array(arrayBuffer)
      for (let i = 0; i < audioData.length; i++) {
        view[i] = audioData.charCodeAt(i)
      }
      
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
      const source = audioContext.createBufferSource()
      source.buffer = audioBuffer
      source.connect(audioContext.destination)
      source.start(0)
    } catch (error) {
      console.error('Audio playback error:', error)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Setup audio context for visualization
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
      analyserRef.current = audioContextRef.current.createAnalyser()
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)
      
      // Setup media recorder
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const reader = new FileReader()
        reader.onloadend = () => {
          const base64Audio = reader.result.split(',')[1]
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
              type: 'audio',
              data: base64Audio
            }))
          }
        }
        reader.readAsDataURL(audioBlob)
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorderRef.current.start()
      setIsRecording(true)
      setStatus('Listening...')
    } catch (error) {
      console.error('Recording error:', error)
      setStatus('Microphone access denied')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setStatus('Processing...')
    }
  }

  const sendTextMessage = () => {
    if (textInput.trim() && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'text',
        data: textInput
      }))
      setMessages(prev => [...prev, {
        role: 'user',
        content: textInput,
        timestamp: new Date()
      }])
      setTextInput('')
      setStatus('Processing...')
    }
  }

  const clearConversation = () => {
    setMessages([])
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'control',
        action: 'end_session'
      }))
    }
  }

  const makePhoneCall = async () => {
    if (!phoneNumber || phoneNumber === '+92') {
      setCallStatus('Please enter a valid phone number')
      return
    }

    setCallStatus('Calling...')
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/phone/outbound?to_number=${encodeURIComponent(phoneNumber)}&message=${encodeURIComponent(phoneMessage)}`,
        { method: 'POST' }
      )
      
      const data = await response.json()
      
      if (data.success) {
        setCallStatus(`✅ Call initiated! Call SID: ${data.call_sid}`)
        setTimeout(() => setShowPhoneModal(false), 3000)
      } else {
        setCallStatus(`❌ Error: ${data.error}`)
      }
    } catch (error) {
      setCallStatus(`❌ Error: ${error.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-5xl bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-white/20">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-8 text-white relative overflow-hidden">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                <span className="text-5xl">🤖</span>
                Voice AI Agent
              </h1>
              <p className="text-indigo-100 text-sm">Web Voice Chat + Phone Calls (Inbound/Outbound)</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowPhoneModal(true)}
                className="flex items-center gap-2 px-5 py-3 bg-white text-indigo-600 rounded-2xl hover:bg-indigo-50 transition-all font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Phone className="w-5 h-5" />
                Make Call
              </button>
              <AgentIndicator agent={currentAgent} emotion={currentEmotion} />
              <div className={`flex items-center gap-2 px-4 py-3 rounded-2xl shadow-lg ${
                isConnected ? 'bg-emerald-500' : 'bg-rose-500'
              }`}>
                <Activity className="w-4 h-4" />
                <span className="text-sm font-medium">{status}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex flex-col h-[650px]">
          {/* Transcript Area */}
          <div className="flex-1 overflow-y-auto p-8 bg-gradient-to-b from-gray-50 to-white">
            <TranscriptDisplay messages={messages} />
          </div>

          {/* Voice Visualizer */}
          {isRecording && (
            <div className="px-8 py-6 bg-gradient-to-r from-indigo-50 to-purple-50 border-t border-indigo-100">
              <VoiceVisualizer analyser={analyserRef.current} />
            </div>
          )}

          {/* Controls */}
          <div className="p-8 bg-white/50 backdrop-blur-sm border-t border-gray-200">
            <div className="flex gap-3 mb-5">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
                placeholder="Type your message or use voice..."
                className="flex-1 px-5 py-4 border-2 border-indigo-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent bg-white/80 backdrop-blur-sm"
                disabled={!isConnected}
              />
              <button
                onClick={sendTextMessage}
                disabled={!isConnected || !textInput.trim()}
                className="px-7 py-4 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-2xl hover:from-indigo-600 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>

            <div className="flex gap-4 justify-center">
              <button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={!isConnected}
                className={`flex items-center gap-3 px-10 py-5 rounded-2xl font-semibold transition-all shadow-xl hover:shadow-2xl transform hover:scale-105 ${
                  isRecording
                    ? 'bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-600 hover:to-pink-600 text-white pulse-ring'
                    : 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 text-white'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isRecording ? (
                  <>
                    <MicOff className="w-6 h-6" />
                    Stop Recording
                  </>
                ) : (
                  <>
                    <Mic className="w-6 h-6" />
                    Start Voice Conversation
                  </>
                )}
              </button>

              <button
                onClick={clearConversation}
                disabled={!isConnected || messages.length === 0}
                className="flex items-center gap-2 px-7 py-5 bg-gradient-to-r from-gray-200 to-gray-300 hover:from-gray-300 hover:to-gray-400 text-gray-700 rounded-2xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Trash2 className="w-5 h-5" />
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 px-8 py-4 text-center border-t border-indigo-100">
          <p className="text-sm text-gray-600 flex items-center justify-center gap-4">
            <span className="flex items-center gap-2">
              <span className="text-lg">📞</span>
              <span className="font-semibold text-indigo-600">Inbound: +1 (978) 570-8547</span>
            </span>
            <span className="mx-2">•</span>
            <a 
              href="analytics.html" 
              target="_blank"
              className="flex items-center gap-2 text-indigo-600 hover:text-indigo-800 font-semibold hover:underline"
            >
              <BarChart3 className="w-4 h-4" />
              View Analytics Dashboard
            </a>
            <span className="mx-2">•</span>
            <span className="text-gray-500">Powered by GPT-4o, Whisper & Twilio</span>
          </p>
        </div>
      </div>

      {/* Phone Call Modal */}
      {showPhoneModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-10 max-w-lg w-full mx-4 shadow-2xl transform transition-all">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent flex items-center gap-3">
                <span className="text-4xl">📞</span>
                Make Outbound Call
              </h2>
              <button
                onClick={() => setShowPhoneModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-all"
              >
                ✕
              </button>
            </div>

            <div className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+923070614159"
                  className="w-full px-5 py-4 border-2 border-indigo-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-2">Format: +92XXXXXXXXXX</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Message to Speak
                </label>
                <textarea
                  value={phoneMessage}
                  onChange={(e) => setPhoneMessage(e.target.value)}
                  rows="4"
                  className="w-full px-5 py-4 border-2 border-indigo-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent resize-none"
                />
              </div>

              {callStatus && (
                <div className={`p-4 rounded-2xl text-sm font-medium ${
                  callStatus.includes('✅') 
                    ? 'bg-emerald-100 text-emerald-800 border-2 border-emerald-200' 
                    : 'bg-rose-100 text-rose-800 border-2 border-rose-200'
                }`}>
                  {callStatus}
                </div>
              )}

              <button
                onClick={makePhoneCall}
                className="w-full flex items-center justify-center gap-3 px-8 py-5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white rounded-2xl hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 font-bold text-lg transition-all shadow-xl hover:shadow-2xl transform hover:scale-105"
              >
                <PhoneCall className="w-6 h-6" />
                Make Call
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
