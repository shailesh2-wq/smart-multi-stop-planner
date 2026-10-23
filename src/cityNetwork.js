export const MAP = { width: 1000, height: 750 };

export const NAV_NODES = {
  home: { x: 500, y: 420, label: "Home" },
  d1: { x: 700, y: 200, label: "Dentist Appointment" },
  d2: { x: 300, y: 200, label: "City College" },
  d5: { x: 850, y: 600, label: "Harbor Market" },
  d4: { x: 250, y: 650, label: "Pulse Fitness" },
  d3: { x: 750, y: 700, label: "Green Fork Cafe" },
};


export function addNavNode(id, x, y, label) {
  NAV_NODES[id] = { x, y, label };
}

export function nodeForId(destId) {
  return destId;
}

export function getShortestPath(startNode, endNode) {
  const p1 = NAV_NODES[startNode];
  const p2 = NAV_NODES[endNode];
  if (!p1 || !p2) return { distance: 999, pathEdges: [] };
  const dist = Math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2);
  return {
    distance: dist,
    pathEdges: [{ u: startNode, v: endNode }]
  };
}

