shader_type canvas_item;
// Soft dark backing behind HUD groups: fades out horizontally away from the
// screen edge (`from_right` picks the edge) and toward the top.

uniform vec4 tint : source_color = vec4(0.043, 0.063, 0.106, 1.0);
uniform float strength = 0.62;
uniform bool from_right = false;

void fragment() {
	float x = from_right ? UV.x : 1.0 - UV.x;
	float h = smoothstep(0.0, 0.7, x);
	float v = smoothstep(0.0, 0.45, UV.y);
	COLOR = vec4(tint.rgb, strength * h * v);
}
