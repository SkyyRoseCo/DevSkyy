/**
 * SkyyRose Product 3D Viewer — PDP "View in 3D" dialog (WS3).
 *
 * Wired to the button inc/woocommerce.php prints next to the gallery
 * (`button.view-3d-model[data-model]`). Nothing 3D is fetched until the
 * first click: three r170 + GLTFLoader + KTX2Loader + OrbitControls +
 * RoomEnvironment + the meshopt decoder are dynamic-import()ed from the
 * self-hosted lib dir (assets/js/lib/three-0.170.0/, CSP script-src 'self').
 *
 * The web GLBs (gltfpack -cc -tc) REQUIRE EXT_meshopt_compression and
 * KHR_texture_basisu, so the loader always registers MeshoptDecoder and a
 * KTX2Loader pointed at the vendored basis transcoder — without both the
 * load fails. Module URLs carry no ?ver: the addons import
 * './three.module.min.js' relatively and a query string on our side would
 * create a second three instance.
 *
 * @package SkyyRose
 * @since 2.3.0
 */
(function () {
  'use strict';

  var config = window.skyyRoseProduct3d || {};
  var libBase = typeof config.libBase === 'string' ? config.libBase : '';
  var i18n = config.i18n || {};
  var triggers = document.querySelectorAll('button.view-3d-model[data-model]');

  if (!triggers.length || !libBase) {
    return;
  }

  var MAX_PIXEL_RATIO = 2;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function text(key, fallback) {
    return typeof i18n[key] === 'string' && i18n[key] ? i18n[key] : fallback;
  }

  function el(tag, className, content) {
    var node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (content) {
      node.textContent = content;
    }
    return node;
  }

  /* ════════════════════════════════════════
	   WebGL availability — checked before any module is fetched
	   ════════════════════════════════════════ */
  function hasWebGL() {
    try {
      var probe = document.createElement('canvas');
      var gl = probe.getContext('webgl2') || probe.getContext('webgl');
      if (!gl) {
        return false;
      }
      var lose = gl.getExtension('WEBGL_lose_context');
      if (lose) {
        lose.loseContext();
      }
      return true;
    } catch (err) {
      return false;
    }
  }

  /* ════════════════════════════════════════
	   Dialog shell
	   ════════════════════════════════════════ */
  function buildDialog(productName) {
    var dialog = el('dialog', 'sr-3d-dialog');
    dialog.setAttribute('aria-labelledby', 'sr-3d-title');

    var head = el('div', 'sr-3d-dialog__head');
    var title = el('h2', 'sr-3d-dialog__title', productName);
    title.id = 'sr-3d-title';
    var close = el('button', 'sr-3d-dialog__close');
    close.type = 'button';
    close.setAttribute('aria-label', text('close', 'Close 3D viewer'));
    close.appendChild(el('span', 'sr-3d-dialog__close-glyph', '×'));
    head.appendChild(title);
    head.appendChild(close);

    var stage = el('div', 'sr-3d-dialog__stage');
    var canvas = el('canvas', 'sr-3d-dialog__canvas');
    canvas.setAttribute('aria-hidden', 'true');
    var status = el('p', 'sr-3d-dialog__status', text('loading', 'Loading 3D model…'));
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    stage.appendChild(canvas);
    stage.appendChild(status);

    var hint = el('p', 'sr-3d-dialog__hint', text('hint', 'Drag to rotate · Scroll or pinch to zoom'));

    dialog.appendChild(head);
    dialog.appendChild(stage);
    dialog.appendChild(hint);

    return { dialog: dialog, close: close, stage: stage, canvas: canvas, status: status };
  }

  function setStatus(ui, message, state) {
    ui.status.textContent = message;
    ui.dialog.classList.remove('is-loading', 'is-ready', 'is-error');
    ui.dialog.classList.add(state);
  }

  /* ════════════════════════════════════════
	   Scroll lock — restore exactly what was there
	   ════════════════════════════════════════ */
  var scrollLock = null;
  function lockScroll() {
    if (scrollLock !== null) {
      return;
    }
    scrollLock = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
  }
  function unlockScroll() {
    if (scrollLock === null) {
      return;
    }
    document.body.style.overflow = scrollLock;
    scrollLock = null;
  }

  /* ════════════════════════════════════════
	   three.js session — one per open dialog, fully disposed on close
	   ════════════════════════════════════════ */
  function disposeMaterial(material) {
    Object.keys(material).forEach(function (key) {
      var value = material[key];
      if (value && value.isTexture) {
        value.dispose();
      }
    });
    material.dispose();
  }

  function disposeObject(root) {
    root.traverse(function (node) {
      if (node.geometry) {
        node.geometry.dispose();
      }
      if (!node.material) {
        return;
      }
      if (Array.isArray(node.material)) {
        node.material.forEach(disposeMaterial);
      } else {
        disposeMaterial(node.material);
      }
    });
  }

  function loadModules() {
    return Promise.all([
      import(libBase + 'three.module.min.js'),
      import(libBase + 'GLTFLoader.js'),
      import(libBase + 'KTX2Loader.js'),
      import(libBase + 'OrbitControls.js'),
      import(libBase + 'RoomEnvironment.js'),
      import(libBase + 'meshopt_decoder.module.js'),
    ]).then(function (mods) {
      return {
        THREE: mods[0],
        GLTFLoader: mods[1].GLTFLoader,
        KTX2Loader: mods[2].KTX2Loader,
        OrbitControls: mods[3].OrbitControls,
        RoomEnvironment: mods[4].RoomEnvironment,
        MeshoptDecoder: mods[5].MeshoptDecoder,
      };
    });
  }

  function createSession(ui, modelUrl) {
    var session = { closed: false, teardown: null };

    loadModules()
      .then(function (lib) {
        if (session.closed) {
          return null;
        }
        var THREE = lib.THREE;
        var renderer = null;
        var envTarget = null;
        var ktx2 = null;
        var controls = null;
        var observer = null;
        var model = null;
        var scene = new THREE.Scene();
        var framing = null;
        var userAdjusted = false;

        // Assigned BEFORE construction: a throw part-way through (a WebGL context
        // refused at the browser's ~16-context cap, a transcoder that will not load)
        // must still release whatever already exists, or every retry leaks a context.
        function teardown() {
          if (renderer) {
            renderer.setAnimationLoop(null);
          }
          if (observer) {
            observer.disconnect();
          }
          reduceMotion.removeEventListener('change', onMotionChange);
          if (controls) {
            controls.dispose();
          }
          if (model) {
            scene.remove(model);
            disposeObject(model);
          }
          scene.environment = null;
          if (envTarget) {
            envTarget.dispose();
          }
          if (ktx2) {
            ktx2.dispose();
          }
          if (renderer) {
            renderer.dispose();
            renderer.forceContextLoss();
          }
        }
        session.teardown = teardown;

        function onMotionChange(event) {
          if (controls) {
            controls.autoRotate = !event.matches;
          }
        }

        var camera = new THREE.PerspectiveCamera(35, 1, 0.01, 100);

        /*
         * Fit BOTH axes. Fitting only the vertical FOV crops every width-dominant
         * garment (shorts, a T-posed jersey, the two-piece sets) on a portrait phone,
         * where the stage aspect is ~0.49 — the horizontal half-angle is the vertical
         * one scaled by aspect, so width needs dividing by it.
         */
        function fitDistance() {
          if (!framing) {
            return null;
          }
          var half = Math.tan((camera.fov * Math.PI) / 180 / 2);
          return Math.max(framing.height / half, framing.width / half / camera.aspect) * 1.35;
        }

        function applyFit(initial) {
          var distance = fitDistance();
          if (!distance) {
            return;
          }
          camera.near = distance / 100;
          camera.far = distance * 100;
          controls.minDistance = distance * 0.45;
          controls.maxDistance = distance * 2.5;
          if (initial) {
            camera.position.set(0, framing.height * 0.1, distance);
          } else if (!userAdjusted) {
            /*
             * Untouched view: re-fit in both directions. A phone rotated to landscape
             * gains width and loses height, so pull-back-only would keep the portrait
             * distance and leave the garment at ~11% of the stage width.
             */
            camera.position.setLength(distance);
          } else if (camera.position.length() < distance) {
            // After the viewer has orbited or zoomed, only ever pull back — never crop.
            camera.position.setLength(distance);
          }
          camera.updateProjectionMatrix();
          controls.update();
        }

        function resize() {
          var width = ui.stage.clientWidth;
          var height = ui.stage.clientHeight;
          if (!width || !height) {
            return;
          }
          camera.aspect = width / height;
          camera.updateProjectionMatrix();
          renderer.setSize(width, height, false);
          applyFit(false);
        }

        try {
          renderer = new THREE.WebGLRenderer({
            canvas: ui.canvas,
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance',
          });
          renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO));
          renderer.outputColorSpace = THREE.SRGBColorSpace;
          renderer.toneMapping = THREE.NeutralToneMapping;
          renderer.toneMappingExposure = 1;

          var pmrem = new THREE.PMREMGenerator(renderer);
          var room = new lib.RoomEnvironment();
          envTarget = pmrem.fromScene(room, 0.04);
          scene.environment = envTarget.texture;
          room.traverse(function (node) {
            if (node.geometry) {
              node.geometry.dispose();
            }
            if (node.material) {
              node.material.dispose();
            }
          });
          pmrem.dispose();

          controls = new lib.OrbitControls(camera, ui.canvas);
          controls.enableDamping = true;
          controls.dampingFactor = 0.08;
          controls.enablePan = false;
          controls.autoRotate = !reduceMotion.matches;
          controls.autoRotateSpeed = 1;
          // 'start' fires on pointer/wheel input only — autoRotate does not trip it.
          controls.addEventListener('start', function () {
            userAdjusted = true;
          });

          ktx2 = new lib.KTX2Loader().setTranscoderPath(libBase + 'basis/').detectSupport(renderer);
          observer = new ResizeObserver(resize);
          observer.observe(ui.stage);
          reduceMotion.addEventListener('change', onMotionChange);
          resize();
        } catch (err) {
          teardown();
          throw err;
        }

        // A context lost after load stops three's render loop silently; say so.
        ui.canvas.addEventListener('webglcontextlost', function () {
          if (!session.closed) {
            setStatus(ui, text('error', 'The 3D model could not be loaded.'), 'is-error');
          }
        });

        var loader = new lib.GLTFLoader().setKTX2Loader(ktx2).setMeshoptDecoder(lib.MeshoptDecoder);
        return loader.loadAsync(modelUrl).then(function (gltf) {
          if (session.closed) {
            disposeObject(gltf.scene);
            return null;
          }
          var box = new THREE.Box3().setFromObject(gltf.scene);
          if (box.isEmpty()) {
            // Renderable-geometry-free GLB: fail loudly instead of an empty stage.
            disposeObject(gltf.scene);
            throw new Error('GLB contains no renderable geometry');
          }
          model = gltf.scene;
          var size = box.getSize(new THREE.Vector3());
          model.position.sub(box.getCenter(new THREE.Vector3()));
          framing = {
            height: (size.y || 1) / 2,
            width: (Math.max(size.x, size.z) || 1) / 2,
          };
          controls.target.set(0, 0, 0);
          applyFit(true);

          scene.add(model);
          renderer.setAnimationLoop(function () {
            controls.update();
            renderer.render(scene, camera);
          });
          setStatus(ui, text('ready', '3D model loaded'), 'is-ready');
          return null;
        });
      })
      .catch(function () {
        if (session.closed) {
          return;
        }
        setStatus(ui, text('error', 'The 3D model could not be loaded. Please try again later.'), 'is-error');
      });

    return session;
  }

  /* ════════════════════════════════════════
	   Open / close
	   ════════════════════════════════════════ */
  function openViewer(trigger) {
    var modelUrl = trigger.getAttribute('data-model');
    var productName = trigger.getAttribute('data-product-name') || text('title', 'View in 3D');
    if (!modelUrl) {
      return;
    }

    var ui = buildDialog(productName);
    document.body.appendChild(ui.dialog);
    lockScroll();

    var session = null;
    if (hasWebGL()) {
      setStatus(ui, text('loading', 'Loading 3D model…'), 'is-loading');
      session = createSession(ui, modelUrl);
    } else {
      setStatus(
        ui,
        text('noWebgl', 'Your browser cannot display 3D models. The photos above show every detail.'),
        'is-error'
      );
    }

    function close() {
      if (ui.dialog.open) {
        ui.dialog.close();
      }
    }
    ui.close.addEventListener('click', close);
    ui.dialog.addEventListener('click', function (event) {
      if (event.target === ui.dialog) {
        close();
      }
    });
    ui.dialog.addEventListener('close', function () {
      if (session) {
        session.closed = true;
        if (session.teardown) {
          session.teardown();
        }
      }
      ui.dialog.remove();
      unlockScroll();
      trigger.focus();
    });

    ui.dialog.showModal();
    ui.close.focus();
  }

  triggers.forEach(function (trigger) {
    trigger.addEventListener('click', function () {
      openViewer(trigger);
    });
  });
})();
