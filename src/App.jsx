import React, { useState, useRef, useEffect } from "react";
import {
  Plus, Pencil, Trash2, X, Car, Bus, Footprints, Clock, Timer,
  AlertTriangle, CheckCircle2, ArrowDown, Info, Navigation, Lightbulb,
  Circle, Sparkles, GraduationCap, ShoppingCart, Dumbbell, Coffee, Stethoscope, MapPin, Home,
  RotateCcw,
  Search, Check,
} from "lucide-react";
import MapContainer from "./MapContainer";
import { nodeForId, getShortestPath, addNavNode } from "./cityNetwork";
import { DEMO_MAP_LOCATIONS } from "./data/demoMapLocations";

/* ---------------------------------------------------------------------- */
/*  TOKENS                                                                 */
/* ---------------------------------------------------------------------- */

const COLOR = {
  paper: "#FAFAF8",
  panel: "#FFFFFF",
  ink: "#14181F",
  inkSoft: "#3A404B",
  muted: "#6B7280",
  faint: "#9CA3AF",
  line: "#E3E5E8",
  lineStrong: "#C7CBD1",
  accent: "#1D5FCB",
  accentSoft: "#E9F0FC",
  success: "#1F7A5C",
  successSoft: "#E7F4EF",
  warn: "#A5570A",
  warnSoft: "#FBEEDF",
  danger: "#B0341F",
  dangerSoft: "#FBEBE7",
  flexible: "#8B93A1",
  mapBg: "#F1F3F6",
  mapBlock: "#E6E9EE",
  mapWater: "#D7E7F7",
};

export const PRIORITY_META = {
  must: { label: "Must Visit", color: COLOR.ink, dot: "#E15B4C", weight: 0 },
  important: { label: "Important", color: COLOR.accent, dot: "#E0A12B", weight: 1 },
  flexible: { label: "Flexible", color: COLOR.flexible, dot: "#3E4C5E", weight: 2 },
};

const MODE_META = {
  driving: { label: "Driving", icon: Car, factor: 1 },
  transit: { label: "Transit", icon: Bus, factor: 1.7 },
  walking: { label: "Walking", icon: Footprints, factor: 2.9 },
};

const STAGES = ["Destinations", "Route", "Itinerary", "Decision"];

/* ---------------------------------------------------------------------- */
/*  TIME HELPERS                                                           */
/* ---------------------------------------------------------------------- */

function toMin(hhmm) {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}
function toClock(mins) {
  const m = ((Math.round(mins) % 1440) + 1440) % 1440;
  const h = Math.floor(m / 60);
  const mm = m % 60;
  return String(h).padStart(2, "0") + ":" + String(mm).padStart(2, "0");
}
function formatDuration(mins) {
  mins = Math.max(0, Math.round(mins));
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}
function hashPair(a, b) {
  const s = a < b ? a + "_" + b : b + "_" + a;
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}
let idCounter = 100;
function genId() {
  idCounter += 1;
  return "d" + idCounter;
}

function formatClock12(hhmm) {
  const [h, m] = hhmm.split(":").map(Number);
  const suffix = h >= 12 ? "PM" : "AM";
  const hour = h % 12 || 12;
  return `${hour}:${String(m).padStart(2, "0")} ${suffix}`;
}

function DestinationGlyph({ name, size = 14 }) {
  const n = name.toLowerCase();
  let Icon = MapPin;
  if (n.includes("dentist") || n.includes("clinic")) Icon = Stethoscope;
  else if (n.includes("college") || n.includes("university")) Icon = GraduationCap;
  else if (n.includes("market") || n.includes("shop")) Icon = ShoppingCart;
  else if (n.includes("fitness") || n.includes("gym")) Icon = Dumbbell;
  else if (n.includes("Cafeé") || n.includes("Cafee") || n.includes("coffee")) Icon = Coffee;
  else if (n.includes("home")) Icon = Home;
  return <Icon size={size} />;
}

/* ---------------------------------------------------------------------- */
/*  DEMO DATA — one internally-consistent dataset used everywhere          */
/* ---------------------------------------------------------------------- */

const DEFAULT_DESTINATIONS = [
  { id: "d1", name: "Dentist Appointment", address: "77 Clinic Rd", priority: "must", duration: 45, openTime: "09:00", closeTime: "17:00", preferredArrival: "10:30", lat: 37.785, lng: -122.420 },
  { id: "d2", name: "City College", address: "142 University Ave", priority: "important", duration: 120, openTime: "08:00", closeTime: "18:00", preferredArrival: "12:00", lat: 37.725, lng: -122.450 },
  { id: "d5", name: "Harbor Market", address: "9 Dockside Ln", priority: "flexible", duration: 45, openTime: "09:00", closeTime: "16:00", preferredArrival: "14:00", lat: 37.808, lng: -122.413 },
  { id: "d4", name: "Pulse Fitness", address: "220 River Rd", priority: "important", duration: 60, openTime: "06:00", closeTime: "21:00", preferredArrival: "15:30", lat: 37.750, lng: -122.420 },
  { id: "d3", name: "Green Fork Cafe", address: "58 Market St", priority: "must", duration: 60, openTime: "11:00", closeTime: "22:00", preferredArrival: "17:30", lat: 37.760, lng: -122.400 },
];

const EMPTY_FORM = { name: "", address: "", priority: "important", duration: 45, openTime: "09:00", closeTime: "18:00", preferredArrival: "" };

/* ---------------------------------------------------------------------- */
/*  TRAVEL ESTIMATES — deterministic prototype data used by the optimizer  */
/* ---------------------------------------------------------------------- */

function baseTravelMinutes(aId, bId, mode) {
  const start = nodeForId(aId === 'home' ? 'home' : aId);
  const end = nodeForId(bId === 'home' ? 'home' : bId);
  const { distance } = getShortestPath(start, end);

  let speed = 50;
  if (mode === 'transit') speed = 25;
  if (mode === 'walking') speed = 8;

  const mins = Math.ceil(distance / speed) + (distance > 0 ? 2 : 0);
  return { minutes: mins, km: +(distance / 100).toFixed(1) };
}

class SyntheticTravelProvider {
  constructor() {
    this.id = "synthetic";
    this.label = "Synthetic estimate";
  }
  async prepare(destinations, mode) {}
  getTravel(aId, bId, mode) {
    return baseTravelMinutes(aId, bId, mode);
  }
}

const travelProvider = new SyntheticTravelProvider();

/* ---------------------------------------------------------------------- */
/*  OPTIMIZATION ENGINE — deterministic, explainable                       */
/* ---------------------------------------------------------------------- */

function buildItinerary(destinations, startTime, endTime, mode, provider = travelProvider) {
  const startMin = toMin(startTime);
  const endMin = toMin(endTime);
  let remaining = destinations.map((d) => ({ ...d }));
  let current = { id: "home", name: "Home", time: startMin };
  const stops = [];
  const excluded = [];

  const score = (d) => {
    const travel = provider.getTravel(current.id, d.id, mode).minutes;
    const rawArrival = current.time + travel;
    const openMin = toMin(d.openTime);
    const closeMin = toMin(d.closeTime);
    let wait = 0;
    let arrival = rawArrival;
    if (arrival < openMin) {
      wait = openMin - arrival;
      arrival = openMin;
    }
    const finish = arrival + d.duration;
    const feasibleHours = arrival <= closeMin && finish <= closeMin;
    const feasibleWindow = finish <= endMin;
    const feasible = feasibleHours && feasibleWindow;
    const minutesUntilClose = closeMin - arrival;
    const urgencyBonus = Math.max(0, 300 - minutesUntilClose) * 0.6;
    const priorityPenalty = PRIORITY_META[d.priority].weight * 12;
    let preferredBonus = 0;
    if (d.preferredArrival) {
      const diff = Math.abs(arrival - toMin(d.preferredArrival));
      preferredBonus = Math.max(0, 60 - diff) * 0.8;
    }
    const cost = travel + wait * 1.5 + priorityPenalty - urgencyBonus - preferredBonus;
    return { d, travel, wait, arrival, finish, feasible, feasibleHours, feasibleWindow, minutesUntilClose, preferredBonus, cost };
  };

  let guard = 0;
  while (remaining.length > 0 && guard < 60) {
    guard += 1;
    const mustLeft = remaining.filter((d) => d.priority === "must");
    const pool = mustLeft.length > 0 ? mustLeft : remaining;
    const scored = pool.map(score);
    const feasible = scored.filter((s) => s.feasible);

    if (feasible.length === 0) {
      scored.forEach((s) => {
        let reason;
        if (!s.feasibleHours) {
          reason = `${s.d.name} was excluded — even prioritized, the earliest realistic arrival (~${toClock(s.arrival)}) leaves no time to finish before it closes at ${s.d.closeTime}.`;
        } else {
          const overflow = formatDuration(s.finish - endMin);
          const note = s.d.priority === "must"
            ? "is marked Must visit, but"
            : `is marked ${PRIORITY_META[s.d.priority].label} rather than Must Visit, and`;
          reason = `${s.d.name} was excluded because it ${note} completing it would push your schedule ${overflow} beyond your ${endTime} end time.`;
        }
        excluded.push({ dest: s.d, reason, estTravel: s.travel, estDuration: s.d.duration, estWait: s.wait });
      });
      remaining = remaining.filter((r) => !pool.find((p) => p.id === r.id));
      continue;
    }

    feasible.sort((a, b) => a.cost - b.cost);
    const chosen = feasible[0];
    const runnerUp = feasible[1];

    let reason = "";
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
    }

    stops.push({
      dest: chosen.d,
      fromName: current.name,
      travel: chosen.travel,
      wait: chosen.wait,
      arrival: chosen.arrival,
      departure: chosen.finish,
      reason,
      short,
      preferredDeviation,
    });

    current = { id: chosen.d.id, name: chosen.d.name, time: chosen.finish };
    remaining = remaining.filter((r) => r.id !== chosen.d.id);
  }

  const totalTravel = stops.reduce((s, x) => s + x.travel, 0);
  const totalActivity = stops.reduce((s, x) => s + x.dest.duration, 0);
  const totalWait = stops.reduce((s, x) => s + x.wait, 0);
  const lastFinish = stops.length ? stops[stops.length - 1].departure : startMin;
  const fits = excluded.length === 0;
  const estimatedTotalNeeded =
    totalActivity + totalTravel + totalWait +
    excluded.reduce((s, e) => s + e.estTravel + e.estDuration + e.estWait, 0);

  return { stops, excluded, totalTravel, totalActivity, totalWait, fits, lastFinish, startMin, endMin, estimatedTotalNeeded };
}

function naiveTravelTotal(destinations, mode, provider = travelProvider) {
  let cur = "home";
  let sum = 0;
  destinations.forEach((d) => {
    sum += provider.getTravel(cur, d.id, mode).minutes;
    cur = d.id;
  });
  return sum;
}

function signatureOf(destinations, startTime, endTime, mode) {
  return JSON.stringify({ destinations, startTime, endTime, mode });
}

/* ---------------------------------------------------------------------- */
/*  SMALL PRESENTATION HELPERS                                             */
/* ---------------------------------------------------------------------- */

function PriorityTag({ priority, compact }) {
  const meta = PRIORITY_META[priority];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded ${compact ? "px-1.5 py-0.5" : "px-2 py-0.5"} font-medium`}
      style={{
        fontSize: 11,
        color: priority === "must" ? "#fff" : meta.color,
        backgroundColor: priority === "must" ? meta.color : "transparent",
        border: priority === "must" ? "none" : `1px solid ${meta.color}`,
      }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: priority === "must" ? "#fff" : meta.dot }} />
      {meta.label}
    </span>
  );
}

function ModeIcon({ mode, size = 14 }) {
  const Icon = MODE_META[mode].icon;
  return <Icon size={size} />;
}

/* ---------------------------------------------------------------------- */
/*  STAGE INDICATOR — Destinations → Route → Itinerary → Decision          */
/* ---------------------------------------------------------------------- */

function StageIndicator({ activeIndex }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      {STAGES.map((label, i) => (
        <React.Fragment key={label}>
          <div className="flex items-center gap-1.5">
            <span
              className="h-1.5 w-1.5 rounded-full shrink-0"
              style={{ backgroundColor: i <= activeIndex ? COLOR.accent : COLOR.lineStrong }}
            />
            <span className="text-xs font-medium" style={{ color: i <= activeIndex ? COLOR.ink : COLOR.faint }}>
              {label}
            </span>
          </div>
          {i < STAGES.length - 1 && (
            <span className="flex-1 h-px" style={{ backgroundColor: i < activeIndex ? COLOR.accent : COLOR.line, minWidth: 12 }} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  DESTINATION ROW + LIST                                                 */
/* ---------------------------------------------------------------------- */

function ScenarioPanel({ onSelectScenario }) {
  return (
    <div className="bg-white rounded-md border border-gray-200 p-3 mb-6 shadow-sm">
      <h3 className="text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">Try a scenario (Demo)</h3>
      <div className="flex flex-col gap-2">
        <button onClick={() => onSelectScenario('A')} className="text-left text-xs font-medium px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors">A: Balanced Day</button>
        <button onClick={() => onSelectScenario('B')} className="text-left text-xs font-medium px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors">B: Must Visit Conflict</button>
        <button onClick={() => onSelectScenario('C')} className="text-left text-xs font-medium px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors">C: Flexible Recovery</button>
      </div>
    </div>
  );
}

function DestinationRow({ dest, orderNumber, isExcluded, onEdit, onRemove, isHovered, isSelected, onHover, onSelect }) {
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
            <span style={{ color: COLOR.muted }}><DestinationGlyph name={dest.name} /></span>
            <span className="text-sm" style={{ color: COLOR.ink, fontWeight: dest.priority === "must" ? 700 : 600 }}>
              {dest.name}
            </span>
            {isExcluded ? (
              <span className="text-[11px] font-medium px-1.5 py-0.5 rounded" style={{ color: COLOR.flexible, border: `1px solid ${COLOR.lineStrong}` }}>Excluded</span>
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
              <span className="inline-flex items-center gap-1"><Clock size={11} />{dest.openTime}–{dest.closeTime}</span>
            )}
            {dest.closeTime && dest.preferredArrival && (
              <span className="inline-flex items-center gap-1"><Clock size={11} />Closes: {dest.closeTime}</span>
            )}
            <span className="inline-flex items-center gap-1"><Timer size={11} />{formatDuration(dest.duration)}</span>
          </div>
        </div>
        <div className="flex items-center gap-0.5 shrink-0 opacity-60 hover:opacity-100 transition-opacity">
          <button onClick={(e) => { e.stopPropagation(); onEdit(dest.id); }} className="p-1.5 rounded hover:bg-gray-100" style={{ color: COLOR.muted }} aria-label={`Edit ${dest.name}`}>
            <Pencil size={13} />
          </button>
          <button onClick={(e) => { e.stopPropagation(); onRemove(dest.id); }} className="p-1.5 rounded hover:bg-gray-100" style={{ color: COLOR.muted }} aria-label={`Remove ${dest.name}`}>
            <Trash2 size={13} />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  DESTINATION EDITOR MODAL                                               */
/* ---------------------------------------------------------------------- */



function DemoLocationSelector({ onAdd, onCancel, existingIds }) {
  const [search, setSearch] = React.useState("");

  const filtered = DEMO_LOCATIONS.filter(loc => 
    loc.name.toLowerCase().includes(search.toLowerCase()) || 
    loc.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md flex flex-col overflow-hidden max-h-[85vh]">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
          <h2 className="font-bold text-gray-900">Add a destination</h2>
          <button onClick={onCancel} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X size={20} />
          </button>
        </div>
        <div className="p-4 border-b border-gray-100">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search demo locations..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-gray-500 text-sm">No locations found matching your search.</div>
          ) : (
            <div className="flex flex-col gap-2">
              {filtered.map(loc => {
                const isAdded = existingIds.includes(loc.id);
                return (
                  <div key={loc.id} className="p-3 rounded-lg border border-gray-100 hover:border-blue-200 hover:bg-blue-50/30 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-semibold text-gray-900 text-sm">{loc.name}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{loc.category}</div>
                      </div>
                      <button 
                        onClick={() => !isAdded && onAdd(loc)}
                        disabled={isAdded}
                        className="text-xs font-medium px-3 py-1.5 rounded-full transition-colors flex items-center gap-1"
                        style={{ 
                          backgroundColor: isAdded ? '#f3f4f6' : '#E0E7FF', 
                          color: isAdded ? '#9ca3af' : '#3730A3',
                          cursor: isAdded ? 'not-allowed' : 'pointer'
                        }}
                      >
                        {isAdded ? (
                          <><Check size={14} /> Added</>
                        ) : (
                          <><Plus size={14} /> Add to route</>
                        )}
                      </button>
                    </div>
                    <div className="text-xs text-gray-600 flex items-center gap-3 mt-2 pt-2 border-t border-gray-50">
                      <span className="flex items-center gap-1"><Clock size={12} className="text-gray-400"/> {loc.openTime} - {loc.closeTime}</span>
                      <span className="flex items-center gap-1"><Timer size={12} className="text-gray-400"/> {loc.duration} min</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DestinationEditor({ initial, onSave, onCancel }) {
  const [form, setForm] = useState(initial || EMPTY_FORM);
  const [error, setError] = useState("");
  const set = (patch) => setForm((f) => ({ ...f, ...patch }));

  const submit = () => {
    if (!form.name.trim()) return setError("Give this stop a name.");
    if (!form.address.trim()) return setError("Add an address so it can be placed on the route.");
    if (toMin(form.closeTime) <= toMin(form.openTime)) return setError("Closing time must be after opening time.");
    if (Number(form.duration) <= 0) return setError("Visit duration must be at least a few minutes.");
    if (form.preferredArrival) {
      if (toMin(form.preferredArrival) < toMin(form.openTime) || toMin(form.preferredArrival) > toMin(form.closeTime)) {
        return setError("Preferred arrival should fall within the opening hours.");
      }
    }
    setError("");
    onSave({ ...form, duration: Number(form.duration) });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ backgroundColor: "rgba(20,24,31,0.45)" }}>
      <div className="w-full max-w-md rounded-md" style={{ backgroundColor: COLOR.panel, border: `1px solid ${COLOR.line}`, boxShadow: "0 12px 32px rgba(20,24,31,0.18)" }}>
        <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: `1px solid ${COLOR.line}` }}>
          <h3 className="text-sm font-semibold" style={{ color: COLOR.ink }}>{initial ? "Edit destination" : "Add destination"}</h3>
          <button onClick={onCancel} className="p-1 rounded hover:bg-gray-100" style={{ color: COLOR.muted }}><X size={16} /></button>
        </div>

        <div className="px-5 py-4 space-y-4 overflow-y-auto" style={{ maxHeight: "70vh" }}>
          <div>
            <label className="text-xs font-medium block mb-1" style={{ color: COLOR.inkSoft }}>Name</label>
            <input value={form.name} onChange={(e) => set({ name: e.target.value })} placeholder="e.g. Riverside Bookstore"
              className="w-full rounded px-3 py-2 text-sm outline-none" style={{ border: `1px solid ${COLOR.lineStrong}`, color: COLOR.ink }} />
          </div>
          <div>
            <label className="text-xs font-medium block mb-1" style={{ color: COLOR.inkSoft }}>Address</label>
            <input value={form.address} onChange={(e) => set({ address: e.target.value })} placeholder="e.g. 12 Willow St"
              className="w-full rounded px-3 py-2 text-sm outline-none" style={{ border: `1px solid ${COLOR.lineStrong}`, color: COLOR.ink }} />
          </div>
          <div>
            <label className="text-xs font-medium block mb-1.5" style={{ color: COLOR.inkSoft }}>Priority</label>
            <div className="flex gap-2">
              {Object.keys(PRIORITY_META).map((p) => (
                <button key={p} onClick={() => set({ priority: p })} className="flex-1 rounded px-2 py-1.5 text-xs font-medium"
                  style={{
                    border: `1px solid ${form.priority === p ? PRIORITY_META[p].color : COLOR.lineStrong}`,
                    backgroundColor: form.priority === p ? (p === "must" ? COLOR.ink : COLOR.accentSoft) : "transparent",
                    color: form.priority === p ? (p === "must" ? "#fff" : COLOR.accent) : COLOR.muted,
                  }}>
                  {PRIORITY_META[p].label}
                </button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium block mb-1" style={{ color: COLOR.inkSoft }}>Visit duration (min)</label>
              <input type="number" min={5} step={5} value={form.duration} onChange={(e) => set({ duration: e.target.value })}
                className="w-full rounded px-3 py-2 text-sm outline-none" style={{ border: `1px solid ${COLOR.lineStrong}`, color: COLOR.ink }} />
            </div>
            <div>
              <label className="text-xs font-medium block mb-1" style={{ color: COLOR.inkSoft }}>Preferred arrival</label>
              <input type="time" value={form.preferredArrival} onChange={(e) => set({ preferredArrival: e.target.value })}
                className="w-full rounded px-3 py-2 text-sm outline-none" style={{ border: `1px solid ${COLOR.lineStrong}`, color: COLOR.ink }} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium block mb-1" style={{ color: COLOR.inkSoft }}>Opens</label>
              <input type="time" value={form.openTime} onChange={(e) => set({ openTime: e.target.value })}
                className="w-full rounded px-3 py-2 text-sm outline-none" style={{ border: `1px solid ${COLOR.lineStrong}`, color: COLOR.ink }} />
            </div>
            <div>
              <label className="text-xs font-medium block mb-1" style={{ color: COLOR.inkSoft }}>Closes</label>
              <input type="time" value={form.closeTime} onChange={(e) => set({ closeTime: e.target.value })}
                className="w-full rounded px-3 py-2 text-sm outline-none" style={{ border: `1px solid ${COLOR.lineStrong}`, color: COLOR.ink }} />
            </div>
          </div>
          {error && (
            <div className="text-xs rounded px-3 py-2" style={{ backgroundColor: COLOR.dangerSoft, color: COLOR.danger }}>{error}</div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 px-5 py-4" style={{ borderTop: `1px solid ${COLOR.line}` }}>
          <button onClick={onCancel} className="px-3 py-1.5 text-sm rounded" style={{ color: COLOR.muted }}>Cancel</button>
          <button onClick={submit} className="px-3.5 py-1.5 text-sm rounded font-medium" style={{ backgroundColor: COLOR.ink, color: "#fff" }}>
            Save destination
          </button>
        </div>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  RESULTS: SUMMARY + TIMELINE + WHY + CONFLICT                           */
/* ---------------------------------------------------------------------- */

function StatBlock({ label, value, sub, tone }) {
  return (
    <div className="px-3 py-2.5">
      <div style={{ color: COLOR.muted, fontSize: 11 }}>{label}</div>
      <div className="text-base font-semibold mt-0.5" style={{ color: tone || COLOR.ink, fontFamily: "ui-monospace, monospace" }}>{value}</div>
      {sub && <div className="mt-0.5" style={{ color: COLOR.faint, fontSize: 11 }}>{sub}</div>}
    </div>
  );
}

function SummaryBar({ result, mode }) {
  const { stops, excluded, fits, totalTravel, totalActivity, lastFinish, endMin, startMin } = result;
  const total = stops.length + excluded.length;
  const available = endMin - startMin;
  const buffer = endMin - lastFinish;
  return (
    <div className="grid grid-cols-3 sm:grid-cols-6 overflow-hidden">
      <StatBlock label="Stops planned" value={fits ? `${stops.length}` : `${stops.length}/${total}`} tone={!fits ? COLOR.warn : undefined} />
      <StatBlock label="Travel time" value={formatDuration(totalTravel)} sub={MODE_META[mode].label} />
      <StatBlock label="Activity time" value={formatDuration(totalActivity)} />
      <StatBlock label="Available" value={formatDuration(available)} />
      <StatBlock label="Buffer" value={fits ? formatDuration(Math.max(0, buffer)) : "—"} tone={fits && buffer < 15 ? COLOR.warn : undefined} />
      <div className="px-3 py-2.5">
        <div style={{ color: COLOR.muted, fontSize: 11 }}>Status</div>
        <div className="flex items-center gap-1.5 mt-1.5">
          {fits ? <CheckCircle2 size={14} color={COLOR.success} /> : <AlertTriangle size={14} color={COLOR.warn} />}
          <span className="text-xs font-semibold" style={{ color: fits ? COLOR.success : COLOR.warn }}>
            {fits ? "Fits your day" : "Doesn't fully fit"}
          </span>
        </div>
      </div>
    </div>
  );
}

function InsightCallout({ text }) {
  return (
    <div className="flex items-start gap-2 rounded-md mt-2.5 px-3 py-2" style={{ backgroundColor: COLOR.accentSoft }}>
      <Lightbulb size={15} color={COLOR.accent} className="mt-0.5 shrink-0" />
      <p className="text-xs" style={{ color: "#123E85" }}>{text}</p>
    </div>
  );
}

function OrderComparison({ original, optimized, excludedNames, savedMinutes, originalLength, optimizedLength }) {
  const sameStops = originalLength === optimizedLength;
  const numExcluded = excludedNames.length;

  return (
    <div className="mt-2 rounded-md px-3 py-2.5 flex flex-col sm:flex-row sm:items-start justify-between gap-3" style={{ backgroundColor: COLOR.panel, border: `1px solid ${COLOR.line}` }}>
      <div className="flex-1 min-w-0">
        <div className="text-[10px] font-bold tracking-wider mb-1" style={{ color: COLOR.inkSoft }}>AS ADDED</div>
        <div className="text-xs mb-2 break-words" style={{ color: COLOR.muted, lineHeight: 1.5 }}>{original.join(" → ")}</div>

        <div className="text-[10px] font-bold tracking-wider mb-1" style={{ color: COLOR.inkSoft }}>OPTIMIZED</div>
        <div className="text-xs break-words font-medium" style={{ color: COLOR.ink, lineHeight: 1.5 }}>
          {optimized.map((name, i) => {
            const circle = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"[i] || `${i + 1}.`;
            return `${circle} ${name}`;
          }).join(" → ")}
        </div>

        {!sameStops && (
          <div className="text-[10px] font-bold tracking-wider mt-2 mb-1" style={{ color: COLOR.warn }}>EXCLUDED</div>
        )}
        {excludedNames.length > 0 && (
          <div className="text-xs font-medium" style={{ color: COLOR.warn }}>{excludedNames.join(", ")}</div>
        )}
      </div>

      <div className="sm:text-right shrink-0">
        {sameStops && savedMinutes >= 1 ? (
          <>
            <div className="text-[10px] font-bold tracking-wider mb-1" style={{ color: COLOR.success }}>TRAVEL SAVED</div>
            <div className="text-lg font-semibold" style={{ color: COLOR.success, fontFamily: "ui-monospace, monospace" }}>{formatDuration(savedMinutes)}</div>
            <div className="text-[10px] mt-0.5" style={{ color: COLOR.faint }}>{travelProvider.id === "synthetic" ? "Synthetic estimate" : "Based on route"}</div>
          </>
        ) : sameStops ? (
          <div className="text-xs font-medium" style={{ color: COLOR.muted, maxWidth: 130 }}>
            Similar travel time in either order.
          </div>
        ) : (
          <div className="text-xs font-medium" style={{ color: COLOR.warn, maxWidth: 120 }}>
            {numExcluded} {numExcluded === 1 ? "stop" : "stops"} excluded to fit the available window.
          </div>
        )}
      </div>
    </div>
  );
}

function TimelineRow({ time, label, kind, priority, meta, deviation }) {
  return (
    <div className="flex items-start gap-3 py-1">
      <span className="text-xs shrink-0 w-11 pt-0.5 text-right" style={{ fontFamily: "ui-monospace, monospace", color: kind === "travel" ? "transparent" : COLOR.muted }}>
        {kind === "travel" ? "" : time}
      </span>
      <div className="flex flex-col items-center pt-1 w-3">
        {kind === "travel" ? (
          <ArrowDown size={14} color={COLOR.faint} />
        ) : kind === "arrive" ? (
          <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: PRIORITY_META[priority].dot }} />
        ) : (
          <Circle size={10} color={COLOR.faint} strokeWidth={2.5} />
        )}
      </div>
      <div className="min-w-0">
        <div className="text-sm flex items-center gap-2" style={{ color: kind === "travel" ? COLOR.muted : COLOR.ink, fontWeight: kind === "arrive" ? 600 : 500 }}>
          {label}
          {deviation && <span className="text-xs font-medium px-1.5 rounded" style={{ backgroundColor: COLOR.warnSoft, color: COLOR.warn }}>{deviation}</span>}
        </div>
        {meta && <div className="text-xs" style={{ color: COLOR.muted }}>{meta}</div>}
      </div>
    </div>
  );
}

function ResultsPanel({ result, mode, hoveredLeg, setHoveredLeg, onEditDest, destinations }) {
  const { stops, fits, excluded, startMin, endMin } = result;
  const total = stops.length + excluded.length;
  const fitText = fits ? `${stops.length} stops fit` : `${stops.length} of ${total} stops fit`;
  const timeText = `${toClock(startMin)}–${toClock(endMin)}`;

  return (
    <div className="rounded-md" style={{ border: `1px solid ${COLOR.line}`, backgroundColor: COLOR.panel }}>
      <div className="px-4 py-2 border-b border-gray-100">
        <h2 className="text-[10px] font-bold tracking-wider mb-1" style={{ color: COLOR.inkSoft }}>YOUR DAY PLAN</h2>
        <p className="text-sm" style={{ color: COLOR.ink }}>{fitText} within your {timeText} window.</p>
      </div>
      <SummaryBar result={result} mode={mode} onEditDest={onEditDest} destinations={destinations} />
      <div className="px-4 py-2" style={{ borderTop: `1px solid ${COLOR.line}` }}>
        <h3 className="text-[10px] font-bold tracking-wider mb-2" style={{ color: COLOR.inkSoft }}>OPTIMIZED ROUTE</h3>
        <div className="space-y-0">
          <TimelineRow time={toClock(result.startMin)} label="Start from Home" kind="depart" />
          {stops.map((s, i) => {
            const u = i === 0 ? "home" : stops[i - 1].dest.id;
            const v = s.dest.id;
            return (
              <React.Fragment key={s.dest.id}>
                <div
                  onMouseEnter={() => setHoveredLeg({ u, v })}
                  onMouseLeave={() => setHoveredLeg(null)}
                  style={{ backgroundColor: hoveredLeg && hoveredLeg.u === u && hoveredLeg.v === v ? '#F3F4F6' : 'transparent', borderRadius: 4 }}
                >
                  <TimelineRow
                    time={`+${formatDuration(s.travel)}`}
                    label={`Travel - ${formatDuration(s.travel)} - ~${travelProvider.getTravel(u, v, mode).km} km`}
                    kind="travel"
                  />
                </div>
              <TimelineRow time={toClock(s.arrival)} label={s.dest.name} kind="arrive" priority={s.dest.priority}
                meta={`${formatDuration(s.dest.duration)}${s.wait > 0 ? ` waited ${formatDuration(s.wait)} for opening` : ""}`}  deviation={s.preferredDeviation} />
              {i < stops.length - 1 && (
                <TimelineRow time={toClock(s.departure)} label={`Leave ${s.dest.name}`} kind="depart" />
              )}
            </React.Fragment>
          );
          })}
        </div>
      </div>
    </div>
  );
}

function WhyThisOrder({ result }) {
  return (
    <div className="mt-2 rounded-md" style={{ border: `1px solid ${COLOR.line}` }}>
      <div className="px-3 py-1.5 text-xs font-semibold" style={{ borderBottom: `1px solid ${COLOR.line}`, color: COLOR.inkSoft, backgroundColor: "#F5F6F7" }}>
        Why this order?
      </div>
      <div className="p-3 bg-white space-y-2">
        <ol className="space-y-2.5">
          {result.stops.map((s, i) => (
            <li key={s.dest.id} className="flex gap-2.5">
              <span className="shrink-0 h-4 w-4 rounded-full flex items-center justify-center font-semibold mt-0.5"
                style={{ backgroundColor: COLOR.accentSoft, color: COLOR.accent, fontFamily: "ui-monospace, monospace", fontSize: 10 }}>
                {i + 1}
              </span>
              <div>
                <div className="text-sm font-medium leading-tight" style={{ color: COLOR.ink }}>{s.dest.name}</div>
                <div className="text-xs mt-0.5 leading-snug" style={{ color: COLOR.muted }}>{s.reason}</div>
              </div>
            </li>
          ))}
        </ol>

        <div className="mt-3 pt-2.5" style={{ borderTop: `1px solid ${COLOR.line}` }}>
          <div className="font-medium mb-1" style={{ color: COLOR.inkSoft, fontSize: 11 }}>Optimization priorities, in order</div>
          <ol className="text-xs space-y-0.5" style={{ color: COLOR.muted }}>
            <li>1. Feasibility (opening hours & available time)</li>
            <li>2. Destination priority</li>
            <li>3. Closing time urgency</li>
            <li>4. Preferred arrival time</li>
            <li>5. Minimizing travel & wait time</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

function ConflictBanner({ result, windowMinutes, onRemoveFlexible, onStartEarlier, onExtendEnd, hasFlexible }) {
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


function computeInsight(destinations, result, mode, provider) {
  if (result.excluded.length > 0) return "Adjust your constraints to fit all destinations.";
  return "This route is fully optimized for " + mode + ".";
}

export default function App() {
  const [destinations, setDestinations] = useState(DEFAULT_DESTINATIONS);
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("17:00");
  const [mode, setMode] = useState("driving");

  const [result, setResult] = useState(() => buildItinerary(DEFAULT_DESTINATIONS, "09:00", "17:00", "driving"));
  const [computedSig, setComputedSig] = useState(() => signatureOf(DEFAULT_DESTINATIONS, "09:00", "17:00", "driving"));
    const [insight, setInsight] = useState("");
  const [recoveryMsg, setRecoveryMsg] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);

  const [editorOpen, setEditorOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [hoveredId, setHoveredId] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [hoveredLeg, setHoveredLeg] = useState(null);
  const [routeEpoch, setRouteEpoch] = useState(0);
  const destinationRowRefs = useRef({});

  useEffect(() => {
    if (selectedId) {
      destinationRowRefs.current[selectedId]?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [selectedId]);

  const currentSig = signatureOf(destinations, startTime, endTime, mode);
  const isStale = currentSig !== computedSig;



  const computeInsight = (d, r, m, provider = travelProvider) => {
    const naive = naiveTravelTotal(d, m, provider);
    const saved = naive - r.totalTravel;
    if (saved >= 5) {
      return "This order saves approximately " + formatDuration(saved) + " of travel compared with visiting destinations in the order they were added.";
    }
    const mustCount = d.filter((x) => x.priority === "must").length;
    return mustCount > 0
      ? "The route prioritizes " + mustCount + " must-visit stop" + (mustCount > 1 ? "s" : "") + " while respecting constraints."
      : "The route keeps " + r.stops.length + " of " + d.length + " destinations within opening hours while minimizing travel.";
  };

  const runOptimize = async (d = destinations, st = startTime, et = endTime, m = mode) => {
    setIsOptimizing(true);
    try {
      const delay = new Promise((res) => window.setTimeout(res, 550));
      await Promise.all([travelProvider.prepare(d, m), delay]);

      const r = buildItinerary(d, st, et, m, travelProvider);
      setResult(r);
      setInsight(computeInsight(d, r, m, travelProvider));
      setComputedSig(signatureOf(d, st, et, m));
      setRouteEpoch((n) => n + 1);
      return r;
    } catch (e) {
      console.error("Optimization failed:", e);
      alert("Optimization failed: " + e.message);
    } finally {
      setIsOptimizing(false);
    }
  };

  const openAdd = () => { setEditingId(null); setEditorOpen(true); };
  const openEdit = (id) => { setEditingId(id); setEditorOpen(true); };
  const closeEditor = () => setEditorOpen(false);

  const saveDestination = (form) => {
    let next;
    if (editingId) {
      next = destinations.map((d) => (d.id === editingId ? { ...d, ...form } : d));
      setSelectedId(editingId);
    } else {
      const customCount = destinations.filter(d => d.isCustom).length;
      const baseIndex = customCount % 3;
      const cycle = Math.floor(customCount / 3);

      const coord = DEMO_MAP_LOCATIONS[baseIndex];
      // Offset by 0.003 degrees (~300m) per cycle to prevent exact overlap
      const offsetLat = coord.lat + (cycle * 0.003);
      const offsetLng = coord.lng + (cycle * 0.003);
      
      // Synthetic map offsets (approx 20px per cycle)
      const offsetX = coord.x + (cycle * 20);
      const offsetY = coord.y + (cycle * 20);

      const newId = genId();
      addNavNode(newId, offsetX, offsetY, form.name);

      const added = { 
        ...form, 
        id: newId,
        isCustom: true,
        lat: offsetLat,
        lng: offsetLng,
        x: offsetX,
        y: offsetY,
        userExcluded: false
      };
      next = [...destinations, added];
      setSelectedId(added.id);
    }
    setDestinations(next);
    setEditorOpen(false);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode);
  };



  const removeDestination = (id) => {
    const next = destinations.map(d => d.id === id ? { ...d, userExcluded: true, exclusionReason: "Removed by user" } : d);
    setDestinations(next);
    setSelectedId((prev) => (prev === id ? null : prev));
    setHoveredId((prev) => (prev === id ? null : prev));
  };

  const changePriority = (id, newPriority) => {
    setDestinations(prev => prev.map(d => d.id === id ? { ...d, priority: newPriority } : d));
  };
  const changeMode = (nextMode) => {
    setMode(nextMode);
    if (!isStale && result.stops.length > 0) {
      runOptimize(destinations, startTime, endTime, nextMode);
    }
  };

  const loadConflictDemo = () => {
    setDestinations(DEFAULT_DESTINATIONS);
    setStartTime("10:00");
    setEndTime("16:00");
    runOptimize(DEFAULT_DESTINATIONS, "10:00", "16:00", mode);
  };

  const resetDemo = () => {
    setRecoveryMsg(null);
    setDestinations(DEFAULT_DESTINATIONS);
    setStartTime("09:00");
    setEndTime("17:00");
    setMode("driving");
    setSelectedId(null);
    setHoveredId(null);
    runOptimize(DEFAULT_DESTINATIONS, "09:00", "17:00", "driving");
  };

  
  const handleScenario = (type) => {
    setRecoveryMsg(null);
    let newDestinations = [...DEFAULT_DESTINATIONS].map(d => ({...d, userExcluded: false}));
    if (type === 'A') {
      setStartTime("09:00");
      setEndTime("18:00");
      newDestinations[0].priority = "must";
      newDestinations[1].priority = "important";
      newDestinations[2].priority = "flexible";
      newDestinations[3].priority = "important";
      newDestinations[4].priority = "must";
    } else if (type === 'B') {
      setStartTime("09:00");
      setEndTime("13:00");
      newDestinations.forEach(d => d.priority = "must");
    } else if (type === 'C') {
      setStartTime("09:00");
      setEndTime("13:00");
      newDestinations[0].priority = "must";
      newDestinations[1].priority = "must";
      newDestinations[2].priority = "flexible";
      newDestinations[3].priority = "must";
      newDestinations[4].priority = "must";
    }
    setDestinations(newDestinations);
    runOptimize(newDestinations.filter(d => !d.userExcluded), type === 'A' ? "09:00" : "09:00", type === 'A' ? "18:00" : "13:00", mode);
  };

  const handleRestore = (id) => {
    const next = destinations.map(d => d.id === id ? { ...d, userExcluded: false } : d);
    setDestinations(next);
  };

  const handleRemoveFlexible = () => {
    const excludedFlexible = result.excluded.find((e) => e.dest.priority === "flexible");
    const target = excludedFlexible ? excludedFlexible.dest : [...destinations].reverse().find((d) => d.priority === "flexible" && !d.userExcluded);
    if (!target) return;
    const next = destinations.map((d) => d.id === target.id ? { ...d, userExcluded: true, exclusionReason: "Skipped to free up time" } : d);
    setDestinations(next);
    runOptimize(next.filter(d => !d.userExcluded), startTime, endTime, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`${target.name} was removed from the active itinerary because it was marked Flexible. The revised plan has been recalculated. ${status}`);
      }
    });
  };

  const handleStartEarlier = () => {
    const next = toClock(toMin(startTime) - 60);
    setStartTime(next);
    runOptimize(destinations.filter(d => !d.userExcluded), next, endTime, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`Start time changed from ${startTime} to ${next}, gaining 1 hour. The route has been recalculated. ${status}`);
      }
    });
  };

  const handleExtendEnd = () => {
    const next = toClock(toMin(endTime) + 60);
    setEndTime(next);
    runOptimize(destinations.filter(d => !d.userExcluded), startTime, next, mode).then(r => {
      if (r) {
        const stillFails = r.excluded.some(e => e.dest.priority === "must");
        const status = stillFails ? "However, the plan still needs attention." : "The conflict was resolved and the plan now fits.";
        setRecoveryMsg(`Your end time was extended from ${endTime} to ${next}, gaining 1 hour. The route has been recalculated. ${status}`);
      }
    });
  };

  const editingDest = editingId ? destinations.find((d) => d.id === editingId) : null;
  const hasFlexible = destinations.some((d) => d.priority === "flexible" && !d.userExcluded);
  const windowMinutes = Math.max(0, toMin(endTime) - toMin(startTime));

  // Compare like-for-like: both orders cover the same planned stops and
  // obtain every leg from the active travel provider.
  const plannedDestinationIds = new Set(result.stops.map((s) => s.dest.id));
  const comparisonDestinations = destinations.filter((d) => plannedDestinationIds.has(d.id));
  const savedMinutes = result.stops.length > 0
    ? naiveTravelTotal(comparisonDestinations, mode, travelProvider) - result.totalTravel
    : 0;

  const stageIndex = destinations.length === 0 ? 0 : isStale || isOptimizing ? 1 : result.stops.length > 0 ? 3 : 2;

  const destOrder = {};
  result.stops.forEach((s, i) => { destOrder[s.dest.id] = i + 1; });
  result.excluded.forEach((e, i) => { destOrder[e.dest.id] = result.stops.length + i + 1; });
  destinations.forEach((d, i) => { if (destOrder[d.id] == null) destOrder[d.id] = 200 + i; });
  const displayDestinations = [...destinations].sort((a, b) => destOrder[a.id] - destOrder[b.id]);
  const excludedIds = new Set(result.excluded.map((e) => e.dest.id));
  const totalKm = result.stops.reduce((sum, s, i) => {
    const from = i === 0 ? "home" : result.stops[i - 1].dest.id;
    return sum + travelProvider.getTravel(from, s.dest.id, mode).km;
  }, 0);

  return (
    <div className="min-h-screen w-full" style={{ backgroundColor: COLOR.paper, fontFamily: "Inter, ui-sans-serif, system-ui" }}>
                                      <style>{`
          input[type="time"]::-webkit-calendar-picker-indicator { opacity: 0.6; }
          @keyframes spin { to { transform: rotate(360deg); } }
          .planner-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; align-items: start; margin-bottom: 4rem; }
          .planner-sidebar { min-width: 0; }
          .map-main { position: sticky; top: 2rem; 
            width: 100%; 
            aspect-ratio: 16 / 10; 
            min-height: 350px;
            max-height: 600px;
            border-radius: 0.75rem; 
            overflow: hidden; 
            background: #F1F3F6;
            margin: 0 auto;
          }
          @media (min-width: 768px) {
            .planner-grid { grid-template-columns: 360px minmax(0, 1fr); }
          }
          @media (min-width: 1024px) {
            .planner-grid { grid-template-columns: 400px minmax(0, 1fr); }
          }
          .spinner { animation: spin 0.8s linear infinite; }
        `}</style>

      {/* Compact Header */}
      <header className="px-4 sm:px-6 py-3" style={{ borderBottom: `1px solid ${COLOR.line}`, background: COLOR.panel }}>
        <div className="max-w-[1440px] mx-auto flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-9 w-9 rounded-full flex items-center justify-center shrink-0" style={{ background: COLOR.accentSoft, color: COLOR.accent }}>
              <Navigation size={16} />
            </div>
            <div className="min-w-0">
              <h1 className="text-base leading-tight" style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, color: COLOR.ink }}>
                Smart Multi-Stop Planner
              </h1>
              <p className="text-[11px]" style={{ color: COLOR.muted }}>Plan your day smarter. More places, less hassle.</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <button onClick={resetDemo} className="text-xs font-medium px-3 py-1.5 rounded-full" style={{ color: COLOR.muted, border: `1px solid ${COLOR.lineStrong}` }}>
              <RotateCcw size={12} className="inline-block mr-1" /> Reset
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-[1440px] mx-auto px-4 sm:px-6 py-4">
        <StageIndicator activeIndex={stageIndex} />

        <div className="planner-grid">
          {/* LEFT PANEL - Planning Workspace */}
          <div className="planner-sidebar flex flex-col gap-3">
            <div className="rounded-xl" style={{ border: `1px solid ${COLOR.line}`, backgroundColor: COLOR.panel }}>
              <div className="flex items-center justify-between px-3.5 py-2.5" style={{ borderBottom: `1px solid ${COLOR.line}` }}>
                <span className="text-sm font-semibold" style={{ color: COLOR.ink }}>Destinations ({destinations.length})</span>
                <button onClick={openAdd} className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1.5 rounded-full" style={{ backgroundColor: COLOR.accentSoft, color: COLOR.accent }}>
                  <Plus size={13} /> Add Stop
                </button>
              </div>
              <div className="px-3.5 pb-3.5">
                {destinations.length === 0 ? (
                  <div className="py-8 text-center">
                    <p className="text-sm" style={{ color: COLOR.muted }}>No destinations yet. Add your first stop to start planning.</p>
                  </div>
                ) : (
                  displayDestinations.map((d, i) => (
                    <div key={d.id} ref={(node) => { destinationRowRefs.current[d.id] = node; }} style={{ borderBottom: i < displayDestinations.length - 1 ? `1px solid ${COLOR.line}` : "none" }}>
                      <DestinationRow
                        dest={d}
                        orderNumber={destOrder[d.id] <= destinations.length ? destOrder[d.id] : i + 1}
                        isExcluded={excludedIds.has(d.id)}
                        onEdit={openEdit}
                        onRemove={removeDestination}
                        isHovered={hoveredId === d.id}
                        isSelected={selectedId === d.id}
                        onHover={setHoveredId}
                        onSelect={(id) => setSelectedId((prev) => (prev === id ? null : id))}
                      />
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* TRANSPORTATION MODE */}
            <div className="rounded-xl" style={{ border: `1px solid ${COLOR.line}`, backgroundColor: COLOR.panel }}>
              <div className="px-3.5 py-2.5 text-xs font-semibold tracking-wider" style={{ color: COLOR.inkSoft, borderBottom: `1px solid ${COLOR.line}` }}>
                TRANSPORTATION
              </div>
              <div className="px-3.5 py-3 flex gap-2">
                {Object.keys(MODE_META).map((m) => (
                  <button
                    key={m}
                    onClick={() => changeMode(m)}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-full px-3 py-2 text-xs font-medium transition-colors"
                    style={{
                      backgroundColor: mode === m ? COLOR.accent : "transparent",
                      color: mode === m ? "#fff" : COLOR.muted,
                      border: mode === m ? "none" : `1px solid ${COLOR.lineStrong}`,
                    }}
                  >
                    <ModeIcon mode={m} size={13} />
                    {MODE_META[m].label}
                  </button>
                ))}
              </div>
            </div>

            {/* AVAILABLE TIME */}
            <div className="rounded-xl" style={{ border: `1px solid ${COLOR.line}`, backgroundColor: COLOR.panel }}>
              <div className="px-3.5 py-2.5 text-xs font-semibold tracking-wider" style={{ color: COLOR.inkSoft, borderBottom: `1px solid ${COLOR.line}` }}>
                AVAILABLE TIME
              </div>
              <div className="px-3.5 py-3 space-y-2">
                <div>
                  <label className="text-xs font-medium block mb-1" style={{ color: COLOR.inkSoft }}>Start time</label>
                  <input
                    type="time"
                    value={startTime}
                    onChange={(e) => { setStartTime(e.target.value); }}
                    className="w-full rounded px-3 py-2 text-sm outline-none"
                    style={{ border: `1px solid ${COLOR.lineStrong}`, color: COLOR.ink, fontFamily: "ui-monospace, monospace" }}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium block mb-1" style={{ color: COLOR.inkSoft }}>End time</label>
                  <input
                    type="time"
                    value={endTime}
                    onChange={(e) => { setEndTime(e.target.value); }}
                    className="w-full rounded px-3 py-2 text-sm outline-none"
                    style={{ border: `1px solid ${COLOR.lineStrong}`, color: COLOR.ink, fontFamily: "ui-monospace, monospace" }}
                  />
                </div>
              </div>
            </div>

            {/* OPTIMIZE & RESET ACTIONS */}
            <div className="rounded-xl" style={{ border: `1px solid ${COLOR.line}`, backgroundColor: COLOR.panel }}>
              <div className="p-3.5 space-y-2">
                <button
                  onClick={() => runOptimize()}
                  disabled={destinations.length === 0 || isOptimizing}
                  className="w-full inline-flex items-center justify-center gap-1.5 rounded-full px-3.5 py-2.5 text-sm font-semibold transition-all"
                  style={{ backgroundColor: COLOR.accent, color: "#fff", opacity: isOptimizing ? 0.75 : 1 }}
                >
                  {isOptimizing ? "Optimizing…" : <> <Sparkles size={15} /> Optimize My Day</>}
                </button>
                <button onClick={resetDemo} className="w-full text-sm font-medium px-3 py-2 rounded-full transition-colors" style={{ color: COLOR.muted, border: `1px solid ${COLOR.lineStrong}`, backgroundColor: "transparent" }}>
                  Reset to defaults
                </button>
              </div>
            </div>

            {/* PLANNING SUMMARY */}
            {!isStale && result.stops.length > 0 && (
              <div className="rounded-xl p-3.5" style={{ border: `1px solid ${COLOR.line}`, backgroundColor: COLOR.panel }}>
                <div className="text-sm font-semibold mb-2" style={{ color: COLOR.ink }}>Optimized Itinerary</div>
                <div className="space-y-1.5 text-xs" style={{ color: COLOR.inkSoft }}>
                  <div className="flex items-center gap-2"><Clock size={12} /> {formatClock12(startTime)} – {formatClock12(endTime)}</div>
                  <div className="flex items-center gap-2"><MapPin size={12} /> {result.stops.length} / {destinations.length} stops fit</div>
                  <div className="flex items-center gap-2"><Car size={12} /> Total travel: {formatDuration(result.totalTravel)}</div>
                  <div className="flex items-center gap-2" style={{ color: COLOR.muted }}>Total distance: {totalKm.toFixed(0)} km (illustrative)</div>
                </div>
              </div>
            )}

            {isStale && !isOptimizing && (
              <p className="text-xs" style={{ color: COLOR.warn }}>Inputs changed — optimize again to update the route.</p>
            )}
            <button onClick={loadConflictDemo} className="w-full text-xs text-left" style={{ color: COLOR.muted, textDecoration: "underline" }}>
              See what happens when everything doesn't fit →
            </button>
          </div>

          {/* RIGHT PANEL - Map Workspace */}
          <div className="map-main flex flex-col">
            <MapContainer
              destinations={destinations}
              result={result}
              hoveredId={hoveredId}
              hoveredLeg={hoveredLeg}
              selectedId={selectedId}
              onHoverDest={setHoveredId}
              onSelectDest={(id) => setSelectedId((prev) => (prev === id ? null : id))}
              mode={mode}
              routeEpoch={routeEpoch}
            />
          </div>

          {/* RESULTS BELOW / CONTINUATION */}
          <div className="results-cell">
            {isOptimizing ? (
              <div className="rounded-md py-8 text-center" style={{ border: `1px solid ${COLOR.line}` }}>
                <span className="spinner inline-block h-5 w-5 rounded-full mb-2" style={{ border: `2px solid ${COLOR.line}`, borderTopColor: COLOR.accent }} />
                <p className="text-sm" style={{ color: COLOR.muted }}>Sequencing stops, checking opening hours, and estimating travel…</p>
              </div>
            ) : isStale ? (
              <div className="rounded-md py-8 text-center" style={{ border: `1px dashed ${COLOR.lineStrong}` }}>
                <Info size={18} color={COLOR.faint} className="mx-auto mb-2" />
                <p className="text-sm" style={{ color: COLOR.muted }}>
                  Your plan has changed. Click <span style={{ color: COLOR.ink, fontWeight: 500 }}>Optimize My Day</span> to see the updated itinerary.
                </p>
              </div>
            ) : (
              <>
                {!result.fits && (
                  <ConflictBanner
                    result={result}
                    windowMinutes={windowMinutes}
                    onRemoveFlexible={handleRemoveFlexible}
                    onStartEarlier={handleStartEarlier}
                    onExtendEnd={handleExtendEnd}
                    hasFlexible={hasFlexible}
                  />
                )}

                <ResultsPanel result={result} mode={mode} hoveredLeg={hoveredLeg} setHoveredLeg={setHoveredLeg} onEditDest={(dest) => openEdit(dest.id)} destinations={destinations} />
                {insight && <InsightCallout text={insight} />}
                {result.stops.length > 0 && (
                  <OrderComparison
                    original={comparisonDestinations.map((d) => d.name)}
                    optimized={result.stops.map((s) => s.dest.name)}
                    excludedNames={result.excluded.map((e) => e.dest.name)}
                    savedMinutes={savedMinutes}
                    originalLength={destinations.length}
                    optimizedLength={result.stops.length}
                  />
                )}
                {result.stops.length > 0 && <WhyThisOrder result={result} />}
              </>
            )}
          </div>
        </div>
      </main>

      {editorOpen && (
        <DestinationEditor
          initial={editingDest ? { ...editingDest, duration: String(editingDest.duration) } : null}
          onSave={saveDestination}
          onCancel={closeEditor}
        />
      )}
    </div>
  );
}


































