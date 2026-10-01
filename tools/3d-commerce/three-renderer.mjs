/** Demand-rendered Three r170 adapter. Parse verified bytes; never refetch a GLB URL. */
export async function createThreeRenderer({ mount, bytes, onContextLost }, vendorBase) {
  const [THREE, { GLTFLoader }] = await Promise.all([
    import(new URL('three.module.min.js', vendorBase).href),
    import(new URL('GLTFLoader.js', vendorBase).href),
  ]);
  if (THREE.REVISION !== '170') throw new Error('Unqualified Three revision');
  let renderer;
  let scene;
  let observer;
  let disposed = false;
  const resources = new Set();
  const contextLost = event => {
    event.preventDefault();
    onContextLost();
  };
  const dispose = () => {
    if (disposed) return;
    disposed = true;
    observer?.disconnect();
    renderer?.domElement.removeEventListener('webglcontextlost', contextLost);
    scene?.traverse(object => {
      if (object.geometry) resources.add(object.geometry);
      for (const material of [].concat(object.material || [])) {
        resources.add(material);
        for (const value of Object.values(material)) if (value?.isTexture) resources.add(value);
      }
    });
    for (const resource of resources) {
      resource.source?.data?.close?.();
      resource.dispose();
    }
    renderer?.dispose();
    renderer?.forceContextLoss();
    renderer?.domElement.remove();
  };
  try {
    const gltf = await new GLTFLoader().parseAsync(bytes, '');
    scene = new THREE.Scene();
    scene.add(gltf.scene);
    const bounds = new THREE.Box3().setFromObject(gltf.scene);
    if (bounds.isEmpty()) throw new Error('Empty model');
    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3()).length();
    if (!Number.isFinite(size) || size <= 0) throw new Error('Invalid bounds');
    scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2));
    const light = new THREE.DirectionalLight(0xffffff, 3);
    light.position.set(3, 5, 4);
    scene.add(light);
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    renderer.domElement.setAttribute('aria-hidden', 'true');
    renderer.domElement.addEventListener('webglcontextlost', contextLost);
    mount.append(renderer.domElement);
    const camera = new THREE.PerspectiveCamera(35, 1, size / 1000, size * 100);
    let yaw = 0;
    let pitch = 0;
    const draw = () => {
      if (disposed) return;
      const width = Math.max(mount.clientWidth, 1);
      const height = Math.max(mount.clientHeight || 360, 1);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      const distance = (size / (2 * Math.tan(THREE.MathUtils.degToRad(35 / 2)))) * Math.max(1, 1 / camera.aspect) * 1.1;
      camera.position.set(
        center.x + Math.sin(yaw) * Math.cos(pitch) * distance,
        center.y + Math.sin(pitch) * distance,
        center.z + Math.cos(yaw) * Math.cos(pitch) * distance
      );
      camera.lookAt(center);
      renderer.render(scene, camera);
      mount.dataset.cameraYaw = String(yaw);
      mount.dataset.cameraPitch = String(pitch);
    };
    observer = new ResizeObserver(draw);
    observer.observe(mount);
    draw();
    return {
      dispose,
      reset() {
        yaw = 0;
        pitch = 0;
        draw();
      },
      rotate(dx, dy) {
        yaw += dx;
        pitch = Math.max(-1.3, Math.min(1.3, pitch + dy));
        draw();
      },
    };
  } catch (error) {
    dispose();
    throw error;
  }
}
