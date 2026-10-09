// Character sprites, drawn in plain screen space with the origin at the
// character's feet. Placed into the room with iso.at().
//
// Biscuit the dog is the player's companion and mirrors the timer:
//   start (idle)       → asleep on the floor
//   ongoing (running)  → sitting up, tail wagging, keeping you company
//   ongoing (paused)   → head tilted, a question mark
//   complete           → bouncing with hearts

const DOG = { fur: '#d49a5c', dark: '#8a5a2e', light: '#f3d9b1', nose: '#2a2420', collar: '#c8463c' };

export function dog(mood) {
  if (mood === 'sleep') return dogSleeping();
  if (mood === 'celebrate') {
    return `<g class="bounce">${dogSitting(false)}</g>${hearts()}`;
  }
  return `<g>${dogSitting(mood === 'curious')}${mood === 'curious' ? bubble('?') : ''}</g>`;
}

function shadow(rx) {
  return `<ellipse cx="0" cy="0" rx="${rx}" ry="${rx / 3}" fill="rgba(60,30,10,.22)"/>`;
}

function dogSitting(tilted) {
  return `
    ${shadow(17)}
    <path class="wag" d="M9 -7 q10 -4 10 -16" stroke="${DOG.fur}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <ellipse cx="6" cy="-7" rx="10" ry="7.5" fill="${DOG.fur}"/>
    <ellipse cx="0" cy="-15" rx="8.5" ry="12" fill="${DOG.fur}"/>
    <ellipse cx="-3.5" cy="-14" rx="4.5" ry="8" fill="${DOG.light}"/>
    <rect x="-7" y="-10" width="3.6" height="10" rx="1.6" fill="${DOG.fur}"/>
    <rect x="-2" y="-10" width="3.6" height="10" rx="1.6" fill="${DOG.fur}"/>
    <path d="M-7 -25 q6 3 11 0" stroke="${DOG.collar}" stroke-width="2.4" fill="none" stroke-linecap="round"/>
    <g class="${tilted ? 'tilt' : 'nod'}">
      <circle cx="-3" cy="-31" r="8.5" fill="${DOG.fur}"/>
      <ellipse cx="-10" cy="-28" rx="6" ry="4.2" fill="${DOG.light}"/>
      <circle cx="-15" cy="-29.5" r="2.1" fill="${DOG.nose}"/>
      <circle cx="-6" cy="-33.5" r="1.4" fill="${DOG.nose}"/>
      <ellipse cx="2.5" cy="-30" rx="3.4" ry="7.5" fill="${DOG.dark}" transform="rotate(14 2.5 -30)"/>
    </g>`;
}

function dogSleeping() {
  return `
    ${shadow(21)}
    <ellipse cx="2" cy="-7" rx="17" ry="8" fill="${DOG.fur}"/>
    <path d="M17 -4 q4 6 -8 6" stroke="${DOG.fur}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <ellipse cx="0" cy="-4" rx="10" ry="3.5" fill="${DOG.light}"/>
    <g class="breathe">
      <circle cx="-12" cy="-8" r="7.5" fill="${DOG.fur}"/>
      <ellipse cx="-18" cy="-5" rx="5.5" ry="3.6" fill="${DOG.light}"/>
      <circle cx="-22.5" cy="-6" r="1.8" fill="${DOG.nose}"/>
      <path d="M-15 -10 q2 1.5 4 0" stroke="${DOG.nose}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
      <ellipse cx="-7" cy="-7" rx="3.2" ry="6.5" fill="${DOG.dark}" transform="rotate(-30 -7 -7)"/>
    </g>
    <g class="zzz" font-family="Georgia, serif" font-weight="700" fill="#8b7a66">
      <text x="-14" y="-22" font-size="8">z</text>
      <text x="-8" y="-31" font-size="10">z</text>
      <text x="0" y="-42" font-size="12">Z</text>
    </g>`;
}

function bubble(text) {
  return `<g class="pop">
    <path d="M-2 -46 h18 a5 5 0 0 1 5 5 v10 a5 5 0 0 1 -5 5 h-10 l-6 5 v-5 h-2 a5 5 0 0 1 -5 -5 v-10 a5 5 0 0 1 5 -5z" fill="#fffdf8" stroke="#d8cbb8"/>
    <text x="7" y="-32" text-anchor="middle" font-family="Georgia, serif" font-weight="700" font-size="13" fill="#6b5b48">${text}</text>
  </g>`;
}

function hearts() {
  const heart = (x, y, s, delay) =>
    `<g transform="translate(${x} ${y}) scale(${s})"><path class="float" style="animation-delay:${delay}s" d="M0 3 C-6 -3 -3 -8 0 -4 C3 -8 6 -3 0 3z" fill="#e2574c"/></g>`;
  return heart(-14, -46, 1.2, 0) + heart(6, -52, 1, 0.5) + heart(-2, -60, 0.9, 1);
}

export function cat() {
  const fur = '#26232a';
  return `
    ${shadow(11)}
    <path class="sway" d="M7 -3 q12 0 9 -14 q-1 -5 3 -7" stroke="${fur}" stroke-width="3.4" fill="none" stroke-linecap="round"/>
    <ellipse cx="2" cy="-9" rx="8" ry="10" fill="${fur}"/>
    <rect x="-4" y="-8" width="3" height="8" rx="1.4" fill="${fur}"/>
    <circle cx="-2" cy="-23" r="7" fill="${fur}"/>
    <path d="M-8 -26 l1 -9 l5 5z M3 -27 l2 -8 l-6 4z" fill="${fur}"/>
    <ellipse class="blink" cx="-5" cy="-23.5" rx="1.4" ry="1.6" fill="#f2c94c"/>
    <ellipse class="blink" cx="0.5" cy="-23.5" rx="1.4" ry="1.6" fill="#f2c94c"/>
    <path d="M-6 -17 q3.5 2 7 0" stroke="#c8463c" stroke-width="1.6" fill="none"/>`;
}
