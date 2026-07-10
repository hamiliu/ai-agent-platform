import { useState, useRef, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { Send, Loader2, Plus } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import {
  streamChat,
  sendChatMessage,
  getConversations,
  getConversation,
  getProviders,
  type ProviderInfo,
} from '../api/client'

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export default function ChatPage() {
  const { conversationId } = useParams()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [providers, setProviders] = useState<Record<string, ProviderInfo[]>>({})
  const [selectedProvider, setSelectedProvider] = useState('openai')
  const [selectedModel, setSelectedModel] = useState('')
  const [conversations, setConversations] = useState<any[]>([])
  const [currentConvId, setCurrentConvId] = useState<string | undefined>(conversationId)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    getProviders().then((data) => {
      setProviders(data.chat || {})
      const first = Object.keys(data.chat || {})[0]
      if (first) {
        setSelectedProvider(first)
        const models = data.chat[first]
        if (models?.length) setSelectedModel(models[0].id)
      }
    })
    loadConversations()
  }, [])

  useEffect(() => {
    if (conversationId) {
      setCurrentConvId(conversationId)
      getConversation(conversationId).then((data) => {
        setMessages(data.messages || [])
      })
    }
  }, [conversationId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadConversations = async () => {
    try {
      const list = await getConversations()
      setConversations(list)
    } catch {}
  }

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider)
    const models = providers[provider]
    if (models?.length) setSelectedModel(models[0].id)
  }

  const handleNewChat = () => {
    setMessages([])
    setCurrentConvId(undefined)
  }

  const handleSend = useCallback(async () => {
    if (!input.trim() || isStreaming) return

    const userMsg: Message = { role: 'user', content: input.trim() }
    const updatedMessages = [...messages, userMsg]
    setMessages(updatedMessages)
    setInput('')
    setIsStreaming(true)

    // Try streaming first
    try {
      const response = await streamChat({
        provider: selectedProvider,
        model: selectedModel,
        messages: updatedMessages.map((m) => ({ role: m.role, content: m.content })),
        conversation_id: currentConvId,
      })

      if (!response.ok) {
        throw new Error('Stream failed')
      }

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let assistantContent = ''
      let buffer = ''

      setMessages((prev) => [...prev, { role: 'assistant', content: '' }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue
            try {
              const parsed = JSON.parse(data)
              if (parsed.token) {
                assistantContent += parsed.token
                setMessages((prev) => {
                  const copy = [...prev]
                  copy[copy.length - 1] = { role: 'assistant', content: assistantContent }
                  return copy
                })
              }
            } catch {}
          }
        }
      }
    } catch {
      // Fallback to non-streaming
      try {
        const result = await sendChatMessage({
          provider: selectedProvider,
          model: selectedModel,
          messages: updatedMessages.map((m) => ({ role: m.role, content: m.content })),
          conversation_id: currentConvId,
        })
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: result.content },
        ])
        if (result.conversation_id) {
          setCurrentConvId(result.conversation_id)
        }
      } catch (err: any) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `**Error**: ${err.response?.data?.detail || err.message}`,
          },
        ])
      }
    }

    setIsStreaming(false)
    loadConversations()
  }, [input, messages, selectedProvider, selectedModel, currentConvId, isStreaming])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const modelList = providers[selectedProvider] || []

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      {/* Conversation sidebar */}
      <div style={{
        width: 280,
        borderRight: '1px solid #e2e8f0',
        background: '#fff',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
      }}>
        <div style={{ padding: 16, borderBottom: '1px solid #e2e8f0' }}>
          <button
            onClick={handleNewChat}
            style={{
              width: '100%',
              padding: '10px 16px',
              background: '#3b82f6',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              cursor: 'pointer',
              fontSize: 14,
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              justifyContent: 'center',
            }}
          >
            <Plus size={18} />
            新对话
          </button>
        </div>
        <div style={{ flex: 1, overflow: 'auto', padding: 8 }}>
          {conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => {
                setCurrentConvId(conv.id)
                getConversation(conv.id).then((data) => {
                  setMessages(data.messages || [])
                })
              }}
              style={{
                padding: '10px 12px',
                borderRadius: 6,
                cursor: 'pointer',
                background: conv.id === currentConvId ? '#eff6ff' : 'transparent',
                marginBottom: 2,
                fontSize: 13,
              }}
            >
              <div style={{ fontWeight: 500, color: '#1e293b', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {conv.title}
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
                {conv.provider} · {conv.message_count} 条消息
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Toolbar */}
        <div style={{
          padding: '10px 20px',
          borderBottom: '1px solid #e2e8f0',
          background: '#fff',
          display: 'flex',
          gap: 12,
          alignItems: 'center',
          flexShrink: 0,
        }}>
          <select
            value={selectedProvider}
            onChange={(e) => handleProviderChange(e.target.value)}
            style={selectStyle}
          >
            {Object.keys(providers).map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          {selectedModel === '__custom__' ? (
            <input
              type="text"
              value=""
              onChange={(e) => setSelectedModel(e.target.value)}
              placeholder="输入模型名或接入点 ID"
              style={{
                ...selectStyle,
                flex: 1,
                minWidth: 200,
              }}
            />
          ) : (
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              style={{
                ...selectStyle,
                maxWidth: 200,
              }}
            >
              {modelList.map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          )}
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflow: 'auto', padding: '20px 0' }}>
          {messages.length === 0 && (
            <div style={{
              textAlign: 'center',
              paddingTop: 120,
              color: '#94a3b8',
            }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>💬</div>
              <div style={{ fontSize: 16, fontWeight: 600, color: '#64748b' }}>开始一段新对话</div>
              <div style={{ fontSize: 13, marginTop: 4 }}>在下方输入你的问题</div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              padding: '6px 20px',
            }}>
              <div style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: 12,
                background: msg.role === 'user' ? '#3b82f6' : '#fff',
                color: msg.role === 'user' ? '#fff' : '#1e293b',
                border: msg.role === 'user' ? 'none' : '1px solid #e2e8f0',
                lineHeight: 1.6,
                fontSize: 14,
              }}>
                {msg.role === 'assistant' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div style={{
          padding: '16px 20px',
          borderTop: '1px solid #e2e8f0',
          background: '#fff',
        }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入消息... (Shift+Enter 换行)"
              rows={2}
              style={{
                flex: 1,
                padding: '10px 14px',
                borderRadius: 8,
                border: '1px solid #e2e8f0',
                fontSize: 14,
                resize: 'none',
                outline: 'none',
                fontFamily: 'inherit',
              }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isStreaming}
              style={{
                padding: '10px 16px',
                background: !input.trim() || isStreaming ? '#e2e8f0' : '#3b82f6',
                color: !input.trim() || isStreaming ? '#94a3b8' : '#fff',
                border: 'none',
                borderRadius: 8,
                cursor: !input.trim() || isStreaming ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                fontSize: 14,
                fontWeight: 600,
              }}
            >
              {isStreaming ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={18} />}
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const selectStyle: React.CSSProperties = {
  padding: '6px 12px',
  borderRadius: 6,
  border: '1px solid #e2e8f0',
  fontSize: 13,
  background: '#f8fafc',
  outline: 'none',
  cursor: 'pointer',
}
