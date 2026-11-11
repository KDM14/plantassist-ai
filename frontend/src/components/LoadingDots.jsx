export default function LoadingDots() {
  return (
    <div className="flex items-center gap-1.5 py-1">
      {[0, 1, 2].map(i => (
        <div
          key={i}
          className="w-2 h-2 bg-sky-400 rounded-full dot-bounce"
          style={{ animationDelay: `${i * 0.18}s` }}
        />
      ))}
      <span className="ml-2 text-slate-400 text-xs">Searching documents...</span>
    </div>
  );
}
