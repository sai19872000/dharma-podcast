/* Shared episode data — consumed by per-episode pages via window.EPISODES.
   Source of truth for episode metadata; app.jsx also carries EP1 inline
   for the landing page (no changes needed there). */

window.EPISODES = {
  EP1: {
    id: '001',
    slug: 'vairagya',
    roman: 'Vairāgya',
    deva: 'वैराग्य',
    gloss: 'the loosening of the grip',
    duration: 402, // 6:42
    publishedAt: 'May 8, 2026',
    audioSrc: '/audio/001.mp3',
    chapters: [
      { t: 0,   label: 'Opening — what the word means' },
      { t: 74,  label: 'Gītā 2.47–71 — let the fruits go' },
      { t: 168, label: 'Yoga Sūtras 1.12–16 — abhyāsa & vairāgya' },
      { t: 245, label: 'Affective forecasting — Gilbert, Wilson' },
      { t: 332, label: 'Where they meet' },
      { t: 378, label: 'Closing breath' }
    ],
    transcript: [
      { t: 0,   role: 'a', text: 'Vairāgya. The word people translate as detachment. I want to push back on that translation before we begin — it sounds cold. The literal sense is closer to "loosened color" — rāga is the dye, the staining of the mind by what it wants. Vairāgya is not the absence of caring. It is caring that has stopped reaching.' },
      { t: 28,  role: 'b', text: 'Loosened color. Why has every popular translation reached for the cold word?' },
      { t: 42,  role: 'a', text: 'Because the alternative requires more sentences. We are going to spend six minutes on those sentences.' },
      { t: 74,  role: 'a', text: 'Start with the Gītā, second discourse. Krishna says — and I will use Arnold here, public domain, slightly modernized — "Let right deeds be thy motive, not the fruit which comes from them."', cite: 'Bhagavad Gītā 2.47', citeShort: 'BG 2.47' },
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
      { id: 'bg247',   source: 'Bhagavad Gītā 2.47',         license: 'PD · Edwin Arnold', locator: 'Discourse 2, verse 47',
        quote: 'Let right deeds be thy motive, not the fruit which comes from them.',
        url: 'https://en.wikisource.org/wiki/The_Song_Celestial', heardAt: 74 },
      { id: 'bg262',   source: 'Bhagavad Gītā 2.62–63',       license: 'PD · Edwin Arnold', locator: 'Discourse 2, verses 62–63',
        quote: 'Brooding on objects forms attachment; attachment becomes longing; longing, anger.',
        url: 'https://en.wikisource.org/wiki/The_Song_Celestial', heardAt: 124 },
      { id: 'ys112',   source: 'Patañjali Yoga Sūtras 1.12',  license: 'PD · multiple', locator: 'Samādhi Pāda 1.12',
        quote: 'abhyāsa-vairāgyābhyāṃ tan-nirodhaḥ — by practice and non-grasping, that stillness.',
        url: 'https://gretil.sub.uni-goettingen.de/gretil.html', heardAt: 168 },
      { id: 'sn-nibb', source: 'Sujato — Saṃyutta Nikāya',    license: 'CC0', locator: 'On nibbidā (disenchantment)',
        quote: 'Seeing thus, the wise disciple grows disenchanted; through disenchantment, the heart is freed.',
        url: 'https://suttacentral.net/', heardAt: 168 },
      { id: 'gilbert98', source: 'Gilbert, Wilson, et al. (1998)', license: 'Academic', locator: 'JPSP — "Immune Neglect"',
        quote: 'People overestimate the duration of their affective reactions to future events.',
        url: 'https://psycnet.apa.org/', heardAt: 245 }
    ]
  }
};
