import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update DestinationRow to support changing priority and rendering Restore button
old_dest_row = '''function DestinationRow({ dest, orderNumber, isExcluded, onEdit, onRemove, isHovered, isSelected, onHover, onSelect }) {
  const meta = PRIORITY_META[dest.priority];
  const rowRef = useRef(null);
  const numberFill = isExcluded ? "#98A2B3" : meta.dot;

  useEffect(() => {
    if (isSelected && rowRef.current) {
      rowRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [isSelected]);

  return (
    <div
      ref={rowRef}
      className="flex items-stretch gap-3 py-2.5 -mx-3.5 px-3.5 rounded-md transition-colors"
      style={{ backgroundColor: isSelected ? COLOR.accentSoft : isHovered ? "#F5F7FA" : "transparent", cursor: "pointer", opacity: isExcluded ? 0.72 : 1 }}
      onMouseEnter={() => onHover && onHover(dest.id)}
      onMouseLeave={() => onHover && onHover(null)}
      onClick={() => onSelect && onSelect(dest.id)}
    >
      <span className="h-6 w-6 rounded-full shrink-0 flex items-center justify-center text-[11px] font-bold text-white mt-0.5" style={{ backgroundColor: numberFill }}>
        {orderNumber}
      </span>
      <div className="flex-1 min-w-0 flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-sm truncate" style={{ color: COLOR.ink, textDecoration: isExcluded ? "line-through" : "none" }}>{dest.name}</h3>
            {!isExcluded && (
              <span className="text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-sm" style={{ backgroundColor: meta.bg, color: meta.text }}>
                {meta.label}
              </span>
            )}
            {isExcluded && (
              <span className="text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-sm bg-gray-100 text-gray-500">
                Unable to schedule
              </span>
            )}
          </div>
          <div className="text-xs mt-1 truncate" style={{ color: COLOR.inkSoft }}>
            {dest.duration} min • {dest.openTime} - {dest.closeTime}
          </div>
          {dest.preferredArrival && (
            <div className="text-xs mt-0.5 truncate" style={{ color: COLOR.muted }}>
              Preferred: {dest.preferredArrival}
            </div>
          )}
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity" style={{ opacity: isHovered || isSelected ? 1 : 0 }}>
          <button onClick={(e) => { e.stopPropagation(); onEdit(dest.id); }} className="p-1.5 rounded-md hover:bg-white/60 transition-colors" style={{ color: COLOR.inkSoft }}><Pencil size={14} /></button>
          <button onClick={(e) => { e.stopPropagation(); onRemove(dest.id); }} className="p-1.5 rounded-md hover:bg-red-50 hover:text-red-600 transition-colors" style={{ color: COLOR.muted }}><Trash2 size={14} /></button>
        </div>
      </div>
    </div>
  );
}'''

new_dest_row = '''function DestinationRow({ dest, orderNumber, isExcluded, isUserExcluded, onEdit, onRemove, onRestore, onChangePriority, isHovered, isSelected, onHover, onSelect }) {
  const meta = PRIORITY_META[dest.priority];
  const rowRef = useRef(null);
  const numberFill = (isExcluded || isUserExcluded) ? "#98A2B3" : meta.dot;

  useEffect(() => {
    if (isSelected && rowRef.current) {
      rowRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [isSelected]);

  return (
    <div
      ref={rowRef}
      className="flex items-stretch gap-3 py-2.5 -mx-3.5 px-3.5 rounded-md transition-colors"
      style={{ backgroundColor: isSelected ? COLOR.accentSoft : isHovered ? "#F5F7FA" : "transparent", cursor: "pointer", opacity: (isExcluded || isUserExcluded) ? 0.72 : 1 }}
      onMouseEnter={() => onHover && onHover(dest.id)}
      onMouseLeave={() => onHover && onHover(null)}
      onClick={() => onSelect && onSelect(dest.id)}
    >
      <span className="h-6 w-6 rounded-full shrink-0 flex items-center justify-center text-[11px] font-bold text-white mt-0.5" style={{ backgroundColor: numberFill }}>
        {isUserExcluded ? <X size={12} /> : orderNumber}
      </span>
      <div className="flex-1 min-w-0 flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-sm truncate" style={{ color: COLOR.ink, textDecoration: (isExcluded || isUserExcluded) ? "line-through" : "none" }}>{dest.name}</h3>
            
            {isUserExcluded ? (
              <span className="text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-sm bg-gray-100 text-gray-500">
                {dest.priority}
              </span>
            ) : isExcluded ? (
              <span className="text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-sm bg-orange-100 text-orange-700">
                Unable to schedule
              </span>
            ) : (
              <select
                value={dest.priority}
                onClick={(e) => e.stopPropagation()}
                onChange={(e) => onChangePriority(dest.id, e.target.value)}
                className="text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-sm border-none cursor-pointer focus:ring-0"
                style={{ backgroundColor: meta.bg, color: meta.text, appearance: "none" }}
              >
                {Object.keys(PRIORITY_META).map(k => (
                  <option key={k} value={k}>{PRIORITY_META[k].label}</option>
                ))}
              </select>
            )}
          </div>
          <div className="text-xs mt-1 truncate" style={{ color: COLOR.inkSoft }}>
            {dest.duration} min • {dest.openTime} - {dest.closeTime}
          </div>
          {isUserExcluded && dest.exclusionReason && (
            <div className="text-xs mt-0.5 truncate text-red-500">
              Excluded: {dest.exclusionReason}
            </div>
          )}
          {!isUserExcluded && dest.preferredArrival && (
            <div className="text-xs mt-0.5 truncate" style={{ color: COLOR.muted }}>
              Preferred: {dest.preferredArrival}
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity" style={{ opacity: isHovered || isSelected ? 1 : 0 }}>
          {isUserExcluded ? (
            <button onClick={(e) => { e.stopPropagation(); onRestore(dest.id); }} className="text-xs font-semibold px-2 py-1 rounded bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors">Restore</button>
          ) : (
            <>
              <button onClick={(e) => { e.stopPropagation(); onEdit(dest.id); }} className="p-1.5 rounded-md hover:bg-white/60 transition-colors" style={{ color: COLOR.inkSoft }}><Pencil size={14} /></button>
              <button onClick={(e) => { e.stopPropagation(); onRemove(dest.id); }} className="p-1.5 rounded-md hover:bg-red-50 hover:text-red-600 transition-colors" style={{ color: COLOR.muted }}><Trash2 size={14} /></button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}'''

code = code.replace(old_dest_row, new_dest_row)

# 2. Add onChangePriority to App
change_prio = '''  const changePriority = (id, newPriority) => {
    setDestinations(prev => prev.map(d => d.id === id ? { ...d, priority: newPriority } : d));
  };'''

if 'const changePriority =' not in code:
    code = code.replace('  const changeMode =', change_prio + '\n  const changeMode =')


# 3. Update removeDestination and handleRemoveFlexible to set userExcluded: true and exclusionReason
code = code.replace(
    '''  const removeDestination = (id) => {
    const next = destinations.filter((d) => d.id !== id);
    setDestinations(next);
    setSelectedId((prev) => (prev === id ? null : prev));
    setHoveredId((prev) => (prev === id ? null : prev));
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };''',
    '''  const removeDestination = (id) => {
    const next = destinations.map(d => d.id === id ? { ...d, userExcluded: true, exclusionReason: "Removed by user" } : d);
    setDestinations(next);
    setSelectedId((prev) => (prev === id ? null : prev));
    setHoveredId((prev) => (prev === id ? null : prev));
  };'''
)

code = code.replace(
    '''    const next = destinations.map((d) => d.id === target.id ? { ...d, userExcluded: true } : d);''',
    '''    const next = destinations.map((d) => d.id === target.id ? { ...d, userExcluded: true, exclusionReason: "Skipped to free up time" } : d);'''
)

# 4. In App's render for destinations, we need to split active and userExcluded
render_destinations_old = '''              {displayDestinations.map((d) => (
                <DestinationRow
                  key={d.id}
                  dest={d}
                  orderNumber={destOrder[d.id] || "-"}
                  isExcluded={excludedIds.has(d.id)}
                  isHovered={hoveredId === d.id}
                  isSelected={selectedId === d.id}
                  onHover={setHoveredId}
                  onSelect={setSelectedId}
                  onEdit={openEdit}
                  onRemove={removeDestination}
                />
              ))}'''

render_destinations_new = '''              {displayDestinations.filter(d => !d.userExcluded).map((d) => (
                <DestinationRow
                  key={d.id}
                  dest={d}
                  orderNumber={destOrder[d.id] || "-"}
                  isExcluded={excludedIds.has(d.id)}
                  isUserExcluded={false}
                  isHovered={hoveredId === d.id}
                  isSelected={selectedId === d.id}
                  onHover={setHoveredId}
                  onSelect={setSelectedId}
                  onEdit={openEdit}
                  onRemove={removeDestination}
                  onChangePriority={changePriority}
                />
              ))}

              {destinations.filter(d => d.userExcluded).length > 0 && (
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <div className="text-xs font-semibold text-gray-500 mb-3 tracking-wider">EXCLUDED STOPS</div>
                  {destinations.filter(d => d.userExcluded).map(d => (
                    <DestinationRow
                      key={d.id}
                      dest={d}
                      orderNumber="-"
                      isExcluded={false}
                      isUserExcluded={true}
                      isHovered={hoveredId === d.id}
                      isSelected={selectedId === d.id}
                      onHover={setHoveredId}
                      onSelect={setSelectedId}
                      onRestore={handleRestore}
                    />
                  ))}
                </div>
              )}'''

code = code.replace(render_destinations_old, render_destinations_new)

# 5. Fix handleRestore
# handleRestore is already implemented as:
#   const handleRestore = (id) => {
#     const next = destinations.map(d => d.id === id ? { ...d, userExcluded: false } : d);
#     setDestinations(next);
#     runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
#   };
# Wait, handleRestore calls runOptimize automatically! The user said: "When a priority changes, immediately update... Recalculate... when user clicks Optimize My Day"
# But for Restore: "Clicking Restore must return the destination to the active destination list... Recalculate the route... after optimization." Wait, if I call runOptimize immediately on restore, it will optimize. Is that what's requested?
# "Recalculate the route, itinerary, map markers, summary, and conflict messages after optimization."
# I should change handleRestore to just `setDestinations` and let it be stale, so they click Optimize My Day to recalculate. 
# BUT wait! If I just `setDestinations` in `handleRestore`, `isStale` will become true, and the user clicks Optimize.
# Let's change `handleRestore` to NOT call `runOptimize` immediately.

code = code.replace(
    '''  const handleRestore = (id) => {
    const next = destinations.map(d => d.id === id ? { ...d, userExcluded: false } : d);
    setDestinations(next);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };''',
    '''  const handleRestore = (id) => {
    const next = destinations.map(d => d.id === id ? { ...d, userExcluded: false } : d);
    setDestinations(next);
  };'''
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
