// Model viewer for the Asset Hub: orbit, inspect, measure. 1 scene unit = 1 meter.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export function createViewer(host) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  host.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b101b);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const studio = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environment = studio;

  const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 2000);
  camera.position.set(2.5, 1.6, 3.2);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  const key = new THREE.DirectionalLight(0xfff1dc, 1.6); key.position.set(3, 5, 4); scene.add(key);
  const rim = new THREE.DirectionalLight(0x9db8ff, 0.8); rim.position.set(-4, 2, -3); scene.add(rim);
  const grid = new THREE.GridHelper(20, 20, 0x46566d, 0x213047); scene.add(grid);
  const axes = new THREE.AxesHelper(0.5); axes.visible = false; scene.add(axes);

  let root = null, mixer = null, actions = [], autoRotate = false, wire = false;
  const clock = new THREE.Clock();
  const loader = new GLTFLoader();

  function resize() {
    const w = host.clientWidth, h = host.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(host);
  resize();

  renderer.setAnimationLoop(() => {
    const dt = clock.getDelta();
    if (mixer) mixer.update(dt);
    if (autoRotate && root) root.rotation.y += dt * 0.4;
    controls.update();
    renderer.render(scene, camera);
  });

  function clear() {
    if (!root) return;
    scene.remove(root);
    root.traverse(o => { if (o.geometry) o.geometry.dispose(); });
    root = null; mixer = null; actions = [];
  }

  function frame() {
    // Precise bounds follow the skeleton, so skinned characters frame correctly.
    root.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(root, true);
    const size = box.getSize(new THREE.Vector3()), center = box.getCenter(new THREE.Vector3());
    root.position.sub(new THREE.Vector3(center.x, box.min.y, center.z));
    const r = Math.max(size.x, size.y, size.z) || 1;
    controls.target.set(0, size.y / 2, 0);
    camera.position.set(r * 1.7, size.y * 0.6 + r * 0.7, r * 2.3);
    camera.near = r / 200; camera.far = r * 200; camera.updateProjectionMatrix();
    const g = Math.max(2, Math.ceil(r * 3));
    grid.scale.setScalar(g / 20);
    return size;
  }

  function stats(gltf, size) {
    let tris = 0, meshes = 0, skinned = false;
    const mats = new Set(), tex = new Set();
    root.traverse(o => {
      if (!o.isMesh) return;
      meshes++; if (o.isSkinnedMesh) skinned = true;
      const g = o.geometry;
      tris += (g.index ? g.index.count : g.attributes.position.count) / 3;
      (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => {
        mats.add(m);
        for (const k in m) if (m[k] && m[k].isTexture) tex.add(m[k]);
      });
    });
    const maxTex = [...tex].reduce((s, t) => Math.max(s, t.image ? Math.max(t.image.width || 0, t.image.height || 0) : 0), 0);
    return {
      tris: Math.round(tris), meshes, materials: mats.size, textures: tex.size, maxTex, skinned,
      size: [size.x, size.y, size.z].map(v => +v.toFixed(2)),
      animations: (gltf.animations || []).map(a => ({ name: a.name || 'Untitled', duration: +a.duration.toFixed(2) }))
    };
  }

  async function show(gltf) {
    clear();
    root = gltf.scene;
    scene.add(root);
    applyWire();
    const size = frame();
    if (gltf.animations && gltf.animations.length) {
      mixer = new THREE.AnimationMixer(root);
      actions = gltf.animations.map(a => mixer.clipAction(a));
    }
    return stats(gltf, size);
  }

  function applyWire() { if (root) root.traverse(o => { if (o.isMesh) (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => (m.wireframe = wire)); }); }

  return {
    /** Load from an ArrayBuffer (.glb) or a JSON string (.gltf). */
    async load(data) { const gltf = await loader.parseAsync(data, ''); return { gltf, info: await show(gltf) }; },
    clear,
    hasModel: () => !!root,
    play(i) { actions.forEach((a, k) => (k === i ? a.reset().play() : a.stop())); },
    stop() { actions.forEach(a => a.stop()); },
    setWire(v) { wire = v; applyWire(); },
    setGrid(v) { grid.visible = v; axes.visible = v; },
    setAutoRotate(v) { autoRotate = v; },
    setLighting(mode) {
      scene.environment = mode === 'flat' ? null : studio;
      scene.background = new THREE.Color(mode === 'sky' ? 0x2b2350 : 0x0b101b);
      key.intensity = mode === 'flat' ? 2.4 : 1.6;
      key.color.set(mode === 'sky' ? 0xffd2a0 : 0xfff1dc);
      rim.color.set(mode === 'sky' ? 0x8fd8ff : 0x9db8ff);
    },
    reset() { if (root) frame(); },
    /** Self-contained .gltf (JSON, textures embedded) for the hub's preview store. */
    async toGltfJson(gltf) {
      const res = await new GLTFExporter().parseAsync(gltf.scene, { binary: false, embedImages: true, animations: gltf.animations || [] });
      return JSON.stringify(res);
    },
    snapshot() { return renderer.domElement.toDataURL('image/webp', 0.85); }
  };
}
