const fs = require('fs');

const code = import React, { useEffect, useMemo, useState } from "react";
import { MAP, NAV_NODES } from "./cityNetwork";

const COLOR = {
  ink: "#14181F",
  bg: "#F1F3F6",
  block: "#E2E6EC",
  route: "#1D5FCB",
};

const BG_BLOCKS = [
  {x: 100, y: 150, w: 80, h: 60}, {x: 320, y: 80, w: 60, h: 40}, {x: 800, y: 120, w: 100, h: 50},
  {x: 750, y: 220, w: 40, h: 30}, {x: 90, y: 350, w: 50, h: 90}, {x: 120, y: 280, w: 40, h: 40},
  {x: 880, y: 300, w: 70, h: 60}, {x: 70, y: 550, w: 60, h: 40}, {x: 150, y: 580, w: 80, h: 30},
  {x: 850, y: 520, w: 50, h: 50}, {x: 230, y: 700, w: 70, h: 40}, {x: 620, y: 750, w: 50, h: 50},
  {x: 900, y: 680, w: 80, h: 30}, {x: 130, y: 820, w: 60, h: 70}, {x: 820, y: 850, w: 90, h: 50},
  {x: 420, y: 300, w: 60, h: 60}, {x: 480, y: 280, w: 50, h: 70}, {x: 520, y: 320, w: 70, h: 50},
  {x: 650, y: 480, w: 80, h: 40}, {x: 380, y: 450, w: 60, h: 40}, {x: 530, y: 460, w: 50, h: 30},
];

export default function IllustrativeCityMap({ result, hoveredLeg, onSelectDest, selectedId, hoveredId, onHoverDest }) {
  const getFramedBounds = (resultStops) => {
    const activeNodes = [];
    if (NAV_NODES.home) activeNodes.push(NAV_NODES.home);
    
    if (resultStops && resultStops.length > 0) {
      resultStops.forEach(s => {
        const pt = NAV_NODES[s.dest.id];
        if (pt) activeNodes.push(pt);
      });
    }

    if (activeNodes.length === 0) {
      return { x: 0, y: 0, w: 1600, h: 1000 };
    }

    let minX = activeNodes[0].x;
    let maxX = activeNodes[0].x;
    let minY = activeNodes[0].y;
    let maxY = activeNodes[0].y;

    activeNodes.forEach(pt => {
      minX = Math.min(minX, pt.x);
      maxX = Math.max(maxX, pt.x);
      minY = Math.min(minY, pt.y);
      maxY = Math.max(maxY, pt.y);
    });

    const PAD = 150;
    const boundsW = (maxX - minX) + (PAD * 2);
    const boundsH = (maxY - minY) + (PAD * 2);

    const TARGET_RATIO = 1.6;
    let finalW = boundsW;
    let finalH = boundsH;

    if (finalW / finalH < TARGET_RATIO) {
      finalW = finalH * TARGET_RATIO;
    } else {
      finalH = finalW / TARGET_RATIO;
    }

    const MIN_ZOOM_OUT_WIDTH = 1600;
    const MAX_ZOOM_IN_WIDTH = 900;

    if (finalW > MIN_ZOOM_OUT_WIDTH) {
      finalW = MIN_ZOOM_OUT_WIDTH;
      finalH = MIN_ZOOM_OUT_WIDTH / TARGET_RATIO;
    } else if (finalW < MAX_ZOOM_IN_WIDTH) {
      finalW = MAX_ZOOM_IN_WIDTH;
      finalH = MAX_ZOOM_IN_WIDTH / TARGET_RATIO;
    }

    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;

    return {
      x: cx - finalW / 2,
      y: cy - finalH / 2,
      w: finalW,
      h: finalH
    };
  };

  const [viewBox, setViewBox] = useState(() => getFramedBounds(result?.stops));

  useEffect(() => {
    setViewBox(getFramedBounds(result?.stops));
  }, [result]);

  const routeLegs = useMemo(() => {
    if (!result || result.stops.length === 0) return [];
    let legs = [];
    let prev = "home";
    const stops = [...result.stops, { dest: { id: "home" } }];
    
    for (let i = 0; i < stops.length; i++) {
      const stop = stops[i];
      const p1 = NAV_NODES[prev];
      const p2 = NAV_NODES[stop.dest.id];
      if (!p1 || !p2) continue;

      const d = "M " + p1.x + " " + p1.y + " L " + p2.x + " " + p2.y;
      
      let arrows = [];
      const dist = Math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2);
      if (dist > 40) {
        const midX = p1.x + (p2.x - p1.x) * 0.5;
        const midY = p1.y + (p2.y - p1.y) * 0.5;
        const angle = Math.atan2(p2.y - p1.y, p2.x - p1.x) * 180 / Math.PI;
        arrows.push({ x: midX, y: midY, angle });
      }
      legs.push({ u: prev, v: stop.dest.id, d, arrows, index: i });
      prev = stop.dest.id;
    }
    return legs;
  }, [result]);

  const destinations = result ? result.stops.map(s => s.dest) : [];

  return (
    <div className="flex flex-col w-full h-full bg-[#F1F3F6] overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-gray-100 bg-white z-10 shrink-0">
        <div className="flex items-center gap-3">
          <h2 className="font-bold text-gray-900">Map</h2>
          <span className="text-sm text-gray-500">Synthetic demo &middot; not real places or live traffic</span>
        </div>
      </div>

      <div className="relative flex-1 w-full h-full overflow-hidden">
        <svg 
          viewBox={viewBox.x + " " + viewBox.y + " " + viewBox.w + " " + viewBox.h}
          className="absolute inset-0 w-full h-full" 
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill={COLOR.route} />
            </marker>
          </defs>

          {BG_BLOCKS.map((b, i) => (
            <rect key={i} x={b.x} y={b.y} width={b.w} height={b.h} fill={COLOR.block} rx="4" />
          ))}

          {routeLegs.map((leg) => {
            const isHovered = hoveredLeg === leg.index;
            return (
              <g key={leg.u + "-" + leg.v} opacity={hoveredLeg !== null && !isHovered ? 0.3 : 1}>
                <path d={leg.d} stroke={COLOR.route} strokeWidth="3" fill="none" />
                {leg.arrows.map((arr, i) => (
                  <polygon
                    key={i}
                    points="-5,-4 5,0 -5,4"
                    fill={COLOR.route}
                    transform={"translate(" + arr.x + "," + arr.y + ") rotate(" + arr.angle + ") scale(1.2)"}
                  />
                ))}
              </g>
            );
          })}

          {destinations.map((d, i) => {
            const pt = NAV_NODES[d.id];
            if (!pt) return null;
            const isHovered = hoveredId === d.id;
            const isSelected = selectedId === d.id;
            const scale = isHovered || isSelected ? 1.25 : 1;
            const order = String(i + 1);

            return (
              <g
                key={d.id}
                transform={"translate(" + pt.x + "," + pt.y + ") scale(" + scale + ")"}
                style={{ cursor: "pointer", transition: "transform 0.15s ease-out" }}
                onClick={(e) => { e.stopPropagation(); onSelectDest(d.id); }}
                onMouseEnter={() => onHoverDest(d.id)}
                onMouseLeave={() => onHoverDest(null)}
              >
                <circle cx="0" cy="0" r="16" fill="white" stroke={COLOR.ink} strokeWidth="2" />
                <text x="0" y="4" fill={COLOR.ink} fontSize="12" fontWeight="bold" textAnchor="middle" fontFamily="system-ui">
                  {order}
                </text>
              </g>
            );
          })}

          {NAV_NODES.home && (
            <g transform={"translate(" + NAV_NODES.home.x + "," + NAV_NODES.home.y + ")"}>
              <circle cx="0" cy="0" r="16" fill={COLOR.ink} />
              <text x="0" y="4" fill="white" fontSize="12" fontWeight="bold" textAnchor="middle" fontFamily="system-ui">H</text>
              <text x="0" y="28" fill={COLOR.ink} fontSize="12" fontWeight="600" textAnchor="middle" fontFamily="system-ui">Home</text>
            </g>
          )}
        </svg>

        <div className="absolute bottom-4 left-4 flex items-center gap-4 bg-white/90 backdrop-blur px-4 py-2 rounded-full text-xs font-medium text-gray-600 shadow-sm border border-gray-100 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gray-900 flex items-center justify-center">
              <span className="text-[8px] text-white font-bold">H</span>
            </div>
            Home
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full border-2 border-gray-900 bg-white"></div>
            Stop
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-[3px] bg-blue-600"></div>
            Route direction
          </div>
          <div className="flex items-center gap-2 opacity-60">
            <div className="w-4 h-4 rounded-full border-2 border-dashed border-gray-400"></div>
            Excluded
          </div>
        </div>
      </div>
    </div>
  );
};

fs.writeFileSync('src/IllustrativeCityMap.jsx', code);
