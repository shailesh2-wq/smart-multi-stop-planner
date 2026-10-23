import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_row = '''function DestinationRow({ dest, orderNumber, isExcluded, userExcluded, onEdit, onRemove, onRestore, isHovered, isSelected, onHover, onSelect }) {
  const meta = PRIORITY_META[dest.priority];
  const rowRef = useRef(null);
  
  // Three states: User Excluded (skipped), Optimizer Excluded (unable to schedule), Scheduled
  const numberFill = userExcluded ? "#E5E7EB" : isExcluded ? "#98A2B3" : meta.dot;

  useEffect(() => {
    if (isSelected && rowRef.current) {
      rowRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [isSelected]);

  return (
    <div
      ref={rowRef}
      className="flex items-stretch gap-3 py-2.5 -mx-3.5 px-3.5 rounded-md transition-colors"
      style={{ backgroundColor: isSelected ? COLOR.accentSoft : isHovered ? "#F5F7FA" : "transparent", cursor: "pointer", opacity: userExcluded ? 0.5 : isExcluded ? 0.8 : 1 }}
      onMouseEnter={() => onHover && onHover(dest.id)}
      onMouseLeave={() => onHover && onHover(null)}
      onClick={() => onSelect && onSelect(dest.id)}
    >
      <span className="h-6 w-6 rounded-full shrink-0 flex items-center justify-center text-[11px] font-bold mt-0.5" style={{ backgroundColor: numberFill, color: userExcluded ? "#9CA3AF" : "#fff" }}>
        {userExcluded ? "-" : orderNumber}
      </span>
      <div className="flex-1 min-w-0 flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span style={{ color: COLOR.muted }}><DestinationGlyph name={dest.name} /></span>
            <span className="text-sm" style={{ color: COLOR.ink, fontWeight: dest.priority === "must" ? 700 : 600, textDecoration: userExcluded ? "line-through" : "none" }}>
              {dest.name}
            </span>
            {userExcluded ? (
              <span className="text-[11px] font-medium px-1.5 py-0.5 rounded" style={{ color: "#6B7280", border: `1px solid #D1D5DB` }}>Skipped by you</span>
            ) : isExcluded ? (
              <span className="text-[11px] font-medium px-1.5 py-0.5 rounded" style={{ color: COLOR.flexible, border: `1px solid ${COLOR.lineStrong}` }}>Unable to schedule</span>
            ) : (
              <PriorityTag priority={dest.priority} compact />
            )}
          </div>
          <div className="flex items-center gap-2.5 mt-1.5" style={{ color: COLOR.muted, fontSize: 11 }}>
            {dest.preferredArrival && (
              <span className="inline-flex items-center gap-1 font-medium" style={{ color: COLOR.accent }}>
                Preferred: {dest.preferredArrival}
              </span>
            )}
            {!dest.preferredArrival && (
              <span className="inline-flex items-center gap-1"><Clock size={11} />{dest.openTime}?"{dest.closeTime}</span>
            )}
            {dest.closeTime && dest.preferredArrival && (
              <span className="inline-flex items-center gap-1"><Clock size={11} />Closes: {dest.closeTime}</span>
            )}
            <span className="inline-flex items-center gap-1"><Timer size={11} />{formatDuration(dest.duration)}</span>
          </div>
        </div>
        <div className="flex items-center gap-0.5 shrink-0 opacity-60 hover:opacity-100 transition-opacity">
          {userExcluded ? (
            <button onClick={(e) => { e.stopPropagation(); onRestore(); }} className="text-xs font-medium px-2 py-1 rounded bg-white text-gray-700 border border-gray-300 shadow-sm hover:bg-gray-50">
              Restore
            </button>
          ) : (
            <>
              <button onClick={(e) => { e.stopPropagation(); onEdit(dest.id); }} className="p-1.5 rounded hover:bg-gray-100" style={{ color: COLOR.muted }} aria-label={`Edit ${dest.name}`}>
                <Pencil size={13} />
              </button>
              <button onClick={(e) => { e.stopPropagation(); onRemove(dest.id); }} className="p-1.5 rounded hover:bg-gray-100" style={{ color: COLOR.muted }} aria-label={`Remove ${dest.name}`}>
                <Trash2 size={13} />
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}'''

code = re.sub(r'function DestinationRow\(\{.*?\} \);\n\}', new_row, code, flags=re.DOTALL)
with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
