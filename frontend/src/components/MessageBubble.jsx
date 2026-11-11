import { User, Bot, AlertTriangle } from 'lucide-react';
import EvidenceBadge from './EvidenceBadge';
import SourceCard from './SourceCard';

function renderAnswer(text) {
  // Simple bold rendering
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end gap-2 mb-4">
        <div className="max-w-[80%]">
          <div className="bg-sky-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed">
            {message.content}
          </div>
        </div>
        <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
          <User size={15} className="text-slate-300" />
        </div>
      </div>
    );
  }

  const isAbstained = message.abstained;
  const hasSafetyNote = message.content.includes('⚠️');

  return (
    <div className="flex gap-2 mb-6">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 ${
        isAbstained ? 'bg-amber-900/60' : 'bg-sky-900/60'
      }`}>
        <Bot size={15} className={isAbstained ? 'text-amber-400' : 'text-sky-400'} />
      </div>

      <div className="flex-1 min-w-0">
        {/* Header row */}
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs text-slate-500 font-medium">PlantAssist AI</span>
          <EvidenceBadge status={message.evidence_status} abstained={message.abstained} />
        </div>

        {/* Safety banner */}
        {hasSafetyNote && (
          <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg px-3 py-2 mb-2 flex items-start gap-2">
            <AlertTriangle size={13} className="text-amber-400 mt-0.5 flex-shrink-0" />
            <span className="text-amber-300 text-xs">
              Safety-related answer — always follow approved plant procedures and confirm with your supervisor.
            </span>
          </div>
        )}

        {/* Answer bubble */}
        <div className={`rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed ${
          isAbstained
            ? 'bg-amber-950/40 border border-amber-800/40 text-amber-200'
            : 'bg-slate-800 border border-slate-700/50 text-slate-200'
        }`}>
          <div
            className="whitespace-pre-wrap"
            dangerouslySetInnerHTML={{ __html: renderAnswer(message.content) }}
          />
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && !isAbstained && (
          <div className="mt-2.5">
            <p className="text-xs text-slate-500 uppercase tracking-wide font-medium mb-1.5">
              Sources
            </p>
            <div className="flex flex-col gap-1.5">
              {message.sources.map((src, i) => (
                <SourceCard key={i} source={src} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
