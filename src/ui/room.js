import { growthOf } from '../core/game.js';
import { STATUS } from '../core/timer.js';
import { cat, dog } from './assets.js';
import { at, box, escapeXml, iso, planeX, planeY, planeZ, poly, rng, shade, TILE } from './iso.js';

// Builds the isometric room as one SVG string from game state. The art is a
// cut-away diorama: a floor island with two back walls, sitting on a slab of
// grass and soil, plus an optional garden island once the player expands.

const N = 6; // floor size in tiles
const RIM = 6.6; // island edge (grass rim in front of the floor)
const WALL_H = 160;
const WALL_T = 0.18;
const SLAB = 58;
const GARDEN = { x0: RIM, x1: 10.4, y0: 1.0, y1: RIM, z: -12 };

const C = {
  wallLeft: '#f5ede2',
  wallRight: '#ebe0d1',
  wallCap: '#fffaf2',
  wallEnd: '#dcd0bf',
  wood: '#b8743d',
  woodDark: '#99602f',
  floor: '#b97a45',
  grass: '#6ea545',
  grassDark: '#4f8a32',
  soil: ['#5f9a3a', '#6d4b2f', '#80593a', '#5b3e27'],
};

// Everything that changes the picture except the clock hand, which the app
// rotates directly every second.
export function roomKey(state) {
  return JSON.stringify([
    Object.keys(state.owned).sort(),
    state.notes,
    state.timer.status,
    growthOf(state, 'plant'),
  ]);
}

export function renderRoom(state) {
  const has = (id) => Boolean(state.owned[id]);
  const status = state.timer.status;
  const lit = status === STATUS.RUNNING || status === STATUS.PAUSED;
  const viewBox = has('garden') ? '-300 -200 700 620' : '-300 -200 600 540';

  const floorItems = [
    has('desk') && { depth: 3.8, svg: desk(has, lit) },
    has('chair') && { depth: 4.9, svg: chair() },
    has('dresser') && { depth: 5.1, svg: dresser(has('shelf')) },
    has('floorLamp') && { depth: 5.7, svg: floorLamp(lit) },
    has('plant') && { depth: 7.2, svg: at(5.45, 1.75, 0, plant(growthOf(state, 'plant'))) },
    has('cushion') && { depth: 7.9, svg: cushion(has('cat')) },
    { depth: 7.6, svg: companion(status) },
  ].filter(Boolean);
  floorItems.sort((a, b) => a.depth - b.depth);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${viewBox}" class="room-svg ${status}" role="img" aria-label="Your room">
    ${defs()}
    <ellipse cx="${has('garden') ? 60 : 0}" cy="${has('garden') ? 360 : 330}" rx="${has('garden') ? 360 : 300}" ry="46" fill="url(#groundShadow)"/>
    ${slab(-WALL_T, RIM, -WALL_T, RIM, 0, SLAB, 11)}
    ${floor()}
    ${walls()}
    ${has('window') ? sunlight() : ''}
    ${wallDecor(state, has, lit)}
    ${has('rug') ? rug() : ''}
    ${floorItems.map((item) => item.svg).join('')}
    ${has('garden') ? garden(has) : ''}
  </svg>`;
}

function defs() {
  return `<defs>
    <radialGradient id="groundShadow"><stop offset="0" stop-color="rgba(60,40,20,.28)"/><stop offset="1" stop-color="rgba(60,40,20,0)"/></radialGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="rgba(255,214,140,.75)"/><stop offset="1" stop-color="rgba(255,214,140,0)"/></radialGradient>
    <radialGradient id="neonGlow"><stop offset="0" stop-color="rgba(140,200,255,.6)"/><stop offset="1" stop-color="rgba(140,200,255,0)"/></radialGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff8e6"/><stop offset="1" stop-color="#f3dcb2"/></linearGradient>
    <linearGradient id="screenOn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8ec5f0"/><stop offset="1" stop-color="#4f7fc4"/></linearGradient>
    <linearGradient id="gardenGrass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7cb84e"/><stop offset="1" stop-color="#5e9a3b"/></linearGradient>
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>`;
}

// ---------------------------------------------------------------- ground

// A grass-topped block of soil spanning [x0,x1] × [y0,y1], top at height z.
function slab(x0, x1, y0, y1, z, depth, seed) {
  const bands = [0, -7, -24, -38, -depth].map((d) => z + d);
  let sides = '';
  for (let i = 0; i < bands.length - 1; i++) {
    const [top, bottom] = [bands[i], bands[i + 1]];
    const color = C.soil[i];
    sides += poly([[x0, y1, bottom], [x1, y1, bottom], [x1, y1, top], [x0, y1, top]], color);
    sides += poly([[x1, y0, bottom], [x1, y1, bottom], [x1, y1, top], [x1, y0, top]], shade(color, -0.16));
  }
  const top = poly([[x0, y0, z], [x1, y0, z], [x1, y1, z], [x0, y1, z]], C.grass);
  return sides + top + grassFringe(x0, x1, y0, y1, z, seed);
}

// Little blades hanging over the front edges so the slab reads as turf.
function grassFringe(x0, x1, y0, y1, z, seed) {
  const rand = rng(seed);
  let out = '';
  const blade = (x, y) => {
    const [sx, sy] = iso(x, y, z);
    const h = 4 + rand() * 6;
    const lean = (rand() - 0.5) * 4;
    const color = rand() > 0.5 ? C.grass : C.grassDark;
    return `<path d="M${(sx - 2).toFixed(1)} ${(sy - 1).toFixed(1)} l${(2 + lean).toFixed(1)} ${h.toFixed(1)} l2 ${(-h).toFixed(1)}z" fill="${color}"/>`;
  };
  for (let x = x0; x < x1; x += 0.09) out += blade(x, y1);
  for (let y = y0; y < y1; y += 0.09) out += blade(x1, y);
  return out;
}

function floor() {
  const rand = rng(3);
  let planks = '';
  const rowH = TILE / 2;
  for (let row = 0; row < N * 2; row++) {
    const v = row * rowH;
    planks += `<rect x="0" y="${v}" width="${N * TILE}" height="${rowH}" fill="${shade(C.floor, (rand() - 0.5) * 0.12)}"/>`;
    let u = -rand() * 60;
    while (u < N * TILE) {
      u += 50 + rand() * 50;
      if (u < N * TILE) planks += `<rect x="${u.toFixed(1)}" y="${v}" width="1.2" height="${rowH}" fill="${C.woodDark}" opacity=".55"/>`;
    }
    planks += `<rect x="0" y="${v}" width="${N * TILE}" height="1" fill="${C.woodDark}" opacity=".6"/>`;
  }
  // Floor edge thickness so the boards sit slightly proud of the grass.
  const lip = poly([[0, N, 0], [N, N, 0], [N, N, 3], [0, N, 3]], '#8e5a30') + poly([[N, 0, 0], [N, N, 0], [N, N, 3], [N, 0, 3]], '#7c4e29');
  return lip + planeZ(0, 0, 3, planks);
}

// ---------------------------------------------------------------- walls

function walls() {
  const h = WALL_H;
  const t = WALL_T;
  return `
    ${poly([[0, 0, 3], [0, N, 3], [0, N, h], [0, 0, h]], C.wallLeft)}
    ${poly([[0, 0, 3], [N, 0, 3], [N, 0, h], [0, 0, h]], C.wallRight)}
    ${poly([[0, 0, 3], [1.2, 0, 3], [0, 0, h]], 'rgba(120,90,60,.06)')}
    ${poly([[0, 0, 3], [0, 1.2, 3], [0, 0, h]], 'rgba(120,90,60,.05)')}
    ${planeY(0, N, 9, `<rect x="0" y="0" width="${N * TILE}" height="6" fill="#e7d9c6"/>`)}
    ${planeX(0, 0, 9, `<rect x="0" y="0" width="${N * TILE}" height="6" fill="#ddcdb8"/>`)}
    ${poly([[-t, N, -1], [0, N, -1], [0, N, h], [-t, N, h]], C.wallEnd)}
    ${poly([[N, -t, -1], [N, 0, -1], [N, 0, h], [N, -t, h]], shade(C.wallEnd, -0.08))}
    ${poly([[-t, -t, h], [-t, N, h], [0, N, h], [0, 0, h]], C.wallCap)}
    ${poly([[-t, -t, h], [N, -t, h], [N, 0, h], [0, 0, h]], C.wallCap)}`;
}

function sunlight() {
  return poly([[1.6, 0.05, 3.2], [3.8, 0.05, 3.2], [4.9, 2.9, 3.2], [2.7, 2.9, 3.2]], '#fff1cf', 'opacity=".38"');
}

function wallDecor(state, has, lit) {
  let out = '';
  if (has('window')) out += windowArt();
  if (has('neon')) out += neon();
  if (has('frame')) out += frameArt();
  if (has('clock')) out += clock();
  if (has('pegboard')) out += pegboard();
  if (has('corkboard')) out += corkboard(state.notes);
  if (has('lights')) out += stringLights(lit);
  return out;
}

function windowArt() {
  return planeX(1.3, 0, 138, `
    <rect x="-3" y="0" width="94" height="76" fill="#fbf8f2"/>
    <rect x="4" y="20" width="38" height="50" fill="url(#glass)"/>
    <rect x="47" y="20" width="38" height="50" fill="url(#glass)"/>
    <rect x="2" y="2" width="85" height="26" fill="#efe1c9"/>
    <rect x="2" y="26" width="85" height="3" fill="#d9c6a6"/>
    <rect x="-6" y="74" width="100" height="5" fill="#f1e9dc"/>`);
}

function neon() {
  const strip = (u) => `<rect x="${u - 10}" y="-5" width="22" height="140" fill="url(#neonGlow)" class="neon-glow"/><rect x="${u}" y="0" width="3" height="130" rx="1.5" fill="#bfe4ff"/>`;
  return planeX(0, 0, 148, strip(10) + strip(150));
}

function frameArt() {
  return planeX(5.15, 0, 132, `
    <rect x="0" y="0" width="30" height="26" fill="#6b4a2f"/>
    <rect x="3" y="3" width="24" height="20" fill="#f3e7d1"/>
    <circle cx="19" cy="9" r="3" fill="#e0a84f"/>
    <path d="M3 23 l8 -9 l5 5 l4 -4 l7 8z" fill="#7c9a6a"/>`);
}

function clock() {
  return planeY(0, 1.45, 152, `
    <circle cx="18" cy="18" r="17" fill="#f8f5ef" stroke="#4b4640" stroke-width="3"/>
    ${[0, 1, 2, 3].map((i) => `<rect x="17.2" y="3.5" width="1.6" height="3" fill="#4b4640" transform="rotate(${i * 90} 18 18)"/>`).join('')}
    <rect x="17" y="10" width="2" height="9" rx="1" fill="#4b4640" transform="rotate(300 18 18)"/>
    <rect id="clock-minute" x="17.4" y="4.5" width="1.2" height="14" rx=".6" fill="#c8463c" transform="rotate(0 18 18)"/>
    <circle cx="18" cy="18" r="1.6" fill="#4b4640"/>`);
}

function pegboard() {
  let holes = '';
  for (let r = 0; r < 5; r++) for (let c = 0; c < 5; c++) holes += `<circle cx="${5 + c * 6}" cy="${5 + r * 6}" r="1.2" fill="#a9512b"/>`;
  return planeY(0, 2.6, 140, `<rect x="0" y="0" width="34" height="34" rx="1.5" fill="#d9733f"/>${holes}`);
}

function corkboard(notes) {
  const slots = notes.slice(0, 6).map((note, i) => {
    const x = 6 + (i % 3) * 18;
    const y = 6 + Math.floor(i / 3) * 18;
    const tilt = ((note.id * 37) % 11) - 5;
    return `<g transform="rotate(${tilt} ${x + 7} ${y + 6})"><title>${escapeXml(note.text)}</title>
      <rect x="${x}" y="${y}" width="14" height="13" fill="${note.color}" stroke="rgba(0,0,0,.08)"/>
      <rect x="${x + 2.5}" y="${y + 4}" width="9" height="1" fill="rgba(0,0,0,.25)"/>
      <rect x="${x + 2.5}" y="${y + 7}" width="6" height="1" fill="rgba(0,0,0,.25)"/>
      <circle cx="${x + 7}" cy="${y + 1.5}" r="1.5" fill="#c8463c"/></g>`;
  });
  return planeY(0, 4.35, 146, `
    <rect x="0" y="0" width="62" height="46" fill="#b98b5c"/>
    <rect x="3" y="3" width="56" height="40" fill="#d9b78e"/>
    ${slots.join('')}`);
}

// Two swags of bulbs along the top of each wall.
function stringLights(lit) {
  const swag = () => {
    let path = 'M0 4';
    let bulbs = '';
    const span = (N * TILE) / 3;
    for (let s = 0; s < 3; s++) {
      const u0 = s * span;
      path += ` Q${u0 + span / 2} 30 ${u0 + span} 4`;
      for (let k = 1; k < 8; k++) {
        const t = k / 8;
        const u = u0 + span * t;
        const v = (1 - t) * (1 - t) * 4 + 2 * (1 - t) * t * 30 + t * t * 4;
        bulbs += `<circle class="twinkle" style="animation-delay:${((s * 8 + k) % 5) * 0.35}s" cx="${u.toFixed(1)}" cy="${(v + 2).toFixed(1)}" r="2.2" fill="#ffdb85"/>`;
      }
    }
    return `<path d="${path}" stroke="#6a5a48" stroke-width=".8" fill="none"/>${bulbs}`;
  };
  const cls = `string-lights ${lit ? 'on' : ''}`;
  return planeX(0, 0, 154, swag(), `class="${cls}"`) + planeY(0, N, 154, swag(), `class="${cls}"`);
}

// ---------------------------------------------------------------- furniture

function floorShadow(x, y, w, d) {
  return poly([[x + 0.08, y + 0.1, 3.2], [x + w + 0.15, y + 0.1, 3.2], [x + w + 0.15, y + d + 0.15, 3.2], [x + 0.08, y + d + 0.15, 3.2]], 'rgba(70,35,10,.18)', 'filter="url(#soft)"');
}

function desk(has, lit) {
  const legs = [[0.16, 1.86], [1.12, 1.86], [0.16, 4.28], [1.12, 4.28]]
    .map(([x, y]) => box(x, y, 3, 0.07, 0.07, 42, C.woodDark))
    .join('');
  const drawers = planeY(1.27, 4.4, 52, `
    <rect x="8" y="1.5" width="40" height="7" rx="1" fill="#f1ebe1"/>
    <rect x="56" y="1.5" width="40" height="7" rx="1" fill="#f1ebe1"/>
    <rect x="25" y="4.5" width="6" height="1.4" rx=".7" fill="#9a8a75"/>
    <rect x="73" y="4.5" width="6" height="1.4" rx=".7" fill="#9a8a75"/>`);
  let onTop = '';
  if (has('computer')) onTop += computer(lit);
  if (has('candle')) onTop += at(1.0, 2.05, 57, candle());
  if (has('deskLamp')) onTop += at(0.35, 4.1, 57, deskLamp(lit));
  if (has('succulent')) onTop += at(0.85, 4.15, 57, succulent());
  return `<g>
    ${floorShadow(0.12, 1.8, 1.15, 2.6)}
    ${legs}
    ${box(0.14, 1.82, 42, 1.13, 2.56, 10, C.wood)}
    ${drawers}
    ${box(0.1, 1.78, 52, 1.19, 2.64, 5, C.wood)}
    ${onTop}
  </g>`;
}

function computer(lit) {
  const screen = lit
    ? `<rect x="2" y="2" width="36" height="22" fill="url(#screenOn)"/>
       <rect x="5" y="6" width="16" height="2" fill="rgba(255,255,255,.75)"/>
       <rect x="5" y="11" width="24" height="2" fill="rgba(255,255,255,.5)"/>
       <rect x="5" y="16" width="12" height="2" fill="rgba(255,255,255,.5)"/>`
    : `<rect x="2" y="2" width="36" height="22" fill="#141418"/>`;
  return `
    ${box(0.36, 2.95, 57, 0.18, 0.28, 2, '#d6d6d6')}
    ${box(0.4, 3.04, 59, 0.05, 0.1, 10, '#cfcfcf')}
    ${box(0.32, 2.55, 66, 0.07, 1.0, 28, '#2a2a2e')}
    ${planeY(0.39, 3.55, 94, screen)}
    ${box(0.75, 2.75, 57, 0.24, 0.62, 1.5, '#f3f3f3')}
    ${box(0.82, 3.55, 57, 0.08, 0.06, 1.5, '#f3f3f3')}`;
}

function deskLamp(lit) {
  return `
    ${lit ? `<circle cx="10" cy="-16" r="30" fill="url(#glow)"/>` : ''}
    <ellipse cx="0" cy="0" rx="6" ry="2.6" fill="#3b3a38"/>
    <path d="M0 -1 L3 -18 L13 -25" stroke="#3b3a38" stroke-width="1.8" fill="none" stroke-linecap="round"/>
    <path d="M9 -28 l9 2 l-4 9z" fill="#3b3a38"/>`;
}

function candle() {
  return `
    <circle class="flicker" cx="0" cy="-12" r="16" fill="url(#glow)"/>
    <rect x="-3.5" y="-9" width="7" height="9" rx="1" fill="#f4ead8"/>
    <ellipse cx="0" cy="-9" rx="3.5" ry="1.4" fill="#fff7ea"/>
    <path class="flicker" d="M0 -16 q2.4 3 0 5 q-2.4 -2 0 -5z" fill="#ffb347"/>`;
}

function succulent() {
  return `
    <path d="M-4.5 -6 h9 l-1.4 6 h-6.2z" fill="#e8e1d6"/>
    <path d="M0 -6 l-4 -6 l3 1 l1 -5 l1 5 l3 -1z" fill="#7aa35a"/>`;
}

function chair() {
  const legs = [[1.57, 2.82], [2.05, 2.82], [1.57, 3.35], [2.05, 3.35]]
    .map(([x, y]) => box(x, y, 3, 0.05, 0.05, 25, '#8f5a31'))
    .join('');
  let weave = '';
  for (let i = 0; i < 5; i++) weave += `<rect x="${2 + i * 4.4}" y="3" width="1.4" height="26" fill="#a9532f"/>`;
  for (let j = 0; j < 4; j++) weave += `<rect x="1" y="${5 + j * 6.5}" width="22" height="1.4" fill="#a9532f"/>`;
  return `<g>
    ${floorShadow(1.5, 2.8, 0.6, 0.6)}
    ${legs}
    ${box(1.55, 2.8, 28, 0.56, 0.62, 4, '#c58a55')}
    ${box(2.03, 2.83, 32, 0.07, 0.56, 32, '#b5784a')}
    ${planeY(2.1, 3.39, 64, `<rect x="0" y="0" width="22.4" height="32" fill="#cf7b4c"/>${weave}`)}
  </g>`;
}

function floorLamp(lit) {
  return at(0.45, 5.35, 3, `
    ${lit ? `<circle cx="0" cy="-122" r="56" fill="url(#glow)"/>` : ''}
    <ellipse cx="0" cy="0" rx="9" ry="3.6" fill="#33312e"/>
    <rect x="-1" y="-116" width="2" height="116" fill="#3b3a38"/>
    <path d="M-11 -146 h22 l6 30 h-34z" fill="${lit ? '#fff4dc' : '#f4ece0'}" stroke="#e2d6c3"/>`);
}

function dresser(withShelf) {
  const fronts = planeX(3.85, 0.78, 46, `
    <rect x="3" y="4" width="32" height="17" rx="1" fill="#8c5835"/>
    <rect x="37" y="4" width="32" height="17" rx="1" fill="#8c5835"/>
    <rect x="3" y="24" width="32" height="17" rx="1" fill="#8c5835"/>
    <rect x="37" y="24" width="32" height="17" rx="1" fill="#8c5835"/>
    ${[[19, 12], [53, 12], [19, 32], [53, 32]].map(([u, v]) => `<circle cx="${u}" cy="${v}" r="1.6" fill="#e3c27a"/>`).join('')}`);
  let shelf = '';
  if (withShelf) {
    const plank = (z) => box(3.95, 0.12, z, 0.96, 0.5, 3, '#a36a3b');
    shelf = `
      ${box(3.98, 0.12, 46, 0.05, 0.05, 106, '#7a4a2a')}
      ${box(4.86, 0.12, 46, 0.05, 0.05, 106, '#7a4a2a')}
      ${plank(78)}
      ${box(4.05, 0.2, 81, 0.1, 0.3, 18, '#5d7f9a')}${box(4.17, 0.2, 81, 0.08, 0.3, 22, '#c8a24a')}${box(4.27, 0.2, 81, 0.1, 0.3, 16, '#8f3b32')}
      ${box(4.55, 0.25, 81, 0.25, 0.25, 9, '#d9d2c4')}
      ${plank(110)}
      ${box(4.1, 0.25, 113, 0.28, 0.2, 13, '#2f2d2b')}
      ${box(4.6, 0.22, 113, 0.18, 0.3, 14, '#e7dcc8')}
      ${plank(144)}
      ${box(4.15, 0.2, 147, 0.08, 0.36, 22, '#c8463c')}${box(4.25, 0.2, 147, 0.08, 0.36, 18, '#e0a84f')}
      ${box(3.98, 0.58, 46, 0.05, 0.05, 106, '#8a5531')}
      ${box(4.86, 0.58, 46, 0.05, 0.05, 106, '#8a5531')}`;
  }
  return `<g>
    ${floorShadow(3.85, 0.08, 1.75, 0.7)}
    ${box(3.85, 0.08, 3, 1.75, 0.7, 43, '#7a4a2a')}
    ${fronts}
    ${shelf}
  </g>`;
}

function plant(growth) {
  const rand = rng(41);
  const stem = 30 + growth * 16;
  const leafCount = 5 + growth * 3;
  const size = 1 + growth * 0.12;
  let leaves = '';
  for (let i = 0; i < leafCount; i++) {
    const y = -20 - (stem * (i + 1)) / leafCount;
    const side = i % 2 ? 1 : -1;
    const x = side * (4 + rand() * 6);
    const angle = side * (25 + rand() * 30);
    const green = ['#4f8a32', '#5f9b3c', '#3f7428', '#6aa547'][i % 4];
    leaves += `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${(8 * size).toFixed(1)}" ry="${(5.2 * size).toFixed(1)}" fill="${green}" transform="rotate(${angle.toFixed(0)} ${x.toFixed(1)} ${y.toFixed(1)})"/>`;
  }
  return `
    <ellipse cx="0" cy="0" rx="14" ry="5" fill="rgba(60,30,10,.22)"/>
    <rect x="-1" y="${-20 - stem}" width="2" height="${stem}" fill="#6b5a3a"/>
    ${leaves}
    <path d="M-10 -20 h20 l-3 20 h-14z" fill="#c9965c"/>
    <path d="M-10 -20 h20 v3 h-20z" fill="#b07e47"/>
    <path d="M-8.5 -12 h17 M-8 -6 h16" stroke="#a87642" stroke-width="1"/>
    <rect x="-7" y="0" width="1.6" height="5" fill="#3b3a38"/><rect x="5.4" y="0" width="1.6" height="5" fill="#3b3a38"/>`;
}

function cushion(withCat) {
  return `<g>
    ${box(3.4, 3.55, 3, 1.0, 0.9, 6, '#ece0cb')}
    ${planeZ(3.4, 3.55, 9.1, `<rect x="4" y="4" width="32" height="28" rx="6" fill="none" stroke="#d7c6a8" stroke-width="1.2"/>`)}
    ${withCat ? at(3.95, 4.05, 9, cat()) : ''}
  </g>`;
}

function rug() {
  let stripes = '';
  const colors = ['#c46a4a', '#8b5e3c', '#c46a4a'];
  for (let i = 0; i < 9; i++) stripes += `<rect x="6" y="${8 + i * 11}" width="76" height="${i % 3 === 1 ? 3 : 1.6}" fill="${colors[i % 3]}" opacity=".85"/>`;
  let fringe = '';
  for (let v = 2; v < 106; v += 3) fringe += `<rect x="-3" y="${v}" width="3" height=".8" fill="#e2d6c1"/><rect x="88" y="${v}" width="3" height=".8" fill="#e2d6c1"/>`;
  return planeZ(1.45, 1.95, 3.6, `<rect x="0" y="0" width="88" height="108" fill="#efe6d5"/>${stripes}${fringe}`);
}

function companion(status) {
  const mood = { idle: 'sleep', running: 'focus', paused: 'curious', complete: 'celebrate' }[status];
  const [x, y] = mood === 'sleep' ? [3.0, 5.15] : [2.6, 4.7];
  return at(x, y, 3, dog(mood), `class="companion"`);
}

// ---------------------------------------------------------------- garden

function garden(has) {
  const { x0, x1, y0, y1, z } = GARDEN;
  const rand = rng(77);
  let tufts = '';
  for (let i = 0; i < 70; i++) {
    const [sx, sy] = iso(x0 + rand() * (x1 - x0), y0 + rand() * (y1 - y0), z);
    tufts += `<path d="M${sx.toFixed(1)} ${sy.toFixed(1)} l-2 -5 l2 3 l1 -6 l1 6 l2 -3 l-2 5z" fill="${C.grassDark}" opacity=".7"/>`;
  }
  let flowers = '';
  if (has('flowers')) {
    for (let i = 0; i < 70; i++) {
      const gx = x0 + 0.15 + rand() * (x1 - x0 - 0.3);
      const gy = y0 + 0.15 + rand() * (y1 - y0 - 0.3);
      if (has('path') && Math.abs(gy - pathY(gx)) < 0.45) continue;
      const [sx, sy] = iso(gx, gy, z);
      const color = rand() > 0.45 ? '#fffdf5' : '#f2c94c';
      flowers += `<circle cx="${sx.toFixed(1)}" cy="${(sy - 2).toFixed(1)}" r="1.8" fill="${color}"/><circle cx="${sx.toFixed(1)}" cy="${(sy - 2).toFixed(1)}" r=".7" fill="#e0a84f"/>`;
    }
  }
  let pines = '';
  if (has('pines')) {
    const spots = [[7.2, 1.6], [8.1, 1.4], [7.6, 2.3], [8.9, 1.9], [9.6, 4.9], [8.8, 5.6], [9.8, 5.9], [7.4, 5.6], [8.1, 6.1], [9.9, 2.4]];
    spots.sort((a, b) => a[0] + a[1] - (b[0] + b[1]));
    pines = spots.map(([px, py], i) => at(px, py, z, pine(38 + ((i * 7) % 4) * 7))).join('');
  }
  return `<g class="garden">
    ${slab(x0, x1, y0, y1, z, SLAB, 19).replace(new RegExp(C.grass, 'g'), 'url(#gardenGrass)')}
    ${tufts}
    ${has('path') ? gardenPath() : ''}
    ${flowers}
    ${pines}
  </g>`;
}

function pathY(x) {
  return 3.4 + Math.sin((x - RIM) * 1.3) * 0.5;
}

function gardenPath() {
  let boards = '';
  for (let i = 0; i < 6; i++) boards += box(6.0 + i * 0.11, 3.0, 1, 0.09, 0.75, 2, i % 2 ? '#a77446' : '#b5804f');
  const rand = rng(5);
  let stones = '';
  for (let x = GARDEN.x0 + 0.1; x < 9.8; x += 0.12) {
    for (let k = 0; k < 3; k++) {
      const y = pathY(x) + (rand() - 0.5) * 0.8;
      const [sx, sy] = iso(x + rand() * 0.1, y, GARDEN.z);
      const grey = ['#b9b3a8', '#a19a8e', '#cfc9bf', '#8f897f'][Math.floor(rand() * 4)];
      stones += `<ellipse cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" rx="${(3 + rand() * 2).toFixed(1)}" ry="${(1.8 + rand()).toFixed(1)}" fill="${grey}"/>`;
    }
  }
  return boards + stones;
}

function pine(height) {
  const w = height * 0.42;
  const tiers = [0, 1, 2]
    .map((i) => {
      const top = -height + i * height * 0.24;
      const bottom = top + height * 0.5;
      const half = w * (0.55 + i * 0.22);
      return `<path d="M0 ${top.toFixed(1)} L${half.toFixed(1)} ${bottom.toFixed(1)} L${(-half).toFixed(1)} ${bottom.toFixed(1)}z" fill="${['#5f9440', '#4f8436', '#3f6e2b'][i]}"/>`;
    })
    .reverse()
    .join('');
  return `
    <ellipse cx="2" cy="0" rx="${(w * 0.6).toFixed(1)}" ry="${(w * 0.22).toFixed(1)}" fill="rgba(40,60,20,.3)"/>
    <rect x="-1.6" y="-9" width="3.2" height="9" fill="#6b4a2f"/>
    ${tiers}`;
}
