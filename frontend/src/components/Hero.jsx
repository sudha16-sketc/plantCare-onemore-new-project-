import "./Hero.css";
import Background3D from "./Background3D";
import { useEffect, useState } from "react";

function Hero() {
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mq.matches) return undefined;

    const onScroll = () => {
      const y = window.scrollY;
      const progress = Math.min(y / 700, 1);
      const newScale = 1.15 - progress * 0.75; // tweak magic here
      setScale(newScale);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <section className="hero-section">
      <Background3D />

      <div
        className="hero-text"
        style={{
          transform: `scale(${scale})`,
          transition: "transform 0.08s linear",
        }}
      >
        <h1>PLANT</h1>
        <h1>CARE</h1>
      </div>
    </section>
  );
}

export default Hero;
