# Three.js r169 Patterns — Immersive Interactive Architect Reference

Load when: Three.js r169 ESM importmap boilerplate, studio lighting, GLTF loading, render loop, instancing, disposal, React integration.

Provenance: embedded copy of `host repo (DevSkyy) .claude/skills/immersive-interactive-architect/references/three-js-patterns.md`; verbatim except the adaptations recorded in [index.md](../index.md).

Canonical patterns for Three.js r169 using ESM importmaps. All code targets the SkyyRose
context: luxury fashion 3D product experiences on skyyrose.co (WordPress) and the
devskyy.app Next.js dashboard.

---

## 1. ESM Importmap Boilerplate (Standalone HTML)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SkyyRose 3D</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #0A0A0A; overflow: hidden; }
    canvas { display: block; }
  </style>

  <script type="importmap">
  {
    "imports": {
      "three":         "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/"
    }
  }
  </script>
</head>
<body>
  <canvas id="canvas"></canvas>
  <script type="module" src="main.js"></script>
</body>
</html>
```

---

## 2. Scene / Camera / Renderer Setup

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// --- Renderer ---
const canvas  = document.getElementById('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // cap DPR — critical for mobile
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type    = THREE.PCFSoftShadowMap;
renderer.outputColorSpace  = THREE.SRGBColorSpace; // r169 default; explicit for clarity
renderer.toneMapping       = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;

// --- Scene ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0A0A0A); // SkyyRose void
scene.fog = new THREE.FogExp2(0x0A0A0A, 0.035); // atmospheric depth

// --- Camera ---
const camera = new THREE.PerspectiveCamera(
  40,                                    // FOV 35-45 for product shots
  window.innerWidth / window.innerHeight,
  0.01,
  100
);
camera.position.set(0, 0.5, 4);

// --- Controls ---
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping    = true;  // smooth inertia
controls.dampingFactor    = 0.05;
controls.minDistance      = 1.5;
controls.maxDistance      = 8;
controls.maxPolarAngle    = Math.PI * 0.85; // prevent looking from below ground
controls.autoRotate       = true;
controls.autoRotateSpeed  = 0.8;
```

---

## 3. Resize Handling

```javascript
// Single ResizeObserver — more accurate than window resize for embedded canvases
const resizeObserver = new ResizeObserver(() => {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});
resizeObserver.observe(document.documentElement);
```

---

## 4. Geometry & Material Basics

```javascript
// Standard fashion product materials — physically-based
const fabricMaterial = new THREE.MeshStandardMaterial({
  color:     0x1C1C1C,
  roughness: 0.85,        // fabric is matte
  metalness: 0.0,
  envMapIntensity: 0.6,
});

const metallicAccent = new THREE.MeshStandardMaterial({
  color:     0xB76E79,    // rose gold
  roughness: 0.15,
  metalness: 0.9,
  envMapIntensity: 1.2,
});

// Geometries available in r169 (no compositing hacks needed)
const capsule  = new THREE.CapsuleGeometry(0.5, 1.2, 4, 16);
const box      = new THREE.BoxGeometry(1, 1, 1, 2, 2, 2);
const sphere   = new THREE.SphereGeometry(0.5, 32, 16);
const cylinder = new THREE.CylinderGeometry(0.4, 0.4, 1.2, 32);
const plane    = new THREE.PlaneGeometry(4, 4, 1, 1);

const mesh = new THREE.Mesh(capsule, fabricMaterial);
scene.add(mesh);
```

---

## 5. Studio 3-Point Lighting (Fashion/Apparel)

```javascript
// Key light — primary illumination
const keyLight = new THREE.DirectionalLight(0xffffff, 2.5);
keyLight.position.set(3, 6, 4);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.camera.near = 0.1;
keyLight.shadow.camera.far  = 20;
keyLight.shadow.bias = -0.001;
scene.add(keyLight);

// Fill light — rose gold warmth (SkyyRose accent)
const fillLight = new THREE.DirectionalLight(0xB76E79, 0.6);
fillLight.position.set(-4, 2, 2);
scene.add(fillLight);

// Rim light — fabric edge glow, creates separation from background
const rimLight = new THREE.DirectionalLight(0xffffff, 1.2);
rimLight.position.set(0, -2, -4);
scene.add(rimLight);

// Ambient — lifts shadows, prevents total blackness
const ambient = new THREE.AmbientLight(0x111111, 0.8);
scene.add(ambient);

// Environment map for reflections on metallic materials
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
new RGBELoader().load('studio_small.hdr', (hdr) => {
  hdr.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = hdr; // applies to all MeshStandardMaterial
});
```

---

## 6. GLTF Loading

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const draco = new DRACOLoader();
draco.setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/libs/draco/');

const loader = new GLTFLoader();
loader.setDRACOLoader(draco);

loader.load(
  'product.glb',
  (gltf) => {
    const model = gltf.scene;
    model.traverse((child) => {
      if (child.isMesh) {
        child.castShadow    = true;
        child.receiveShadow = true;
        child.material.envMapIntensity = 0.8;
      }
    });
    // Center model at origin
    const box  = new THREE.Box3().setFromObject(model);
    const size = box.getSize(new THREE.Vector3());
    model.position.y = -box.min.y; // sit on y=0
    scene.add(model);
  },
  (xhr) => console.log(`${(xhr.loaded / xhr.total * 100).toFixed(0)}% loaded`),
  (err) => console.error('GLTF load error:', err)
);
```

`product.glb` above is a placeholder name. The single editable product source of truth is `logo-registry.json` (DevSkyy: root symlink to `<theme-root>/data/logo-registry.json`). Its `products[sku]` records own commerce fields and image/source bindings. CSV, dossiers, and `sot-images.json` manifests are generated projections or consumers, read through sanctioned readers and never authored. Corey, the founder and maker, is authoritative on his own product specs: `FOUNDER_CONFIRMED`, with no third-party verification demanded. 3D product models must be the correct garment for the SKU. Never present a hallucinated or never-made product.

> **Host-repo gotcha (DevSkyy mascot rig):** Draco compression corrupted the skinned meshes of the DevSkyy mascot rig. For skinned or animated characters use meshopt + quantize instead, and every consumer must call `loader.setMeshoptDecoder(MeshoptDecoder)` before loading or the GLB fails to parse. Draco remains fine for static meshes.

---

## 7. Render Loop

```javascript
// Pause rendering when canvas is not visible — major battery/GPU saving
let isVisible = true;
const visibilityObserver = new IntersectionObserver(
  ([entry]) => { isVisible = entry.isIntersecting; },
  { threshold: 0.05 }
);
visibilityObserver.observe(canvas);

// Clock for delta-time based animation (frame-rate independent)
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  if (!isVisible) return;

  const delta = clock.getDelta();

  controls.update(); // required when enableDamping = true

  // Example: constant slow rotation regardless of frame rate
  if (mesh) mesh.rotation.y += delta * 0.4;

  renderer.render(scene, camera);
}
animate();
```

---

## 8. InstancedMesh for Repeated Objects (Particles / Floor Tiles)

```javascript
// Draw 1000 particles as a single draw call — critical for performance
const COUNT   = 1000;
const iGeo    = new THREE.SphereGeometry(0.02, 4, 4);
const iMat    = new THREE.MeshStandardMaterial({ color: 0xB76E79, roughness: 0.3 });
const instanced = new THREE.InstancedMesh(iGeo, iMat, COUNT);
instanced.instanceMatrix.setUsage(THREE.DynamicDrawUsage); // update each frame

const dummy = new THREE.Object3D();
const positions = Array.from({ length: COUNT }, () => ({
  x: (Math.random() - 0.5) * 10,
  y: Math.random() * 8,
  z: (Math.random() - 0.5) * 10,
  speed: 0.2 + Math.random() * 0.6,
}));

function updateParticles(elapsed) {
  positions.forEach((p, i) => {
    p.y -= p.speed * 0.016; // drift downward
    if (p.y < -1) p.y = 8;  // loop
    dummy.position.set(p.x, p.y, p.z);
    dummy.updateMatrix();
    instanced.setMatrixAt(i, dummy.matrix);
  });
  instanced.instanceMatrix.needsUpdate = true;
}
scene.add(instanced);
```

---

## 9. Frustum Culling

Three.js enables frustum culling by default. To verify it has not been disabled:

```javascript
// Default is true — only set explicitly if you deliberately disabled it before
mesh.frustumCulled = true;

// For objects that should always render (UI planes, skybox) disable culling:
skyboxMesh.frustumCulled = false;
```

---

## 10. Draw-Call Budget Guidelines

| Scenario                    | Target Draw Calls | Notes                                     |
|-----------------------------|-------------------|-------------------------------------------|
| Single product viewer       | < 20              | Merged geometry + atlas texture           |
| Collection page (4 products)| < 60              | InstancedMesh for environmental elements  |
| Full showroom (WP embed)    | < 120 mobile      | LOD + frustum cull aggressively           |
| Particle system             | 1                 | Always InstancedMesh, never individual meshes |

Use `renderer.info.render.calls` in dev to monitor:
```javascript
// Log draw calls per frame during development
// Guard process.env — it throws ReferenceError in non-bundled importmap browser contexts.
// Use import.meta.env.DEV in Vite; typeof-guard for universal/plain-browser scripts.
if (typeof process !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('Draw calls:', renderer.info.render.calls);
  renderer.info.reset(); // reset per-frame counter
}
```

---

## 11. Resource Disposal / Cleanup

Failure to dispose causes GPU memory leaks — critical in React's useEffect and WP
single-page navigation.

```javascript
function disposeScene(scene, renderer) {
  scene.traverse((object) => {
    if (!object.isMesh) return;

    // Dispose geometry
    object.geometry.dispose();

    // Dispose material(s) — handle both single and array
    const materials = Array.isArray(object.material)
      ? object.material
      : [object.material];

    materials.forEach((mat) => {
      // Dispose all texture slots
      ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'emissiveMap',
       'aoMap', 'alphaMap', 'envMap'].forEach((key) => {
        if (mat[key]) mat[key].dispose();
      });
      mat.dispose();
    });
  });

  renderer.dispose();
  renderer.forceContextLoss(); // release WebGL context
}

// React useEffect cleanup:
// return () => { disposeScene(scene, renderer); controls.dispose(); };

// WordPress: call on page navigation events
document.addEventListener('skyyrose:navigate-away', () => disposeScene(scene, renderer));
```

---

## 12. React / Next.js Integration Pattern

```javascript
import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export default function ProductViewer({ glbUrl }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    const w = mount.clientWidth;
    const h = mount.clientHeight;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    mount.appendChild(renderer.domElement);

    const scene    = new THREE.Scene();
    const camera   = new THREE.PerspectiveCamera(40, w / h, 0.01, 100);
    camera.position.set(0, 0, 4);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // Lights, loaders, model load... (see sections above)

    let rafId;
    const tick = () => { rafId = requestAnimationFrame(tick); controls.update(); renderer.render(scene, camera); };
    tick();

    const handleResize = () => {
      const w2 = mount.clientWidth;
      const h2 = mount.clientHeight;
      camera.aspect = w2 / h2;
      camera.updateProjectionMatrix();
      renderer.setSize(w2, h2);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', handleResize);
      controls.dispose();
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [glbUrl]);

  return <div ref={mountRef} style={{ width: '100%', height: '500px' }} />;
}
```
