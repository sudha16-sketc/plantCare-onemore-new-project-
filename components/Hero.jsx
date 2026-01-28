import './Hero.css'
import Background3D from "./Background3D";
import { useEffect, useState } from "react";


function Hero() {
    const [scale, setScale] = useState(1);

  useEffect(() => {
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
<div className="logo-container">
            <svg className="logo-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C12 2 8 6 8 10C8 11.0609 8.42143 12.0783 9.17157 12.8284C9.92172 13.5786 10.9391 14 12 14C13.0609 14 14.0783 13.5786 14.8284 12.8284C15.5786 12.0783 16 11.0609 16 10C16 6 12 2 12 2Z" fill="currentColor"/>
              <path d="M12 14V22M8 18H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <h1 className="app-title">
              <span className="title-main">PlantCare</span>
              <span className="title-sub">AI Guide</span>
            </h1>
          </div>
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
