// Tunable game constants. Everything balance-related lives here so the
// prototype can be re-tuned without touching game logic.
export const CONFIG = {
  // One focus session ("pomodoro"). The design calls for a one-hour block.
  pomodoroMinutes: 60,

  // Coins paid for a completed session.
  coinsPerPomodoro: 25,

  // Extra coins when a session is completed without ever being paused.
  unbrokenFocusBonus: 5,

  // Cost of pinning one written note to the room.
  noteCost: 2,
  noteMaxLength: 80,

  // Shows the dev panel (Complete now, coin grants, short durations).
  // Can also be toggled with ?debug=0 / ?debug=1 in the URL.
  debug: true,

  // localStorage key for the save file.
  saveKey: 'focus-rooms/save/v1',
};
