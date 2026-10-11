// The Orbit Royale production asset list: the single source for docs/asset-list.md
// and the Asset Hub's tracker. Run: node asset-hub/asset-list.js
// Budgets are proposals for a browser target until hardware/performance targets are agreed.
const fs = require('fs');
const path = require('path');

const M = { found: 'Foundations', trav: 'Traversal', combat: 'Combat and inventory', visual: 'Visual slice', loop: 'Match loop', equip: 'Equipment and rotation', full: 'Full local match' };
const assets = [];
let order = 0;
const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
function add(category, kind, name, o) {
  const id = o.id || slug(name);
  const folder = { model: 'models', audio: 'audio', art: 'art', vfx: 'vfx', ui: 'ui', animation: 'animations' }[kind];
  const ext = { model: 'glb', audio: 'ogg', art: 'png', vfx: 'glb', ui: 'svg', animation: 'glb' }[kind];
  assets.push({
    id, name, category, kind, group: o.group || null, milestone: o.milestone, stage: 'Not started',
    parts: (o.parts || []).map(n => ({ n, done: false })),
    budget: o.budget || null,
    // Game-ready exports live inside the Godot project (res://assets/...); multi-file
    // sets (audio, UI icon sets) get a folder. Editable sources stay outside it in art/.
    path: o.path || (kind === 'audio' || kind === 'ui' ? `game/assets/${folder}/${slug(category)}/${id}/` : `game/assets/${folder}/${slug(category)}/${id}.${ext}`),
    source: ['model', 'animation', 'vfx'].includes(kind) ? `art/${slug(category)}/${id}.blend` : kind === 'audio' ? `art/${slug(category)}/${id}/` : null,
    decision: o.decision || null, notes: o.notes || '', order: order++
  });
}

// ---- Characters
add('Characters', 'model', 'Operator (third-person)', { milestone: M.combat, budget: '20k tris · 2048² textures · 3 LODs', parts: ['Concept sheet', 'Base mesh', 'Materials and textures', 'Rig and skinning', 'LODs', 'Bot variants (gear and color swaps)'], notes: 'One original expedition-suit operator. Bots reuse it with gear and color swaps so 59 bots stay readable.' });
add('Characters', 'model', 'First-person arms', { milestone: M.trav, budget: '8k tris · 2048² textures', parts: ['Mesh', 'Materials', 'Rig matching the operator skeleton'], decision: 'Combat camera: first-person combat is proposed, not approved.' });
add('Characters', 'animation', 'Locomotion set', { milestone: M.trav, parts: ['Idle', 'Walk', 'Sprint', 'Crouch and crouch-walk', 'Jump, fall, land', 'Slow walk while healing'], notes: 'No fall damage: landings from any height need a clean recovery, not a stagger.' });
add('Characters', 'animation', 'Tethercaster traversal set', { milestone: M.trav, parts: ['Fire hook', 'Reel in', 'Swing loop', 'Release and momentum carry'] });
add('Characters', 'animation', 'Weapon handling set', { milestone: M.combat, parts: ['Equip and holster per weapon', 'Hip and aim poses', 'Fire and recoil', 'Reload per weapon', 'Grenade throw'] });
add('Characters', 'animation', 'Healing use set', { milestone: M.combat, parts: ['Field Patch / Trauma Kit (apply)', 'Shield Cell / Pack / Core (insert)', 'Phoenix Capsule (inject)', 'Interrupted exit'] });
add('Characters', 'animation', 'Freefall and landing', { milestone: M.loop, parts: ['Exit transport', 'Freefall pose and steering', 'Descent device deploy', 'Landing'], decision: 'Drop rules: how players slow down after jumping (glider, thruster pack, or none) is undecided.' });
add('Characters', 'animation', 'Vehicle set', { milestone: M.equip, parts: ['Enter and exit (ground vehicles)', 'Driver sit and steer', 'Kestrel pilot', 'Airborne exit'] });
add('Characters', 'animation', 'Elimination', { milestone: M.loop, parts: ['Elimination fall', 'Results screen pose'] });

// ---- Weapons
const W = [
  ['AR-7 Wayfarer', 'Assault rifle', M.combat], ['SG-4 Breaker', 'Shotgun', M.combat],
  ['P-12 Spark', 'Pistol', M.equip], ['S-9 Wisp', 'SMG', M.equip], ['SR-8 Longview', 'Sniper', M.equip]
];
for (const [name, group, ms] of W) {
  add('Weapons', 'model', name, { group, milestone: ms, budget: '12k tris viewmodel · 3k world model · 2048² textures', parts: ['Concept and silhouette', 'First-person viewmodel mesh', 'World / pickup mesh + LODs', 'Materials and textures', 'Rig (magazine, bolt, trigger)', 'Animations: equip, fire, reload, sprint', 'Inventory and HUD icon', 'Fire VFX: muzzle, tracer, casing'] });
  add('Weapon audio', 'audio', `${name} audio`, { id: slug(name) + '-audio', group, milestone: ms, budget: 'WAV 48 kHz mono one-shots (QOA-compressed on import)', parts: ['Fire (close)', 'Fire (distant tail)', 'Reload', 'Equip', 'Dry fire'] });
}

// ---- Items
const H = [
  ['Field Patch', '+25 health · stack 6'], ['Shield Cell', '+25 shields · stack 6'], ['Shield Pack', '+50 shields · stack 3'],
  ['Shield Core', 'Full shields · stack 1'], ['Trauma Kit', 'Full health · stack 1'], ['Phoenix Capsule', 'Full health and shields · stack 1']
];
for (const [name, effect] of H) add('Healing items', 'model', name, { group: effect, milestone: ['Field Patch', 'Shield Pack'].includes(name) ? M.combat : M.equip, budget: '2k tris · 1024² textures', parts: ['Pickup mesh', 'Held mesh', 'Materials', 'Inventory icon', 'Use VFX'], notes: 'Distinct silhouette per item; health items coral, shield items cyan.' });
add('Item audio', 'audio', 'Healing item audio', { milestone: M.combat, parts: ['Use loop per item (6)', 'Use complete', 'Use interrupted', 'Pickup'] });
const G = [['Fragmentation grenade', 'Timed explosive'], ['Arc grenade', 'Shield and vehicle disruption'], ['Veil grenade', 'Concealment cloud']];
for (const [name, role] of G) add('Grenades', 'model', name, { group: role, milestone: M.equip, budget: '1.5k tris · 1024² textures', parts: ['Mesh', 'Materials', 'Inventory icon', 'Detonation VFX'] });
add('Item audio', 'audio', 'Grenade audio', { milestone: M.equip, parts: ['Pin and throw', 'Bounce', 'Frag detonation (close / distant)', 'Arc burst', 'Veil hiss and cloud'] });
add('Utility', 'model', 'Tethercaster', { group: 'Grapple', milestone: M.trav, budget: '6k tris viewmodel · 2048² textures', parts: ['Viewmodel mesh', 'Pickup mesh', 'Hook head', 'Cable material and shader', 'Rig', 'Inventory icon', 'Recharge indicator'] });
add('Item audio', 'audio', 'Tethercaster audio', { milestone: M.trav, parts: ['Fire', 'Anchor hit', 'Reel loop', 'Release', 'Recharge complete'] });
add('Pickups', 'model', 'Ammunition boxes', { milestone: M.combat, budget: '800 tris each', parts: ['Light', 'Medium', 'Heavy', 'Shells'] });
add('Pickups', 'model', 'Colony supply crate', { milestone: M.combat, budget: '3k tris', parts: ['Mesh', 'Open animation', 'Loot glow VFX'], notes: 'Proposed loot source; confirm looting design.' });

// ---- Vehicles
const V = [
  ['Mule', 'Colony buggy · reliable, loud', '35k tris'], ['Skimmer', 'One-seat hover bike · fast, exposed', '25k tris'],
  ['Strider', 'Heavy survey rover · slow, durable', '40k tris'], ['Kestrel', 'Unarmed utility rotorcraft', '40k tris']
];
for (const [name, role, tris] of V) {
  add('Vehicles', 'model', name, { group: role, milestone: M.equip, budget: `${tris} · 2048² textures · 3 LODs`, parts: ['Concept and silhouette', 'Blockout and scale test', 'Exterior mesh + LODs', name === 'Kestrel' ? 'Cockpit interior' : 'Seat and controls', 'Damage states', 'Materials and textures', 'Rig: ' + (name === 'Kestrel' ? 'rotors, skids, doors' : name === 'Skimmer' ? 'hover pads, handlebars' : 'wheels, suspension, doors'), name === 'Kestrel' ? 'Rotor wash VFX' : 'Dust and exhaust VFX'], decision: name === 'Kestrel' ? 'Seating, flight ceiling, energy and airborne exit rules are open.' : null });
  add('Vehicle audio', 'audio', `${name} audio`, { id: slug(name) + '-audio', milestone: M.equip, budget: 'Ogg Vorbis 48 kHz · seamless loops', parts: ['Engine loop (idle / load / high)', 'Distant pass-by (audible warning)', 'Enter / exit', 'Impacts', 'Destroyed'] });
}

// ---- Drop transport
add('Drop transport', 'model', 'Drop transport', { group: 'Start-of-match carrier (working name needed)', milestone: M.loop, budget: '45k tris · 2048² textures · 2 LODs', parts: ['Concept and silhouette', 'Blockout and scale (60 jumpers)', 'Exterior mesh + LODs', 'Interior hold and rear ramp', 'Materials and textures', 'Rig: ramp, engines, landing gear', 'Flight-path and ramp-open animation', 'Engine contrail VFX'], notes: 'Flies a straight line across Ringfall at match start; players jump from the rear ramp. Original colony-carrier design, readable against the ringed sky.', decision: 'Deployment: transport route, jump window and drop rules are undecided.' });
add('Drop transport', 'model', 'Descent device', { milestone: M.loop, budget: '5k tris', parts: ['Concept', 'Mesh', 'Deploy animation', 'Trail VFX'], decision: 'Whether players use a glider, thruster pack or nothing (no fall damage) is undecided.' });
add('Drop transport', 'audio', 'Drop transport audio', { milestone: M.loop, parts: ['Engine loop (exterior, distant)', 'Hold interior ambience', 'Ramp open', 'Jump-out wind gust', 'Freefall wind loop', 'Landing'] });

// ---- Environment: Ringfall
add('Environment', 'model', 'Ringed sky dome', { milestone: M.visual, budget: 'Sky shader + 4096² ring texture', parts: ['Ring band texture and shader', 'Planet and moon', 'Stars and haze', 'Fixed lighting setup'], notes: 'Rings visible from most outdoor locations; start with fixed sky and lighting.' });
add('Environment', 'model', 'Ringfall terrain', { milestone: M.visual, budget: 'Heightmap + 4 splat layers', parts: ['Greybox heightmap', 'Crater lake basin', 'Final heightmap', 'Terrain materials: basalt, grassland, black glass, sand', 'Water shader (turquoise lakes)'], decision: 'Map size and final location layout are undecided.' });
add('Environment', 'model', 'Luminous vegetation kit', { milestone: M.visual, budget: '1–4k tris per plant · instanced', parts: ['Pale grass cards', 'Glowing shrubs', 'Giant Bloomwild plants', 'Luminous roots', 'Emissive material'] });
add('Environment', 'model', 'Colony structure kit', { milestone: M.visual, budget: 'Modular · 2048² trim sheets', parts: ['Habitat module', 'Warehouse', 'Cargo pad', 'Comms mast', 'Gantries and stairs', 'Pipes and cables', 'Amber work lights'] });
add('Environment', 'model', 'Ancient ruins kit', { milestone: M.full, budget: 'Modular · 2048² trim sheets', parts: ['Wall and arch pieces', 'Pillars', 'Bridge spans (The Spine)', 'Canyon ruin set (Hollow Array)'] });
for (const [name, parts] of [
  ['Crown Observatory', ['Telescope domes', 'Fractured comms dish']],
  ['Anchorport', ['Grounded transports', 'Warehouses', 'Cargo containers']],
  ['Glass Basin', ['Black glass formations', 'Islands', 'Ring fragment impact']],
  ['Relay Nine', ['Power station', 'Maintenance tunnels', 'Gantry network']],
  ['The Spine', ['Ancient bridge', 'Cliff high ground']],
  ['Hollow Array', ['Canyon ruins', 'Array structures']],
  ['Bloomwild', ['Giant plant canopy', 'Streams']]
]) add('Locations', 'model', name, { milestone: name === 'Glass Basin' ? M.visual : M.full, parts: ['Layout blockout', ...parts, 'Landmark silhouette pass'], notes: 'Every elevated position needs two attack routes and an escape route.' });
add('Environment', 'model', 'Prop kit', { milestone: M.visual, budget: '0.5–3k tris each', parts: ['Crates and barrels', 'Fences and barriers', 'Lamps', 'Debris', 'Vehicle spawn pads'] });

// ---- VFX
add('VFX', 'vfx', 'Ion storm', { milestone: M.loop, parts: ['Storm wall shader', 'Clouds and particles', 'Distant lightning', 'Boundary interference (screen)'], notes: 'Edge must stay unmistakable in a firefight.' });
add('VFX', 'vfx', 'Combat impacts', { milestone: M.combat, parts: ['Bullet impacts: basalt, grass, metal, glass, water', 'Shield hit', 'Shield break', 'Health hit'] });
add('VFX', 'vfx', 'Healing effects', { milestone: M.combat, parts: ['Health heal particles', 'Shield recharge shimmer'] });
add('VFX', 'vfx', 'Traversal effects', { milestone: M.trav, parts: ['Landing dust', 'Sprint dust', 'Water splash'] });

// ---- UI and brand
add('Brand and UI', 'ui', 'ORBIT logo masters', { milestone: M.visual, parts: ['Stacked lockup', 'Horizontal lockup', 'Orbital emblem', 'Monochrome dark / light', 'Favicon', 'Small-size variants'], notes: 'Planetary O crossed by one orbital arc; ring must not obscure the counter.' });
add('Brand and UI', 'ui', 'Item and weapon icons', { milestone: M.combat, parts: ['5 weapons', '6 healing items', '3 grenades', 'Tethercaster', '4 ammo types'] });
add('Brand and UI', 'ui', 'HUD icon set', { milestone: M.combat, parts: ['Health', 'Shield', 'Survivors', 'Eliminations', 'Storm', 'Map markers', 'Status: success / warning / error'] });
add('Brand and UI', 'ui', 'Controller and key glyphs', { milestone: M.loop, parts: ['Keyboard and mouse', 'Xbox', 'PlayStation'] });
add('Brand and UI', 'art', 'Ringfall map illustration', { milestone: M.loop, budget: '4096² top-down', parts: ['Top-down render', 'Location labels', 'Minimap version'] });
add('Brand and UI', 'art', 'Loading and menu key art', { milestone: M.visual, budget: '3840×2160', parts: ['Ringfall vista', 'Menu composition', 'Loading variants'] });
add('Brand and UI', 'ui', 'Font files', { milestone: M.visual, parts: ['Compare specimens', 'Display family', 'UI family', 'License check and bundling'] });

// ---- Audio: music, ambience, UI, foley
add('Music', 'audio', 'Main menu theme', { milestone: M.loop, budget: 'Loopable · stereo', parts: ['Composition', 'Loop edit', 'Mix'] });
add('Music', 'audio', 'Match stingers', { milestone: M.loop, parts: ['Drop start', 'Storm closing', 'Final survivors', 'Victory', 'Eliminated'] });
add('Ambience', 'audio', 'Ringfall ambience', { milestone: M.visual, parts: ['Wind (open ground)', 'Bloomwild wildlife', 'Glass Basin water', 'Colony hum', 'Interior tone'] });
add('Ambience', 'audio', 'Ion storm audio', { milestone: M.loop, parts: ['Storm wall loop', 'Thunder (distant / close)', 'Inside-storm damage tone'] });
add('UI audio', 'audio', 'Interface sounds', { milestone: M.loop, parts: ['Navigate', 'Confirm', 'Back', 'Toggle', 'Slider tick', 'Error'] });
add('UI audio', 'audio', 'Match feedback sounds', { milestone: M.combat, parts: ['Hit marker', 'Elimination confirm', 'Shield break', 'Low health', 'Pickup', 'Inventory full', 'Storm warning'] });
add('Foley', 'audio', 'Footsteps', { milestone: M.trav, parts: ['Basalt', 'Grass', 'Metal', 'Glass', 'Shallow water', 'Jump and land'] });
add('Voice', 'audio', 'Announcer callouts', { milestone: M.full, parts: ['Storm closing', 'Survivors remaining', 'Victory'], decision: 'Whether the game has announcer voice lines is undecided (subtitles are planned).' });

const out = path.join(__dirname, 'asset-list.json');
fs.writeFileSync(out, JSON.stringify(assets, null, 2) + '\n');

// Readable copy for the repo
const cats = [...new Set(assets.map(a => a.category))];
let md = `# Asset list\n\nGenerated from \`asset-hub/asset-list.js\` (${assets.length} assets). Track progress in the Asset Hub; edit this list in the script and regenerate.\n\nBudgets are proposals for a browser target and change once hardware and performance targets are agreed. Items marked **Decision needed** depend on open design decisions in [claude-handoff.md](claude-handoff.md).\n`;
for (const c of cats) {
  md += `\n## ${c}\n\n| Asset | Milestone | Deliverables | Budget | File |\n|---|---|---|---|---|\n`;
  for (const a of assets.filter(x => x.category === c)) md += `| ${a.name}${a.group ? ` (${a.group})` : ''}${a.decision ? `<br>**Decision needed:** ${a.decision}` : ''} | ${a.milestone} | ${a.parts.map(p => p.n).join('; ')} | ${a.budget || '—'} | \`${a.path}\` |\n`;
}
fs.writeFileSync(path.join(__dirname, '..', 'docs', 'asset-list.md'), md);
console.log(`wrote ${assets.length} assets in ${cats.length} categories`);
