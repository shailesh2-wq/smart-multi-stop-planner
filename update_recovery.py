import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Update recovery functions
code = code.replace(
    '''  const handleRemoveFlexible = () => {
    const excludedFlexible = result.excluded.find((e) => e.dest.priority === "flexible");
    const target = excludedFlexible ? excludedFlexible.dest : [...destinations].reverse().find((d) => d.priority === "flexible" && !d.userExcluded);
    if (!target) return;
    const next = destinations.map((d) => d.id === target.id ? { ...d, userExcluded: true } : d);
    setDestinations(next);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };''',
    '''  const handleRemoveFlexible = () => {
    const excludedFlexible = result.excluded.find((e) => e.dest.priority === "flexible");
    const target = excludedFlexible ? excludedFlexible.dest : [...destinations].reverse().find((d) => d.priority === "flexible" && !d.userExcluded);
    if (!target) return;
    const next = destinations.map((d) => d.id === target.id ? { ...d, userExcluded: true } : d);
    setDestinations(next);
    setRecoveryMsg(`${target.name} was removed from the active itinerary because it was marked Flexible. The revised plan has been recalculated.`);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };'''
)

code = code.replace(
    '''  const handleStartEarlier = () => {
    const next = toClock(toMin(startTime) - 60);
    setStartTime(next);
    runOptimize(destinations.filter(d => !d.userExcluded), next, endTime, mode);
  };''',
    '''  const handleStartEarlier = () => {
    const next = toClock(toMin(startTime) - 60);
    setStartTime(next);
    setRecoveryMsg(`Start time changed from ${startTime} to ${next}. The route has been recalculated.`);
    runOptimize(destinations.filter(d => !d.userExcluded), next, endTime, mode);
  };'''
)

code = code.replace(
    '''  const handleExtendEnd = () => {
    const next = toClock(toMin(endTime) + 60);
    setEndTime(next);
    runOptimize(destinations.filter(d => !d.userExcluded), startTime, next, mode);
  };''',
    '''  const handleExtendEnd = () => {
    const next = toClock(toMin(endTime) + 60);
    setEndTime(next);
    setRecoveryMsg(`Your end time was extended from ${endTime} to ${next}. The route has been recalculated.`);
    runOptimize(destinations.filter(d => !d.userExcluded), startTime, next, mode);
  };'''
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
