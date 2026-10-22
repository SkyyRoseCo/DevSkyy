'use client';

import { Canvas } from '@react-three/fiber';
import {
  OrbitControls,
  Environment,
  ContactShadows,
  PresentationControls,
  Stage,
  Lightformer,
  useGLTF,
  Center,
  AccumulativeShadows,
  RandomizedLight,
  Float,
} from '@react-three/drei';
import { EffectComposer, Bloom, ToneMapping } from '@react-three/postprocessing';
import { motion } from 'framer-motion';
import { Suspense, useState } from 'react';
import * as THREE from 'three';

interface LuxuryProductViewerProps {
  modelUrl: string;
  productName: string;
  environment?:
    'sunset' | 'dawn' | 'night' | 'warehouse' | 'forest' | 'apartment' | 'studio' | 'city' | 'park' | 'lobby';
  enableAR?: boolean;
  autoRotate?: boolean;
  showEffects?: boolean;
}

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);

  // Apply luxury materials
  scene.traverse(child => {
    if ((child as THREE.Mesh).isMesh) {
      const mesh = child as THREE.Mesh;
      if (mesh.material) {
        (mesh.material as THREE.MeshStandardMaterial).metalness = 0.9;
        (mesh.material as THREE.MeshStandardMaterial).roughness = 0.1;
        (mesh.material as THREE.MeshStandardMaterial).envMapIntensity = 1.5;
      }
    }
  });

  return (
    <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
      <primitive object={scene} />
    </Float>
  );
}

function LuxuryShadows() {
  return (
    <AccumulativeShadows
      temporal
      frames={100}
      color='#B76E79'
      colorBlend={2}
      toneMapped={true}
      alphaTest={0.9}
      opacity={1}
      scale={12}
      position={[0, -0.5, 0]}
    >
      <RandomizedLight amount={8} radius={10} ambient={0.5} intensity={1} position={[5, 5, -10]} bias={0.001} />
    </AccumulativeShadows>
  );
}

function LuxuryEnvironment() {
  return (
    <Environment resolution={256}>
      <group rotation={[-Math.PI / 3, 0, 1]}>
        <Lightformer
          form='circle'
          intensity={4}
          rotation-x={Math.PI / 2}
          position={[0, 5, -9]}
          scale={2}
          color='#B76E79'
        />
        <Lightformer
          form='circle'
          intensity={2}
          rotation-y={Math.PI / 2}
          position={[-5, 1, -1]}
          scale={2}
          color='#8B5A62'
        />
        <Lightformer
          form='circle'
          intensity={2}
          rotation-y={-Math.PI / 2}
          position={[10, 1, 0]}
          scale={8}
          color='#ffffff'
        />
        <Lightformer
          form='ring'
          color='#B76E79'
          intensity={1}
          onUpdate={self => self.lookAt(0, 0, 0)}
          position={[10, 10, 0]}
          scale={10}
        />
      </group>
    </Environment>
  );
}

export default function LuxuryProductViewer({
  modelUrl,
  productName,
  environment = 'studio',
  enableAR = true,
  autoRotate = true,
  showEffects = true,
}: LuxuryProductViewerProps) {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className='relative w-full h-full min-h-[600px] bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 rounded-lg overflow-hidden'
    >
      {/* Loading overlay */}
      {isLoading && (
        <div className='absolute inset-0 flex items-center justify-center bg-slate-950/80 z-10'>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className='text-center'>
            <div className='w-16 h-16 border-4 border-[#B76E79] border-t-transparent rounded-full animate-spin mx-auto mb-4' />
            <p className='text-[#B76E79] font-light tracking-wider'>Loading {productName}...</p>
          </motion.div>
        </div>
      )}

      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ position: [0, 0, 5], fov: 45 }}
        gl={{ preserveDrawingBuffer: true, antialias: true }}
        onCreated={() => setIsLoading(false)}
      >
        <Suspense fallback={null}>
          <PresentationControls
            global
            snap
            rotation={[0, 0.3, 0]}
            polar={[-Math.PI / 3, Math.PI / 3]}
            azimuth={[-Math.PI / 1.4, Math.PI / 2]}
            speed={1.5}
          >
            <Stage environment={environment} intensity={0.5} shadows={false}>
              <Center>
                <Model url={modelUrl} />
              </Center>
            </Stage>
          </PresentationControls>

          <LuxuryEnvironment />
          <LuxuryShadows />
          <ContactShadows position={[0, -0.8, 0]} opacity={0.4} scale={10} blur={2} far={0.8} />

          <OrbitControls
            autoRotate={autoRotate}
            autoRotateSpeed={0.5}
            enableZoom={true}
            enablePan={false}
            minPolarAngle={Math.PI / 2.5}
            maxPolarAngle={Math.PI / 1.5}
            makeDefault
          />

          {showEffects && (
            <EffectComposer>
              <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.9} intensity={1.5} />
              <ToneMapping />
            </EffectComposer>
          )}
        </Suspense>
      </Canvas>

      {/* Product info overlay */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className='absolute bottom-6 left-6 text-white'
      >
        <h3 className='text-2xl font-light tracking-wider mb-1'>{productName}</h3>
        <p className='text-[#B76E79] text-sm tracking-widest'>THE SKYY ROSE COLLECTION</p>
      </motion.div>

      {/* AR button */}
      {enableAR && (
        <motion.button
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className='absolute top-6 right-6 px-6 py-3 bg-[#B76E79] text-white rounded-full font-light tracking-wider hover:bg-[#8B5A62] transition-colors'
        >
          View in AR
        </motion.button>
      )}
    </motion.div>
  );
}

// Preload GLTF model
export function preloadModel(url: string) {
  useGLTF.preload(url);
}
