import { FileText } from 'lucide-react';

export default function SourceCard({ source }) {
  const displayName = source.document_name
    .replace(/\.pdf$/i, '')
    .replace(/_/g, ' ');

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-lg p-3 text-sm">
      <div className="flex items-start gap-2 mb-1.5">
        <FileText size={13} className="text-sky-400 mt-0.5 flex-shrink-0" />
        <div className="min-w-0">
          <p className="text-sky-300 font-medium leading-tight text-xs truncate" title={source.document_name}>
            {displayName}
          </p>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-slate-400 text-xs">Page {source.page_number}</span>
            {source.similarity != null && (
              <span className="text-slate-500 text-xs">
                · {Math.round(source.similarity * 100)}% match
              </span>
            )}
          </div>
        </div>
      </div>
      <p className="text-slate-400 text-xs leading-relaxed line-clamp-3 pl-5">
        {source.excerpt}
      </p>
    </div>
  );
}
