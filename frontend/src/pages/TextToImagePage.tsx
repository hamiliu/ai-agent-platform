import { useState, useEffect } from 'react'
import { Sparkles, Loader2, Download } from 'lucide-react'
import { textToImage, getProviders, type ProviderInfo } from '../api/client'

export default function TextToImagePage() {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState<{ url: string; revised_prompt?: string } | null>(null)
  const [error, setError] = useState('')
  const [providers, setProviders] = useState<Record<string, ProviderInfo[]>>({})
  const [selectedProvider, setSelectedProvider] = useState('stability')
  const [selectedModel, setSelectedModel] = useState('')

  useEffect(() => {
    getProviders().then((data) => {
      const imageProviders = data.image || {}
      setProviders(imageProviders)
      // 优先选 alibaba（阿里通义万相免费额度）
      const preferred = imageProviders['alibaba'] ? 'alibaba'
                     : imageProviders['stability'] ? 'stability'
                     : Object.keys(imageProviders)[0] || ''
      if (preferred) {
        setSelectedProvider(preferred)
        const models = imageProviders[preferred]
        if (models?.length) setSelectedModel(models[0].id)
      }
    })
  }, [])

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    setIsGenerating(true)
    setError('')
    setResult(null)

    try {
      const res = await textToImage({
        provider: selectedProvider,
        model: selectedModel,
        prompt: prompt.trim(),
      })
      setResult(res)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Generation failed')
    }

    setIsGenerating(false)
  }

  const modelList = providers[selectedProvider] || []

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 24px' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a', marginBottom: 24 }}>
        文生图
      </h1>

      {/* Controls */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <select
          value={selectedProvider}
          onChange={(e) => {
            setSelectedProvider(e.target.value)
            const models = providers[e.target.value]
            if (models?.length) setSelectedModel(models[0].id)
          }}
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
            style={{ ...selectStyle, flex: 1 }}
          />
        ) : (
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            style={selectStyle}
          >
            {modelList.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        )}
      </div>

      {/* Input */}
      <div style={{ marginBottom: 16 }}>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="描述你想要生成的图片..."
          rows={4}
          style={{
            width: '100%',
            padding: '12px 16px',
            borderRadius: 8,
            border: '1px solid #e2e8f0',
            fontSize: 14,
            resize: 'vertical',
            outline: 'none',
            fontFamily: 'inherit',
          }}
        />
      </div>

      <button
        onClick={handleGenerate}
        disabled={!prompt.trim() || isGenerating}
        style={{
          padding: '10px 24px',
          background: !prompt.trim() || isGenerating ? '#e2e8f0' : '#8b5cf6',
          color: !prompt.trim() || isGenerating ? '#94a3b8' : '#fff',
          border: 'none',
          borderRadius: 8,
          cursor: !prompt.trim() || isGenerating ? 'not-allowed' : 'pointer',
          fontSize: 14,
          fontWeight: 600,
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
        }}
      >
        {isGenerating ? (
          <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> 生成中...</>
        ) : (
          <><Sparkles size={18} /> 生成图片</>
        )}
      </button>

      {/* Error */}
      {error && (
        <div style={{
          marginTop: 20,
          padding: 12,
          background: '#fef2f2',
          color: '#dc2626',
          borderRadius: 8,
          fontSize: 13,
        }}>
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{
          marginTop: 24,
          background: '#fff',
          borderRadius: 12,
          border: '1px solid #e2e8f0',
          overflow: 'hidden',
        }}>
          <img
            src={result.url}
            alt="Generated"
            style={{ width: '100%', display: 'block' }}
          />
          <div style={{ padding: 16 }}>
            {result.revised_prompt && (
              <p style={{ fontSize: 13, color: '#64748b', marginBottom: 12 }}>
                {result.revised_prompt}
              </p>
            )}
            <a
              href={result.url}
              download
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 16px',
                background: '#f1f5f9',
                color: '#1e293b',
                borderRadius: 6,
                textDecoration: 'none',
                fontSize: 13,
                fontWeight: 500,
              }}
            >
              <Download size={16} /> 下载图片
            </a>
          </div>
        </div>
      )}
    </div>
  )
}

const selectStyle: React.CSSProperties = {
  padding: '6px 12px',
  borderRadius: 6,
  border: '1px solid #e2e8f0',
  fontSize: 13,
  background: '#fff',
  outline: 'none',
  cursor: 'pointer',
}
