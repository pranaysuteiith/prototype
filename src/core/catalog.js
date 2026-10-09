// Everything the player can buy. Positions in the room are owned by the
// renderer (src/ui/room.js); the catalog only describes price, gating and
// flavour, so balancing never touches drawing code.
//
// stage    – journey stage index that unlocks the item (see journey.js)
// requires – item ids that must already be owned

export const CATEGORIES = [
  { id: 'furniture', label: 'Furniture' },
  { id: 'tech', label: 'Tech' },
  { id: 'decor', label: 'Decor' },
  { id: 'life', label: 'Life' },
  { id: 'expansion', label: 'Expansion' },
];

export const ITEMS = [
  // Furniture
  { id: 'desk', name: 'Oak Desk', category: 'furniture', price: 20, stage: 0, description: 'Every journey starts with a place to sit down and work.' },
  { id: 'chair', name: 'Woven Chair', category: 'furniture', price: 15, stage: 0, description: 'Comfortable enough for a whole hour.' },
  { id: 'rug', name: 'Striped Rug', category: 'furniture', price: 25, stage: 1, description: 'Warms up the floorboards.' },
  { id: 'floorLamp', name: 'Floor Lamp', category: 'furniture', price: 30, stage: 1, description: 'Soft light for late sessions.' },
  { id: 'cushion', name: 'Pet Cushion', category: 'furniture', price: 15, stage: 2, description: 'Somewhere for a friend to nap.' },
  { id: 'dresser', name: 'Low Dresser', category: 'furniture', price: 50, stage: 2, description: 'Walnut drawers for all your things.' },
  { id: 'shelf', name: 'Ladder Shelf', category: 'furniture', price: 60, stage: 2, requires: ['dresser'], description: 'Books, a camera, a few keepsakes.' },

  // Tech
  { id: 'computer', name: 'Desktop Computer', category: 'tech', price: 40, stage: 1, requires: ['desk'], description: 'The main tool of the trade.' },
  { id: 'deskLamp', name: 'Desk Lamp', category: 'tech', price: 15, stage: 1, requires: ['desk'], description: 'Focused light for focused work.' },
  { id: 'neon', name: 'Neon Strip', category: 'tech', price: 30, stage: 3, description: 'A cool glow along the corner.' },

  // Decor
  { id: 'window', name: 'Window & Blind', category: 'decor', price: 35, stage: 1, description: 'Let the afternoon sun in.' },
  { id: 'clock', name: 'Wall Clock', category: 'decor', price: 20, stage: 1, description: 'Ticks along with your timer.' },
  { id: 'corkboard', name: 'Corkboard', category: 'decor', price: 20, stage: 1, description: 'Unlocks writing: pin notes, goals and quotes.' },
  { id: 'pegboard', name: 'Pegboard', category: 'decor', price: 20, stage: 2, description: 'A splash of terracotta on the wall.' },
  { id: 'frame', name: 'Framed Print', category: 'decor', price: 25, stage: 2, description: 'A little art for the right wall.' },
  { id: 'candle', name: 'Candle', category: 'decor', price: 10, stage: 3, requires: ['desk'], description: 'A tiny flame for the evening shift.' },
  { id: 'lights', name: 'String Lights', category: 'decor', price: 45, stage: 3, description: 'The room finally feels like yours.' },

  // Life
  { id: 'plant', name: 'Fiddle-leaf Fig', category: 'life', price: 25, stage: 1, description: 'Grows a little with every two sessions.' },
  { id: 'succulent', name: 'Desk Succulent', category: 'life', price: 10, stage: 2, requires: ['desk'], description: 'Low maintenance, high morale.' },
  { id: 'cat', name: 'Black Cat', category: 'life', price: 80, stage: 2, requires: ['cushion'], description: 'Moves in once there is a cushion. Ignores you beautifully.' },

  // Expansion
  { id: 'garden', name: 'Garden Plot', category: 'expansion', price: 120, stage: 4, description: 'Expand outward: a new patch of land beside the room.' },
  { id: 'path', name: 'Stone Path', category: 'expansion', price: 30, stage: 4, requires: ['garden'], description: 'A boardwalk and pebbles from the door to the grass.' },
  { id: 'flowers', name: 'Wildflowers', category: 'expansion', price: 25, stage: 4, requires: ['garden'], description: 'Daisies and dandelions.' },
  { id: 'pines', name: 'Pine Grove', category: 'expansion', price: 60, stage: 5, requires: ['garden'], description: 'A small forest of your own.' },
];

const BY_ID = new Map(ITEMS.map((item) => [item.id, item]));

export function getItem(id) {
  return BY_ID.get(id);
}
