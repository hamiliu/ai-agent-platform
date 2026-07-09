import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import TextToImagePage from './pages/TextToImagePage'
import ImageToImagePage from './pages/ImageToImagePage'
import VoiceClonePage from './pages/VoiceClonePage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:conversationId" element={<ChatPage />} />
        <Route path="/text-to-image" element={<TextToImagePage />} />
        <Route path="/image-to-image" element={<ImageToImagePage />} />
        <Route path="/voice-clone" element={<VoiceClonePage />} />
      </Route>
    </Routes>
  )
}
