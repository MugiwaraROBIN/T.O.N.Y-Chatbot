import React, { useState } from 'react'

export default function ChatInput({ onSend, disabled, accent }) {
  const [text, setText] = useState('')
  const handleSend = () => {
    const t = text.trim()
    if (!t) return
    onSend?.(t)
    setText('')
  }
  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }
  return (
    <div className="fixed bottom-0 left-0 right-0">
      <div className="mx-auto max-w-3xl p-4">
        <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-white/90 backdrop-blur p-2 shadow-lg dark:bg-slate-900/80 dark:border-slate-700">
          <textarea className="flex-1 resize-none rounded-xl p-2 outline-none focus:ring-2 dark:bg-slate-900" style={{ boxShadow: 'inset 0 0 0 1px rgba(0,0,0,0.03)' }} rows={2} placeholder="Type your message..." value={text} onChange={e => setText(e.target.value)} onKeyDown={onKeyDown} />
          <button className={`rounded-xl px-4 py-2 text-white flex items-center gap-2 ${disabled ? 'opacity-60' : ''}`} style={{ backgroundColor: accent }} disabled={disabled || !text.trim()} onClick={handleSend}>
            <span>Send</span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4"><path d="M2.25 12l18-9-4.5 9 4.5 9-18-9z"/></svg>
          </button>
        </div>
      </div>
    </div>
  )
}


