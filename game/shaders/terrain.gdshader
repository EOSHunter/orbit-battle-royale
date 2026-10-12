shader_type spatial;
// Ringfall terrain. Each chunk is a flat grid; the vertex shader lifts it from
// the 16-bit heightmap (R = high byte, G = low byte) so the download carries
// one small image instead of mesh data. Materials are procedural: pale grass,
// basalt, sand and black glass blended by the splat map, with regional tints
// (red rock at Hollow Array, grey ash at Relay Nine).

uniform sampler2D heightmap : filter_nearest, repeat_disable;
uniform sampler2D splatmap : filter_linear, repeat_disable;
uniform float map_half = 512.0;
uniform float spacing = 2.0;
uniform float height_min = -30.0;
uniform float height_range = 140.0;
uniform int samples = 513;

uniform vec3 grass_color : source_color = vec3(0.47, 0.55, 0.36);
uniform vec3 grass_dark : source_color = vec3(0.2, 0.29, 0.19);
uniform vec3 rock_color : source_color = vec3(0.15, 0.16, 0.19);
uniform vec3 sand_color : source_color = vec3(0.66, 0.6, 0.46);
uniform vec3 glass_color : source_color = vec3(0.05, 0.06, 0.08);
uniform vec3 red_rock : source_color = vec3(0.4, 0.2, 0.12);
uniform vec3 ash_color : source_color = vec3(0.36, 0.37, 0.39);
uniform vec2 red_center = vec2(278.0, 228.0);
uniform vec2 ash_center = vec2(285.0, -215.0);

varying vec3 world_pos;
varying float slope;

float h_at(ivec2 t) {
	t = clamp(t, ivec2(0), ivec2(samples - 1));
	vec2 rg = texelFetch(heightmap, t, 0).rg;
	return height_min + (rg.r * 65280.0 + rg.g * 255.0) / 65535.0 * height_range;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y);
}

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	ivec2 t = ivec2(round((wp.xz + map_half) / spacing));
	float h = h_at(t);
	float hx = h_at(t + ivec2(1, 0)) - h_at(t - ivec2(1, 0));
	float hz = h_at(t + ivec2(0, 1)) - h_at(t - ivec2(0, 1));
	VERTEX.y = h;
	NORMAL = normalize(vec3(-hx, 2.0 * spacing, -hz));
	world_pos = vec3(wp.x, h, wp.z);
	slope = 1.0 - NORMAL.y;
}

void fragment() {
	vec2 uv = (world_pos.xz + map_half) / (map_half * 2.0);
	vec4 s = texture(splatmap, uv);
	s.a = max(0.0, 1.0 - s.r - s.g - s.b);  // black glass is whatever the other three leave
	float n1 = noise(world_pos.xz * 0.35);
	float n2 = noise(world_pos.xz * 0.04);
	float n3 = fract(n1 * 7.13);  // cheap fine variation, no extra noise lookup

	vec3 grass = mix(grass_dark, grass_color, 0.35 + 0.5 * n2 + 0.15 * n1);
	vec3 rock = rock_color * (0.75 + 0.45 * n1) + 0.04 * n3;
	vec3 sand = sand_color * (0.88 + 0.18 * n1);
	vec3 glass = glass_color + 0.05 * n3;

	float red = smoothstep(190.0, 110.0, distance(world_pos.xz, red_center));
	rock = mix(rock, red_rock * (0.8 + 0.4 * n1), red);
	grass = mix(grass, mix(red_rock, sand_color, 0.5), red * 0.75);
	float ash = smoothstep(170.0, 100.0, distance(world_pos.xz, ash_center));
	rock = mix(rock, ash_color * (0.8 + 0.35 * n1), ash);

	vec3 col = grass * s.r + rock * s.g + sand * s.b + glass * s.a;
	// Wet band at the waterline.
	col *= mix(0.7, 1.0, smoothstep(-0.2, 0.6, world_pos.y));
	ALBEDO = col;
	ROUGHNESS = mix(0.9, 0.12, s.a) * (0.9 + 0.1 * n3);
	METALLIC = 0.35 * s.a;
	SPECULAR = mix(0.2, 0.5, s.a);
}
