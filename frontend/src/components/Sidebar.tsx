import { NavLink } from 'react-router-dom'
import { Bot, ImageIcon, Shuffle, Mic, MessageSquare } from 'lucide-react'

const navItems = [
  { to: '/chat', label: 'AI 对话', icon: MessageSquare },
  { to: '/text-to-image', label: '文生图', icon: ImageIcon },
  { to: '/image-to-image', label: '图生图', icon: Shuffle },
  { to: '/voice-clone', label: '声音克隆', icon: Mic },
]

export default function Sidebar() {
  return (
    <aside style={{
      width: 260,
      background: '#0f172a',
      color: '#cbd5e1',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{
        padding: '20px 20px',
        borderBottom: '1px solid #1e293b',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Bot size={28} color="#3b82f6" />
          <span style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9' }}>
            AI Agent
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 8px' }}>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/chat'}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '10px 14px',
              borderRadius: 8,
              textDecoration: 'none',
              color: isActive ? '#f1f5f9' : '#94a3b8',
              background: isActive ? '#1e293b' : 'transparent',
              fontSize: 14,
              fontWeight: isActive ? 600 : 400,
              marginBottom: 2,
              transition: 'all 0.15s',
            })}
          >
            <item.icon size={20} />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div style={{
        padding: '12px 20px',
        borderTop: '1px solid #1e293b',
        fontSize: 12,
        color: '#475569',
      }}>
        AI Agent Platform v1.0
      </div>
    </aside>
  )
}
