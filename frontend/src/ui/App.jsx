import React, { useEffect, useMemo, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ChatMessage from '../ui/components/ChatMessage.jsx'
import ChatInput from '../ui/components/ChatInput.jsx'
import Header from '../ui/components/Header.jsx'
import Sidebar from '../ui/components/Sidebar.jsx'

const ACCENT = '#FFA500'

export default function App() {
  const [dark, setDark] = useState(false)
  const [model, setModel] = useState('gemini-1.5-flash-8b')
  const [conversations, setConversations] = useState(() => {
    const saved = localStorage.getItem('gemini-conversations')
    return saved ? JSON.parse(saved) : []
  })
  const [currentId, setCurrentId] = useState(() => conversations[0]?.id || null)
  const [messages, setMessages] = useState(() => getMessages(conversations, currentId))
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    localStorage.setItem('gemini-conversations', JSON.stringify(conversations))
  }, [conversations])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, loading])

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return
    const userMsg = { id: crypto.randomUUID(), role: 'user', content: text, ts: Date.now() }
    const botMsg = { id: crypto.randomUUID(), role: 'assistant', content: '', ts: Date.now() }
    const nextMessages = [...messages, userMsg, botMsg]
    setMessages(nextMessages)
    upsertConversation(setConversations, currentId, model, nextMessages)
    setLoading(true)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, model })
      })
      const data = await res.json()
      const resolved = (data && data.response) ? data.response : 'Error contacting server.'
      const updated = nextMessages.map(m => m.id === botMsg.id ? { ...m, content: resolved } : m)
      setMessages(updated)
      upsertConversation(setConversations, currentId, model, updated)
    } catch (e) {
      const updated = nextMessages.map(m => m.id === botMsg.id ? { ...m, content: 'Error contacting server.' } : m)
      setMessages(updated)
      upsertConversation(setConversations, currentId, model, updated)
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    upsertConversation(setConversations, currentId, model, [])
  }

  const newChat = () => {
    const id = crypto.randomUUID()
    const conv = { id, ts: Date.now(), title: 'New chat', model, messages: [] }
    const next = [conv, ...conversations]
    setConversations(next)
    setCurrentId(id)
    setMessages([])
  }

  const selectChat = (id) => {
    setCurrentId(id)
    const conv = conversations.find(c => c.id === id)
    setMessages(conv ? conv.messages : [])
  }

  const deleteChat = (id) => {
    const next = conversations.filter(c => c.id !== id)
    setConversations(next)
    if (currentId === id) {
      const newest = next[0]
      setCurrentId(newest?.id || null)
      setMessages(newest?.messages || [])
    }
  }

  return (
    <div className={`${dark ? 'dark' : ''}`}>
      <div className="min-h-screen bg-gradient-to-b from-white to-orange-50 text-slate-900 dark:from-slate-950 dark:to-slate-900 dark:text-slate-100">
        <Header accent={ACCENT} onClear={clearChat} dark={dark} setDark={setDark} />
      <div className="flex">
        <Sidebar conversations={conversations} currentId={currentId} onNew={newChat} onSelect={selectChat} onDelete={deleteChat} model={model} setModel={setModel} />
        <main className="flex-1 mx-auto max-w-3xl p-4 pb-28" ref={scrollRef}>
        <AnimatePresence>
          {messages.map(m => (
            <motion.div key={m.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
              <ChatMessage role={m.role} content={m.content} ts={m.ts} accent={ACCENT} />
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <div className="mt-2 text-sm text-slate-500">Assistant is typing…</div>
        )}
        </main>
      </div>
        <ChatInput accent={ACCENT} onSend={sendMessage} disabled={loading} />
      </div>
    </div>
  )
}

function getMessages(conversations, id){
  const conv = conversations.find(c => c.id === id)
  return conv ? conv.messages : []
}

function upsertConversation(setConversations, id, model, messages){
  setConversations(prev => {
    // create if not exists
    if (!id) {
      const newId = crypto.randomUUID()
      const title = inferTitle(messages)
      return [{ id: newId, ts: Date.now(), title, model, messages }, ...prev]
    }
    return prev.map(c => c.id === id ? { ...c, model, messages, title: inferTitle(messages) } : c)
  })
}

function inferTitle(messages){
  const firstUser = messages.find(m => m.role === 'user')
  if (!firstUser) return 'New chat'
  const t = firstUser.content.trim()
  return t.length > 40 ? t.slice(0,40) + '…' : t
}


