import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Make runOptimize return r
code = code.replace(
    'setRouteEpoch((n) => n + 1);\n    } catch',
    'setRouteEpoch((n) => n + 1);\n      return r;\n    } catch'
)

# Update resetDemo to clear recoveryMsg
code = code.replace(
    '  const resetDemo = () => {',
    '  const resetDemo = () => {\n    setRecoveryMsg(null);'
)

# Update handleRemoveFlexible
code = code.replace(
    '''    setRecoveryMsg(`${target.name} was removed from the active itinerary because it was marked Flexible. The revised plan has been recalculated.`);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };''',
    '''    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`${target.name} was removed from the active itinerary because it was marked Flexible. The revised plan has been recalculated. ${status}`);
      }
    });
  };'''
)

# Update handleStartEarlier
code = code.replace(
    '''    setRecoveryMsg(`Start time changed from ${startTime} to ${next}. The route has been recalculated.`);
    runOptimize(destinations.filter(d => !d.userExcluded), next, endTime, mode);
  };''',
    '''    runOptimize(destinations.filter(d => !d.userExcluded), next, endTime, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`Start time changed from ${startTime} to ${next}, gaining 1 hour. The route has been recalculated. ${status}`);
      }
    });
  };'''
)

# Update handleExtendEnd
code = code.replace(
    '''    setRecoveryMsg(`Your end time was extended from ${endTime} to ${next}. The route has been recalculated.`);
    runOptimize(destinations.filter(d => !d.userExcluded), startTime, next, mode);
  };''',
    '''    runOptimize(destinations.filter(d => !d.userExcluded), startTime, next, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`Your end time was extended from ${endTime} to ${next}, gaining 1 hour. The route has been recalculated. ${status}`);
      }
    });
  };'''
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
