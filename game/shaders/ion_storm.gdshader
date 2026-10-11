shader_type spatial;
// Ion storm wall: drifting violet-cyan curtains on the inside face of a tall
// open cylinder, brightest near the ground and at the wall's crackling edge.
// Must stay unmistakable in a firefight (asset list: "Ion storm").
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, fog_disabled;

uniform vec3 core_color : source_color = vec3(0.55, 0.32, 1.0);
uniform vec3 edge_color : source_color = vec3(0.44, 0.84, 1.0);
uniform float intensity = 1.2;
uniform float height = 400.0;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y);
}

float fbm(vec2 p) {
	float v = 0.0;
	float a = 0.5;
	for (int i = 0; i < 4; i++) {
		v += a * noise(p);
		p *= 2.03;
		a *= 0.5;
	}
	return v;
}

void fragment() {
	float t = TIME;
	vec2 uv = UV * vec2(80.0, 6.0);
	float curtains = fbm(uv + vec2(t * 0.15, -t * 0.35));
	float streaks = fbm(vec2(uv.x * 3.0 + t * 0.6, uv.y * 0.6 - t));
	float ground = exp(-(1.0 - UV.y) * height * 0.012);
	float bolt = step(0.985, noise(vec2(uv.x * 2.0, floor(t * 12.0))));
	vec3 col = mix(core_color, edge_color, streaks) * (0.35 + curtains * 0.9);
	col += edge_color * bolt * 2.0;
	float a = (0.25 + 0.75 * curtains) * (0.35 + ground * 0.9) * intensity;
	// Fade the top so the wall doesn't end in a hard line against the sky.
	// CylinderMesh UV.y runs from 0 at the top to 1 at the bottom.
	a *= smoothstep(0.0, 0.3, UV.y);
	ALBEDO = col * a;
}
