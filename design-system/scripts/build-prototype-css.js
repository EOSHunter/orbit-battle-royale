// Compiles project/tokens.json to CSS custom properties and copies the component
// stylesheet and helpers into prototype/ds/ and asset-hub/ds/, so both pages run on the design system.
// Run: node design-system/scripts/build-prototype-css.js
const fs = require('fs');
const path = require('path');
const ds = path.join(__dirname, '..', 'project');
const outs = ['prototype', 'asset-hub'].map(d => path.join(__dirname, '..', '..', d, 'ds'));
const t = JSON.parse(fs.readFileSync(path.join(ds, 'tokens.json'), 'utf8'));
const theme = t.color.themes[0].id;

const lines = [];
for (const c of t.color.tokens) lines.push(`  --${c.name}: ${typeof c.value === 'string' ? c.value : c.value[theme]};`);
for (const fam of ['spacing', 'size', 'radius']) for (const s of t[fam].tokens) lines.push(`  --${s.name}: ${s.value};`);
for (const [k, v] of Object.entries(t.type.families)) lines.push(`  --font-${k}: ${v};`);

const styles = t.type.groups.flatMap(g => g.styles.map(s => {
  const fam = s.family || g.family;
  return `.${s.name} { font-family: var(--font-${fam}); font-size: ${s.fontSize}; line-height: ${s.lineHeight}; font-weight: ${s.fontWeight};${s.letterSpacing ? ` letter-spacing: ${s.letterSpacing};` : ''} }`;
}));

const tokensCss = `/* Orbit Royale — generated from design-system/project/tokens.json. Do not edit. */\n:root {\n  color-scheme: dark;\n${lines.join('\n')}\n}\n${styles.join('\n')}\n`;
for (const out of outs) {
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, 'tokens.css'), tokensCss);
  fs.copyFileSync(path.join(ds, 'components', 'bundle.css'), path.join(out, 'bundle.css'));
  fs.copyFileSync(path.join(ds, 'components', 'bundle.js'), path.join(out, 'bundle.js'));
}
console.log('wrote ds/{tokens.css,bundle.css,bundle.js} into prototype/ and asset-hub/');
