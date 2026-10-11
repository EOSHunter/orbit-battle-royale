shader_type sky;
// Ringfall's sky: dusk gradient, stars, the planet's ring system arcing across the
// sky, a neighbouring planet and the sun. Everything is analytic (no textures),
// so it costs nothing to download. Asset: "Ringed sky dome" in the asset list.

uniform vec3 zenith_color : source_color = vec3(0.078, 0.102, 0.208);
uniform vec3 horizon_color : source_color = vec3(0.42, 0.353, 0.557);
uniform vec3 ground_color : source_color = vec3(0.043, 0.063, 0.106);
uniform float star_density = 0.0025;

// Rings: a plane through the planet's center seen from its surface. Directions
// whose elevation above the ring plane falls between inner and outer show ring.
uniform vec3 ring_normal = vec3(0.26, 0.93, 0.25);
uniform float ring_inner_deg = 9.0;
uniform float ring_outer_deg = 27.0;
uniform vec3 ring_color : source_color = vec3(0.93, 0.89, 0.98);
uniform vec3 ring_shadow_color : source_color = vec3(0.55, 0.5, 0.72);
uniform float ring_opacity = 0.75;

uniform vec3 planet_dir = vec3(0.38, 0.22, -0.9);
uniform float planet_size_deg = 7.5;
uniform vec3 planet_color : source_color = vec3(0.26, 0.2, 0.46);
uniform vec3 planet_rim : source_color = vec3(0.78, 0.6, 1.0);

uniform float sun_size_deg = 1.6;
uniform vec3 sun_color : source_color = vec3(1.0, 0.89, 0.76);

float hash(vec3 p) {
	p = fract(p * 0.3183099 + 0.1);
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float noise1(float x) {
	float i = floor(x);
	float f = fract(x);
	float a = fract(sin(i * 127.1) * 43758.55);
	float b = fract(sin((i + 1.0) * 127.1) * 43758.55);
	return mix(a, b, f * f * (3.0 - 2.0 * f));
}

void sky() {
	vec3 d = normalize(EYEDIR);
	float h = d.y;

	// Gradient: ground below the horizon, dusk band at the horizon, deep blue above.
	vec3 col = mix(horizon_color, zenith_color, smoothstep(0.0, 0.55, h));
	col = mix(col, ground_color, smoothstep(0.0, -0.08, h));
	col += horizon_color * 0.25 * exp(-abs(h) * 18.0);

	// Stars, fading out near the horizon.
	vec3 cell = floor(d * 380.0);
	float star = step(1.0 - star_density, hash(cell));
	col += vec3(star) * smoothstep(0.05, 0.35, h) * (0.5 + 0.5 * hash(cell + 7.0));

	// Neighbouring planet with a lit rim.
	vec3 pd = normalize(planet_dir);
	float pa = degrees(acos(clamp(dot(d, pd), -1.0, 1.0)));
	float disc = smoothstep(planet_size_deg, planet_size_deg - 0.15, pa);
	float rim = smoothstep(planet_size_deg - 1.2, planet_size_deg, pa) * disc;
	vec3 pcol = planet_color * (0.6 + 0.4 * noise1(dot(d, vec3(40.0, 90.0, 20.0)))) + planet_rim * rim * 0.6;
	col = mix(col, pcol, disc);

	// Ring system.
	vec3 n = normalize(ring_normal);
	float elev = degrees(asin(clamp(dot(d, n), -1.0, 1.0)));
	float r = (elev - ring_inner_deg) / (ring_outer_deg - ring_inner_deg);
	if (r > 0.0 && r < 1.0 && h > -0.05) {
		float bands = 0.55 + 0.45 * noise1(r * 38.0) * noise1(r * 9.0 + 3.0);
		float gap = smoothstep(0.0, 0.015, abs(r - 0.62)) * smoothstep(0.0, 0.01, abs(r - 0.31));
		float edge = smoothstep(0.0, 0.03, r) * smoothstep(1.0, 0.94, r);
		float a = ring_opacity * bands * gap * edge * smoothstep(-0.05, 0.12, h) * (1.0 - disc);
		vec3 rc = mix(ring_shadow_color, ring_color, smoothstep(0.2, 0.9, r));
		col = mix(col, rc, a);
	}

	// Sun disc and glow (the scene's directional light).
	if (LIGHT0_ENABLED) {
		float sa = dot(d, LIGHT0_DIRECTION);
		col += sun_color * pow(max(sa, 0.0), 300.0) * 0.6;
		col = mix(col, sun_color * 3.0, smoothstep(cos(radians(sun_size_deg)), cos(radians(sun_size_deg * 0.8)), sa));
	}
	COLOR = col;
}
