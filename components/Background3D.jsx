import { useEffect, useState, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, useGLTF } from "@react-three/drei";

/* =========================
   Scroll → Scale Hook
========================= */
function useScrollScale({
  min = 0.75,
  max = 1.1,
  scrollRange = 700,
} = {}) {
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      const progress = Math.min(y / scrollRange, 1);
      const newScale = max - (max - min) * progress;
      setScale(newScale);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [min, max, scrollRange]);

  return scale;
}

/* =========================
   3D Model
========================= */
function Model({ scale }) {
  const ref = useRef();
  const { scene } = useGLTF("/models/ficus_bonsai.glb");

  useFrame(() => {
    if (ref.current) {
      ref.current.scale.setScalar(scale * 4); // base scale = 4
    }
  });

  return (
    <primitive
      ref={ref}
      object={scene}
      position={[0, -1, 0]}
      rotation={[0, Math.PI / 4, 0]}
    />
  );
}

/* =========================
   Background Canvas
========================= */
export default function Background3D() {
  const scale = useScrollScale();

  return (
    <Canvas
      camera={{ position: [0, 1, 5], fov: 45 }}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: -1,
      }}
    >
      <ambientLight intensity={1} />
      <directionalLight position={[5, 5, 5]} intensity={1} />

      <Model scale={scale} />

      <OrbitControls
        enableRotate={false}
        enableZoom={false}
        enablePan={false}
      />
    </Canvas>
  );
}
