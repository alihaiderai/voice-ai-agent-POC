import { useState, useEffect } from 'react'
import { Phone, PhoneIncoming, PhoneOutgoing, Clock, DollarSign, TrendingUp, Users, BarChart3 } from 'lucide-react'

const AnalyticsDashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(7)

  useEffect(() => {
    fetchAnalytics()
    const interval = setInterval(fetchAnalytics, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [days])

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/analytics/dashboard?days=${days}`)
      const data = await response.json()
      setStats(data)
      setLoading(false)
    } catch (error) {
      console.error('Analytics fetch error:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="text-center text-gray-500 py-12">
        <BarChart3 className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>No analytics data available</p>
      </div>
    )
  }

  const StatCard = ({ icon: Icon, label, value, color, subtext }) => (
    <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100 hover:shadow-xl transition-all">
      <div className="flex items-center justify-between mb-3">
        <div className={`p-3 rounded-xl ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <span className="text-3xl font-bold text-gray-800">{value}</span>
      </div>
      <p className="text-sm font-medium text-gray-600">{label}</p>
      {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-indigo-600" />
            Analytics Dashboard
          </h2>
          <p className="text-gray-500 mt-1">Call metrics and performance insights</p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-4 py-2 border-2 border-indigo-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          <option value={1}>Last 24 hours</option>
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Phone}
          label="Total Calls"
          value={stats.total_calls}
          color="bg-gradient-to-br from-indigo-500 to-purple-500"
        />
        <StatCard
          icon={PhoneIncoming}
          label="Inbound Calls"
          value={stats.inbound_calls}
          color="bg-gradient-to-br from-emerald-500 to-teal-500"
        />
        <StatCard
          icon={PhoneOutgoing}
          label="Outbound Calls"
          value={stats.outbound_calls}
          color="bg-gradient-to-br from-blue-500 to-cyan-500"
        />
        <StatCard
          icon={Clock}
          label="Avg Duration"
          value={`${stats.avg_duration}s`}
          color="bg-gradient-to-br from-orange-500 to-amber-500"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          icon={DollarSign}
          label="Total Cost"
          value={`$${stats.total_cost}`}
          color="bg-gradient-to-br from-rose-500 to-pink-500"
          subtext={`$${stats.cost_per_call} per call`}
        />
        <StatCard
          icon={TrendingUp}
          label="Success Rate"
          value={`${stats.success_rate}%`}
          color="bg-gradient-to-br from-green-500 to-emerald-500"
        />
        <StatCard
          icon={Users}
          label="Transfer Rate"
          value={`${stats.transfer_rate}%`}
          color="bg-gradient-to-br from-violet-500 to-purple-500"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Calls by Agent */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-600" />
            Calls by Agent
          </h3>
          {Object.keys(stats.calls_by_agent).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(stats.calls_by_agent).map(([agent, count]) => (
                <div key={agent} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-indigo-500"></div>
                    <span className="text-sm font-medium text-gray-700 capitalize">{agent}</span>
                  </div>
                  <span className="text-sm font-bold text-gray-800">{count} calls</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No data available</p>
          )}
        </div>

        {/* Calls by Emotion */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-xl">😊</span>
            Calls by Emotion
          </h3>
          {Object.keys(stats.calls_by_emotion).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(stats.calls_by_emotion).map(([emotion, count]) => {
                const emotionEmojis = {
                  happy: '😊',
                  sad: '😢',
                  angry: '😠',
                  neutral: '😐',
                  excited: '🤩',
                  frustrated: '😤'
                }
                return (
                  <div key={emotion} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{emotionEmojis[emotion] || '😐'}</span>
                      <span className="text-sm font-medium text-gray-700 capitalize">{emotion}</span>
                    </div>
                    <span className="text-sm font-bold text-gray-800">{count} calls</span>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No data available</p>
          )}
        </div>
      </div>

      {/* Top Queries */}
      {stats.top_queries && stats.top_queries.length > 0 && (
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-600" />
            Top Customer Queries
          </h3>
          <div className="space-y-2">
            {stats.top_queries.slice(0, 5).map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <span className="text-sm text-gray-700">{item.query}</span>
                <span className="text-sm font-bold text-indigo-600">{item.count}x</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Daily Call Volume */}
      {stats.daily_calls && stats.daily_calls.length > 0 && (
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-indigo-600" />
            Daily Call Volume
          </h3>
          <div className="space-y-2">
            {stats.daily_calls.map((item, index) => (
              <div key={index} className="flex items-center gap-3">
                <span className="text-xs text-gray-500 w-24">{item.date}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full flex items-center justify-end pr-2"
                    style={{ width: `${(item.count / Math.max(...stats.daily_calls.map(d => d.count))) * 100}%` }}
                  >
                    <span className="text-xs font-bold text-white">{item.count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AnalyticsDashboard
