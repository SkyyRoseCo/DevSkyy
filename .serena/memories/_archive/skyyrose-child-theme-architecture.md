# SkyyRose Immersive Child Theme Architecture

## Research Summary - Complete Implementation Guide

---

## 1. WordPress Child Theme Structure

### Required Files

```
skyyrose-immersive/
├── style.css              # Theme header + custom CSS
├── functions.php          # Enqueue scripts, register widgets
├── screenshot.png         # Theme thumbnail (1200x900)
├── assets/
│   ├── js/
│   │   ├── three.min.js           # Three.js library
│   │   ├── GLTFLoader.js          # Model loader
│   │   ├── OrbitControls.js       # Camera controls
│   │   ├── signature-experience.js # Rose garden 3D
│   │   ├── lovehurts-experience.js # Castle 3D
│   │   └── blackrose-experience.js # Gothic garden 3D
│   ├── css/
│   │   └── immersive.css          # Collection page styles
│   ├── models/                     # GLB 3D models
│   ├── textures/                   # HDR environments
│   └── images/                     # Static assets
├── widgets/
│   └── class-threejs-viewer-widget.php
├── templates/
│   ├── template-signature.php
│   ├── template-lovehurts.php
│   └── template-blackrose.php
└── inc/
    └── elementor-widgets.php
```

### style.css Header

```css
/*
Theme Name: SkyyRose Immersive
Theme URI: https://skyyrose.co
Description: Immersive 3D collection experiences for SkyyRose e-commerce
Author: SkyyRose LLC
Author URI: https://skyyrose.co
Template: flavor           # Parent theme folder name
Version: 1.0.0
License: Proprietary
Text Domain: skyyrose-immersive
*/
```

### functions.php Pattern

```php
<?php
// Enqueue parent + child styles
add_action('wp_enqueue_scripts', 'skyyrose_enqueue_styles');
function skyyrose_enqueue_styles() {
    wp_enqueue_style('parent-style', get_template_directory_uri() . '/style.css');
    wp_enqueue_style('child-style', get_stylesheet_uri(), ['parent-style']);
}

// Register Three.js and experiences
add_action('wp_enqueue_scripts', 'skyyrose_register_3d_scripts');
function skyyrose_register_3d_scripts() {
    wp_register_script('threejs', get_stylesheet_directory_uri() . '/assets/js/three.min.js', [], '0.160.0', true);
    wp_register_script('gltf-loader', get_stylesheet_directory_uri() . '/assets/js/GLTFLoader.js', ['threejs'], '1.0.0', true);
    wp_register_script('orbit-controls', get_stylesheet_directory_uri() . '/assets/js/OrbitControls.js', ['threejs'], '1.0.0', true);
}
```

---

## 2. Elementor Integration

### Register Custom Widget

```php
add_action('elementor/widgets/register', 'skyyrose_register_widgets');
function skyyrose_register_widgets($widgets_manager) {
    require_once(get_stylesheet_directory() . '/widgets/class-threejs-viewer-widget.php');
    $widgets_manager->register(new \SkyyRose_ThreeJS_Viewer_Widget());
}

// Enqueue scripts for Elementor
add_action('elementor/frontend/after_register_scripts', 'skyyrose_elementor_scripts');
function skyyrose_elementor_scripts() {
    wp_register_script('signature-experience',
        get_stylesheet_directory_uri() . '/assets/js/signature-experience.js',
        ['threejs', 'gltf-loader', 'orbit-controls'],
        '1.0.0', true
    );
}
```

### Widget Structure

```php
class SkyyRose_ThreeJS_Viewer_Widget extends \Elementor\Widget_Base {
    public function get_name() { return 'skyyrose_3d_viewer'; }
    public function get_title() { return 'SkyyRose 3D Viewer'; }
    public function get_icon() { return 'eicon-eye'; }
    public function get_categories() { return ['skyyrose']; }

    public function get_script_depends() {
        return ['threejs', 'gltf-loader', 'orbit-controls', 'signature-experience'];
    }

    protected function register_controls() {
        $this->start_controls_section('content', [
            'label' => 'Experience Settings',
            'tab' => \Elementor\Controls_Manager::TAB_CONTENT,
        ]);

        $this->add_control('experience_type', [
            'label' => 'Collection',
            'type' => \Elementor\Controls_Manager::SELECT,
            'options' => [
                'signature' => 'Signature (Rose Garden)',
                'lovehurts' => 'Love Hurts (Castle)',
                'blackrose' => 'Black Rose (Gothic)',
            ],
            'default' => 'signature',
        ]);

        $this->add_control('height', [
            'label' => 'Height',
            'type' => \Elementor\Controls_Manager::SLIDER,
            'range' => ['px' => ['min' => 400, 'max' => 1000]],
            'default' => ['size' => 600, 'unit' => 'px'],
        ]);

        $this->end_controls_section();
    }

    protected function render() {
        $settings = $this->get_settings_for_display();
        $type = $settings['experience_type'];
        $height = $settings['height']['size'];
        ?>
        <div class="skyyrose-3d-container"
             data-experience="<?php echo esc_attr($type); ?>"
             style="height: <?php echo esc_attr($height); ?>px;">
        </div>
        <?php
    }
}
```

---

## 3. Three.js Implementation Patterns

### Basic Scene Setup

```javascript
const container = document.getElementById('container');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.35;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 2, 5);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.minDistance = 2;
controls.maxDistance = 10;
```

### HDR Environment + GLB Model Loading

```javascript
const hdrLoader = new HDRLoader().setPath('textures/');
const gltfLoader = new GLTFLoader().setPath('models/');

const [texture, gltf] = await Promise.all([
    hdrLoader.loadAsync('environment.hdr'),
    gltfLoader.loadAsync('product.glb'),
]);

texture.mapping = THREE.EquirectangularReflectionMapping;
scene.background = texture;
scene.environment = texture;
scene.add(gltf.scene);
```

### Post-Processing (Bloom + DoF)

```javascript
const renderPass = new RenderPass(scene, camera);
const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    1.5,  // strength
    0.4,  // radius
    0.85  // threshold
);
const bokehPass = new BokehPass(scene, camera, {
    focus: 1.0,
    aperture: 0.025,
    maxblur: 0.01
});
const outputPass = new OutputPass();

const composer = new EffectComposer(renderer);
composer.addPass(renderPass);
composer.addPass(bloomPass);
composer.addPass(bokehPass);
composer.addPass(outputPass);
```

### Particle System (Falling Petals)

```javascript
const geometry = new THREE.BufferGeometry();
const vertices = [];
const velocities = [];

for (let i = 0; i < 1000; i++) {
    vertices.push(
        Math.random() * 20 - 10,  // x
        Math.random() * 20,        // y
        Math.random() * 20 - 10   // z
    );
    velocities.push({
        x: Math.random() * 0.02 - 0.01,
        y: -Math.random() * 0.02 - 0.01,
        z: Math.random() * 0.02 - 0.01,
        rotation: Math.random() * 0.1
    });
}

geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));

const material = new THREE.PointsMaterial({
    color: 0x1a1a1a,  // Black rose petals
    size: 0.1,
    transparent: true,
    opacity: 0.8,
    map: petalTexture
});

const particles = new THREE.Points(geometry, material);
scene.add(particles);
```

---

## 4. Collection-Specific Experiences

### Signature (Rose Garden)

- Colors: Crimson (#DC143C), Gold (#FFD700), Ivory (#FFFFF0), Rose Gold (#B76E79)
- Elements: Fountain, rose bushes, golden pathways, product pedestals
- Lighting: Warm sunlight, ambient glow
- Effects: Soft bloom, depth of field

### Love Hurts (Enchanted Castle)

- Colors: Deep Burgundy (#722F37), Midnight Blue (#1a1a2e), Gold Dust (#D4AF37)
- Elements: Castle walls, candelabras, gothic mirrors, enchanted rose under dome
- Lighting: Candlelight flicker, moonlight through windows
- Effects: Strong bloom on flames, fog particles

### Black Rose (Gothic Moonlit Garden)

- Colors: Obsidian (#0a0a0a), Silver Mist (#a0a0a0), Blood Red (#4a0a0a)
- Elements: Iron arbors, black/silver roses, thorned vines
- Lighting: Moonlight with blue tint
- Effects: Falling petals, ground fog, subtle bloom

---

## 5. Deployment Checklist

1. [ ] Create child theme directory on server
2. [ ] Upload style.css, functions.php, screenshot.png
3. [ ] Upload assets (js, css, models, textures)
4. [ ] Activate child theme in WordPress
5. [ ] Register Elementor widgets
6. [ ] Create/update collection pages with 3D widgets
7. [ ] Test on mobile (reduce particle count, simpler effects)
8. [ ] Performance optimize (lazy load 3D, compress models)

---

## 6. Performance Considerations

- Use Draco compression for GLB models
- Lazy load Three.js only on collection pages
- Reduce particle count on mobile
- Use LOD (Level of Detail) for distant objects
- Implement progressive loading with loading screen
