import { Wrench, Shield, ClipboardCheck, Calendar } from 'lucide-react';

const ACTIONS = [
  {
    icon: Wrench,
    title: 'Machine Troubleshooting',
    description: 'Alarms & fault resolution',
    color: 'text-orange-400',
    border: 'border-orange-800/40',
    bg: 'bg-orange-950/40 hover:bg-orange-950/70',
    question: 'The TX-200 CNC is showing alarm AL-104. What does it mean and what should the operator do?',
  },
  {
    icon: Shield,
    title: 'Safety Procedures',
    description: 'LOTO & isolation steps',
    color: 'text-red-400',
    border: 'border-red-800/40',
    bg: 'bg-red-950/40 hover:bg-red-950/70',
    question: 'What is the lockout tagout procedure before performing maintenance on a machine?',
  },
  {
    icon: ClipboardCheck,
    title: 'Quality Inspection',
    description: 'Incoming material checks',
    color: 'text-emerald-400',
    border: 'border-emerald-800/40',
    bg: 'bg-emerald-950/40 hover:bg-emerald-950/70',
    question: 'What is the outer diameter tolerance for the BH-220 bearing housing?',
  },
  {
    icon: Calendar,
    title: 'Preventive Maintenance',
    description: 'PM schedules & checks',
    color: 'text-sky-400',
    border: 'border-sky-800/40',
    bg: 'bg-sky-950/40 hover:bg-sky-950/70',
    question: 'How often should spindle runout be checked on the TX-200, and who is responsible?',
  },
];

export default function QuickActions({ onSelect }) {
  return (
    <div className="mb-6">
      <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-3">
        Quick Actions
      </p>
      <div className="grid grid-cols-2 gap-3">
        {ACTIONS.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.title}
              onClick={() => onSelect(action.question)}
              className={`touch-target flex flex-col items-start gap-2 p-4 rounded-xl border transition-colors text-left ${action.bg} ${action.border}`}
              aria-label={`Quick action: ${action.title}`}
            >
              <Icon size={20} className={action.color} />
              <div>
                <p className="text-sm font-semibold text-slate-200 leading-tight">{action.title}</p>
                <p className="text-xs text-slate-400 mt-0.5">{action.description}</p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
