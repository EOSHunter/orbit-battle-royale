// Greybox measuring material: 1 m minor lines, 5 m major lines in world space.
// Hookable surfaces add a lime stripe on the 5 m grid so eligibility is visible.
shader_type spatial;

uniform vec3 base_color : source_color = vec3(0.17, 0.19, 0.31);
uniform vec3 line_color : source_color = vec3(0.32, 0.37, 0.48);
uniform vec3 accent_color : source_color = vec3(0.77, 0.95, 0.47);
uniform float accent_strength : hint_range(0.0, 1.0) = 0.0;
uniform float roughness_value : hint_range(0.0, 1.0) = 0.9;

varying vec3 world_pos;
varying vec3 world_normal;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

float grid_line(vec2 p, float width) {
	vec2 d = abs(fract(p - 0.5) - 0.5) / max(fwidth(p), vec2(0.0001));
	return 1.0 - min(min(d.x, d.y) / width, 1.0);
}

void fragment() {
	vec3 n = abs(world_normal);
	vec2 uv = n.y > 0.5 ? world_pos.xz : (n.x > 0.5 ? world_pos.zy : world_pos.xy);
	float minor = grid_line(uv, 1.0);
	float major = grid_line(uv / 5.0, 1.5);
	vec3 c = mix(base_color, line_color, minor * 0.45);
	c = mix(c, line_color * 1.35, major * 0.8);
	float stripe = grid_line(uv / 5.0 + 0.5, 2.5);
	c = mix(c, accent_color, stripe * accent_strength);
	ALBEDO = c;
	ROUGHNESS = roughness_value;
}
