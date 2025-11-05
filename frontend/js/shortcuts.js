// ---- Keyboard Shortcuts for onTrack (Windows + macOS) ----
console.log("shortcuts.js loaded");

// Expose helpers so inline HTML can call them (for the ? button)
function toggleHelp() {
  const panel = document.getElementById('shortcut-help');
  if (!panel) { console.warn('No #shortcut-help found'); return; }
  const hidden = panel.getAttribute('aria-hidden') === 'true';
  panel.setAttribute('aria-hidden', String(!hidden));
}
function closeHelp() {
  document.getElementById('shortcut-help')?.setAttribute('aria-hidden', 'true');
}
// Make globally accessible for the inline "?" button
window.toggleHelp = toggleHelp;


// Helper: find a *visible* button by its text (case-insensitive)
function findVisibleButtonByText(txt) {
  const t = txt.trim().toLowerCase();
  return Array.from(document.querySelectorAll('button'))
    .find(b => b.textContent.trim().toLowerCase() === t && b.offsetParent !== null);
}

// Helper: is any dialog/modal open?
function modalIsOpen() {
  return document.querySelector('[role="dialog"]:not([aria-hidden="true"])') ||
         document.querySelector('.modal, .dialog');
}

// Helper: find a *visible* button by its text (case-insensitive)
function findVisibleButtonByText(txt) {
  const t = txt.trim().toLowerCase();
  return Array.from(document.querySelectorAll('button'))
    .find(b => b.textContent.trim().toLowerCase() === t && b.offsetParent !== null);
}

// Helper: is any dialog/modal open?
function modalIsOpen() {
  return document.querySelector('[role="dialog"]:not([aria-hidden="true"])') ||
         document.querySelector('.modal, .dialog');
}

// UPDATED delete logic that checks modal first
function deleteSelectedEvent() {
  if (modalIsOpen()) {
    const modalDelete = findVisibleButtonByText('Delete');
    if (modalDelete) { modalDelete.click(); return; }
  }

  if (typeof window.onDelete === 'function') {
    window.onDelete();
    return;
  }

  const delBtn =
    document.querySelector('[data-action="delete-event"]') ||
    document.getElementById('deleteEventBtn') ||
    document.querySelector('.delete-event');
  delBtn?.click();
}

// ---- Hooks to your actual UI ----
// Try a few common selectors; tweak to match your DOM if needed.
function createEvent() {
  const addBtn =
    document.querySelector('[data-action="add-event"]') ||
    document.getElementById('addEventBtn') ||
    document.querySelector('button.add-event') ||
    // fallback: a button with exact text "Add event"
    Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim().toLowerCase() === 'add event');
  addBtn?.click();
}

function deleteSelectedEvent() {
  const delBtn =
    document.querySelector('[data-action="delete-event"]') ||
    document.getElementById('deleteEventBtn') ||
    document.querySelector('button.delete-event') ||
    // fallback: a button with exact text "Delete"
    Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim().toLowerCase() === 'delete');
  delBtn?.click();
}

function focusTitle() {
  const el =
    document.querySelector('input[name="eventTitle"]') ||
    document.getElementById('title') ||
    document.querySelector('[data-field="title"]') ||
    // fallback: first text input inside your quick add panel
    document.querySelector('aside, .sidebar, .quick-add, .card input[type="text"]') ||
    document.querySelector('input[type="text"]');
  if (el) { el.focus(); el.select?.(); }
}

// ---- Key handling (conflict-free with browsers) ----
// Chosen combos: Shift+A (new), Delete or Shift+Backspace (delete), Shift+E (focus), ? (toggle), Esc (close)
window.addEventListener('keydown', (e) => {
  // console.log('keydown', { key: e.key, code: e.code, shift: e.shiftKey, ctrl: e.ctrlKey, meta: e.metaKey, target: e.target.tagName });

  // Toggle help on "?" (Shift + Slash)
  const isQuestion = e.key === '?' || (e.shiftKey && (e.key === '/' || e.code === 'Slash'));
  if (isQuestion) { e.preventDefault(); toggleHelp(); return; }

  // Close help with Escape
  if (e.key === 'Escape') { closeHelp(); return; }

  // Ignore plain typing in inputs / textareas / contentEditable
  const t = e.target;
  const typing = t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable);
  // For our Shift-based combos we still allow them while typing; remove this if you prefer to block inside inputs.

  // Create new event: Shift + A
  if (e.shiftKey && e.key.toLowerCase() === 'a') {
    e.preventDefault();
    createEvent();
    return;
  }

  // Delete selected: Delete key or Shift + Backspace
  if (e.key === 'Delete' || (e.shiftKey && e.key === 'Backspace')) {
    e.preventDefault();
    deleteSelectedEvent();
    return;
  }

  // Focus title: Shift + E
  if (e.shiftKey && e.key.toLowerCase() === 'e') {
    e.preventDefault();
    focusTitle();
    return;
  }

// Instant delete (no modal): Shift + D
if (e.shiftKey && e.key.toLowerCase() === 'd') {
  e.preventDefault();
  if (typeof window.onDelete === 'function') {
    window.onDelete();  // uses your built-in delete handler
  } else {
    deleteSelectedEvent(); // fallback
  }
  return;
 }

});
