# MediaPipe AR / Virtual Try-On Patterns — Immersive Interactive Architect Reference

Load when: MediaPipe Tasks Vision pose landmarks for garment overlay / virtual try-on: webcam init, landmark-to-garment mapping, graceful degradation.

Provenance: embedded copy of `host repo (DevSkyy) .claude/skills/immersive-interactive-architect/references/ar-mediapipe.md`; verbatim except the adaptations recorded in [index.md](../index.md).

MediaPipe Tasks (Vision) for pose estimation and body landmark detection, enabling
garment overlay / virtual try-on on skyyrose.co. Includes webcam init, landmark
to garment-mesh mapping, and graceful degradation.

**Product source of truth.** The single editable product source of truth is `logo-registry.json` (DevSkyy: root symlink to `<theme-root>/data/logo-registry.json`). Its `products[sku]` records own commerce fields and image/source bindings. CSV, dossiers, and `sot-images.json` manifests are generated projections or consumers, read through sanctioned readers and never authored. Corey, the founder and maker, is authoritative on his own product specs: `FOUNDER_CONFIRMED`, with no third-party verification demanded. 3D product models must be the correct garment for the SKU. Never present a hallucinated or never-made product.

---

## 1. Library Setup — MediaPipe Tasks Vision

Use the official `@mediapipe/tasks-vision` package (Tasks API, not the legacy
`@mediapipe/pose` or `holistic` packages which are deprecated).

```html
<!-- Option A: CDN importmap (standalone HTML / WordPress embed) -->
<script type="importmap">
{
  "imports": {
    "@mediapipe/tasks-vision": "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs"
  }
}
</script>

<script type="module">
import {
  PoseLandmarker,
  FilesetResolver,
  DrawingUtils,
} from '@mediapipe/tasks-vision';
// ...
</script>
```

```bash
# Option B: npm (Next.js dashboard)
npm install @mediapipe/tasks-vision
```

```javascript
// NPM usage
import { PoseLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';
```

---

## 2. Feature Detection + Graceful Fallback

**Always run this before initializing camera or MediaPipe.**

```javascript
async function checkARCapabilities() {
  const caps = {
    camera:    false,
    mediaDevices: false,
    webgl:     false,
    webxr:     false,
  };

  // Camera API
  caps.mediaDevices = Boolean(navigator.mediaDevices?.getUserMedia);

  // WebGL (required for MediaPipe WASM processing)
  try {
    const testCanvas  = document.createElement('canvas');
    const gl = testCanvas.getContext('webgl2') || testCanvas.getContext('webgl');
    caps.webgl = Boolean(gl);
  } catch (_) {}

  // WebXR (for true AR placement — optional upgrade)
  if (navigator.xr) {
    caps.webxr = await navigator.xr.isSessionSupported('immersive-ar').catch(() => false);
  }

  return caps;
}

// Tier selection
async function selectARTier() {
  const caps = await checkARCapabilities();

  if (!caps.mediaDevices || !caps.webgl) {
    return 'static';           // Fallback: show editorial product photo
  }
  if (caps.webxr) {
    return 'webxr';            // Best: real-world surface placement
  }
  return 'mediapipe-overlay';  // Good: live video garment overlay
}
```

---

## 3. Webcam Initialization

```javascript
let videoElement = null;
let stream       = null;

async function initWebcam(targetElement = null) {
  // Request rear camera on mobile (better lighting), front on desktop
  const isMobile = /Mobi|Android/i.test(navigator.userAgent);

  const constraints = {
    video: {
      facingMode: isMobile ? 'environment' : 'user',
      width:  { ideal: 1280 },
      height: { ideal: 720 },
    },
  };

  try {
    stream = await navigator.mediaDevices.getUserMedia(constraints);
  } catch (err) {
    // Handle denial or hardware absence gracefully
    if (err.name === 'NotAllowedError') {
      showFallbackUI('Camera permission denied. Enable camera access to use AR try-on.');
    } else if (err.name === 'NotFoundError') {
      showFallbackUI('No camera detected on this device.');
    } else {
      showFallbackUI('Camera unavailable. Please try on a different device.');
    }
    return null;
  }

  // Create or reuse the <video> element
  videoElement = targetElement || document.createElement('video');
  videoElement.srcObject = stream;
  videoElement.setAttribute('playsinline', '');  // iOS: prevent fullscreen takeover
  videoElement.setAttribute('autoplay', '');
  videoElement.muted = true;                     // required for autoplay

  await new Promise((resolve) => {
    videoElement.addEventListener('loadedmetadata', resolve, { once: true });
  });
  await videoElement.play();

  return videoElement;
}

function stopWebcam() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  if (videoElement) {
    videoElement.srcObject = null;
  }
}
```

---

## 4. PoseLandmarker Initialization

```javascript
let poseLandmarker = null;

async function initPoseLandmarker() {
  // FilesetResolver points to WASM binaries — host locally for production
  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm'
  );

  poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task',
      // Use pose_landmarker_full for better accuracy at higher CPU cost
      delegate: 'GPU',  // 'GPU' or 'CPU' — GPU strongly preferred for frame rate
    },
    runningMode:         'VIDEO',    // 'IMAGE' for single frames, 'VIDEO' for webcam
    numPoses:            1,          // one person for try-on; up to 3 for group
    minPoseDetectionConfidence: 0.5,
    minPosePresenceConfidence:  0.5,
    minTrackingConfidence:      0.5,
    outputSegmentationMasks: false,  // set true for silhouette cutout (heavier)
  });
}
```

---

## 5. Landmark → Garment-Mesh Mapping

MediaPipe provides 33 landmarks (world + image coordinates).
Key landmarks for garment overlays:

| Index | Landmark             | Garment Use          |
|-------|----------------------|----------------------|
|  11   | LEFT_SHOULDER        | Jacket/shirt shoulder pivot |
|  12   | RIGHT_SHOULDER       | Jacket/shirt shoulder pivot |
|  23   | LEFT_HIP             | Jacket/shirt hemline |
|  24   | RIGHT_HIP            | Jacket/shirt hemline |
|   0   | NOSE                 | Hat brim position    |
|  13   | LEFT_ELBOW           | Sleeve end reference |
|  14   | RIGHT_ELBOW          | Sleeve end reference |

```javascript
// @mediapipe/tasks-vision does NOT export POSE_LANDMARKS — landmarks are plain integer
// indices 0–32.  Key indices for garment overlays:
//   11 = LEFT_SHOULDER   12 = RIGHT_SHOULDER
//   23 = LEFT_HIP        24 = RIGHT_HIP
//    0 = NOSE            13 = LEFT_ELBOW    14 = RIGHT_ELBOW
// Access via result.landmarks[0][index] where 0 is the first detected pose.

function computeGarmentTransform(landmarks, videoWidth, videoHeight) {
  const lShoulder = landmarks[11];  // { x, y, z } — normalized 0-1
  const rShoulder = landmarks[12];
  const lHip      = landmarks[23];
  const rHip      = landmarks[24];

  // Convert normalized coords to pixel space
  const toPixel = (lm) => ({
    x: lm.x * videoWidth,
    y: lm.y * videoHeight,
  });

  const ls = toPixel(lShoulder);
  const rs = toPixel(rShoulder);
  const lh = toPixel(lHip);

  // Garment width = shoulder-to-shoulder distance
  const garmentWidth  = Math.abs(rs.x - ls.x) * 1.3; // 30% wider than shoulders
  const garmentHeight = Math.abs(lh.y - ls.y) * 1.15;
  const centerX       = (ls.x + rs.x) / 2;
  const centerY       = ls.y;

  // Rotation: tilt angle from shoulder line
  const angle = Math.atan2(rs.y - ls.y, rs.x - ls.x);

  return { centerX, centerY, garmentWidth, garmentHeight, angle };
}
```

---

## 6. Canvas Overlay Render Loop

```javascript
const overlayCanvas  = document.getElementById('ar-overlay');
const ctx2d          = overlayCanvas.getContext('2d');
const garmentImage   = new Image();
// Garment image URL is bound from logo-registry.json products[sku] image bindings
// (resolved server-side through the host repo's sanctioned readers) — never hardcoded.
garmentImage.src     = document.getElementById('skyyrose-ar-tryon').dataset.garmentUrl;

let lastVideoTime = -1;
let rafId;

function detectAndRender() {
  rafId = requestAnimationFrame(detectAndRender);

  if (!videoElement || !poseLandmarker) return;
  if (videoElement.currentTime === lastVideoTime) return; // no new frame — skip
  lastVideoTime = videoElement.currentTime;

  // Match canvas dimensions to video
  overlayCanvas.width  = videoElement.videoWidth;
  overlayCanvas.height = videoElement.videoHeight;

  // Clear previous frame
  ctx2d.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

  // Run pose detection on current video frame
  const result = poseLandmarker.detectForVideo(videoElement, performance.now());

  if (result.landmarks.length === 0) return; // no person detected — skip overlay

  const lms = result.landmarks[0]; // first person
  const {
    centerX, centerY, garmentWidth, garmentHeight, angle,
  } = computeGarmentTransform(lms, overlayCanvas.width, overlayCanvas.height);

  // Draw garment image centered on torso with rotation
  ctx2d.save();
  ctx2d.translate(centerX, centerY);
  ctx2d.rotate(angle);
  ctx2d.globalAlpha = 0.92; // slight transparency for realism
  ctx2d.drawImage(
    garmentImage,
    -garmentWidth  / 2,
    0,             // top of garment at shoulder line
    garmentWidth,
    garmentHeight,
  );
  ctx2d.restore();

  // Optional: draw skeleton overlay for debug
  if (window.DEBUG_AR) {
    const drawUtils = new DrawingUtils(ctx2d);
    drawUtils.drawLandmarks(lms, { color: '#B76E79', lineWidth: 2 });
    drawUtils.drawConnectors(lms, PoseLandmarker.POSE_CONNECTIONS, { color: '#333', lineWidth: 1 });
  }
}
```

---

## 7. Full AR Try-On Component (WordPress Shortcode Target)

```html
<!-- WordPress shortcode output target -->
<!-- $sku, $garment_url, $fallback_url and $product_name are resolved from logo-registry.json
     products[sku] (the single product source of truth) via the host repo's sanctioned readers.
     The garment image must be the correct garment for the SKU — never a hallucinated product. -->
<div id="skyyrose-ar-tryon"
     data-product-sku="<?php echo esc_attr( $sku ); ?>"
     data-garment-url="<?php echo esc_url( $garment_url ); ?>">

  <!-- Video feed (hidden visually — canvas is the display) -->
  <video id="ar-video" style="display:none;" playsinline muted></video>

  <!-- Canvas overlay where garment is composited -->
  <canvas id="ar-overlay" style="width:100%;height:auto;border-radius:8px;"></canvas>

  <!-- Fallback for no-camera / denied -->
  <div id="ar-fallback" style="display:none;">
    <img src="<?php echo esc_url( $fallback_url ); ?>"
         alt="<?php echo esc_attr( $product_name ); ?> — editorial view" style="width:100%;">
    <p>Enable camera access to view this item in AR.</p>
  </div>

  <!-- Controls -->
  <div class="ar-controls">
    <button id="ar-start-btn" class="btn-sweep">Try On →</button>
    <button id="ar-stop-btn"  class="btn-sweep" style="display:none;">Stop Camera</button>
  </div>
</div>
```

```javascript
function showFallbackUI(message) {
  document.getElementById('ar-fallback').style.display = 'block';
  document.getElementById('ar-overlay').style.display  = 'none';
  if (message) {
    const p = document.querySelector('#ar-fallback p');
    if (p) p.textContent = message;
  }
}

document.getElementById('ar-start-btn').addEventListener('click', async () => {
  const tier = await selectARTier();
  if (tier === 'static') { showFallbackUI('AR try-on requires camera access.'); return; }

  await initPoseLandmarker();
  const video = await initWebcam(document.getElementById('ar-video'));
  if (!video) return; // permission denied — fallback shown inside initWebcam

  document.getElementById('ar-start-btn').style.display = 'none';
  document.getElementById('ar-stop-btn').style.display  = 'inline-block';
  detectAndRender();
});

document.getElementById('ar-stop-btn').addEventListener('click', () => {
  cancelAnimationFrame(rafId);
  stopWebcam();
  ctx2d.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
  document.getElementById('ar-start-btn').style.display = 'inline-block';
  document.getElementById('ar-stop-btn').style.display  = 'none';
});
```

---

## 8. Performance Targets and Tuning

| Model variant           | Inference ms (mobile) | Accuracy |
|-------------------------|-----------------------|----------|
| `pose_landmarker_lite`  | ~10-20ms              | Good     |
| `pose_landmarker_full`  | ~30-50ms              | Better   |
| `pose_landmarker_heavy` | ~80-120ms             | Best     |

- Target minimum **24fps** for the overlay — below that the experience feels broken.
- At < 24fps: switch to `pose_landmarker_lite` and halve the `numPoses`.
- Use `runningMode: 'IMAGE'` for single-frame analysis (cheaper); `'VIDEO'` for real-time.
- WASM files should be self-hosted in production — CDN adds ~200ms first-inference latency.
  Copy from `node_modules/@mediapipe/tasks-vision/wasm/` to your static directory.

---

## 9. Privacy and Consent UX

Camera access requires explicit user action — never auto-start.

```javascript
// Show consent card before any getUserMedia call
function showCameraConsentCard() {
  const card = document.createElement('div');
  card.className = 'ar-consent-card';
  card.innerHTML = `
    <h3>Virtual Try-On</h3>
    <p>Camera access is used only to overlay the garment on your video — no footage is
       recorded, stored, or transmitted. Processing happens entirely on your device.</p>
    <button id="ar-consent-accept" class="btn-sweep">Enable Camera</button>
    <button id="ar-consent-skip">Skip — just show me the product</button>
  `;
  document.getElementById('skyyrose-ar-tryon').prepend(card);

  document.getElementById('ar-consent-accept').addEventListener('click', async () => {
    card.remove();
    await initWebcam();
  });
  document.getElementById('ar-consent-skip').addEventListener('click', () => {
    card.remove();
    showFallbackUI(''); // show editorial image
  });
}
```
