/* @ds-bundle: {"format":4,"namespace":"Orbit","components":[{"name":"ScreenShell"},{"name":"SettingsShell"},{"name":"Button"},{"name":"Tabs"},{"name":"SettingRow"},{"name":"Switch"},{"name":"Slider"},{"name":"Select"},{"name":"BindingCapture"},{"name":"Keycap"},{"name":"Dialog"},{"name":"Toast"},{"name":"LoadingProgress"},{"name":"HUDGroup"},{"name":"InventorySlot"}]} */
(function () {
  // Placeholder glyphs until production icons exist. 24x24 grid, currentColor, 2px strokes.
  var P = {
    health: '<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z" fill="currentColor"/>',
    shield: '<path d="M12 2l8.5 4.9v10.2L12 22l-8.5-4.9V6.9z" fill="currentColor"/>',
    shieldOutline: '<path d="M12 3l7.8 4.5v9L12 21l-7.8-4.5v-9z" fill="none" stroke="currentColor" stroke-width="2"/>',
    rifle: '<path d="M2 10h13l2-2h5v3h-3l-1 2h-4l-1 1v4h-3l-1-3H6l-1 2H3l1-4H2z" fill="currentColor"/>',
    shotgun: '<path d="M1 10h15v2H9l-1 1H5l-2 4H1l1-5H1zM16 9h7v3h-7z" fill="currentColor"/>',
    pistol: '<path d="M4 7h16v4h-9l-1 2H8l-1 5H3l2-7H4z" fill="currentColor"/>',
    smg: '<path d="M3 8h14l2-1h3v3h-5l-1 2h-3v6h-3l-1-6H6l-1 3H3l1-4H3z" fill="currentColor"/>',
    sniper: '<path d="M1 11h21v2h-9l-1 1H8l-2 4H4l1-4H1zM8 7h6v3H8z" fill="currentColor"/>',
    grapple: '<path d="M12 2v13M12 15c-4 0-6-2-6-5M12 15c4 0 6-2 6-5M6 10l-2 2M18 10l2 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="19" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/>',
    grenade: '<circle cx="12" cy="14" r="7" fill="currentColor"/><path d="M10 4h4v3h-4zM14 5l4-2" stroke="currentColor" stroke-width="2" fill="none"/>',
    survivors: '<circle cx="12" cy="7" r="4" fill="currentColor"/><path d="M4 21c0-5 3.5-8 8-8s8 3 8 8z" fill="currentColor"/>',
    eliminations: '<path d="M12 2a9 9 0 0 0-9 9c0 3 1.5 5 3 6v4h12v-4c1.5-1 3-3 3-6a9 9 0 0 0-9-9z" fill="currentColor"/><circle cx="8.5" cy="11" r="2" fill="var(--background)"/><circle cx="15.5" cy="11" r="2" fill="var(--background)"/>',
    storm: '<path d="M13 2L5 14h6l-2 8 10-13h-7z" fill="currentColor"/>',
    check: '<path d="M4 12l5 5L20 6" fill="none" stroke="currentColor" stroke-width="2.5"/>',
    warning: '<path d="M12 3l10 18H2z" fill="currentColor"/><path d="M12 10v5M12 17v2" stroke="var(--background)" stroke-width="2"/>',
    error: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M8 8l8 8M16 8l-8 8" stroke="var(--background)" stroke-width="2.5"/>'
  };
  function icon(name, cls) {
    return '<svg class="' + (cls || '') + '" viewBox="0 0 24 24" aria-hidden="true">' + (P[name] || '') + '</svg>';
  }
  // Fill an or-meter__track (4 segments of 25) from a 0-100 value.
  function meterSegments(value) {
    var out = '';
    for (var i = 0; i < 4; i++) {
      var pct = Math.max(0, Math.min(25, value - i * 25)) * 4;
      out += '<span class="or-meter__seg"><i style="width:' + pct + '%"></i></span>';
    }
    return out;
  }
  window.Orbit = window.Orbit || {};
  window.Orbit.icon = icon;
  window.Orbit.icons = Object.keys(P);
  window.Orbit.meterSegments = meterSegments;
})();
