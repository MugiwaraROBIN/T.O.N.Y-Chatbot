import React, { useState } from 'react'

export default function Header({ accent, onClear, dark, setDark }) {
  return (
    <header className={`sticky top-0 z-10 border-b bg-white/70 backdrop-blur text-slate-900 dark:bg-slate-950/80 dark:text-white dark:border-slate-800`}>
      <div className="mx-auto max-w-3xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg" style={{ background: `conic-gradient(from 180deg at 50% 50%, ${accent}, #ffedd5, white)` }} />
          <div className="font-semibold text-lg" style={{ color: accent }}>T.O.N.Y Chatbot</div>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1 rounded-md border border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800" onClick={onClear}>Clear</button>
          <button className="px-3 py-1 rounded-md border border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800" onClick={() => setDark(v => !v)}>{dark ? '🌞' : '🌙'}</button>
        </div>
      </div>
    </header>
  )
}


