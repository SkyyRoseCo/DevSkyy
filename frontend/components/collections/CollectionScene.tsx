'use client';

import { Suspense, useRef, useState, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, ContactShadows, Html, useProgress } from '@react-three/drei';
import * as THREE from 'three';
import { motion } from 'motion/react';
import type { CollectionConfig } from '@/lib/collections';

const ENVIRONMENT_MAP: Record<string, string> = {
  night: 'night',
  apartment: 'apartment',
  studio: 'studio',
};

function Loader() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className='flex flex-col items-center gap-3'>
        <div className='w-16 h-16 border-2 border-[#B76E79] border-t-transparent rounded-full animate-spin' />
        <p className='text-[#B76E79] text-sm tracking-widest'>{progress.toFixed(0)}%</p>
      </div>
    </Html>
  );
}

function FloatingParticles({ count, color }: { count: number; color: string }) {
  const ref = useRef<THREE.Points>(null);
  const positions = useRef(Float32Array.from({ length: count * 3 }, () => (Math.random() - 0.5) * 10)).current;

  useFrame((_, delta) => {
    if (!ref.current) return;
    ref.current.rotation.y += delta * 0.02;
    const pos = ref.current.geometry.attributes.position;
    for (let i = 0; i < count; i++) {
      const y = pos.getY(i);
      pos.setY(i, y + Math.sin(Date.now() * 0.001 + i) * 0.001);
    }
    pos.needsUpdate = true;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach='attributes-position' args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial color={color} size={0.02} transparent opacity={0.6} sizeAttenuation />
    </points>
  );
}

function LuxuryPedestal({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh position={[0, 0.5, 0]}>
        <cylinderGeometry args={[0.3, 0.35, 1, 32]} />
        <meshStandardMaterial color='#1a1a1a' metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[0, 1.02, 0]}>
        <cylinderGeometry args={[0.35, 0.35, 0.04, 32]} />
        <meshStandardMaterial
          color='#B76E79'
          metalness={0.9}
          roughness={0.1}
          emissive='#B76E79'
          emissiveIntensity={0.1}
        />
      </mesh>
    </group>
  );
}

interface CollectionSceneProps {
  collection: CollectionConfig;
  className?: string;
}

export default function CollectionScene({ collection, className = '' }: CollectionSceneProps) {
  const [isReady, setIsReady] = useState(false);

  const handleCreated = useCallback(() => {
    setIsReady(true);
  }, []);

  const pedestalPositions: [number, number, number][] = [
    [-3, 0, -1],
    [-1.5, 0, -2],
    [0, 0, -1.5],
    [1.5, 0, -2],
    [3, 0, -1],
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isReady ? 1 : 0.3 }}
      transition={{ duration: 0.8 }}
      className={`relative w-full h-[500px] md:h-[600px] rounded-lg overflow-hidden ${className}`}
      style={{ backgroundColor: collection.bgColor }}
    >
      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ position: [0, 2, 6], fov: 50 }}
        gl={{ preserveDrawingBuffer: true, antialias: true }}
        onCreated={handleCreated}
      >
        <Suspense fallback={<Loader />}>
          <ambientLight intensity={0.3} />
          <spotLight
            position={[5, 8, 5]}
            angle={0.3}
            penumbra={0.8}
            intensity={1.2}
            color={collection.accentColor}
            castShadow
            shadow-mapSize={[1024, 1024]}
          />
          <spotLight position={[-5, 6, -3]} angle={0.4} penumbra={1} intensity={0.6} color='#ffffff' />

          {/* Pedestals */}
          {pedestalPositions.map((pos, i) => (
            <LuxuryPedestal key={i} position={pos} />
          ))}

          {/* Floating particles */}
          <FloatingParticles count={50} color={collection.accentColor} />

          <ContactShadows position={[0, -0.01, 0]} opacity={0.4} scale={12} blur={2} far={4} />

          <Environment preset={ENVIRONMENT_MAP[collection.environment] as 'night' | 'apartment' | 'studio'} />

          <OrbitControls
            autoRotate
            autoRotateSpeed={0.3}
            enableZoom={false}
            enablePan={false}
            minPolarAngle={Math.PI / 3}
            maxPolarAngle={Math.PI / 2.2}
            makeDefault
          />

          {/* Post-processing requires @react-three/postprocessing to be installed */}
        </Suspense>
      </Canvas>

      {/* Scene Label */}
      <div className='absolute bottom-4 left-4 z-10'>
        <p className='text-xs tracking-[0.2em] uppercase' style={{ color: collection.accentColor }}>
          3D Experience
        </p>
        <p className='text-white/60 text-sm mt-1'>{collection.name} Collection</p>
      </div>

      {/* Fullscreen hint */}
      <div className='absolute top-4 right-4 z-10 text-white/30 text-xs tracking-wider'>Drag to explore</div>
    </motion.div>
  );
}
