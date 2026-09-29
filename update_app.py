import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update `handleRemoveFlexible`
code = code.replace(
    '''  const handleRemoveFlexible = () => {
    const excludedFlexible = result.excluded.find((e) => e.dest.priority === "flexible");
    const target = excludedFlexible ? excludedFlexible.dest : [...destinations].reverse().find((d) => d.priority === "flexible");
    if (!target) return;
    const next = destinations.filter((d) => d.id !== target.id);
    setDestinations(next);
    runOptimize(next, startTime, endTime, mode);
  };''',
    '''  const handleRemoveFlexible = () => {
    const excludedFlexible = result.excluded.find((e) => e.dest.priority === "flexible");
    const target = excludedFlexible ? excludedFlexible.dest : [...destinations].reverse().find((d) => d.priority === "flexible" && !d.userExcluded);
    if (!target) return;
    const next = destinations.map((d) => d.id === target.id ? { ...d, userExcluded: true } : d);
    setDestinations(next);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };'''
)

# 2. Add `handleRestore`
if 'const handleRestore =' not in code:
    code = code.replace(
        'const handleRemoveFlexible = () => {',
        '''const handleRestore = (id) => {
    const next = destinations.map(d => d.id === id ? { ...d, userExcluded: false } : d);
    setDestinations(next);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };

  const handleRemoveFlexible = () => {'''
    )

# 3. Update `saveDestination` to filter userExcluded
code = code.replace(
    'runOptimize(next, startTime, endTime, mode);',
    'runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);'
)

# 4. Update the `useEffect` that runs `runOptimize` internally
code = code.replace(
    'runOptimize(destinations, startTime, endTime, mode);',
    'runOptimize(destinations.filter(d => !d.userExcluded), startTime, endTime, mode);'
)
code = code.replace(
    'runOptimize(destinations, next, endTime, mode);',
    'runOptimize(destinations.filter(d => !d.userExcluded), next, endTime, mode);'
)
code = code.replace(
    'runOptimize(destinations, startTime, next, mode);',
    'runOptimize(destinations.filter(d => !d.userExcluded), startTime, next, mode);'
)
code = code.replace(
    'runOptimize(destinations, startTime, endTime, m);',
    'runOptimize(destinations.filter(d => !d.userExcluded), startTime, endTime, m);'
)

# 5. Fix DestinationRow mapping to pass onRestore and userExcluded
code = code.replace(
    '''                        onRemove={removeDestination}
                        isHovered={hoveredDest === d.id}''',
    '''                        onRemove={removeDestination}
                        onRestore={() => handleRestore(d.id)}
                        userExcluded={d.userExcluded}
                        isHovered={hoveredDest === d.id}'''
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
