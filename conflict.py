with open('src/App.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith('function ConflictBanner('):
        start_idx = i
    if line.startswith('export default function App()'):
        end_idx = i - 1
        break

if start_idx != -1 and end_idx != -1:
    new_banner = '''function ConflictBanner({ result, windowMinutes, onRemoveFlexible, onStartEarlier, onExtendEnd, hasFlexible }) {
  const mustExcludes = result.excluded.filter(e => e.dest.priority === "must");
  
  const totalNeeded = result.estimatedTotalNeeded;
  const deficit = totalNeeded - windowMinutes;
  
  return (
    <div className="rounded-md mb-4" style={{ border: `1px solid ${COLOR.warn}`, backgroundColor: COLOR.warnSoft }}>
      <div className="flex items-start gap-2.5 px-3 py-3 border-b border-orange-200/50">
        <AlertTriangle size={18} color={COLOR.warn} className="mt-0.5 shrink-0" />
        <div className="flex-1">
          <div className="text-sm font-semibold" style={{ color: COLOR.warn }}>
            {mustExcludes.length > 0 
              ? `Must Visit Conflict: ${mustExcludes.map(e => e.dest.name).join(", ")} cannot fit.`
              : `Schedule Alert: Some requested destinations cannot fit.`
            }
          </div>
          <div className="text-xs mt-1" style={{ color: "#9A5012", lineHeight: 1.5 }}>
            Your available window is {formatDuration(windowMinutes)}, but scheduling these stops requires at least {formatDuration(totalNeeded)} (a {formatDuration(deficit)} shortage).
          </div>
        </div>
      </div>
      
      <div className="px-3 py-3 bg-orange-50/30">
        <div className="text-[10px] font-bold tracking-wider mb-2 text-orange-800/70">RECOVERY ACTIONS</div>
        <div className="flex flex-col gap-2">
          
          <div className="flex items-center justify-between p-2 rounded border border-orange-200 bg-white">
            <div className="flex-1 pr-4">
              <div className="text-sm font-medium text-gray-900">Remove a Flexible stop</div>
              <div className="text-xs text-gray-500 mt-0.5">
                {hasFlexible 
                  ? "Skip a flexible destination to free up time for your higher-priority stops." 
                  : "No Flexible destinations are available to remove. Change a destination's priority."}
              </div>
            </div>
            <button 
              onClick={onRemoveFlexible} 
              disabled={!hasFlexible}
              className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap"
              style={{ backgroundColor: hasFlexible ? COLOR.warn : "#E5E7EB", color: hasFlexible ? "#fff" : "#9CA3AF" }}
            >
              Skip flexible
            </button>
          </div>

          <div className="flex items-center justify-between p-2 rounded border border-orange-200 bg-white">
            <div className="flex-1 pr-4">
              <div className="text-sm font-medium text-gray-900">Expand your time window</div>
              <div className="text-xs text-gray-500 mt-0.5">
                Add more time to your day. (Ensure destinations are open during the new hours).
              </div>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={onStartEarlier} 
                className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap bg-orange-50 text-orange-700 hover:bg-orange-100 transition-colors"
              >
                Start earlier
              </button>
              <button 
                onClick={onExtendEnd} 
                className="text-xs font-medium px-3 py-1.5 rounded whitespace-nowrap bg-orange-50 text-orange-700 hover:bg-orange-100 transition-colors"
              >
                End later
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

'''
    
    with open('src/App.jsx', 'w', encoding='utf-8') as f:
        f.writelines(lines[:start_idx])
        f.write(new_banner)
        f.writelines(lines[end_idx:])
