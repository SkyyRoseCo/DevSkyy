/**
 * SkyyRose V2 immersive story-world engine.
 *
 * The complete page is rendered by PHP first. This module adds restrained DOM
 * choreography and an optional Three.js atmosphere only after the platform's
 * authoritative loader dispatches `three-ready`.
 */

(function immersiveWorlds() {
  'use strict';

  const root = document.querySelector('.sr2-immersive');

  if (!root) {
    return;
  }

  const canvas = root.querySelector('.sr2-immersive__canvas');
  const poster = root.querySelector('.sr2-immersive__poster img');
  const status = root.querySelector('.sr2-immersive__scene-status');
  const configNode = root.querySelector('.sr2-immersive__config');
  const progress = root.querySelector('.sr2-immersive__progress span');
  const chapters = Array.from(root.querySelectorAll('.sr2-immersive__chapter'));
  const chapterLinks = Array.from(root.querySelectorAll('.sr2-immersive__chapter-nav a'));
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const saveData = Boolean(navigator.connection && navigator.connection.saveData);
  let config = {};

  try {
    config = configNode ? JSON.parse(configNode.textContent) : {};
  } catch (error) {
    root.dataset.sceneState = 'config-error';
  }

  function announce(message) {
    if (status) {
      status.textContent = message;
    }
  }

  function usePoster(reason) {
    root.classList.remove('is-motion-ready');
    root.dataset.sceneState = reason;
    if (canvas) {
      canvas.hidden = true;
    }
    announce('The static story scene is ready.');
  }

  function recoverImage(image) {
    if (!poster || image === poster || image.dataset.fallbackApplied === 'true') {
      return;
    }
    image.dataset.fallbackApplied = 'true';
    image.src = poster.currentSrc || poster.src;
    image.alt = '';
  }

  // Only editorial chapter imagery may fall back to scenery. SKU images retain
  // their own identity and accessible product link when media fails.
  root.querySelectorAll('.sr2-immersive__chapter-media > img').forEach(image => {
    image.addEventListener('error', () => recoverImage(image), { once: true });
  });

  function updateProgress() {
    if (!progress) {
      return;
    }
    const maximum = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const current = Math.min(1, Math.max(0, window.scrollY / maximum));
    progress.style.transform = `scaleX(${current})`;
  }

  let progressFrame = 0;
  window.addEventListener(
    'scroll',
    () => {
      if (progressFrame) {
        return;
      }
      progressFrame = window.requestAnimationFrame(() => {
        updateProgress();
        progressFrame = 0;
      });
    },
    { passive: true }
  );
  updateProgress();

  if ('IntersectionObserver' in window) {
    const chapterObserver = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          entry.target.classList.toggle('is-active', entry.isIntersecting);
          if (!entry.isIntersecting) {
            return;
          }
          const chapterId = entry.target.id;
          chapterLinks.forEach(link => {
            if (link.getAttribute('href') === `#${chapterId}`) {
              link.setAttribute('aria-current', 'step');
            } else {
              link.removeAttribute('aria-current');
            }
          });
        });
      },
      { rootMargin: '-34% 0px -52%', threshold: 0.02 }
    );
    chapters.forEach(chapter => chapterObserver.observe(chapter));
  }

  function canUseWebGL() {
    if (!canvas || !window.WebGLRenderingContext) {
      return false;
    }
    try {
      const probe = document.createElement('canvas');
      return Boolean(probe.getContext('webgl2') || probe.getContext('webgl'));
    } catch (error) {
      return false;
    }
  }

  if (reducedMotion.matches) {
    usePoster('reduced-motion');
    return;
  }

  if (saveData) {
    usePoster('save-data');
    return;
  }

  if (!canUseWebGL()) {
    usePoster('webgl-unavailable');
    return;
  }

  let booted = false;

  function bootThree() {
    if (booted || !window.THREE || !canvas) {
      return;
    }
    booted = true;

    try {
      const THREE = window.THREE;
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
      const renderer = new THREE.WebGLRenderer({
        canvas,
        alpha: true,
        antialias: true,
        powerPreference: 'high-performance',
      });
      const world = createWorld(THREE, scene, camera, config);
      const clock = new THREE.Clock();
      const pointer = new THREE.Vector2();
      const entry = root.querySelector('.sr2-immersive__entry');
      let running = false;
      let frame = 0;
      let inView = true;

      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 0.88;

      function resize() {
        const width = Math.max(1, canvas.clientWidth);
        const height = Math.max(1, canvas.clientHeight);
        const pixelWidth = Math.floor(width * renderer.getPixelRatio());
        const pixelHeight = Math.floor(height * renderer.getPixelRatio());

        if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
          renderer.setSize(width, height, false);
          camera.aspect = width / height;
          camera.updateProjectionMatrix();
        }
      }

      function render() {
        if (!running) {
          return;
        }
        const elapsed = clock.getElapsedTime();
        world.update(elapsed, pointer);
        renderer.render(scene, camera);
        frame = window.requestAnimationFrame(render);
      }

      function start() {
        if (running || document.hidden || !inView) {
          return;
        }
        running = true;
        clock.start();
        frame = window.requestAnimationFrame(render);
      }

      function stop() {
        running = false;
        if (frame) {
          window.cancelAnimationFrame(frame);
          frame = 0;
        }
      }

      function onPointerMove(event) {
        pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
        pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
      }

      function onVisibilityChange() {
        if (document.hidden) {
          stop();
        } else {
          start();
        }
      }

      function destroy() {
        stop();
        window.removeEventListener('resize', resize);
        window.removeEventListener('pointermove', onPointerMove);
        document.removeEventListener('visibilitychange', onVisibilityChange);
        world.dispose();
        renderer.dispose();
      }

      window.addEventListener('resize', resize, { passive: true });
      window.addEventListener('pointermove', onPointerMove, { passive: true });
      document.addEventListener('visibilitychange', onVisibilityChange);
      window.addEventListener('pagehide', destroy, { once: true });

      if ('IntersectionObserver' in window && entry) {
        const sceneObserver = new IntersectionObserver(
          entries => {
            inView = entries.some(item => item.isIntersecting);
            if (inView) {
              start();
            } else {
              stop();
            }
          },
          { rootMargin: '20% 0px', threshold: 0.01 }
        );
        sceneObserver.observe(entry);
      }

      resize();
      canvas.hidden = false;
      root.classList.add('is-motion-ready');
      root.dataset.sceneState = 'three-ready';
      announce('The optional atmospheric story layer is ready.');
      start();
    } catch (error) {
      usePoster('scene-error');
    }
  }

  function createWorld(THREE, scene, camera, worldConfig) {
    const collection = worldConfig.collection || root.dataset.collection;
    const accent = new THREE.Color(worldConfig.accent || '#b76e79');
    const ambient = new THREE.HemisphereLight(0xf5f5f0, 0x0a0a0a, 0.55);
    const rim = new THREE.DirectionalLight(accent, 2.4);
    const fill = new THREE.PointLight(0xf5f5f0, 1.2, 24);
    const disposables = [];
    let updateWorld = function updateBase() {};

    rim.position.set(4, 6, 4);
    fill.position.set(-4, 2, 5);
    scene.add(ambient, rim, fill);

    function track(item) {
      disposables.push(item);
      return item;
    }

    function makeMaterial(options) {
      return track(
        new THREE.MeshStandardMaterial(
          Object.assign(
            {
              color: accent,
              roughness: 0.36,
              metalness: 0.72,
            },
            options || {}
          )
        )
      );
    }

    function makeInstances(geometry, material, count, place) {
      const instances = new THREE.InstancedMesh(track(geometry), material, count);
      const dummy = new THREE.Object3D();
      for (let index = 0; index < count; index += 1) {
        place(dummy, index, count);
        dummy.updateMatrix();
        instances.setMatrixAt(index, dummy.matrix);
      }
      instances.instanceMatrix.needsUpdate = true;
      scene.add(instances);
      return { instances, dummy };
    }

    if (collection === 'signature') {
      camera.position.set(0, 1.4, 9.5);
      const deckMaterial = makeMaterial({ color: 0x0a0a0a, roughness: 0.6, metalness: 0.5 });
      const lineMaterial = makeMaterial({ color: 0xd4af37, emissive: 0xd4af37, emissiveIntensity: 0.28 });
      const deck = new THREE.Mesh(track(new THREE.BoxGeometry(12, 0.12, 0.7)), deckMaterial);
      deck.position.y = -1.2;
      scene.add(deck);
      const posts = makeInstances(new THREE.BoxGeometry(0.05, 2.6, 0.05), lineMaterial, 32, (dummy, index, count) => {
        const progress = index / (count - 1);
        dummy.position.set(-5.5 + progress * 11, -0.1 + Math.sin(progress * Math.PI) * 0.75, 0);
        dummy.scale.y = 0.5 + Math.sin(progress * Math.PI) * 0.55;
      });
      const cable = new THREE.Line(
        track(
          new THREE.BufferGeometry().setFromPoints(
            Array.from({ length: 49 }, (_, index) => {
              const value = index / 48;
              return new THREE.Vector3(-5.5 + value * 11, 0.8 + Math.cos((value - 0.5) * Math.PI) * 1.7, 0);
            })
          )
        ),
        track(new THREE.LineBasicMaterial({ color: 0xd4af37, transparent: true, opacity: 0.78 }))
      );
      scene.add(cable);
      updateWorld = (elapsed, pointer) => {
        posts.instances.rotation.y = Math.sin(elapsed * 0.08) * 0.08;
        camera.position.x += (pointer.x * 0.45 - camera.position.x) * 0.025;
        camera.lookAt(0, -0.15, 0);
      };
    } else if (collection === 'black-rose') {
      camera.position.set(0, 0.7, 9);
      scene.fog = new THREE.FogExp2(0x0a0a0a, 0.075);
      const stone = makeMaterial({ color: 0x0a0a0a, roughness: 0.72, metalness: 0.18 });
      const silver = makeMaterial({ color: 0xc0c0c0, roughness: 0.32, metalness: 0.86 });
      for (const side of [-1, 1]) {
        for (let index = 0; index < 5; index += 1) {
          const pillar = new THREE.Mesh(track(new THREE.CylinderGeometry(0.22, 0.32, 6, 8)), stone);
          pillar.position.set(side * (2.2 + index * 1.1), 0.4, -index * 1.25);
          scene.add(pillar);
        }
      }
      const petals = makeInstances(new THREE.IcosahedronGeometry(0.055, 0), silver, 110, (dummy, index, count) => {
        const turn = index * 2.399963;
        const radius = 0.7 + (index / count) * 5.2;
        dummy.position.set(
          Math.cos(turn) * radius,
          -1.2 + ((index * 31) % 100) / 24,
          -2.5 + Math.sin(turn) * radius * 0.35
        );
        dummy.rotation.set(turn, turn * 0.5, turn * 0.2);
      });
      updateWorld = (elapsed, pointer) => {
        petals.instances.rotation.y = elapsed * 0.025;
        camera.position.x += (pointer.x * 0.24 - camera.position.x) * 0.02;
        camera.lookAt(0, 0.25, -1.5);
      };
    } else if (collection === 'love-hurts') {
      camera.position.set(0, 0.3, 9.2);
      scene.fog = new THREE.FogExp2(0x0a0a0a, 0.065);
      const shardMaterial = makeMaterial({
        color: 0xdc143c,
        emissive: 0xdc143c,
        emissiveIntensity: 0.12,
        roughness: 0.5,
      });
      const shards = makeInstances(new THREE.TetrahedronGeometry(0.22, 0), shardMaterial, 54, (dummy, index) => {
        const side = index % 2 === 0 ? -1 : 1;
        dummy.position.set(side * (1.3 + ((index * 17) % 40) / 10), -2 + ((index * 29) % 60) / 12, -1 - (index % 7));
        dummy.rotation.set(index * 0.27, index * 0.41, index * 0.13);
        dummy.scale.setScalar(0.45 + (index % 5) * 0.18);
      });
      const heart = new THREE.Mesh(track(new THREE.OctahedronGeometry(1.3, 1)), shardMaterial);
      heart.scale.set(0.88, 1.15, 0.45);
      scene.add(heart);
      updateWorld = (elapsed, pointer) => {
        shards.instances.rotation.y = Math.sin(elapsed * 0.18) * 0.18;
        heart.rotation.y = Math.sin(elapsed * 0.35) * 0.16;
        heart.rotation.x = pointer.y * 0.08;
        camera.lookAt(0, 0, 0);
      };
    } else {
      camera.position.set(0, 1.15, 9.5);
      const roseGold = makeMaterial({ color: 0xb76e79, emissive: 0xb76e79, emissiveIntensity: 0.08, roughness: 0.4 });
      const tokens = makeInstances(new THREE.OctahedronGeometry(0.2, 0), roseGold, 44, (dummy, index) => {
        const column = index % 11;
        const row = Math.floor(index / 11);
        dummy.position.set(-4 + column * 0.8, -1.6 + row * 1.1, -1 - (index % 4));
        dummy.rotation.set(index * 0.2, index * 0.33, index * 0.1);
        dummy.scale.setScalar(0.5 + (index % 4) * 0.12);
      });
      updateWorld = (elapsed, pointer) => {
        const dummy = tokens.dummy;
        for (let index = 0; index < 44; index += 2) {
          const column = index % 11;
          const row = Math.floor(index / 11);
          dummy.position.set(
            -4 + column * 0.8,
            -1.6 + row * 1.1 + Math.sin(elapsed * 0.8 + index) * 0.12,
            -1 - (index % 4)
          );
          dummy.rotation.set(index * 0.2, elapsed * 0.25 + index * 0.1, index * 0.1);
          dummy.scale.setScalar(0.5 + (index % 4) * 0.12);
          dummy.updateMatrix();
          tokens.instances.setMatrixAt(index, dummy.matrix);
        }
        tokens.instances.instanceMatrix.needsUpdate = true;
        camera.position.x += (pointer.x * 0.35 - camera.position.x) * 0.025;
        camera.lookAt(0, 0, 0);
      };
    }

    return {
      update: updateWorld,
      dispose() {
        scene.traverse(object => {
          if (object.geometry && typeof object.geometry.dispose === 'function') {
            object.geometry.dispose();
          }
        });
        disposables.forEach(item => {
          if (item && typeof item.dispose === 'function') {
            item.dispose();
          }
        });
      },
    };
  }

  document.addEventListener('three-ready', bootThree, { once: true });
  window.addEventListener('three-ready', bootThree, { once: true });

  if (window.THREE) {
    bootThree();
  } else {
    root.dataset.sceneState = 'waiting-for-three';
    const detail = {
      correlation_id: config.correlationId || root.dataset.correlationId || '',
      source: 'immersive-world',
    };
    if (typeof window.skyyRoseLoadThree === 'function') {
      window.skyyRoseLoadThree(() => bootThree());
    } else {
      window.dispatchEvent(new CustomEvent('skyyrose:request-three', { detail }));
    }
  }

  window.setTimeout(() => {
    if (!booted) {
      usePoster('three-timeout');
    }
  }, 12000);
})();
