/** Focused DOM/state contract tests; rendering and WebGL require browser QA. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const theme = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const { harness, Element } = require('./fixtures/skyy-dom-harness.cjs');
function text(el) {
  return (el.textContent || '') + el.children.map(text).join(' ');
}
function links(el) {
  return el.children.flatMap(child => [...(child.tagName === 'a' ? [child] : []), ...links(child)]);
}
const guide = {
  greeting: 'Welcome to the house.',
  products: [
    { name: 'The Signature Hoodie', sku: 'SG-005', url: '/product/signature-hoodie/', collection: 'Signature' },
  ],
  intents: [
    { id: 'hi', patterns: ['hi'], answer: 'Hello.' },
    {
      id: 'shipping',
      patterns: ['shipping'],
      answer: 'Read the current shipping policy.',
      link: '/shipping/',
      label: 'Shipping information',
    },
    { id: 'unsafe', patterns: ['unsafe'], answer: '<img src=x onerror=alert(1)>', link: 'https://outside.invalid/' },
  ],
  pages: { contact: { label: 'Contact', url: '/contact/' } },
};
test('native dialog opens on invitation, closes and returns focus; modified links remain native', () => {
  const h = harness();
  h.window.SKYY_GUIDE_DATA = guide;
  h.run('mascot.js');
  assert.equal(h.click(h.ids['skyyrose-mascot-recall'], { ctrlKey: true }).defaultPrevented, false);
  h.click(h.ids['skyyrose-mascot-recall']);
  assert.equal(h.ids['skyy-ask-dialog'].open, true);
  assert.equal(h.ids['skyyrose-mascot'].dataset.state, 'walking-in');
  assert.equal(h.document.activeElement, h.ids['skyy-ask-input']);
  h.click(h.ids['skyy-ask-cancel']);
  assert.equal(h.ids['skyyrose-mascot'].dataset.state, 'hidden');
  assert.equal(h.document.activeElement, h.ids['skyyrose-mascot-recall']);
  assert.equal(h.timers.size, 0);
});
test('real SKU discovery supplies exact native URL; phrase boundaries avoid hi matching shipping', () => {
  const h = harness();
  h.window.SKYY_GUIDE_DATA = guide;
  h.run('mascot.js');
  h.window.skyyRoseConcierge.open();
  h.submit('Find SG-005');
  assert.equal(links(h.ids['skyy-conversation']).at(-1).href, 'http://localhost:8899/product/signature-hoodie/');
  assert.match(text(h.ids['skyy-conversation']), /The Signature Hoodie · SG-005/);
  h.submit('shipping');
  assert.match(text(h.ids['skyy-conversation'].children.at(-1)), /Read the current shipping policy/);
  assert.doesNotMatch(text(h.ids['skyy-conversation'].children.at(-1)), /Hello/);
});
test('answer text cannot become markup and external links are excluded; transcript is bounded', () => {
  const h = harness();
  h.window.SKYY_GUIDE_DATA = guide;
  h.run('mascot.js');
  h.window.skyyRoseConcierge.open();
  h.submit('unsafe');
  const answer = h.ids['skyy-conversation'].children.at(-1);
  assert.match(text(answer), /<img src=x/);
  assert.equal(
    answer.children.some(el => el.tagName === 'img'),
    false
  );
  assert.equal(links(answer).length, 0);
  for (let i = 0; i < 30; i++) h.submit('unknown');
  assert.equal(h.ids['skyy-conversation'].children.length, 20);
  assert.equal(h.timers.size, 1);
});
test('loader waits for invitation, deduplicates requests, and failure preserves contact fallback', async () => {
  const h = harness();
  h.window.SKYY_LOADER_CONFIG = { mascotUrl: '/mascot.js', skyy3dUrl: '/skyy-3d.js' };
  h.run('mascot-loader.js');
  assert.equal(h.document.head.children.length, 0);
  h.click(h.ids['skyyrose-mascot-recall']);
  h.click(h.ids['skyyrose-mascot-recall']);
  assert.equal(h.document.head.children.length, 1);
  h.document.head.children[0].onerror();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.ids['skyyrose-mascot-recall'].replacement.href, 'http://localhost:8899/contact/');
  assert.equal(h.timers.size, 0);
});
test('Save-Data and reduced motion keep the canonical fallback without requesting 3D', () => {
  for (const options of [{ reduced: true }, { saveData: true }]) {
    const h = harness(options);
    h.window.SKYY_LOADER_CONFIG = { mascotUrl: '/mascot.js', skyy3dUrl: '/skyy-3d.js' };
    h.run('mascot-loader.js');
    h.document.dispatchEvent({ type: 'skyy:walking-in' });
    assert.equal(h.document.head.children.length, 0);
  }
});
test('unavailable WebGL returns a static character without fetching the model or throwing', async () => {
  const h = harness();
  h.ids['skyyrose-mascot'].dataset.state = 'walking-in';
  h.run('skyy-3d.js');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.window.skyyRoseMascot3D.isReady(), false);
  assert.equal(h.window.skyyRoseMascot3D.getFailureReason(), 'webgl-context');
  assert.equal(h.ids['skyyrose-mascot'].dataset.renderer, 'static');
  assert.equal(h.sprite.style.display, 'block');
});
test('canonical GLB contains the current embedded materials, skin and six populated action clips', () => {
  const bytes = fs.readFileSync(path.join(theme, 'assets/models/skyy-mascot.glb'));
  assert.equal(bytes.toString('ascii', 0, 4), 'glTF');
  const gltf = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString('utf8'));
  assert.ok(
    gltf.extensionsRequired.includes('KHR_draco_mesh_compression'),
    'The canonical asset requires the local Draco decoder'
  );
  assert.ok(gltf.skins.length > 0 && gltf.skins.every(skin => skin.joints.length > 0));
  assert.ok(gltf.images.length > 0 && gltf.images.every(image => Number.isInteger(image.bufferView)));
  for (const name of ['skyy_idle', 'skyy_walk', 'skyy_wave', 'skyy_talk', 'skyy_joy', 'skyy_exit']) {
    const clip = gltf.animations.find(clip => clip.name.toLowerCase() === name);
    assert.ok(clip && clip.channels.length && clip.samplers.length, name);
  }
});

test('ordinary greeting, product discovery and close invoke wave, joy and exit from actual controls', () => {
  const h = harness();
  h.window.SKYY_GUIDE_DATA = guide;
  h.run('mascot.js');
  h.window.skyyRoseConcierge.open();
  const seen = [];
  for (const state of ['wave', 'joy', 'exit', 'hidden'])
    h.document.addEventListener('skyy:' + state, () => seen.push(state));
  h.submit('hello Skyy');
  assert.equal(seen.at(-1), 'wave');
  h.submit('SG-005');
  assert.equal(seen.at(-1), 'joy');
  h.ids['skyyrose-mascot'].dataset.renderer = '3d';
  h.click(h.ids['skyy-ask-cancel']);
  assert.equal(seen.at(-1), 'exit');
  assert.equal(h.ids['skyy-ask-dialog'].open, true);
  [...h.timers.values()].at(-1)();
  assert.equal(seen.at(-1), 'hidden');
  assert.equal(h.ids['skyy-ask-dialog'].open, false);
});
test('a resumed renderer restores its visible Pause control after a lightweight fallback', () => {
  const h = harness();
  h.run('mascot.js');
  h.document.dispatchEvent({ type: 'skyy:3d-ready' });
  assert.equal(h.ids['skyy-motion-toggle'].hidden, false);
  h.document.dispatchEvent({ type: 'skyy:3d-fallback' });
  assert.equal(h.ids['skyy-motion-toggle'].hidden, true);
  h.document.dispatchEvent({ type: 'skyy:3d-visible' });
  assert.equal(h.ids['skyy-motion-toggle'].hidden, false);
  h.click(h.ids['skyy-motion-toggle']);
  assert.equal(h.ids['skyy-motion-toggle'].getAttribute('aria-pressed'), 'true');
});
test('delayed guide completion does not steal focus after the visitor moves elsewhere', async () => {
  const h = harness();
  h.window.SKYY_LOADER_CONFIG = { mascotUrl: '/mascot.js' };
  h.run('mascot-loader.js');
  h.click(h.ids['skyyrose-mascot-recall']);
  let opens = 0;
  h.window.skyyRoseConcierge = {
    open() {
      opens++;
    },
  };
  h.document.activeElement = new Element('input');
  h.document.head.children[0].onload();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(opens, 0);
  assert.equal(h.ids['skyyrose-mascot-recall'].getAttribute('aria-busy'), undefined);
});
test('a late 3D script cannot start after its loader timed out', async () => {
  const h = harness();
  h.window.SKYY_LOADER_CONFIG = { mascotUrl: '/mascot.js', skyy3dUrl: '/skyy-3d.js' };
  h.run('mascot-loader.js');
  h.document.dispatchEvent({ type: 'skyy:walking-in' });
  [...h.timers.values()][0]();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.window.SKYY_3D_CONFIG.loadFailed, true);
  h.ids['skyyrose-mascot'].dataset.state = 'walking-in';
  h.ids['skyy-3d-canvas'].getContext = () => {
    throw new Error('Late renderer must not initialize');
  };
  h.run('skyy-3d.js');
  assert.equal(h.window.skyyRoseMascot3D.isReady(), false);
});

test('Home mounts the same static stage immediately, then defers preparation while offscreen', () => {
  const h = harness({ home: true });
  let prepared = 0;
  h.document.addEventListener('skyy:prepare', () => prepared++);
  h.run('mascot.js');
  assert.equal(h.ids['skyyrose-mascot'].parentElement, h.ids['skyy-hero-stage']);
  assert.equal(prepared, 0);
  assert.equal(h.ids['skyy-ask-dialog'].open, undefined);
  h.intersect(false);
  h.window.skyyRoseConcierge.prepareHome();
  assert.equal(prepared, 0);
  h.intersect(true);
  assert.equal(prepared, 1);
  h.window.skyyRoseMascot3D = { isReady: () => true };
  h.document.dispatchEvent({ type: 'skyy:3d-ready' });
  assert.equal(h.ids['skyyrose-mascot'].dataset.state, 'walking-in');
  assert.equal(h.document.activeElement, h.ids['skyyrose-mascot-recall']);
});
test('Home stage is reparented into conversation and restored without duplicating the character', () => {
  const h = harness({ home: true });
  h.run('mascot.js');
  const stage = h.ids['skyyrose-mascot'];
  h.click(h.ids['skyy-hero-chat']);
  assert.equal(stage.parentElement, h.ids['skyy-dialog-stage']);
  assert.equal(h.ids['skyy-hero-stage'].children.length, 0);
  h.click(h.ids['skyy-ask-cancel']);
  assert.equal(stage.parentElement, h.ids['skyy-hero-stage']);
  assert.equal(h.ids['skyy-dialog-stage'].children.length, 0);
});
test('Home dismissal and offscreen state stop the renderer; header chat remains available', () => {
  const h = harness({ home: true });
  h.run('mascot.js');
  h.intersect(false);
  assert.equal(h.ids['skyyrose-mascot'].dataset.state, 'hidden');
  h.intersect(true);
  h.ids['skyy-hero-dismiss'].focus();
  h.click(h.ids['skyy-hero-dismiss']);
  assert.equal(h.ids['skyyrose-mascot'].hidden, true);
  assert.equal(h.document.activeElement, h.ids['skyyrose-mascot-recall']);
  h.click(h.ids['skyyrose-mascot-recall']);
  assert.equal(h.ids['skyy-ask-dialog'].open, true);
  assert.equal(h.ids['skyyrose-mascot'].hidden, false);
  h.click(h.ids['skyy-ask-cancel']);
  assert.equal(h.ids['skyyrose-mascot'].hidden, true);
});
test('reduced-motion and Save-Data Home retain static portrait without requesting automatic 3D', () => {
  for (const options of [{ reduced: true }, { saveData: true }]) {
    const h = harness({ home: true, ...options });
    let prepared = 0;
    h.document.addEventListener('skyy:prepare', () => prepared++);
    h.run('mascot.js');
    h.window.skyyRoseConcierge.prepareHome();
    assert.equal(prepared, 0);
    assert.equal(h.ids['skyyrose-mascot'].dataset.motionPaused, 'true');
    assert.equal(h.ids['skyyrose-mascot'].parentElement, h.ids['skyy-hero-stage']);
  }
});

test('hero conversation opener is restored after its stage leaves the closed dialog', () => {
  const h = harness({ home: true });
  h.run('mascot.js');
  const opener = h.ids['skyy-hero-chat'];
  opener.focus();
  h.click(opener);
  assert.equal(h.document.activeElement, h.ids['skyy-ask-input']);
  h.click(h.ids['skyy-ask-cancel']);
  assert.equal(opener.parentElement, h.ids['skyyrose-mascot']);
  assert.equal(h.document.activeElement, opener);
});

test('held canonical clips receive real quaternion motion on the same rig without altering source tracks', async () => {
  const vm = require('node:vm');
  const { pathToFileURL } = require('node:url');
  const THREE = await import(pathToFileURL(path.join(theme, 'assets/js/lib/three-r170/three.module.min.js')).href);
  const bytes = fs.readFileSync(path.join(theme, 'assets/models/skyy-mascot.glb'));
  const jsonLength = bytes.readUInt32LE(12),
    gltf = JSON.parse(bytes.subarray(20, 20 + jsonLength));
  const binary = 28 + jsonLength;
  function read(index) {
    const accessor = gltf.accessors[index],
      view = gltf.bufferViews[accessor.bufferView];
    const width = { SCALAR: 1, VEC3: 3, VEC4: 4 }[accessor.type];
    assert.equal(accessor.componentType, 5126);
    return Array.from({ length: accessor.count * width }, (_, i) =>
      bytes.readFloatLE(
        binary +
          (view.byteOffset || 0) +
          (accessor.byteOffset || 0) +
          Math.floor(i / width) * (view.byteStride || width * 4) +
          (i % width) * 4
      )
    );
  }
  const root = new THREE.Group();
  const joints = new Set(gltf.skins.flatMap(skin => skin.joints));
  const nodes = gltf.nodes.map((node, index) => {
    const object = joints.has(index) ? new THREE.Bone() : new THREE.Group();
    object.name = THREE.PropertyBinding.sanitizeNodeName(node.name || `node${index}`);
    if (node.rotation) object.quaternion.fromArray(node.rotation);
    if (node.translation) object.position.fromArray(node.translation);
    if (node.scale) object.scale.fromArray(node.scale);
    return object;
  });
  gltf.nodes.forEach((node, index) => (node.children || []).forEach(child => nodes[index].add(nodes[child])));
  nodes.filter(node => !node.parent).forEach(node => root.add(node));
  const clips = gltf.animations.map(
    animation =>
      new THREE.AnimationClip(
        animation.name,
        -1,
        animation.channels.map(channel => {
          const sampler = animation.samplers[channel.sampler],
            type = channel.target.path;
          const values = read(sampler.output),
            times = read(sampler.input),
            width = values.length / times.length;
          assert(
            values.every((value, i) => Math.abs(value - values[i % width]) < 0.00001),
            'Current source clip is a held pose; do not claim baked motion'
          );
          const property = { rotation: 'quaternion', translation: 'position', scale: 'scale' }[type];
          const Track = type === 'rotation' ? THREE.QuaternionKeyframeTrack : THREE.VectorKeyframeTrack;
          return new Track(nodes[channel.target.node].name + '.' + property, times, values);
        })
      )
  );
  const before = JSON.stringify(clips.map(clip => THREE.AnimationClip.toJSON(clip)));
  const source = fs.readFileSync(path.join(theme, 'assets/js/skyy-3d.js'), 'utf8');
  const helper = source.slice(source.indexOf('  function deriveRigMotion('), source.indexOf('  var required ='));
  const derive = vm.runInNewContext(helper + '\nderiveRigMotion', { Set });
  const motion = derive(THREE, clips, root);
  assert.equal(motion.clips.length, 6);
  assert(motion.source.every(clip => !clip.varying));
  for (const clip of motion.clips) {
    assert.equal(clip.skyyMotionSource, 'runtime-rig-upgrade-v1');
    const mixer = new THREE.AnimationMixer(root),
      action = mixer.clipAction(clip).play();
    mixer.setTime(0.1);
    const first = Object.values(motion.bones).flatMap(bone => bone.quaternion.toArray());
    mixer.setTime(0.32);
    const second = Object.values(motion.bones).flatMap(bone => bone.quaternion.toArray());
    assert(
      second.some((value, i) => Math.abs(value - first[i]) > 0.0001),
      `${clip.name} must visibly change rig pose`
    );
    if (clip.name === 'Skyy_Idle') {
      root.updateMatrixWorld(true);
      const shoulder = motion.bones.upperarml.getWorldPosition(new THREE.Vector3());
      const wrist = motion.bones.handl.getWorldPosition(new THREE.Vector3());
      assert(wrist.y < shoulder.y - 0.1, 'Relaxed hand must be below shoulder, not a forward-held source pose');
    }
    if (clip.name === 'Skyy_Walk') {
      const thighs = ['thighl', 'thighr'];
      for (const name of thighs) {
        mixer.setTime(0.1);
        const a = motion.bones[name].quaternion.clone();
        mixer.setTime(0.5);
        assert(a.angleTo(motion.bones[name].quaternion) > 0.3, `${name} changes across step phases`);
      }
    }
    action.stop();
    mixer.uncacheRoot(root);
  }
  assert.equal(JSON.stringify(clips.map(clip => THREE.AnimationClip.toJSON(clip))), before);
});

test('repeated transient requests renew the actual runtime interval without restarting its clip phase', () => {
  const vm = require('node:vm');
  const source = fs.readFileSync(path.join(theme, 'assets/js/skyy-3d.js'), 'utf8');
  const action = { phase: 2.3 };
  const context = {
    clearTimeout() {},
    timer: null,
    ready: true,
    actions: { skyy_talk: action },
    currentAction: action,
    lightMode: () => false,
    actionElapsed: 2.3,
    actionDuration: 2.4,
  };
  vm.createContext(context);
  vm.runInContext(source.slice(source.indexOf('  function play('), source.indexOf('  async function boot(')), context);
  context.play('skyy_talk', 2400);
  assert.equal(context.actionElapsed, 0);
  assert.equal(context.actionDuration, 2.4);
  assert.equal(action.phase, 2.3);
});

test('WebGL fallback teardown clears rig references and motion diagnostics return null', () => {
  const vm = require('node:vm');
  const source = fs.readFileSync(path.join(theme, 'assets/js/skyy-3d.js'), 'utf8');
  const context = {
    clearTimeout() {},
    timer: null,
    stop() {},
    controller: null,
    draco: null,
    mixer: null,
    model: {},
    rigMotion: { bones: {} },
    disposeModel() {},
    actions: {},
    currentAction: {},
    ready: true,
    renderer: null,
    scene: {},
  };
  vm.createContext(context);
  vm.runInContext(
    source.slice(source.indexOf('  function teardown('), source.indexOf('  function fallback(')),
    context
  );
  context.teardown();
  assert.equal(context.rigMotion, null);
  assert.equal(context.model, null);
  const start = source.indexOf('    getMotionEvidence: function () {');
  const end = source.indexOf('    getFailureReason:', start);
  vm.runInContext('var diagnostic = ({' + source.slice(start, end) + '}).getMotionEvidence;', context);
  assert.equal(context.diagnostic(), null);
});

test('presence hands the same portrait to the canvas once, with a paint boundary and no repeated fade on pause', () => {
  const h = harness({ home: true });
  const frames = new Map();
  let next = 0;
  h.window.requestAnimationFrame = callback => {
    frames.set(++next, callback);
    return next;
  };
  h.window.cancelAnimationFrame = id => frames.delete(id);
  h.run('mascot.js');
  h.window.skyyRoseConcierge.prepareHome();
  assert.equal(h.ids['skyyrose-mascot'].dataset.presence, 'loading');
  assert.match(h.ids['skyy-presence-status'].textContent, /joining/);
  h.sprite.style.display = 'none'; // Same behavior as the preserved renderer immediately before its event.
  h.document.dispatchEvent({ type: 'skyy:3d-visible' });
  assert.equal(h.sprite.style.display, 'block');
  assert.equal(h.ids['skyyrose-mascot'].dataset.presence, 'entering');
  assert.equal(frames.size, 1);
  const callback = [...frames.values()][0];
  frames.clear();
  callback();
  assert.equal(h.ids['skyyrose-mascot'].dataset.presence, 'entering');
  const reveal = [...frames.values()][0];
  frames.clear();
  reveal();
  assert.equal(h.ids['skyyrose-mascot'].dataset.presence, 'live');
  h.document.dispatchEvent({ type: 'skyy:3d-visible' });
  assert.equal(frames.size, 0);
  assert.equal(h.ids['skyyrose-mascot'].dataset.presence, 'live');
});

test('fallback cancels a pending reveal and does not become an endless loading state', () => {
  const h = harness({ home: true });
  const frames = new Map();
  h.window.requestAnimationFrame = callback => {
    frames.set(1, callback);
    return 1;
  };
  h.window.cancelAnimationFrame = id => frames.delete(id);
  h.run('mascot.js');
  h.document.dispatchEvent({ type: 'skyy:3d-visible' });
  h.document.dispatchEvent({ type: 'skyy:3d-fallback' });
  assert.equal(frames.size, 0);
  h.window.skyyRoseConcierge.prepareHome();
  h.intersect(false);
  h.intersect(true);
  assert.equal(h.ids['skyyrose-mascot'].dataset.presence, 'failed');
  assert.match(h.ids['skyy-presence-status'].textContent, /still ask/);
  h.click(h.ids['skyy-hero-chat']);
  assert.equal(h.ids['skyy-ask-dialog'].open, true);
  h.submit('shipping');
  assert(h.ids['skyy-conversation'].children.length > 0);
  assert.equal(h.ids['skyyrose-mascot'].dataset.presence, 'failed');
});

test('reduced and data-saving presence remain truthful and cannot reveal a late canvas', () => {
  for (const options of [{ reduced: true }, { saveData: true }]) {
    const h = harness({ home: true, ...options });
    h.run('mascot.js');
    h.window.skyyRoseConcierge.prepareHome();
    h.document.dispatchEvent({ type: 'skyy:3d-visible' });
    const expected = options.reduced ? 'reduced' : 'saving';
    assert.equal(h.ids['skyyrose-mascot'].dataset.presence, expected);
    h.click(h.ids['skyy-hero-chat']);
    assert.equal(h.ids['skyyrose-mascot'].dataset.presence, expected);
  }
});

test('offscreen departure cancels a pending presence handoff and a later visible event can resume it', () => {
  const h = harness({ home: true });
  const frames = new Map();
  let next = 0;
  h.window.requestAnimationFrame = callback => {
    frames.set(++next, callback);
    return next;
  };
  h.window.cancelAnimationFrame = id => frames.delete(id);
  h.run('mascot.js');
  h.document.dispatchEvent({ type: 'skyy:3d-visible' });
  h.intersect(false);
  assert.equal(frames.size, 0);
  assert.equal(h.ids['skyyrose-mascot'].dataset.presence, 'static');
  h.intersect(true);
  h.document.dispatchEvent({ type: 'skyy:3d-visible' });
  assert.equal(frames.size, 1);
});

test('failed guide uses translated template labels for its native Contact fallback', async () => {
  const h = harness();
  const label = new Element('span');
  h.ids['skyyrose-mascot-recall'].querySelector = () => label;
  h.ids['skyy-presence-status'].dataset.guideFailed = 'La guía no está disponible. Contacta con nosotros.';
  h.ids['skyy-presence-status'].dataset.contact = 'Contacto';
  h.window.SKYY_LOADER_CONFIG = { mascotUrl: '/mascot.js' };
  h.run('mascot-loader.js');
  h.click(h.ids['skyyrose-mascot-recall']);
  h.document.head.children[0].onerror();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(label.textContent, 'Contacto');
  assert.equal(h.ids['skyyrose-mascot-recall'].title, h.ids['skyy-presence-status'].dataset.guideFailed);
  assert.equal(h.ids['skyyrose-mascot-recall'].replacement.href, 'http://localhost:8899/contact/');
  assert.equal(h.document.activeElement, h.ids['skyyrose-mascot-recall'].replacement);
});

test('conversation exposes listening, synchronous thinking and truthful catalog failure states', () => {
  const h = harness();
  h.window.SKYY_GUIDE_DATA = guide;
  h.run('mascot.js');
  h.window.skyyRoseConcierge.open();
  h.ids['skyy-ask-input'].dispatchEvent({ type: 'input' });
  assert.equal(h.ids['skyyrose-mascot'].dataset.conversation, 'listening');
  let thinking = 0;
  h.document.addEventListener('skyy:thinking', () => thinking++);
  h.submit('SG-005');
  assert.equal(thinking, 1);
  assert.equal(h.ids['skyyrose-mascot'].dataset.conversation, 'gesture');
  const broken = harness();
  broken.run('mascot.js');
  broken.window.skyyRoseConcierge.open();
  broken.submit('SG-005');
  assert.equal(broken.ids['skyyrose-mascot'].dataset.conversation, 'chat-failure');
  assert.match(text(broken.ids['skyy-conversation']), /guide is unavailable/);
});

test('native conversation records closed and document hidden independently of motion', () => {
  const h = harness();
  h.window.SKYY_GUIDE_DATA = guide;
  h.run('mascot.js');
  h.window.skyyRoseConcierge.open();
  assert.equal(h.ids['skyyrose-mascot'].dataset.chat, 'open');
  h.document.hidden = true;
  h.document.dispatchEvent({ type: 'visibilitychange' });
  assert.equal(h.ids['skyyrose-mascot'].dataset.visibility, 'document-hidden');
  h.document.hidden = false;
  h.document.dispatchEvent({ type: 'visibilitychange' });
  h.click(h.ids['skyy-ask-cancel']);
  assert.equal(h.ids['skyyrose-mascot'].dataset.chat, 'closed');
});

test('minimize retains conversation and header recall opens the same stage and transcript', () => {
  const h = harness();
  h.window.SKYY_GUIDE_DATA = guide;
  h.run('mascot.js');
  h.window.skyyRoseConcierge.open();
  h.submit('shipping');
  const transcript = text(h.ids['skyy-conversation']);
  h.click(h.ids['skyy-ask-minimize']);
  assert.equal(h.ids['skyyrose-mascot'].dataset.chat, 'minimized');
  assert.equal(h.ids['skyy-ask-dialog'].open, false);
  h.click(h.ids['skyyrose-mascot-recall']);
  assert.equal(h.ids['skyyrose-mascot'].dataset.chat, 'open');
  assert.equal(text(h.ids['skyy-conversation']), transcript);
});

test('quantized 60Hz timestamps sustain the intended active and idle cadence instead of falling to 20fps', () => {
  const vm = require('node:vm');
  const source = fs.readFileSync(path.join(theme, 'assets/js/skyy-3d.js'), 'utf8');
  for (const [clip, expected] of [
    ['Skyy_Talk', 30],
    ['Skyy_Idle', 15],
  ]) {
    let loop,
      frames = 0;
    const context = {
      stop() {},
      ready: true,
      renderer: {
        setAnimationLoop(fn) {
          loop = fn;
        },
      },
      visible: true,
      document: { hidden: false, dispatchEvent() {} },
      disposed: false,
      lightMode: () => false,
      canvas: { style: {} },
      sprite: { style: {} },
      stage: { dataset: {}, style: { setProperty() {} } },
      firstReveal: false,
      renderFrame() {
        frames++;
      },
      paused: false,
      running: false,
      lastFrame: 0,
      revealAt: 0,
      currentAction: { getClip: () => ({ name: clip }) },
      profile: { intervals: [] },
      mixer: { update() {} },
      actionElapsed: 0,
      actionDuration: 0,
      model: { rotation: {} },
      facing: 0,
      CustomEvent: class {},
      clock: () => 0,
    };
    vm.createContext(context);
    vm.runInContext(source.slice(source.indexOf('  function sync() {'), source.indexOf('  function play(')), context);
    context.sync();
    for (let i = 1; i <= 120; i++) loop(Math.round(((i * 1000) / 60) * 10) / 10);
    assert(frames >= expected * 2 - 2 && frames <= expected * 2 + 3, `${clip}: ${frames} frames in two seconds`);
  }
});

test('initial greeting starts at its beginning; subsequent answers follow the latest message', () => {
  const h = harness();
  h.window.SKYY_GUIDE_DATA = guide;
  h.ids['skyy-conversation'].scrollHeight = 200;
  h.run('mascot.js');
  h.window.skyyRoseConcierge.open();
  assert.equal(h.ids['skyy-conversation'].scrollTop, 0);
  h.submit('shipping');
  assert.equal(h.ids['skyy-conversation'].scrollTop, 200);
});

test('Home load completion keeps the static guide until character pointer intent; repeated intent loads once', async () => {
  const h = harness({ home: true });
  h.ids['skyy-hero-stage'].closest = () => null;
  h.document.readyState = 'complete';
  const character = new Element();
  h.ids['skyyrose-mascot-trigger'] = character;
  h.window.SKYY_LOADER_CONFIG = { mascotUrl: '/mascot.js', skyy3dUrl: '/skyy-3d.js' };
  let prepares = 0;
  h.window.skyyRoseConcierge = {
    prepareHome() {
      prepares++;
      h.document.dispatchEvent({ type: 'skyy:prepare' });
    },
  };
  h.run('mascot-loader.js');
  h.document.head.children[0].onload();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(prepares, 0);
  assert.equal(h.document.head.children.length, 1);
  character.dispatchEvent({ type: 'pointerenter' });
  character.dispatchEvent({ type: 'pointerdown' });
  assert.equal(prepares, 1);
  assert.equal(h.document.head.children.length, 2);
});

test('Home keyboard intent prepares only the Ask action after guide readiness and honors lightweight modes', async () => {
  for (const reduced of [false, true]) {
    const h = harness({ home: true, reduced });
    h.ids['skyy-hero-stage'].closest = () => null;
    h.document.readyState = 'complete';
    h.window.SKYY_LOADER_CONFIG = { mascotUrl: '/mascot.js', skyy3dUrl: '/skyy-3d.js' };
    let prepares = 0;
    h.window.skyyRoseConcierge = {
      prepareHome() {
        prepares++;
        h.document.dispatchEvent({ type: 'skyy:prepare' });
      },
    };
    h.run('mascot-loader.js');
    h.ids['skyy-hero-stage'].dispatchEvent({ type: 'focusin', target: { id: 'skyy-hero-dismiss' } });
    assert.equal(prepares, 0);
    h.ids['skyy-hero-stage'].dispatchEvent({ type: 'focusin', target: { id: 'skyy-hero-chat' } });
    assert.equal(prepares, 0);
    h.document.head.children[0].onload();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(prepares, 1);
    assert.equal(h.document.head.children.length, reduced ? 1 : 2);
  }
});

test('cooperative skinned bounds exactly match Three and yield without publishing a partial box', async () => {
  const vm = require('node:vm');
  const { pathToFileURL } = require('node:url');
  const THREE = await import(pathToFileURL(path.join(theme, 'assets/js/lib/three-r170/three.module.min.js')).href);
  const source = fs.readFileSync(path.join(theme, 'assets/js/skyy-3d.js'), 'utf8');
  const helper = source.slice(source.indexOf('  async function prepareBounds('), source.indexOf('  var firstReveal'));
  const prepare = vm.runInNewContext(helper + '\nprepareBounds');
  const geometry = new THREE.BufferGeometry();
  const count = 16385,
    positions = new Float32Array(count * 3),
    weights = new Float32Array(count * 4);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = Math.sin(i);
    positions[i * 3 + 1] = i / count;
    weights[i * 4] = 1;
  }
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(new Uint16Array(count * 4), 4));
  geometry.setAttribute('skinWeight', new THREE.BufferAttribute(weights, 4));
  const mesh = new THREE.SkinnedMesh(geometry, new THREE.MeshBasicMaterial());
  const bone = new THREE.Bone();
  mesh.add(bone);
  mesh.bind(new THREE.Skeleton([bone]));
  bone.rotation.z = 0.2;
  mesh.updateMatrixWorld(true);
  mesh.computeBoundingBox();
  const expected = mesh.boundingBox.clone();
  mesh.boundingBox = null;
  let yields = 0;
  assert.equal(
    await prepare(
      THREE,
      mesh,
      () => false,
      async () => {
        yields++;
        assert.equal(mesh.boundingBox, null);
      }
    ),
    true
  );
  assert.equal(yields, 2);
  assert(mesh.boundingBox.equals(expected));
  mesh.computeBoundingSphere();
  const expectedSphere = mesh.boundingSphere.clone();
  mesh.boundingSphere = null;
  assert.equal(
    await prepare(
      THREE,
      mesh,
      () => false,
      async () => {},
      true
    ),
    true
  );
  assert(mesh.boundingSphere.equals(expectedSphere));
  mesh.boundingBox = null;
  let cancelled = false;
  assert.equal(
    await prepare(
      THREE,
      mesh,
      () => cancelled,
      async () => {
        cancelled = true;
      }
    ),
    false
  );
  assert.equal(mesh.boundingBox, null);
  geometry.dispose();
  mesh.material.dispose();
});

test('shader warmup owns cancellation and avoids r170 material polls after disposal', async () => {
  const vm = require('node:vm');
  const vendor = fs.readFileSync(path.join(theme, 'assets/js/lib/three-r170/three.module.min.js'), 'utf8');
  const start = vendor.indexOf('this.compileAsync=function');
  const end = vendor.indexOf(';let ', start);
  assert(start > 0 && end > start, 'Extract the actual installed r170 compileAsync implementation');
  const timers = [],
    material = {},
    properties = new Map([[material, { currentProgram: { isReady: () => false } }]]);
  const mockedRenderer = { compile: () => new Set([material]) };
  vm.runInNewContext('(function(){' + vendor.slice(start, end) + ';}).call(renderer)', {
    renderer: mockedRenderer,
    Promise,
    tt: { get: key => properties.get(key) || {} },
    J: { get: () => ({}) },
    setTimeout: callback => timers.push(callback),
  });
  let settled = false;
  mockedRenderer.compileAsync({}, {}).then(() => {
    settled = true;
  });
  assert.equal(timers.length, 1);
  properties.clear(); // Mirrors renderer/material disposal while the vendor poll waits.
  assert.throws(() => timers.shift()(), /isReady/);
  await Promise.resolve();
  assert.equal(settled, false, 'The vendor exception escapes its Promise and leaves it pending');

  const source = fs.readFileSync(path.join(theme, 'assets/js/skyy-3d.js'), 'utf8');
  const helper = source.slice(
    source.indexOf('  async function prepareShaders('),
    source.indexOf('  // Preserve Three r170')
  );
  const warmup = vm.runInNewContext(helper + '\nprepareShaders');
  let disposed = false,
    calls = 0;
  const renderer = {
    compile() {
      calls++;
    },
    compileAsync() {
      assert.fail('Uncancellable vendor poll must never run');
    },
  };
  assert.equal(
    await warmup(
      renderer,
      {},
      {},
      () => disposed,
      async () => {
        disposed = true;
      }
    ),
    false
  );
  assert.equal(calls, 1);
  assert.equal(
    await warmup(
      renderer,
      {},
      {},
      () => disposed,
      async () => {}
    ),
    false
  );
  assert.equal(calls, 1, 'Already-disposed initialization cannot compile again');
  disposed = false;
  assert.equal(
    await warmup(
      renderer,
      {},
      {},
      () => disposed,
      async () => {}
    ),
    true
  );
  assert.equal(calls, 2);
});
