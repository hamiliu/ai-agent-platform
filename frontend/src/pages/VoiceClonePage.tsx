import { useState, useEffect, useRef } from 'react'
import { Upload, Mic, Loader2, X, Volume2, Download } from 'lucide-react'
import { cloneVoice, uploadFile, getProviders, type ProviderInfo } from '../api/client'

export default function VoiceClonePage() {
  const [text, setText] = useState('')
  const [audioFiles, setAudioFiles] = useState<File[]>([])
  const [audioUrls, setAudioUrls] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [resultUrl, setResultUrl] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [providers, setProviders] = useState<Record<string, ProviderInfo[]>>({})
  const [selectedProvider, setSelectedProvider] = useState('elevenlabs')
  const [selectedModel, setSelectedModel] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    getProviders().then((data) => {
      setProviders(data.voice || {})
      const first = Object.keys(data.voice || {})[0]
      if (first) {
        setSelectedProvider(first)
        const models = data.voice[first]
        if (models?.length) setSelectedModel(models[0].id)
      }
    })
  }, [])

  const handleFilesSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length) {
      setAudioFiles((prev) => [...prev, ...files])
      setAudioUrls((prev) => [
        ...prev,
        ...files.map((f) => URL.createObjectURL(f)),
      ])
      setResultUrl(null)
    }
  }

  const modelList = providers[selectedProvider] || []

  const removeFile = (index: number) => {
    URL.revokeObjectURL(audioUrls[index])
    setAudioFiles((prev) => prev.filter((_, i) => i !== index))
    setAudioUrls((prev) => prev.filter((_, i) => i !== index))
  }

  const handleGenerate = async () => {
    if (!text.trim() || audioFiles.length === 0) return
    setIsGenerating(true)
    setError('')
    setResultUrl(null)

    try {
      // Upload all audio files
      const fileIds: string[] = []
      for (const file of audioFiles) {
        const uploaded = await uploadFile(file)
        fileIds.push(uploaded.file_id)
      }

      // Clone voice
      const res = await cloneVoice({
        provider: selectedProvider,
        model: selectedModel,
        text: text.trim(),
        sample_file_ids: fileIds,
      })
      setResultUrl(res.audio_url)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Voice cloning failed')
    }

    setIsGenerating(false)
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 24px' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a', marginBottom: 24 }}>
        声音克隆
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

      {/* Audio samples upload */}
      <div style={{ marginBottom: 16 }}>
        <label style={{ fontSize: 13, fontWeight: 600, color: '#475569', marginBottom: 8, display: 'block' }}>
          上传声音样本（至少1个，建议2-3个短音频）
        </label>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
          {audioUrls.map((url, i) => (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '6px 12px',
              background: '#f1f5f9',
              borderRadius: 6,
              border: '1px solid #e2e8f0',
            }}>
              <Volume2 size={16} color="#64748b" />
              <span style={{ fontSize: 12, color: '#475569', maxWidth: 100, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {audioFiles[i]?.name}
              </span>
              <button
                onClick={() => removeFile(i)}
                style={{ padding: 2, background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
        <div
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: '2px dashed #cbd5e1',
            borderRadius: 8,
            padding: 24,
            textAlign: 'center',
            cursor: 'pointer',
            color: '#94a3b8',
          }}
        >
          <Upload size={24} style={{ margin: '0 auto 6px', display: 'block' }} />
          <div style={{ fontSize: 13, fontWeight: 500 }}>点击上传音频样本</div>
          <div style={{ fontSize: 11, marginTop: 2 }}>支持 MP3/WAV/OGG</div>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          multiple
          onChange={handleFilesSelect}
          style={{ display: 'none' }}
        />
      </div>

      {/* Text to speak */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="输入你想要克隆声音朗读的文本..."
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
        disabled={!text.trim() || audioFiles.length === 0 || isGenerating}
        style={{
          padding: '10px 24px',
          background: !text.trim() || audioFiles.length === 0 || isGenerating ? '#e2e8f0' : '#ec4899',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          cursor: !text.trim() || audioFiles.length === 0 || isGenerating ? 'not-allowed' : 'pointer',
          fontSize: 14,
          fontWeight: 600,
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
        }}
      >
        {isGenerating ? (
          <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> 克隆中...</>
        ) : (
          <><Mic size={18} /> 克隆声音</>
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
      {resultUrl && (
        <div style={{
          marginTop: 24,
          padding: 20,
          background: '#fff',
          borderRadius: 12,
          border: '1px solid #e2e8f0',
        }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a', marginBottom: 12 }}>
            克隆结果
          </div>
          <audio ref={audioRef} src={resultUrl} controls style={{ width: '100%' }} />
          <div style={{ marginTop: 12 }}>
            <a
              href={resultUrl}
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
              <Download size={16} /> 下载音频
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
