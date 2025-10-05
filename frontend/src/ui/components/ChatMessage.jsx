import React from 'react'

export default function ChatMessage({ role, content, ts, accent }) {
  const isUser = role === 'user'
  return (
    <div className={`w-full mb-3 flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex items-start gap-2 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm ${isUser ? 'bg-orange-100 text-orange-700' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'}`}>
          {isUser ? '🧑' : '🤖'}
        </div>
        <div className={`rounded-2xl px-4 py-2 shadow-sm ${isUser ? 'text-white' : 'bg-white border border-slate-200 text-slate-900 dark:bg-slate-900 dark:border-slate-700 dark:text-slate-100'}`} style={isUser ? { backgroundColor: accent } : {}}>
          <div className="whitespace-pre-wrap leading-relaxed">{content}</div>
          <div className="text-[10px] mt-1 opacity-70">{new Date(ts).toLocaleTimeString()}</div>
        </div>
      </div>
    </div>
  )
}


