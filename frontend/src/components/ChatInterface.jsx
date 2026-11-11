import { useState, useRef, useEffect } from 'react';
import { Send, Trash2 } from 'lucide-react';
import MessageBubble from './MessageBubble';
import LoadingDots from './LoadingDots';
import QuickActions from './QuickActions';

export default function ChatInterface({ messages, isLoading, onSend, onClear }) {
  const [input, setInput] = useState('');
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = () => {
    const q = input.trim();
    if (!q || isLoading) return;
    onSend(q);
    setInput('');
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickAction = (question) => {
    onSend(question);
    setInput('');
  };

  const isEmpty = messages.length === 0;
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="flex flex-col h-full">
      {/* Scrollable messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="max-w-2xl mx-auto">
          {isEmpty ? (
            <>
              <div className="mb-8 pt-2">
                <h2 className="text-2xl font-bold text-white mb-1">{greeting}, Supervisor.</h2>
                <p className="text-slate-400 text-sm">
                  How can I help you with your operations today?
                </p>
              </div>
              <QuickActions onSelect={handleQuickAction} />
              <p className="text-xs text-slate-600 text-center mt-6">
                Answers are based solely on indexed plant documents. Always verify safety procedures with your supervisor.
              </p>
            </>
          ) : (
            <>
              {messages.map(msg => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isLoading && (
                <div className="flex gap-2 mb-4">
                  <div className="w-8 h-8 bg-sky-900/60 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sky-400 text-xs font-bold">AI</span>
                  </div>
                  <div className="bg-slate-800 border border-slate-700/50 rounded-2xl rounded-tl-sm px-4 py-3">
                    <LoadingDots />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </>
          )}
        </div>
      </div>

      {/* Input bar */}
      <div className="border-t border-slate-800 bg-slate-900/80 px-4 py-3">
        <div className="max-w-2xl mx-auto">
          {!isEmpty && (
            <div className="flex justify-end mb-2">
              <button
                onClick={onClear}
                className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1 transition-colors"
              >
                <Trash2 size={11} />
                Clear conversation
              </button>
            </div>
          )}

          <div className="flex gap-2 items-end">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about procedures, maintenance, safety..."
              rows={1}
              disabled={isLoading}
              className="flex-1 bg-slate-800 border border-slate-700 text-slate-100 placeholder-slate-500 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:border-sky-500 transition-colors leading-relaxed disabled:opacity-50"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              aria-label="Send"
              className="touch-target w-12 h-12 bg-sky-600 hover:bg-sky-500 active:bg-sky-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center transition-colors flex-shrink-0"
            >
              <Send size={17} />
            </button>
          </div>

          <p className="text-xs text-slate-600 mt-2 text-center">
            PlantAssist AI · Kaveri Precision Components · Answers from indexed SOPs only
          </p>
        </div>
      </div>
    </div>
  );
}
