import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    '''  const addDemoLocation = (loc) => {
    const next = [...destinations, { ...loc, userExcluded: false }];
    setDestinations(next);
    setEditorOpen(false);
    setRecoveryMsg(`Added ${loc.name} to your route.`);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };''',
    '''  const addDemoLocation = (loc) => {
    const next = [...destinations, { ...loc, userExcluded: false }];
    setDestinations(next);
    setEditorOpen(false);
    setSelectedId(loc.id);
    setRecoveryMsg(`Added ${loc.name} to your route.`);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };'''
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
