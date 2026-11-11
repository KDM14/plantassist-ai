import { useState, useEffect } from 'react';
import { Factory, Wifi, WifiOff, PlusCircle, FileText } from 'lucide-react';
import { getHealth } from '../utils/api';

export default function Header({ onNewChat }) {
  const [health, setHealth] = useState(null);
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const check = async () => {
      try {
        const h = await getHealth();
        setHealth(h);
        setOnline(true);
      } catch {
        setOnline(false);
      }
    };
    check();
    const id = setInterval(check, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-sky-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <Factory size={19} className="text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white leading-tight">PlantAssist AI</h1>
          <p className="text-xs text-slate-500">Manufacturing Knowledge Copilot</p>
        </div>
      </div>

      {/* Status + Action */}
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            {online
              ? <Wifi size={13} className="text-emerald-400" />
              : <WifiOff size={13} className="text-red-400" />}
            <span className={online ? 'text-emerald-400' : 'text-red-400'}>
              {online ? 'Online' : 'Offline'}
            </span>
          </div>
          {health && (
            <div className="flex items-center gap-1.5">
              <FileText size={13} className="text-slate-500" />
              <span className="text-slate-400">{health.indexed_documents} docs</span>
            </div>
          )}
        </div>

        <button
          onClick={onNewChat}
          className="touch-target flex items-center gap-1.5 px-3 py-2 bg-sky-700 hover:bg-sky-600 active:bg-sky-800 text-white text-sm rounded-lg transition-colors font-medium"
        >
          <PlusCircle size={15} />
          <span className="hidden sm:inline">New Chat</span>
        </button>
      </div>
    </header>
  );
}
