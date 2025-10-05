import React, { useEffect } from 'react'

export default function Sidebar({ conversations, currentId, onNew, onSelect, onDelete, model, setModel }) {
  const [models, setModels] = React.useState([])

  useEffect(() => {
    fetch('/api/models').then(r => r.json()).then(d => setModels(d.models || [])).catch(() => setModels([]))
  }, [])

  return (
    <aside className="hidden md:flex w-72 flex-col border-r border-slate-200 bg-white/90 backdrop-blur h-screen sticky top-0 dark:bg-slate-900/70 dark:border-slate-800">
      <div className="p-3 border-b border-slate-200 flex items-center justify-between dark:border-slate-800">
        <div className="font-semibold">Conversations</div>
        <button className="px-2 py-1 text-sm rounded border dark:border-slate-700" onClick={onNew}>New</button>
      </div>
      <div className="p-3 border-b border-slate-200 dark:border-slate-800">
        <label className="text-xs text-slate-500 dark:text-slate-400">Model</label>
        <select className="mt-1 w-full rounded border p-2 dark:bg-slate-900 dark:border-slate-700" value={model} onChange={e => setModel(e.target.value)}>
          {models.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>
      <div className="flex-1 overflow-auto p-2">
        {conversations.length === 0 && (
          <div className="text-sm text-slate-500 p-2 dark:text-slate-400">No conversations yet</div>
        )}
        {conversations.map(c => (
          <button key={c.id} className={`w-full text-left px-3 py-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800 border ${currentId===c.id? 'border-slate-300 dark:border-slate-700' : 'border-transparent'} mb-2`} onClick={() => onSelect(c.id)}>
            <div className="text-sm font-medium truncate">{c.title || 'New chat'}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">{new Date(c.ts).toLocaleString()}</div>
            <div className="mt-1">
              <button className="text-xs text-rose-600" onClick={(e)=>{e.stopPropagation(); onDelete(c.id)}}>Delete</button>
            </div>
          </button>
        ))}
      </div>
    </aside>
  )
}


