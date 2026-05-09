/* samvāda — dharma podcast landing page
   Aura design system + custom mandala mark.
   Tweakable: devanagari motif, player style, layout density. */

const { useState, useEffect } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "devanagari": true,
  "playerStyle": "wave",
  "density": "comfortable",
  "showName": "samvāda"
}/*EDITMODE-END*/;

/* ── Episode 001 data ─────────────────────────────────────────── */
const EP1 = {
  id: '001',
  slug: 'vairagya',
  roman: 'Vairāgya',
  deva: 'वैराग्य',
  gloss: 'the loosening of the grip',
  duration: 402, // 6:42
  audioSrc: 'https://dharma-podcast-audio.r2.dev/audio/001.mp3',
  publishedAt: 'May 8, 2026',
  chapters: [
    { t: 0,   label: 'Opening — what the word means' },
    { t: 74,  label: 'Gītā 2.47–71 — let the fruits go' },
    { t: 168, label: 'Yoga Sūtras 1.12–16 — abhyāsa & vairāgya' },
    { t: 245, label: 'Affective forecasting — Gilbert, Wilson' },
    { t: 332, label: 'Where they meet' },
    { t: 378, label: 'Closing breath' }
  ],
  transcript: [
    { t: 0, role: 'a', text: 'Vairāgya. The word people translate as detachment. I want to push back on that translation before we begin — it sounds cold. The literal sense is closer to "loosened color" — rāga is the dye, the staining of the mind by what it wants. Vairāgya is not the absence of caring. It is caring that has stopped reaching.' },
    { t: 28, role: 'b', text: 'Loosened color. Why has every popular translation reached for the cold word?' },
    { t: 42, role: 'a', text: 'Because the alternative requires more sentences. We are going to spend six minutes on those sentences.' },
    { t: 74, role: 'a', text: 'Start with the Gītā, second discourse. Krishna says — and I will use Arnold here, public domain, slightly modernized — "Let right deeds be thy motive, not the fruit which comes from them."', cite: 'Bhagavad Gītā 2.47', citeShort: 'BG 2.47' },
    { t: 108, role: 'b', text: 'So the instruction is: act, but do not lean forward into the result.' },
    { t: 124, role: 'a', text: 'Yes. And five verses later he names the trap directly: the mind that broods on objects forms attachment to them; from attachment comes longing; from longing, anger; from anger, confusion. A causal chain, ending in a forgotten self.', cite: 'Bhagavad Gītā 2.62–63', citeShort: 'BG 2.62–63' },
    { t: 168, role: 'a', text: 'Patañjali, three centuries later, sharpens this. In Yoga Sūtras 1.12 he says the stilling of the mind happens by two means — abhyāsa, repeated practice, and vairāgya. He pairs them. Discipline alone is brittle; non-grasping alone is passive. Together they hold.', cite: 'Yoga Sūtras 1.12', citeShort: 'YS 1.12' },
    { t: 210, role: 'b', text: 'So vairāgya is not the practice. It is what makes the practice not a striving.' },
    { t: 245, role: 'a', text: 'Now turn to a different room — Cambridge, late 1990s. Dan Gilbert and Tim Wilson coin the phrase affective forecasting. The finding: humans are systematically wrong about how much future events will affect them. We overestimate the joy of getting the thing, the grief of losing it, and how long either lasts.', cite: 'Gilbert & Wilson, 1998', citeShort: 'Gilbert 1998' },
    { t: 290, role: 'b', text: 'They call this the impact bias.' },
    { t: 302, role: 'a', text: 'Yes. And the data is stable across decades. Lottery winners and paraplegics return to baseline happiness within a year. The mind, left alone, will tell you a story about the future that is more vivid than the future will be.' },
    { t: 332, role: 'a', text: 'Place these together. The Gītā says: do not lean on the fruit. Patañjali says: practice and non-grasping are one motion. Gilbert and Wilson say: the mind is a poor forecaster of its own future feeling. Three traditions, two and a half millennia apart, looking at the same shape — the gap between wanting and the wanting being satisfied.' },
    { t: 378, role: 'b', text: 'Vairāgya is not renunciation. It is calibration.' },
    { t: 392, role: 'a', text: 'It is calibration. Read the Gītā passages this week. Notice the verbs.' }
  ],
  citations: [
    { id: 'bg247', source: 'Bhagavad Gītā 2.47', license: 'PD · Edwin Arnold', locator: 'Discourse 2, verse 47',
      quote: 'Let right deeds be thy motive, not the fruit which comes from them.',
      url: 'https://en.wikisource.org/wiki/The_Song_Celestial', heardAt: 74 },
    { id: 'bg262', source: 'Bhagavad Gītā 2.62–63', license: 'PD · Edwin Arnold', locator: 'Discourse 2, verses 62–63',
      quote: 'Brooding on objects forms attachment; attachment becomes longing; longing, anger.',
      url: 'https://en.wikisource.org/wiki/The_Song_Celestial', heardAt: 124 },
    { id: 'ys112', source: 'Patañjali Yoga Sūtras 1.12', license: 'PD · multiple', locator: 'Sādhanā Pāda — wait, Samādhi Pāda 1.12',
      quote: 'abhyāsa-vairāgyābhyāṃ tan-nirodhaḥ — by practice and non-grasping, that stillness.',
      url: 'https://gretil.sub.uni-goettingen.de/gretil.html', heardAt: 168 },
    { id: 'sn-nibb', source: 'Sujato — Saṃyutta Nikāya', license: 'CC0', locator: 'On nibbidā (disenchantment)',
      quote: 'Seeing thus, the wise disciple grows disenchanted; through disenchantment, the heart is freed.',
      url: 'https://suttacentral.net/', heardAt: 168 },
    { id: 'gilbert98', source: 'Gilbert, Wilson, et al. (1998)', license: 'Academic', locator: 'JPSP — "Immune Neglect"',
      quote: 'People overestimate the duration of their affective reactions to future events.',
      url: 'https://psycnet.apa.org/', heardAt: 245 }
  ]
};

/* Concept queue (upcoming + ep001) */
const QUEUE = [
  { num: '001', roman: 'vairāgya',  deva: 'वैराग्य',   gloss: 'the loosening of the grip',   pair: 'affective forecasting · Gilbert / Wilson', status: 'in review', date: 'May 8' },
  { num: '002', roman: 'anattā',    deva: 'अनात्मन्',  gloss: 'no fixed self',                pair: 'predictive self-models · Metzinger',         status: 'queued',     date: '—' },
  { num: '003', roman: 'sākṣī',     deva: 'साक्षिन्',  gloss: 'the witness',                  pair: 'analytic idealism · Kastrup',                status: 'queued',     date: '—' },
  { num: '004', roman: 'dhyāna',    deva: 'ध्यान',     gloss: 'absorption',                   pair: 'attention training · Wallace',                status: 'queued',     date: '—' },
  { num: '005', roman: 'turīya',    deva: 'तुरीय',     gloss: 'the fourth state',             pair: 'states of consciousness · Seth',              status: 'queued',     date: '—' },
  { num: '006', roman: 'nibbidā',   deva: 'निब्बिदा',  gloss: 'disenchantment',               pair: 'hedonic adaptation · Brickman',               status: 'queued',     date: '—' },
  { num: '007', roman: 'ātman',     deva: 'आत्मन्',    gloss: 'the self that knows',          pair: 'conscious agents · Hoffman',                  status: 'queued',     date: '—' },
  { num: '008', roman: 'karma',     deva: 'कर्म',      gloss: 'action and consequence',       pair: 'agency & determinism · Sapolsky',             status: 'concept',    date: '—' },
  { num: '009', roman: 'dharma',    deva: 'धर्म',      gloss: 'the order one is fitted to',   pair: 'role morality · MacIntyre',                   status: 'concept',    date: '—' }
];

/* ── Page ─────────────────────────────────────────────────────── */
const App = () => {
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [tweaksOpen, setTweaksOpen] = useState(false);

  // density class on root
  useEffect(() => {
    document.documentElement.dataset.density = tweaks.density;
    document.documentElement.dataset.devanagari = tweaks.devanagari ? 'on' : 'off';
  }, [tweaks.density, tweaks.devanagari]);

  return (
    <>
      <TweaksPanel open={tweaksOpen} setOpen={setTweaksOpen} title="Tweaks">
        <TweakSection title="Show name">
          <TweakText label="name" value={tweaks.showName} onChange={(v) => setTweak('showName', v)} />
        </TweakSection>
        <TweakSection title="Visual">
          <TweakToggle label="Devanagari motif" value={tweaks.devanagari} onChange={(v) => setTweak('devanagari', v)} />
          <TweakRadio
            label="Player style"
            value={tweaks.playerStyle}
            options={[{ value: 'wave', label: 'Waveform' }, { value: 'minimal', label: 'Minimal bar' }]}
            onChange={(v) => setTweak('playerStyle', v)}
          />
          <TweakRadio
            label="Layout density"
            value={tweaks.density}
            options={[{ value: 'compact', label: 'Compact' }, { value: 'comfortable', label: 'Comfortable' }, { value: 'spacious', label: 'Spacious' }]}
            onChange={(v) => setTweak('density', v)}
          />
        </TweakSection>
      </TweaksPanel>

      <div className="stars" />
      <div className="page-glow" />

      <Nav showName={tweaks.showName} />
      <Hero showName={tweaks.showName} />
      <FeaturedEpisode playerStyle={tweaks.playerStyle} />
      <ConceptQueue devanagari={tweaks.devanagari} />
      <Subscribe />
      <Footer />
    </>
  );
};

const Nav = ({ showName }) => (
  <nav className="nav">
    <a className="wm" href="#">
      <MandalaSmall size={24} />
      <span className="wm-text">
        <span className="wm-show">{showName}</span>
        <span className="wm-host"> · dharma<span className="wm-dot">.</span>saiteja.ai</span>
      </span>
    </a>
    <div className="nav-links">
      <a href="#episodes">Episodes</a>
      <a href="#about">About</a>
      <a href="#queue">Queue</a>
      <a href="/feed.xml">RSS</a>
    </div>
    <div className="nav-status">
      <span className="status-dot" />
      <span>Ep 001 · in review</span>
    </div>
  </nav>
);

const Hero = ({ showName }) => (
  <section className="hero">
    <div className="hero-text">
      <div className="stamp">◐ a podcast from saiteja.ai · weekly · 5–8 min</div>
      <h1 className="hero-title">
        <span className="show-name">{showName}</span>
        <span className="show-deva" data-deva-only>संवाद</span>
      </h1>
      <p className="hero-tag">
        Two voices in one room — eastern source <em>×</em> modern science.
      </p>
      <p className="hero-lede">
        A weekly dialogue drawing from the Gītā, the Upaniṣads,
        the Pali canon, and the cognitive sciences. Both voices are
        AI-generated. The reading is careful. The citations are real.
      </p>
      <div className="hero-cta">
        <a className="btn btn-primary" href="#ep001">
          <svg viewBox="0 0 24 24" width="14" height="14"><path d="M7 4 L20 12 L7 20 Z" fill="currentColor" /></svg>
          Play Episode 001
        </a>
        <a className="btn btn-ghost" href="#queue">See the queue →</a>
      </div>
    </div>
    <div className="hero-mark">
      <Mandala size={460} />
    </div>
  </section>
);

const FeaturedEpisode = ({ playerStyle }) => (
  <section id="ep001" className="featured">
    <div className="section-stamp">◐ episode 001 · published {EP1.publishedAt}</div>
    <Player episode={EP1} playerStyle={playerStyle} />
  </section>
);

const ConceptQueue = ({ devanagari }) => (
  <section id="queue" className="queue-section">
    <div className="queue-head">
      <div>
        <div className="section-stamp">◐ concept queue</div>
        <h2 className="queue-title">
          Nine words.<br /><em>One a week, until they are all read.</em>
        </h2>
      </div>
      <div className="queue-meta">
        <div className="qm-row"><span className="qm-k">total</span><span className="qm-v">9 concepts</span></div>
        <div className="qm-row"><span className="qm-k">published</span><span className="qm-v">0</span></div>
        <div className="qm-row"><span className="qm-k">in review</span><span className="qm-v">1</span></div>
        <div className="qm-row"><span className="qm-k">cadence</span><span className="qm-v">weekly · sat</span></div>
      </div>
    </div>

    <div className="queue-list">
      {QUEUE.map((q) => (
        <article key={q.num} className={`queue-card status-${q.status.replace(/\s/g, '-')}`}>
          {devanagari && <span className="qc-deva-bg">{q.deva}</span>}
          <div className="qc-num">EP {q.num}</div>
          <div className="qc-body">
            <div className="qc-title-row">
              <span className="qc-roman">{q.roman}</span>
              <span className="qc-deva-inline">{q.deva}</span>
            </div>
            <div className="qc-gloss">{q.gloss}</div>
            <div className="qc-pair">
              <span className="qc-pair-label">paired with</span>
              <span className="qc-pair-text">{q.pair}</span>
            </div>
          </div>
          <div className="qc-status">
            <span className={`qc-status-dot ${q.status.replace(/\s/g, '-')}`} />
            <span className="qc-status-text">{q.status}</span>
            <span className="qc-date">{q.date}</span>
          </div>
        </article>
      ))}
    </div>
  </section>
);

const Subscribe = () => (
  <section id="about" className="subscribe">
    <div className="sub-inner">
      <div className="section-stamp">◐ about</div>
      <h2 className="sub-title">
        A reading practice,<br /><em>kept on a feed.</em>
      </h2>
      <p className="sub-lede">
        Both voices are generated by ElevenLabs. Scripts are drafted
        by a research agent reading from license-clean primary sources —
        Sujato's Pali (CC0), Edwin Arnold's Gītā (PD), Max Müller's
        Upaniṣads (PD) — and reviewed sentence by sentence before
        publish. Every quote carries its source and its license.
      </p>
      <div className="sub-feeds">
        <a className="feed-btn" href="/feed.xml">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"><path d="M4 11a9 9 0 0 1 9 9" /><path d="M4 4a16 16 0 0 1 16 16" /><circle cx="5" cy="19" r="1.5" fill="currentColor" /></svg>
          <span className="feed-name">RSS</span>
          <span className="feed-host">dharma.saiteja.ai/feed.xml</span>
        </a>
        <a className="feed-btn" href="#">
          <span className="feed-glyph">♫</span>
          <span className="feed-name">Spotify</span>
          <span className="feed-host">add via the RSS link</span>
        </a>
        <a className="feed-btn" href="#">
          <span className="feed-glyph">◍</span>
          <span className="feed-name">Apple Podcasts</span>
          <span className="feed-host">add via the RSS link</span>
        </a>
      </div>
    </div>
  </section>
);

const Footer = () => (
  <footer className="footer">
    <div className="footer-credit">
      <MandalaSmall size={14} />
      <span>quietly forged at saiteja.ai</span>
    </div>
    <div className="footer-meta">
      <span>© 2026 · dharma podcast</span>
      <span className="dot-sep">·</span>
      <span>license-clean corpus only</span>
      <span className="dot-sep">·</span>
      <a href="mailto:hello@saiteja.ai">hello@saiteja.ai</a>
    </div>
  </footer>
);

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
