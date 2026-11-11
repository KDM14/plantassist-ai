import { CheckCircle, AlertCircle, XCircle } from 'lucide-react';

export default function EvidenceBadge({ status, abstained }) {
  if (abstained || status === 'insufficient') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-900/50 text-amber-300 text-xs font-medium border border-amber-700/50">
        <AlertCircle size={11} />
        Not in documents
      </span>
    );
  }
  if (status === 'supported') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-900/50 text-emerald-300 text-xs font-medium border border-emerald-700/50">
        <CheckCircle size={11} />
        Document sourced
      </span>
    );
  }
  if (status === 'error') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-900/50 text-red-300 text-xs font-medium border border-red-700/50">
        <XCircle size={11} />
        Error
      </span>
    );
  }
  return null;
}
