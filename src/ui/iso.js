// Isometric projection and SVG drawing primitives.
//
// World space: x runs toward the right-hand wall's open end, y toward the
// left-hand wall's open end, z is height in screen pixels. One floor tile is
// TILE wide on screen (2:1 isometric).

export const TILE = 40; // half the on-screen width of a tile diamond
export const HALF = TILE / 2;

export function iso(x, y, z = 0) {
  return [(x - y) * TILE, (x + y) * HALF - z];
}

export function pts(points) {
  return points.map(([x, y, z]) => iso(x, y, z).map(round).join(',')).join(' ');
}

export function poly(points, fill, extra = '') {
  return `<polygon points="${pts(points)}" fill="${fill}" ${extra}/>`;
}

const round = (n) => Math.round(n * 10) / 10;

// Axis-aligned cuboid; draws the three faces a viewer can see.
export function box(x, y, z, w, d, h, color, extra = '') {
  const c = typeof color === 'string' ? tones(color) : color;
  return `<g ${extra}>
    ${poly([[x + w, y, z], [x + w, y + d, z], [x + w, y + d, z + h], [x + w, y, z + h]], c.right)}
    ${poly([[x, y + d, z], [x + w, y + d, z], [x + w, y + d, z + h], [x, y + d, z + h]], c.left)}
    ${poly([[x, y, z + h], [x + w, y, z + h], [x + w, y + d, z + h], [x, y + d, z + h]], c.top)}
  </g>`;
}

// Local 2D drawing planes. Inside each group, 1 unit = 1 screen pixel and
// TILE units = one tile, so ordinary <rect>/<circle> art lands flush on the
// surface.

// A vertical plane facing +y (the right-hand wall, fronts of furniture).
// Local u runs along +x, local v runs downward from height z.
export function planeX(x, y, z, inner, extra = '') {
  const [ox, oy] = iso(x, y, z);
  return `<g transform="matrix(1 0.5 0 1 ${round(ox)} ${round(oy)})" ${extra}>${inner}</g>`;
}

// A vertical plane facing +x (the left-hand wall). Local u runs along -y so
// art reads left to right on screen; (x, y) is the plane's left edge.
export function planeY(x, y, z, inner, extra = '') {
  const [ox, oy] = iso(x, y, z);
  return `<g transform="matrix(1 -0.5 0 1 ${round(ox)} ${round(oy)})" ${extra}>${inner}</g>`;
}

// The floor plane at height z. Local u runs along +x, v along +y.
export function planeZ(x, y, z, inner, extra = '') {
  const [ox, oy] = iso(x, y, z);
  return `<g transform="matrix(1 0.5 -1 0.5 ${round(ox)} ${round(oy)})" ${extra}>${inner}</g>`;
}

// Anchors free-standing sprite art (drawn in plain screen space) at a world point.
export function at(x, y, z, inner, extra = '') {
  const [ox, oy] = iso(x, y, z);
  return `<g transform="translate(${round(ox)} ${round(oy)})" ${extra}>${inner}</g>`;
}

// Top / left / right face colours derived from one base colour.
export function tones(hex) {
  return { top: shade(hex, 0.12), left: hex, right: shade(hex, -0.14) };
}

export function shade(hex, amount) {
  const n = parseInt(hex.slice(1), 16);
  const channel = (shift) => {
    const v = (n >> shift) & 255;
    const out = amount >= 0 ? v + (255 - v) * amount : v * (1 + amount);
    return Math.max(0, Math.min(255, Math.round(out)));
  };
  return `#${[16, 8, 0].map((s) => channel(s).toString(16).padStart(2, '0')).join('')}`;
}

// Small deterministic RNG so grass and flowers look the same every render.
export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function escapeXml(text) {
  return String(text).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch]);
}
