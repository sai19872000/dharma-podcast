/* Episode player — waveform / minimal bar, two-voice transcript, chapters, citations rail. */

const { useState, useEffect, useRef, useMemo } = React;

const fmt = (s) => {
  const m = Math.floor(s / 60);
  const ss = Math.floor(s % 60).toString().padStart(2, '0');
  return `${m}:${ss}`;
};

/* Deterministic pseudo-random waveform — looks like a real audio waveform but
   stable across renders. Lower amplitude during pauses (silences between turns). */
const makeWaveform = (duration, samples = 180, chapters = []) => {
  const arr = [];
  for (let i = 0; i < samples; i++) {
    const t = (i / samples) * duration;
    // detect chapter boundary breaths (low amp window)
    const nearBoundary = chapters.some(c => Math.abs(c.t - t) < duration * 0.012);
    const seed = Math.sin(i * 12.9898) * 43758.5453;
    const r = seed - Math.floor(seed);
    let amp = 0.35 + r * 0.5;
    // Low-frequency envelope (sentences breathe)
    amp *= 0.6 + 0.4 * Math.abs(Math.sin(i / 7.3));
    if (nearBoundary) amp *= 0.25;
    arr.push(amp);
  }
  return arr;
};

const Waveform = ({ duration, current, chapters, onSeek, style = 'wave' }) => {
  const ref = useRef(null);
  const bars = useMemo(() => makeWaveform(duration, 200, chapters), [duration, chapters]);

  const handleClick = (e) => {
    const rect = ref.current.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    onSeek(Math.max(0, Math.min(duration, pct * duration)));
  };

  const progress = current / duration;

  if (style === 'minimal') {
    return (
      <div className="player-minimal-wrap">
        <div ref={ref} className="player-minimal" onClick={handleClick}>
          <div className="player-minimal-track" />
          <div className="player-minimal-fill" style={{ width: `${progress * 100}%` }} />
          {chapters.map((c, i) => (
            <button
              key={i}
              className="player-chapter-tick"
              style={{ left: `${(c.t / duration) * 100}%` }}
              onClick={(e) => { e.stopPropagation(); onSeek(c.t); }}
              title={c.label}
            />
          ))}
          <div className="player-minimal-thumb" style={{ left: `${progress * 100}%` }} />
        </div>
      </div>
    );
  }

  return (
    <div className="waveform-wrap">
      <div ref={ref} className="waveform" onClick={handleClick}>
        {bars.map((amp, i) => {
          const passed = (i / bars.length) <= progress;
          return (
            <div
              key={i}
              className={`wf-bar ${passed ? 'passed' : ''}`}
              style={{ height: `${amp * 100}%` }}
            />
          );
        })}
        {chapters.map((c, i) => (
          <button
            key={`ch-${i}`}
            className="wf-chapter"
            style={{ left: `${(c.t / duration) * 100}%` }}
            onClick={(e) => { e.stopPropagation(); onSeek(c.t); }}
            title={c.label}
          />
        ))}
        <div className="wf-playhead" style={{ left: `${progress * 100}%` }} />
      </div>
    </div>
  );
};

const Player = ({ episode, playerStyle, onCiteHover }) => {
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [speed, setSpeed] = useState(1);
  const [activeTab, setActiveTab] = useState('transcript');
  const [hoveredCite, setHoveredCite] = useState(null);
  const tickRef = useRef(null);
  const transcriptRef = useRef(null);
  const audioRef = useRef(null);           // real <audio> element
  const [simulated, setSimulated] = useState(false); // true = audio unavailable, use fake timer

  const duration = episode.duration;

  // Real audio — sync current from audio.currentTime via timeupdate.
  // Falls back to simulated mode on error (dev preview, missing file, etc.).
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onTimeUpdate = () => { if (!simulated) setCurrent(audio.currentTime); };
    const onEnded = () => setPlaying(false);
    const onError = () => setSimulated(true);
    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('error', onError);
    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('error', onError);
    };
  }, [simulated]);

  // Simulated playback timer — only runs when real audio is unavailable.
  useEffect(() => {
    if (!playing || !simulated) return;
    tickRef.current = setInterval(() => {
      setCurrent((c) => {
        const next = c + 0.1 * speed;
        if (next >= duration) {
          setPlaying(false);
          return duration;
        }
        return next;
      });
    }, 100);
    return () => clearInterval(tickRef.current);
  }, [playing, speed, duration, simulated]);

  // Auto-scroll transcript to active line
  useEffect(() => {
    if (!transcriptRef.current) return;
    const active = transcriptRef.current.querySelector('.tx-line.active');
    if (active) {
      const wrap = transcriptRef.current;
      const wt = wrap.scrollTop;
      const wh = wrap.clientHeight;
      const at = active.offsetTop;
      const ah = active.offsetHeight;
      // keep active line in middle third
      if (at < wt + wh * 0.3 || at + ah > wt + wh * 0.7) {
        wrap.scrollTo({ top: at - wh * 0.4, behavior: 'smooth' });
      }
    }
  }, [current]);

  const togglePlay = () => {
    const audio = audioRef.current;
    const next = !playing;
    if (audio && !simulated && episode.audioSrc) {
      if (next) audio.play().catch(() => setSimulated(true));
      else audio.pause();
    }
    setPlaying(next);
  };
  const seek = (t) => {
    const audio = audioRef.current;
    if (audio && !simulated && episode.audioSrc) audio.currentTime = t;
    setCurrent(t);
  };
  const cycleSpeed = () => {
    const speeds = [0.85, 1, 1.25, 1.5];
    const idx = speeds.indexOf(speed);
    const nextSpeed = speeds[(idx + 1) % speeds.length];
    const audio = audioRef.current;
    if (audio && !simulated && episode.audioSrc) audio.playbackRate = nextSpeed;
    setSpeed(nextSpeed);
  };

  const activeChapter = [...episode.chapters].reverse().find(c => current >= c.t) || episode.chapters[0];
  const activeLineIdx = episode.transcript.findIndex((l, i) => {
    const next = episode.transcript[i + 1];
    return current >= l.t && (!next || current < next.t);
  });

  return (
    <div className="player">
      <div className="player-head">
        <div className="player-head-left">
          <div className="player-stamp">◐ ep 001 · {fmt(duration)} · {episode.citations.length} citations</div>
          <h2 className="player-title">
            <span className="ep-deva">वैराग्य</span>
            <span className="ep-roman">Vairāgya</span>
            <span className="ep-gloss">— the loosening of the grip</span>
          </h2>
          <p className="player-blurb">
            <em>Two voices on dispassion.</em> The Gītā says <em>let the fruits go</em>;
            Patañjali calls it <em>abhyāsa-vairāgya</em>, two wings of one bird;
            and modern affective forecasting tells us why we keep getting the future wrong.
          </p>
        </div>

        <button className={`play-btn ${playing ? 'playing' : ''}`} onClick={togglePlay} aria-label={playing ? 'Pause' : 'Play'}>
          {playing ? (
            <svg viewBox="0 0 24 24" width="22" height="22"><rect x="6" y="5" width="4" height="14" fill="currentColor" rx="0.5" /><rect x="14" y="5" width="4" height="14" fill="currentColor" rx="0.5" /></svg>
          ) : (
            <svg viewBox="0 0 24 24" width="22" height="22"><path d="M7 4 L20 12 L7 20 Z" fill="currentColor" /></svg>
          )}
        </button>
      </div>

      {/* Chapter strip */}
      <div className="chapters">
        {episode.chapters.map((c, i) => {
          const next = episode.chapters[i + 1];
          const end = next ? next.t : duration;
          const isActive = current >= c.t && current < end;
          return (
            <button
              key={i}
              className={`chapter ${isActive ? 'active' : ''}`}
              onClick={() => seek(c.t)}
            >
              <span className="ch-num">{String(i + 1).padStart(2, '0')}</span>
              <span className="ch-label">{c.label}</span>
              <span className="ch-time">{fmt(c.t)}</span>
            </button>
          );
        })}
      </div>

      <Waveform
        duration={duration}
        current={current}
        chapters={episode.chapters}
        onSeek={seek}
        style={playerStyle}
      />

      <div className="player-controls">
        <div className="time-display">
          <span className="t-cur">{fmt(current)}</span>
          <span className="t-sep"> / </span>
          <span className="t-total">{fmt(duration)}</span>
        </div>
        <div className="now-playing">
          <span className="np-label">now</span>
          <span className="np-chapter">{activeChapter.label}</span>
        </div>
        <div className="player-actions">
          <button className="ctrl-btn" onClick={() => seek(Math.max(0, current - 15))} title="Back 15s">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /></svg>
            <span>15</span>
          </button>
          <button className="ctrl-btn speed" onClick={cycleSpeed} title="Playback speed">{speed}×</button>
          <button className="ctrl-btn" onClick={() => seek(Math.min(duration, current + 30))} title="Forward 30s">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 1 1-3-6.7" /><path d="M21 4v5h-5" /></svg>
            <span>30</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        {['transcript', 'citations', 'notes'].map((t) => (
          <button
            key={t}
            className={`tab ${activeTab === t ? 'active' : ''}`}
            onClick={() => setActiveTab(t)}
          >
            {t}
            {t === 'citations' && <span className="tab-count">{episode.citations.length}</span>}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'transcript' && (
          <div className="transcript" ref={transcriptRef}>
            {episode.transcript.map((line, i) => {
              const isActive = i === activeLineIdx;
              const cited = line.cite && (hoveredCite === line.cite);
              return (
                <button
                  key={i}
                  className={`tx-line ${line.role} ${isActive ? 'active' : ''} ${cited ? 'cited' : ''}`}
                  onClick={() => seek(line.t)}
                >
                  <span className="tx-meta">
                    <span className="tx-role">{line.role === 'a' ? 'Teacher' : 'Student'}</span>
                    <span className="tx-time">{fmt(line.t)}</span>
                  </span>
                  <span className="tx-text">
                    {line.text}
                    {line.cite && (
                      <span className="tx-cite-tag" title={line.cite}>[{line.citeShort || line.cite}]</span>
                    )}
                  </span>
                </button>
              );
            })}
          </div>
        )}

        {activeTab === 'citations' && (
          <div className="citations">
            {episode.citations.map((c, i) => (
              <div
                key={i}
                className="cite"
                onMouseEnter={() => setHoveredCite(c.id)}
                onMouseLeave={() => setHoveredCite(null)}
              >
                <div className="cite-head">
                  <span className="cite-num">{String(i + 1).padStart(2, '0')}</span>
                  <span className="cite-source">{c.source}</span>
                  <span className="cite-license">{c.license}</span>
                </div>
                <div className="cite-locator">{c.locator}</div>
                <div className="cite-quote">
                  <em>{c.quote}</em>
                </div>
                <div className="cite-foot">
                  <a href={c.url} target="_blank" rel="noopener">{c.url.replace(/^https?:\/\//, '')}</a>
                  <span className="cite-tref">→ heard at {fmt(c.heardAt)}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'notes' && episode.showNotes && (
          <div className="notes">
            <div className="notes-section">
              <div className="notes-stamp">what this episode explores</div>
              <p>{episode.showNotes.whatItExplores}</p>
            </div>
            <div className="notes-section">
              <div className="notes-stamp">primary source citations</div>
              <ul>
                {episode.showNotes.primarySources.map((s, i) => (
                  <li key={i}>
                    <a href={s.url} target="_blank" rel="noopener">{s.label}</a>
                    {' '}<span className="notes-detail">{s.detail}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="notes-section">
              <div className="notes-stamp">modern thinker context</div>
              <p>{episode.showNotes.modernThinkerContext}</p>
            </div>
            <div className="notes-section">
              <div className="notes-stamp">soul.md — anti-patterns active this episode</div>
              <ul>
                {episode.showNotes.antiPatterns.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
      {/* Real audio element — hidden; drives playback once R2 audio is live.
          Simulated waveform + transcript-sync remain intact; audio.currentTime
          drives the same `current` state. Falls back to fake timer on error. */}
      {episode.audioSrc && (
        <audio ref={audioRef} src={episode.audioSrc} preload="metadata" style={{ display: 'none' }} />
      )}
    </div>
  );
};

window.Player = Player;
