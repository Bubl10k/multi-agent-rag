const NODE_WIDTH = 160;
const NODE_HEIGHT = 48;
const H_GAP = 80;
const V_GAP = 64;

export { NODE_WIDTH, NODE_HEIGHT };

export function buildGraphLayout(
  rawNodes: { id: string }[],
  rawEdges: { source: string; target: string }[],
): Map<string, { x: number; y: number }> {
  const childrenOf = new Map<string, string[]>();
  const parentCount = new Map<string, number>();

  for (const n of rawNodes) {
    childrenOf.set(n.id, []);
    parentCount.set(n.id, 0);
  }
  for (const e of rawEdges) {
    childrenOf.get(e.source)?.push(e.target);
    parentCount.set(e.target, (parentCount.get(e.target) ?? 0) + 1);
  }

  const layers: string[][] = [];
  let queue = rawNodes.filter(n => (parentCount.get(n.id) ?? 0) === 0).map(n => n.id);
  const visited = new Set<string>();

  while (queue.length > 0) {
    layers.push(queue);
    queue.forEach(id => visited.add(id));
    const next: string[] = [];
    for (const id of queue) {
      for (const child of childrenOf.get(id) ?? []) {
        if (!visited.has(child)) next.push(child);
      }
    }
    queue = [...new Set(next)];
  }

  const unreached = rawNodes.filter(n => !visited.has(n.id)).map(n => n.id);
  if (unreached.length) layers.push(unreached);

  const positions = new Map<string, { x: number; y: number }>();
  layers.forEach((layer, col) => {
    const totalHeight = layer.length * NODE_HEIGHT + (layer.length - 1) * V_GAP;
    layer.forEach((id, row) => {
      positions.set(id, {
        x: col * (NODE_WIDTH + H_GAP),
        y: row * (NODE_HEIGHT + V_GAP) - totalHeight / 2,
      });
    });
  });

  return positions;
}