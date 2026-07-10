import axios from 'axios'

const BACKEND_URL = '' // Same-origin when served via nginx
const baseURL = import.meta.env.VITE_API_BASE_URL || BACKEND_URL || '/'

const apiClient = axios.create({
  baseURL,
  timeout: 120000,
})

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'Request failed'
    console.error('API Error:', msg)
    return Promise.reject(err)
  }
)

export default apiClient

// --- Chat API ---
export async function sendChatMessage(params: {
  provider: string
  model: string
  messages: { role: string; content: string }[]
  conversation_id?: string
  temperature?: number
}) {
  const res = await apiClient.post('/api/chat/', params)
  return res.data
}

export function streamChat(params: {
  provider: string
  model: string
  messages: { role: string; content: string }[]
  conversation_id?: string
  temperature?: number
}): Promise<Response> {
  const base = import.meta.env.VITE_API_BASE_URL || BACKEND_URL || ''
  return fetch(`${base}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
}

export async function getConversations() {
  const res = await apiClient.get('/api/chat/conversations')
  return res.data.conversations
}

export async function getConversation(id: string) {
  const res = await apiClient.get(`/api/chat/conversations/${id}`)
  return res.data
}

// --- Image API ---
export async function textToImage(params: {
  provider: string
  model: string
  prompt: string
  size?: string
}) {
  const res = await apiClient.post('/api/images/text-to-image', params)
  return res.data
}

export async function imageToImage(params: {
  provider: string
  model: string
  prompt: string
  image_file_id: string
  strength?: number
}) {
  const res = await apiClient.post('/api/images/image-to-image', params)
  return res.data
}

// --- Voice API ---
export async function cloneVoice(params: {
  provider: string
  model: string
  text: string
  sample_file_ids: string[]
}) {
  const res = await apiClient.post('/api/voice/clone', params)
  return res.data
}

// --- File API ---
export async function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await apiClient.post('/api/files/upload', formData)
  return res.data
}

// --- Providers API ---
export async function getProviders() {
  const res = await apiClient.get('/api/providers/')
  return res.data
}

export interface ProviderInfo {
  id: string
  name: string
  provider: string
  capabilities: string[]
}
