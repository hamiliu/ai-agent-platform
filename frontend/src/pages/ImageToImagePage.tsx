import { useState, useEffect, useRef } from 'react'
import { Upload, Sparkles, Loader2, Download, X } from 'lucide-react'
import { imageToImage, uploadFile, getProviders, type ProviderInfo } from '../api/client'

export default function ImageToImagePage() {
  const [prompt, setPrompt] = useState('')
  const [sourceImage, setSourceImage] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState<{ url: string; revised_prompt?: string } | null>(null)
  const [error, setError] = useState('')
  const [providers, setProviders] = useState<Record<string, ProviderInfo[]>>({})
  const [selectedProvider, setSelectedProvider] = useState('stability')
  const [selectedModel, setSelectedModel] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    getProviders().then((data) => {
      const imageProviders = data.image || {}
      setProviders(imageProviders)
      // 优先选 stability
      const preferred = imageProviders['stability'] ? 'stability'
                     : Object.keys(imageProviders)[0] || ''
      if (preferred) {
        setSelectedProvider(preferred)
        const models = imageProviders[preferred]
        if (models?.length) setSelectedModel(models[0].id)
      }
    })
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSourceImage(file)
      setPreviewUrl(URL.createObjectURL(file))
      setResult(null)
    }
  }

  const handleRemoveImage = () => {
    setSourceImage(null)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
  }

  const handleGenerate = async () => {
    if (!prompt.trim() || !sourceImage) return
    setIsGenerating(true)
    setError('')
    setResult(null)

    try {
      // Upload source image first
      const uploaded = await uploadFile(sourceImage)

      // Then generate
      const res = await imageToImage({
        provider: selectedProvider,
        model: selectedModel,
        prompt: prompt.trim(),
        image_file_id: uploaded.file_id,
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
        图生图
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

      {/* Source image upload */}
      <div style={{ marginBottom: 16 }}>
        {previewUrl ? (
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <img
              src={previewUrl}
              alt="Source"
              style={{ maxHeight: 240, borderRadius: 8, border: '1px solid #e2e8f0' }}
            />
            <button
              onClick={handleRemoveImage}
              style={{
                position: 'absolute',
                top: 8,
                right: 8,
                padding: 4,
                background: 'rgba(0,0,0,0.6)',
                color: '#fff',
                border: 'none',
                borderRadius: '50%',
                cursor: 'pointer',
                display: 'flex',
              }}
            >
              <X size={16} />
            </button>
          </div>
        ) : (
          <div
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: '2px dashed #cbd5e1',
              borderRadius: 8,
              padding: 40,
              textAlign: 'center',
              cursor: 'pointer',
              color: '#94a3b8',
              transition: 'border-color 0.15s',
            }}
          >
            <Upload size={32} style={{ margin: '0 auto 8px', display: 'block' }} />
            <div style={{ fontSize: 14, fontWeight: 500 }}>点击上传源图片</div>
            <div style={{ fontSize: 12, marginTop: 4 }}>支持 JPG/PNG/WebP</div>
          </div>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {/* Prompt */}
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="描述你想要的变换效果..."
        rows={3}
        style={{
          width: '100%',
          padding: '12px 16px',
          borderRadius: 8,
          border: '1px solid #e2e8f0',
          fontSize: 14,
          resize: 'vertical',
          outline: 'none',
          fontFamily: 'inherit',
          marginBottom: 16,
        }}
      />

      <button
        onClick={handleGenerate}
        disabled={!prompt.trim() || !sourceImage || isGenerating}
        style={{
          padding: '10px 24px',
          background: !prompt.trim() || !sourceImage || isGenerating ? '#e2e8f0' : '#8b5cf6',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          cursor: !prompt.trim() || !sourceImage || isGenerating ? 'not-allowed' : 'pointer',
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
          <img src={result.url} alt="Result" style={{ width: '100%', display: 'block' }} />
          <div style={{ padding: 16 }}>
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
