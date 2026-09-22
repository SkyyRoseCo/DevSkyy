/** Canonical Skyy rig; self-hosted Three r170; invitation-owned GPU lifecycle. */
(function () {
  'use strict';
  var config = window.SKYY_3D_CONFIG || {};
  var canvas = document.getElementById('skyy-3d-canvas');
  var stage = document.getElementById('skyyrose-mascot');
  if (!canvas || !stage || window.skyyRoseMascot3D) return;
  var sprite = stage.querySelector('.skyyrose-mascot__image');
  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var connection = navigator.connection;
  var renderer, scene, camera, mixer, model, modules, controller, draco;
  var phase = 'dormant';
  var clock = function () { return window.performance ? window.performance.now() : Date.now(); };
  var profile = { startedAt: null, firstStableFrameMs: null, modelBytes: 0, frames: [], intervals: [], stages: [] };
  var phaseStarted = 0;
  function markPhase(next) {
    var now = clock();
    if (phaseStarted) profile.stages.push({ name: phase, startedAt: phaseStarted, duration: now - phaseStarted });
    phase = next;
    phaseStarted = now;
  }
  function yieldMainThread() {
    return window.scheduler && window.scheduler.yield
      ? window.scheduler.yield()
      : new Promise(function (resolve) { setTimeout(resolve, 0); });
  }
  async function prepareShaders(targetRenderer, targetScene, targetCamera, cancelled, yieldTask) {
    if (cancelled()) return false;
    // r170 compileAsync leaves an uncancellable material poll after disposal.
    // Start compilation synchronously, then yield through our owned lifecycle.
    targetRenderer.compile(targetScene, targetCamera);
    await yieldTask();
    return !cancelled();
  }
  // Preserve Three r170's exact skinned box/sphere vertex order and math,
  // but avoid one synchronous million-vertex task before the first frame.
  async function prepareBounds(THREE, root, cancelled, yieldTask, sphere) {
    var field = sphere ? 'boundingSphere' : 'boundingBox';
    var meshes = [];
    root.updateMatrixWorld(true);
    root.traverse(function (node) {
      if (node.isSkinnedMesh && node[field] === null) meshes.push(node);
    });
    for (var mesh of meshes) {
      var bounds = sphere ? new THREE.Sphere() : new THREE.Box3();
      var point = new THREE.Vector3();
      var count = mesh.geometry.getAttribute('position').count;
      for (var start = 0; start < count; start += 8192) {
        if (cancelled()) return false;
        var end = Math.min(start + 8192, count);
        for (var index = start; index < end; index++) {
          mesh.getVertexPosition(index, point);
          bounds.expandByPoint(point);
        }
        if (end < count) await yieldTask();
      }
      mesh[field] = bounds;
    }
    return !cancelled();
  }
  var firstReveal = true;
  var revealAt = 0;
  var failureReason = null;
  var actions = {};
  var currentAction;
  var ready = false;
  var started = false;
  var failed = false;
  var disposed = false;
  var visible = stage.dataset.state !== 'hidden';
  var paused = false;
  var timer;
  var lastFrame = 0;
  var frameCount = 0;
  var running = false;
  var rigMotion,
    actionElapsed = 0,
    actionDuration = 0;
  var facing = 0;
  // NEW UPGRADE: the approved GLB contains six held poses, not baked motion.
  // Clone their tracks and animate only existing rig joints; never mutate source clips.
  function deriveRigMotion(THREE, sourceClips, root) {
    var bones = {};
    root.traverse(function (node) {
      if (node.isBone) bones[node.name.toLowerCase().replace(/[^a-z0-9]/g, '')] = node;
    });
    var requiredBones = [
      'thighl',
      'thighr',
      'shinl',
      'shinr',
      'footl',
      'footr',
      'upperarml',
      'upperarmr',
      'forearml',
      'forearmr',
      'chest',
      'head',
      'pelvis',
    ];
    if (
      requiredBones.some(function (name) {
        return !bones[name];
      })
    )
      throw new Error('Skyy gait joints incomplete');
    var summaries = [];
    var upgraded = sourceClips.map(function (source) {
      var moving = source.tracks.some(function (track) {
        var stride = track.getValueSize();
        return Array.from(track.values).some(function (value, i) {
          return i >= stride && Math.abs(value - track.values[i % stride]) > 0.00001;
        });
      });
      summaries.push({ name: source.name, varying: moving, tracks: source.tracks.length });
      if (moving) return source; // Future approved baked motion retains precedence.
      var kind = source.name.toLowerCase().replace('skyy_', '');
      var duration = kind === 'idle' ? 3.2 : kind === 'talk' ? 2.4 : kind === 'walk' || kind === 'exit' ? 1.6 : 1.4;
      var frames = 48,
        times = [],
        replacements = [];
      for (var i = 0; i <= frames; i++) times.push((i * duration) / frames);
      requiredBones.forEach(function (key) {
        var bone = bones[key];
        var original = source.tracks.find(function (track) {
          return track.name === bone.name + '.quaternion';
        });
        var useBindShoulder = key.startsWith('upperarm') || key.startsWith('forearm');
        var base =
          original && !useBindShoulder ? new THREE.Quaternion().fromArray(original.values) : bone.quaternion.clone();
        var values = [];
        times.forEach(function (time) {
          var cycle = (time * Math.PI * 2) / 0.8;
          var breath = Math.sin((time * Math.PI * 2) / duration);
          var walking = kind === 'walk' || kind === 'exit';
          var side = key.endsWith('l') ? 1 : -1;
          var stride = Math.sin(cycle + (side === 1 ? 0 : Math.PI));
          var x = 0,
            z = 0;
          if (key.startsWith('thigh') && walking) x = 0.38 * stride;
          if (key.startsWith('shin') && walking) x = -0.58 * Math.max(0, -stride);
          if (key.startsWith('foot') && walking) x = 0.18 * Math.max(0, -stride);
          if (key.startsWith('upperarm')) {
            z = -side * 1.15; // Relax the source horizontal arms toward the torso.
            if (walking) x = -0.25 * stride;
            if (kind === 'wave' && side === 1) {
              z = -0.25;
              x = 0.12 * breath;
            }
            if (kind === 'talk') x = 0.08 * breath * side;
            if (kind === 'joy') z += side * 0.16 * Math.sin((Math.PI * time) / duration);
          }
          if (key.startsWith('forearm')) {
            x = -0.1;
            if (kind === 'wave' && side === 1) z = 0.45 + 0.22 * Math.sin((time * Math.PI * 6) / duration);
            if (kind === 'talk') x -= 0.1 * Math.max(0, breath);
          }
          if (key === 'chest') x = 0.012 * breath;
          if (key === 'head') x = (kind === 'talk' ? 0.045 : 0.012) * breath;
          var offset = new THREE.Quaternion().setFromEuler(new THREE.Euler(x, 0, z, 'XYZ'));
          // Parent-space offsets: the source shoulder axes differ left/right.
          var rotation = key.startsWith('upperarm') ? offset.multiply(base) : base.clone().multiply(offset);
          rotation.normalize().toArray(values, values.length);
        });
        replacements.push(new THREE.QuaternionKeyframeTrack(bone.name + '.quaternion', times, values));
      });
      var pelvis = bones.pelvis;
      var sourcePosition = source.tracks.find(function (track) {
        return track.name === pelvis.name + '.position';
      });
      var position = sourcePosition ? Array.from(sourcePosition.values.slice(0, 3)) : pelvis.position.toArray();
      var positions = [];
      times.forEach(function (time) {
        var bob =
          kind === 'walk' || kind === 'exit'
            ? 0.004 * (1 - Math.cos((time * Math.PI * 4) / 0.8))
            : 0.0015 * Math.sin((time * Math.PI * 2) / duration);
        positions.push(position[0], position[1] + bob, position[2]);
      });
      replacements.push(new THREE.VectorKeyframeTrack(pelvis.name + '.position', times, positions));
      var changed = new Set(
        replacements.map(function (track) {
          return track.name;
        })
      );
      var retained = source.tracks
        .filter(function (track) {
          return !changed.has(track.name);
        })
        .map(function (track) {
          return track.clone();
        });
      var clip = new THREE.AnimationClip(source.name, duration, retained.concat(replacements));
      clip.skyyMotionSource = 'runtime-rig-upgrade-v1';
      return clip;
    });
    return { clips: upgraded, source: summaries, bones: bones };
  }

  var required = ['skyy_idle', 'skyy_walk', 'skyy_wave', 'skyy_talk', 'skyy_joy', 'skyy_exit'];
  function local(value) {
    if (typeof value !== 'string' || !value) throw new Error('Skyy asset URL missing');
    var url = new URL(value, location.href);
    if (url.origin !== location.origin || !/^https?:$/.test(url.protocol)) throw new Error('Skyy assets must be local');
    return url.href;
  }
  function limited(promise, ms) {
    return new Promise(function (resolve, reject) {
      var timeout = setTimeout(function () {
        reject(new Error('Skyy dependency timed out'));
      }, ms);
      promise.then(
        function (value) {
          clearTimeout(timeout);
          resolve(value);
        },
        function (error) {
          clearTimeout(timeout);
          reject(error);
        }
      );
    });
  }
  var dependency;
  function loadThree(callback) {
    if (!dependency)
      dependency = Promise.resolve()
        .then(function () {
          var base = local(config.moduleBase);
          if (!base.endsWith('/')) throw new Error('Skyy moduleBase must be a directory');
          return limited(
            Promise.all([
              import(base + 'three.module.min.js'),
              import(base + 'GLTFLoader.js'),
              import(base + 'DRACOLoader.js'),
            ]),
            15000
          );
        })
        .then(function (loaded) {
          window.THREE = loaded[0];
          window.THREE_GLTFLoader = loaded[1].GLTFLoader;
          window.THREE_DRACOLoader = loaded[2].DRACOLoader;
          document.dispatchEvent(new Event('three-ready'));
          return loaded;
        });
    var result = dependency.then(function (loaded) {
      if (callback) callback(loaded[0]);
      return loaded;
    });
    // The shared legacy callback API also has a handled rejection for callers
    // that retain their own DOM scene without awaiting the optional renderer.
    result.catch(function () {});
    return result;
  }
  window.skyyRoseLoadThree = loadThree;
  window.addEventListener('skyyrose:request-three', function () {
    loadThree();
  });
  function lightMode() {
    return motion.matches || !!(connection && connection.saveData);
  }
  function stop() {
    if (renderer) renderer.setAnimationLoop(null);
    running = false;
    lastFrame = 0;
  }
  function renderFrame() {
    var began = clock();
    renderer.render(scene, camera);
    if (profile.firstRenderCpuMs === undefined) profile.firstRenderCpuMs = clock() - began;
    frameCount++;
    if (profile.frames.length < 120) profile.frames.push(clock() - began);
    if (profile.firstStableFrameMs === null) profile.firstStableFrameMs = clock() - profile.startedAt;
  }
  function profileModel() {
    var textures = new Set(), materials = new Set(), bones = new Set(), geometries = new Set();
    var geometryBytes = 0, textureBytes = 0;
    model.traverse(function (node) {
      if (node.isBone) bones.add(node);
      if (node.geometry && !geometries.has(node.geometry)) {
        geometries.add(node.geometry);
        Object.values(node.geometry.attributes).forEach(function (a) { geometryBytes += a.array.byteLength; });
        if (node.geometry.index) geometryBytes += node.geometry.index.array.byteLength;
      }
      (Array.isArray(node.material) ? node.material : [node.material]).filter(Boolean).forEach(function (material) {
        materials.add(material);
        Object.values(material).forEach(function (value) {
          if (value && value.isTexture && !textures.has(value)) {
            textures.add(value);
            var image = value.image || {};
            textureBytes += (image.width || 0) * (image.height || 0) * 4 * (value.generateMipmaps ? 4 / 3 : 1);
          }
        });
      });
    });
    var context = renderer.getContext(), debug = context.getExtension('WEBGL_debug_renderer_info');
    profile.gpuRenderer = debug ? context.getParameter(debug.UNMASKED_RENDERER_WEBGL) : context.getParameter(context.RENDERER);
    profile.materials = materials.size; profile.bones = bones.size; profile.textures = textures.size;
    profile.geometryDecodedBytes = geometryBytes; profile.textureDecodedBytesEstimate = Math.ceil(textureBytes);
    profile.memoryBoundary = 'Typed geometry arrays plus RGBA8 texture and mip estimate; excludes driver, decoder and JavaScript heap.';
  }
  function showFallback() {
    firstReveal = true;
    canvas.hidden = true;
    canvas.style.display = 'none';
    if (sprite) sprite.style.display = 'block';
    stage.dataset.renderer = 'static';
    document.dispatchEvent(new CustomEvent('skyy:3d-fallback'));
  }
  function disposeModel(object) {
    if (!object) return;
    var textures = new Set();
    var materials = new Set();
    var geometries = new Set();
    object.traverse(function (node) {
      if (node.geometry) geometries.add(node.geometry);
      (Array.isArray(node.material) ? node.material : [node.material]).filter(Boolean).forEach(function (material) {
        materials.add(material);
        Object.values(material).forEach(function (value) {
          if (value && value.isTexture) textures.add(value);
        });
      });
    });
    textures.forEach(function (texture) {
      texture.dispose();
    });
    materials.forEach(function (material) {
      material.dispose();
    });
    geometries.forEach(function (geometry) {
      geometry.dispose();
    });
  }
  function teardown() {
    clearTimeout(timer);
    stop();
    if (controller) controller.abort();
    if (draco) {
      draco.dispose();
      draco = null;
    }
    if (mixer) {
      mixer.stopAllAction();
      if (model) mixer.uncacheRoot(model);
    }
    disposeModel(model);
    model = null;
    rigMotion = null;
    mixer = null;
    actions = {};
    currentAction = null;
    ready = false;
    if (renderer) {
      renderer.dispose();
      renderer = null;
    }
    scene = null;
  }
  function fallback(reason) {
    failureReason = reason || phase;
    stage.dataset.failureReason = failureReason;
    failed = true;
    teardown();
    showFallback();
  }
  function sync() {
    stop();
    if (!ready || !renderer || !visible || document.hidden || disposed) return;
    if (lightMode()) {
      showFallback();
      return;
    }
    canvas.hidden = false;
    canvas.style.display = 'block';
    // Render the settled poster pose before exposing the canvas, never a bind/T pose.
    if (firstReveal) {
      mixer.stopAllAction(); currentAction = null;
      play('skyy_idle');
      mixer.setTime(0); model.rotation.y = facing;
      stage.style.setProperty('--skyy-entry-progress', '1');
      stage.style.setProperty('--skyy-entry-shift', '0px');
      renderFrame();
      firstReveal = false; revealAt = clock() + 300;
    } else renderFrame();
    if (sprite) sprite.style.display = 'block';
    stage.dataset.renderer = '3d';
    document.dispatchEvent(new CustomEvent('skyy:3d-visible'));
    if (paused) {
      renderFrame();
      return;
    }
    running = true;
    renderer.setAnimationLoop(function (time) {
      if (!lastFrame) {
        lastFrame = time;
        renderFrame();
        return;
      }
      var targetFps = currentAction && /skyy_idle/i.test(currentAction.getClip().name) ? 15 : 30;
      // RAF timestamps are quantized:33.3ms must not be rejected as below33.333ms.
      if (time - lastFrame + 0.5 < 1000 / targetFps) return;
      if (revealAt && clock() < revealAt) { lastFrame = time; return; }
      if (revealAt) { revealAt = 0; play('skyy_walk', 1600); }
      if (profile.intervals.length < 120) profile.intervals.push(time - lastFrame);
      var delta = Math.min((time - lastFrame) / 1000, 0.5);
      mixer.update(delta);
      actionElapsed += delta;
      var locomotion = currentAction && /skyy_(walk|exit)/i.test(currentAction.getClip().name);
      var progress = locomotion ? Math.min(1, actionElapsed / 1.6) : 1;
      stage.style.setProperty('--skyy-entry-progress', progress.toFixed(4));
      stage.style.setProperty('--skyy-entry-shift', (locomotion ? -20 * Math.sin(progress * Math.PI) : 0).toFixed(2) + 'px');
      // Begin and end on the same frontal anchor; the existing rig takes a short
      // two-step arc, then turns back without a discontinuous first-frame jump.
      model.rotation.y = facing + (locomotion ? Math.sin(progress * Math.PI) * 0.45 : 0);
      if (locomotion && progress > 0.75) stage.dataset.actionPhase = 'turning';
      else stage.dataset.actionPhase = locomotion ? 'walking-in' : 'idle';
      if (actionDuration && actionElapsed >= actionDuration) {
        play('skyy_idle');
        stage.dataset.actionPhase = 'idle';
        document.dispatchEvent(new CustomEvent('skyy:action-complete'));
      }
      lastFrame = time;
      renderFrame();
    });
  }
  function play(name, transient) {
    clearTimeout(timer);
    timer = null;
    if (!ready || !actions[name] || lightMode()) return;
    var next = actions[name];
    if (currentAction !== next) {
      var previous = currentAction;
      if (previous) previous.fadeOut(0.25);
      next.reset().setEffectiveWeight(1).setEffectiveTimeScale(1).play();
      if (previous) next.fadeIn(0.25);
      else {
        mixer.update(0);
        model.rotation.y = facing;
        stage.style.setProperty('--skyy-entry-progress', /skyy_(walk|exit)/.test(name) ? '0' : '1');
      }
      currentAction = next;
      actionElapsed = 0;
    }
    if (transient) actionElapsed = 0;
    actionDuration = transient ? transient / 1000 : 0;
  }
  async function boot() {
    if (started || failed || disposed || config.loadFailed || lightMode()) return;
    started = true;
    profile.startedAt = clock();
    stage.dataset.renderer = 'loading';
    try {
      markPhase('webgl-context');
      var context = canvas.getContext('webgl2', { alpha: true, antialias: true, powerPreference: 'low-power' });
      if (!context) throw new Error('WebGL unavailable');
      markPhase('local-modules');
      modules = await loadThree();
      if (disposed || failed) return;
      var THREE = modules[0];
      var modelUrl = local(config.modelUrl);
      markPhase('model-fetch');
      controller = new AbortController();
      var fetchTimer = setTimeout(function () {
        controller.abort();
      }, 15000);
      var bytes;
      try {
        var response = await fetch(modelUrl, {
          signal: controller.signal,
          credentials: 'same-origin',
          redirect: 'error',
        });
        if (!response.ok || new URL(response.url).origin !== location.origin) throw new Error('Skyy model unavailable');
        bytes = await response.arrayBuffer();
        profile.modelBytes = bytes.byteLength;
      } finally {
        clearTimeout(fetchTimer);
      }
      if (disposed || failed) return;
      var manager = new THREE.LoadingManager();
      // The canonical GLB embeds its textures. Any future external dependency
      // must still remain on this origin; blob URLs only come from GLTFLoader.
      manager.setURLModifier(function (url) {
        return /^(blob:|data:)/.test(url) ? url : local(url);
      });
      var loader = new modules[1].GLTFLoader(manager);
      markPhase('draco-decoder');
      draco = new modules[2].DRACOLoader(manager);
      draco.setDecoderPath(local(config.decoderPath));
      draco.setWorkerLimit(1);
      loader.setDRACOLoader(draco);
      markPhase('model-decode');
      var parsing = loader.parseAsync(bytes, new URL('.', modelUrl).href).then(function (result) {
        if (failed || disposed) disposeModel(result.scene);
        return result;
      });
      var gltf = await limited(parsing, 15000);
      bytes = null; // The parsed scene owns decoded buffers; release our fetch reference.
      if (draco) {
        draco.dispose();
        draco = null;
      }
      if (disposed || failed) {
        disposeModel(gltf.scene);
        return;
      }
      model = gltf.scene;
      markPhase('canonical-rig');
      var skinned = false;
      model.traverse(function (node) {
        if (node.isSkinnedMesh && node.skeleton && node.skeleton.bones.length) {
          skinned = true;
          node.frustumCulled = false;
        }
      });
      var clips = gltf.animations || [];
      if (
        !skinned ||
        required.some(function (name) {
          return !clips.some(function (clip) {
            return clip.name.toLowerCase() === name && clip.tracks.length && clip.duration > 0;
          });
        })
      )
        throw new Error('Skyy canonical rig/action set incomplete');
      markPhase('model-bounds');
      if (!(await prepareBounds(THREE, model, function () { return disposed || failed; }, yieldMainThread))) return;
      var size = new THREE.Box3().setFromObject(model).getSize(new THREE.Vector3());
      if (!Number.isFinite(size.y) || size.y <= 0) throw new Error('Skyy model bounds invalid');
      model.scale.setScalar(1.8 / size.y);
      var box = new THREE.Box3().setFromObject(model);
      var center = box.getCenter(new THREE.Vector3());
      model.position.x -= center.x;
      model.position.z -= center.z;
      model.position.y -= box.min.y;
      markPhase('renderer-initialization');
      renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        context: context,
        alpha: true,
        antialias: true,
        powerPreference: 'low-power',
      });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
      renderer.setSize(220, 340, false);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(30, 220 / 340, 0.1, 50);
      camera.position.set(0, 1.1, 4.1);
      camera.lookAt(0, 0.9, 0);
      scene.add(new THREE.AmbientLight(0xffffff, 1.4));
      var key = new THREE.DirectionalLight(0xfff5e6, 1.8);
      key.position.set(2, 4, 3);
      scene.add(key);
      var fill = new THREE.DirectionalLight(0xe6f0ff, 0.6);
      fill.position.set(-2, 2, -1);
      scene.add(fill);
      scene.add(model);
      markPhase('animation-setup');
      mixer = new THREE.AnimationMixer(model);
      facing = model.rotation.y;
      rigMotion = deriveRigMotion(THREE, clips, model);
      rigMotion.clips.forEach(function (clip) {
        actions[clip.name.toLowerCase()] = mixer.clipAction(clip);
      });
      markPhase('resource-profile');
      profileModel();
      // Start shader preparation before cooperative sphere work, giving the
      // driver time to compile without an uncancellable asynchronous poll.
      // Three's first render also scans every skinned vertex for its sort sphere.
      // Cache the exact time-zero idle-pose sphere cooperatively before revealing.
      actions.skyy_idle.play();
      mixer.setTime(0);
      markPhase('shader-prepare');
      if (!(await prepareShaders(renderer, scene, camera, function () { return disposed || failed; }, yieldMainThread))) return;
      markPhase('idle-sphere');
      if (!(await prepareBounds(THREE, model, function () { return disposed || failed; }, yieldMainThread, true))) return;
      markPhase('texture-upload');
      var uploadTextures = new Set();
      model.traverse(function (node) {
        (Array.isArray(node.material) ? node.material : [node.material]).filter(Boolean).forEach(function (material) {
          Object.values(material).forEach(function (value) { if (value && value.isTexture) uploadTextures.add(value); });
        });
      });
      for (var texture of uploadTextures) {
        if (disposed || failed) return;
        renderer.initTexture(texture);
        await yieldMainThread();
      }
      if (disposed || failed) return;
      ready = true;
      markPhase('ready');
      document.dispatchEvent(new CustomEvent('skyy:3d-ready', { detail: { clips: Object.keys(actions) } }));
      // The source clips remain intact; held poses receive the documented runtime gait.
      play('skyy_idle');
      sync();
    } catch (_) {
      if (!disposed) fallback();
    }
  }
  document.addEventListener('skyy:walking-in', function () {
    visible = true;
    boot();
    if (ready) {
      play('skyy_walk', 1600);
      sync();
    }
  });
  document.addEventListener('skyy:prepare', function () {
    visible = true;
    boot();
    sync();
  });
  document.addEventListener('skyy:show', function () {
    visible = true;
    if (ready) play('skyy_idle');
    sync();
  });
  document.addEventListener('skyy:hidden', function () {
    visible = false;
    clearTimeout(timer);
    stop();
    canvas.hidden = true;
  });
  document.addEventListener('skyy:idle', function () {
    if (!actionDuration) play('skyy_idle');
  });
  document.addEventListener('skyy:speaking', function () {
    play('skyy_talk', 2400);
  });
  ['wave', 'joy', 'exit'].forEach(function (name) {
    document.addEventListener('skyy:' + name, function () {
      play('skyy_' + name, 1400);
    });
  });
  document.addEventListener('skyy:motion', function (event) {
    paused = !!(event.detail && event.detail.paused);
    sync();
  });
  document.addEventListener('visibilitychange', sync);
  motion.addEventListener('change', sync);
  if (connection && connection.addEventListener) connection.addEventListener('change', sync);
  canvas.addEventListener('webglcontextlost', function (event) {
    event.preventDefault();
    fallback('webgl-context-lost');
  });
  window.addEventListener('pagehide', function (event) {
    stop();
    if (!event.persisted) {
      disposed = true;
      teardown();
    }
  });
  window.addEventListener('pageshow', function (event) {
    if (event.persisted) sync();
  });
  window.skyyRoseMascot3D = Object.freeze({
    isReady: function () {
      return ready;
    },
    getActions: function () {
      return Object.keys(actions);
    },
    getCurrentAction: function () {
      return currentAction ? currentAction.getClip().name : null;
    },
    getMotionEvidence: function () {
      if (!rigMotion || !model) return null;
      var poses = {};
      ['thighl', 'thighr', 'shinl', 'shinr', 'footl', 'footr', 'upperarml', 'upperarmr', 'head'].forEach(
        function (key) {
          poses[key] = rigMotion.bones[key].quaternion.toArray();
        }
      );
      return {
        sourceClips: rigMotion.source,
        motionSource: currentAction ? currentAction.getClip().skyyMotionSource || 'source-clip' : null,
        clipTime: currentAction ? currentAction.time : null,
        elapsed: actionElapsed,
        poses: poses,
        facing: model.rotation.y,
      };
    },
    getFailureReason: function () {
      return failureReason;
    },
    resetFrameProfile: function () { profile.frames = []; profile.intervals = []; },
    getProfile: function () {
      return Object.assign({}, profile, { frames: profile.frames.slice(), intervals: profile.intervals.slice(), stages: profile.stages.slice(),
        triangles: renderer ? renderer.info.render.triangles : null,
        drawCalls: renderer ? renderer.info.render.calls : null,
        runtimeGeometries: renderer ? renderer.info.memory.geometries : null,
        runtimeTextures: renderer ? renderer.info.memory.textures : null });
    },
    capturePoster: function () {
      if (!ready || !renderer) return null;
      stop(); mixer.stopAllAction(); currentAction = null;
      play('skyy_idle'); mixer.setTime(0); model.rotation.y = facing;
      renderer.render(scene, camera);
      return canvas.toDataURL('image/png');
    },
    getRenderState: function () {
      return { phase: phase, frames: frameCount, running: running, visible: visible, paused: paused };
    },
  });
  if (visible) boot();
})();
