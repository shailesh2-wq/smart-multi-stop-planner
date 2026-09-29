import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the entire reason logic block inside `buildItinerary`
new_logic = '''    let reason = "";
    let short = "";

    const diff = chosen.d.preferredArrival ? chosen.arrival - toMin(chosen.d.preferredArrival) : 0;
    const absDiff = Math.abs(diff);

    if (stops.length === 0 && chosen.d.priority === "must") {
      if (chosen.d.preferredArrival && absDiff > 10) {
        reason = `${chosen.d.name} is a Must Visit scheduled first to preserve overall route feasibility, resulting in a ${toClock(chosen.arrival)} arrival (${formatDuration(absDiff)} ${diff < 0 ? "early" : "late"} compared to your ${chosen.d.preferredArrival} preference).`;
        short = "Trade-off for feasibility";
      } else {
        reason = `${chosen.d.name} comes first — it's marked Must visit${chosen.d.preferredArrival ? `, with a preferred arrival of ${chosen.d.preferredArrival}` : ""}.`;
        short = "Must visit, scheduled first";
      }
    } else if (chosen.d.priority === "must") {
      if (chosen.d.preferredArrival && absDiff > 10) {
        reason = `${chosen.d.name} is a Must Visit placed here to ensure it and other critical stops fit the schedule. It is reached at ${toClock(chosen.arrival)}, which is ${formatDuration(absDiff)} ${diff < 0 ? "early" : "late"} relative to your ${chosen.d.preferredArrival} preference.`;
        short = "Trade-off for feasibility";
      } else {
        reason = `${chosen.d.name} is marked Must visit, so it's prioritized ahead of the remaining stops.`;
        short = "Must visit";
      }
    }
    
    if (!reason && runnerUp) {
      const closeGap = runnerUp.minutesUntilClose - chosen.minutesUntilClose;
      if (closeGap > 60 && chosen.minutesUntilClose < 240) {
        reason = `${chosen.d.name} is scheduled before ${runnerUp.d.name} because ${chosen.d.name} closes at ${chosen.d.closeTime}, while ${runnerUp.d.name} remains open until ${runnerUp.d.closeTime}.`;
        short = `Scheduled before closing at ${chosen.d.closeTime}`;
      }
    }
    if (!reason && chosen.preferredBonus > 15) {
      reason = `${chosen.d.name} was scheduled around ${toClock(chosen.arrival)} to stay close to its preferred arrival time of ${chosen.d.preferredArrival}.`;
      short = `Matched to preferred arrival ${chosen.d.preferredArrival}`;
    }
    if (!reason && chosen.d.preferredArrival) {
      if (absDiff > 10) {
        reason = `${chosen.d.name} is a ${PRIORITY_META[chosen.d.priority].label} stop with a preferred arrival of ${chosen.d.preferredArrival}. It was scheduled at ${toClock(chosen.arrival)} (${formatDuration(absDiff)} ${diff < 0 ? "early" : "late"}) because this placement preserves the feasibility of the remaining destinations within your available time window.`;
        short = "Trade-off for route feasibility";
      }
    }
    if (!reason) {
      if (runnerUp) {
        const extraTravel = runnerUp.travel - chosen.travel;
        if (extraTravel > 0) {
          reason = `${chosen.d.name} follows ${current.name} because both stops remain feasible, and this sequence saves ${formatDuration(extraTravel)} of travel versus the next-best option (${runnerUp.d.name}).`;
          short = "Placed to minimize added travel";
        } else {
          reason = `${chosen.d.name} follows ${current.name} because its calculated score (travel, wait, priority) is lower than the next feasible option (${runnerUp.d.name}).`;
          short = "Lowest calculated score";
        }
      } else {
        reason = `${chosen.d.name} was placed here as the only remaining feasible stop.`;
        short = "Only remaining feasible stop";
      }
    }

    let preferredDeviation = null;
    if (chosen.d.preferredArrival && absDiff >= 10) {
      // Don't show misleading badges if it's explicitly explained in the short reason
      if (!short.includes("Trade-off")) {
         preferredDeviation = `${formatDuration(absDiff)} ${diff < 0 ? "early" : "late"}`;
      }
    }'''

code = re.sub(
    r'    let reason = "";.*?let preferredDeviation = null;.*?if \(Math\.abs\(diff\) >= 10\) \{.*?\}',
    new_logic,
    code,
    flags=re.DOTALL
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
