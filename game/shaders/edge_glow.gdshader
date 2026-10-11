// Screen-edge glow for damage direction, healing and low health.
// direction = screen-space vector toward the source (zero: glow on every edge).
shader_type canvas_item;

uniform vec4 glow_color : source_color = vec4(1.0, 0.47, 0.5, 1.0);
uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform vec2 direction = vec2(0.0);
uniform float width : hint_range(0.05, 1.0) = 0.4;

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float edge = max(abs(p.x), abs(p.y));
	float v = smoothstep(1.0 - width, 1.0, mix(length(p) * 0.72, edge, 0.5));
	if (length(direction) > 0.001) {
		float facing = clamp(dot(normalize(p + vec2(0.0001)), normalize(direction)), 0.0, 1.0);
		v *= facing * facing;
	}
	COLOR = vec4(glow_color.rgb, glow_color.a * v * strength);
}
