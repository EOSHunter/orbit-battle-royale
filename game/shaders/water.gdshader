shader_type spatial;
// Sea and crater lake: one plane at the water level. Depth comes from the
// terrain heightmap, so shallows glow turquoise, deep water turns navy and a
// foam band traces every shore. Small moving ripples, no textures.
render_mode blend_mix, depth_draw_opaque, cull_disabled;

uniform sampler2D heightmap : filter_nearest, repeat_disable;
uniform float map_half = 512.0;
uniform float height_min = -30.0;
uniform float height_range = 140.0;
uniform vec3 shallow : source_color = vec3(0.25, 0.82, 0.8);
uniform vec3 deep : source_color = vec3(0.03, 0.17, 0.3);
uniform vec3 foam : source_color = vec3(0.92, 0.98, 1.0);

uniform float spacing = 2.0;
uniform int samples = 513;

float h_at(ivec2 t) {
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

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	// Bilinear over the decoded 16-bit heights (filtering the encoded bytes would break them).
	vec2 g = (world_pos.xz + map_half) / spacing;
	float ground = -30.0;
	if (g.x > 0.0 && g.y > 0.0 && g.x < float(samples - 1) && g.y < float(samples - 1)) {
		ivec2 i = ivec2(floor(g));
		vec2 f = fract(g);
		ground = mix(mix(h_at(i), h_at(i + ivec2(1, 0)), f.x), mix(h_at(i + ivec2(0, 1)), h_at(i + ivec2(1, 1)), f.x), f.y);
	}
	float depth = max(world_pos.y - ground, 0.0);
	float t = TIME;
	float ripple = noise(world_pos.xz * 0.15 + vec2(t * 0.3, t * 0.2)) + 0.5 * noise(world_pos.xz * 0.5 - vec2(t * 0.4, 0.0));
	vec3 col = mix(shallow, deep, smoothstep(0.5, 14.0, depth));
	float shore = smoothstep(0.7, 0.05, depth + 0.25 * sin(t * 1.5 + ripple * 4.0));
	col = mix(col, foam, shore * 0.85);
	ALBEDO = col;
	ROUGHNESS = 0.08;
	METALLIC = 0.1;
	SPECULAR = 0.6;
	NORMAL_MAP = normalize(vec3(ripple - 0.75, 0.0, 0.0) * 0.4 + vec3(0.5, 0.5, 1.0));
	ALPHA = mix(0.55, 1.0, smoothstep(0.0, 6.0, depth)) + shore * 0.3;
}
