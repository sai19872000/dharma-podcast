/* Mandala mark — sibling to the Aura breathing ring.
   8-petal lotus (aṣṭadala) inscribed in concentric rings,
   16 ticks on the inner ring (sahasrāra echo),
   bindu at the center.  Petals rotate on a 24s breath. */

const Mandala = ({ size = 480, breathing = true }) => {
  // 8 petals at 45° spacing, drawn as teardrops radiating from center
  const petals = Array.from({ length: 8 }, (_, i) => i * 45);
  // 16 small ticks on the inner ring
  const ticks = Array.from({ length: 16 }, (_, i) => i * 22.5);

  return (
    <svg viewBox="0 0 200 200" width={size} height={size} style={{ display: 'block' }}>
      <defs>
        <radialGradient id="mandalaGlow" cx="50%" cy="50%">
          <stop offset="40%" stopColor="#8AB6FF" stopOpacity="0" />
          <stop offset="100%" stopColor="#8AB6FF" stopOpacity="0.22" />
        </radialGradient>
        <radialGradient id="mandalaCore" cx="50%" cy="50%">
          <stop offset="0%" stopColor="#8AB6FF" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#8AB6FF" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* outermost dim ring */}
      <circle cx="100" cy="100" r="94" fill="none" stroke="#C9D7E8" strokeWidth="0.35" opacity="0.18" />
      <circle cx="100" cy="100" r="82" fill="none" stroke="#C9D7E8" strokeWidth="0.35" opacity="0.28" />

      {/* outer petal ring (8 teardrop petals) — slow counter-rotation */}
      <g className={breathing ? "mandala-petals-outer" : ""} style={{ transformOrigin: '100px 100px' }}>
        {petals.map((deg) => (
          <g key={`po-${deg}`} transform={`rotate(${deg} 100 100)`}>
            {/* teardrop pointing up, tip at y=22, base at y=70 */}
            <path
              d="M 100 70 Q 78 48 100 22 Q 122 48 100 70 Z"
              fill="none"
              stroke="#8AB6FF"
              strokeWidth="0.55"
              opacity="0.55"
            />
          </g>
        ))}
      </g>

      {/* mid ring with 16 ticks (sahasrāra echo) */}
      <circle cx="100" cy="100" r="56" fill="none" stroke="#C9D7E8" strokeWidth="0.4" opacity="0.4" />
      <g className={breathing ? "mandala-ticks" : ""} style={{ transformOrigin: '100px 100px' }}>
        {ticks.map((deg) => (
          <line
            key={`tk-${deg}`}
            x1="100" y1="50"
            x2="100" y2="54"
            stroke="#C9D7E8"
            strokeWidth="0.5"
            opacity="0.5"
            transform={`rotate(${deg} 100 100)`}
          />
        ))}
      </g>

      {/* inner petal ring (8 small petals, offset by 22.5°) — slow rotation */}
      <g className={breathing ? "mandala-petals-inner" : ""} style={{ transformOrigin: '100px 100px' }}>
        {petals.map((deg) => (
          <g key={`pi-${deg}`} transform={`rotate(${deg + 22.5} 100 100)`}>
            <path
              d="M 100 80 Q 92 70 100 60 Q 108 70 100 80 Z"
              fill="none"
              stroke="#8AB6FF"
              strokeWidth="0.5"
              opacity="0.7"
            />
          </g>
        ))}
      </g>

      {/* inner solid ring */}
      <circle cx="100" cy="100" r="34" fill="none" stroke="#8AB6FF" strokeWidth="0.7" opacity="0.85" />

      {/* breathing pulse rings */}
      {breathing && (
        <>
          <circle className="mandala-pulse mandala-pulse-1" cx="100" cy="100" fill="none" stroke="#8AB6FF" strokeWidth="0.6" />
          <circle className="mandala-pulse mandala-pulse-2" cx="100" cy="100" fill="none" stroke="#8AB6FF" strokeWidth="0.6" />
        </>
      )}

      {/* core glow */}
      <circle cx="100" cy="100" r="28" fill="url(#mandalaCore)" />
      <circle cx="100" cy="100" r="20" fill="url(#mandalaGlow)" />

      {/* bindu */}
      <circle
        className={breathing ? "mandala-bindu" : ""}
        cx="100" cy="100" r="2.6"
        fill="#8AB6FF"
      />
    </svg>
  );
};

/* Compact mark — for nav, episode tiles, footer credit. No animation. */
const MandalaSmall = ({ size = 22, color = "#8AB6FF", dim = "#C9D7E8" }) => (
  <svg viewBox="0 0 100 100" width={size} height={size} style={{ display: 'block' }}>
    <circle cx="50" cy="50" r="44" fill="none" stroke={dim} strokeWidth="0.5" opacity="0.35" />
    {Array.from({ length: 8 }, (_, i) => i * 45).map((deg) => (
      <g key={deg} transform={`rotate(${deg} 50 50)`}>
        <path d="M 50 38 Q 40 25 50 10 Q 60 25 50 38 Z" fill="none" stroke={color} strokeWidth="0.7" opacity="0.7" />
      </g>
    ))}
    <circle cx="50" cy="50" r="20" fill="none" stroke={color} strokeWidth="0.8" />
    <circle cx="50" cy="50" r="3" fill={color} />
  </svg>
);

window.Mandala = Mandala;
window.MandalaSmall = MandalaSmall;
