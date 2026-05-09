/* Shared episode data — consumed by per-episode pages via window.EPISODES.
   Source of truth for episode metadata; app.jsx also carries EP1 inline
   for the landing page (no changes needed there). */

/*
  Transcript timestamp heuristic (v4, 2026-05-09):
  Source: v4 script.json (22 turns — IPA reverted, sthitaprajña removed,
  post-Student gaps tightened to 350ms, closing turn intact).
  Method: char-proportional distribution over v4 actual duration.
    t[i] = round((cumulative_chars_before_turn_i / total_chars) * duration)
    total_chars = 7181 (break tags stripped)
    duration = 498s (v4 actual; v3 was 517s — 19s shorter due to gap tightening)
  Citations: BG 2.47 (t=45), BG 2.56 (t=86), YS 1.15 (t=133), AN 6.55 (t=359).
  v4 changes vs v3: sthitaprajña removed from T4; YS 1.15 citation added;
  AN 5.30 corrected to AN 6.55; transcript tracks v4 script.json directly.
*/

window.EPISODES = {
  EP1: {
    id: '001',
    slug: 'vairagya',
    roman: 'Vairāgya',
    deva: 'वैराग्य',
    gloss: 'the loosening of the grip',
    duration: 498, // v4 actual: 498s (8m18s); v3 was 517s. Shorter: post-Student gaps fixed 350ms + sthitaprajña removed
    publishedAt: 'May 8, 2026',
    audioSrc: '/audio/001.mp3',
    chapters: [
      { t: 0,   label: 'Cold open — the question worth sitting with' },
      { t: 45,  label: 'Gītā 2.47–56 — let right deeds be thy motive' },
      { t: 161, label: 'Affective forecasting — impact bias & immune neglect' },
      { t: 291, label: 'The fault line — calibration vs. niṣkāma karma' },
      { t: 359, label: 'Buddhist parallel — AN 6.55 & Soṇa' },
      { t: 483, label: 'Closing — two questions' }
    ],
    transcript: [
      // T0 — Voice A (t=0s)
      { t: 0, role: 'a', text: 'This is Dharma — two voices, one careful question per episode. Today we\'re holding a concept from the Bhagavad Gītā called vairāgya — non-attachment — next to a finding from modern psychology: that humans are remarkably bad at predicting how future events will actually make them feel.' },
      // T1 — Voice B (t=20s)
      { t: 20, role: 'b', text: 'So here\'s what I keep getting stuck on. Krishna tells Arjuna to act without clinging to the outcome. And then twenty-five centuries later, Daniel Gilbert\'s lab at Harvard shows that people systematically overestimate how good the good stuff will feel and how bad the bad stuff will hurt. Are they noticing the same glitch in us… or are they talking past each other?' },
      // T2 — Voice A (t=45s) — cited: Bhagavad Gita 2.47
      { t: 45, role: 'a', text: 'That\'s the right question, and the answer is both. Let\'s let Krishna speak first. In the Gītā, chapter two, Edwin Arnold\'s translation — Krishna says to Arjuna: "Let right deeds be thy motive, not the fruit which comes from them. And live in action! Labour! Make thine acts thy piety, casting all self aside, contemning gain and merit; equable in good or evil: equability is Yog, is piety!"', cite: 'Bhagavad Gita 2.47–2.48 (Arnold)', citeShort: 'BG 2.47' },
      // T3 — Voice B (t=72s)
      { t: 72, role: 'b', text: '"Casting all self aside." That\'s a stronger claim than just… don\'t get too excited about your promotion. He\'s saying the problem isn\'t the outcome — it\'s the self that\'s wrapped around the outcome.' },
      // T4 — Voice A (t=86s) — cited: Bhagavad Gita 2.56
      { t: 86, role: 'a', text: 'Exactly. And the Gītā builds on this. Arjuna asks what a person who\'s actually achieved this looks like — someone with steady insight, what the text calls the one of steady wisdom. Krishna\'s answer is vivid. He says such a person is "in sorrows not dejected, and in joys not overjoyed; dwelling outside the stress of passion, fear, and anger; fixed in calms of lofty contemplation." And then this image: like the ocean, day by day receiving floods from all lands, which never overflows.', cite: 'Bhagavad Gita 2.56–2.57 (Arnold)', citeShort: 'BG 2.56' },
      // T5 — Voice B (t=120s)
      { t: 120, role: 'b', text: 'That ocean image is striking — everything pours in, but the water level doesn\'t change. It\'s not that the person stops experiencing things. It\'s that the experiencing doesn\'t destabilize them.' },
      // T6 — Voice A (t=133s) — cited: Yoga Sūtras 1.15
      { t: 133, role: 'a', text: 'Right. And Patañjali sharpens the mechanism. In the Yoga Sūtras, sūtra 1.15, Vivekananda translates it this way: "That effect which comes to those who have given up their thirst after objects, either seen or heard, and which wills to control the objects, is non-attachment." So the target isn\'t the object — it\'s the thirst. The pull toward the anticipated pleasure of having or avoiding something.', cite: 'Yoga Sūtras 1.15 (Vivekananda)', citeShort: 'YS 1.15' },
      // T7 — Voice B (t=161s)
      { t: 161, role: 'b', text: 'And that\'s where Gilbert enters, isn\'t it? Because his research is precisely about what that thirst is aimed at — the mental image of how the future will feel.' },
      // T8 — Voice A (t=172s)
      { t: 172, role: 'a', text: 'It is. Gilbert and his colleague Timothy Wilson have spent decades studying what they call affective forecasting — how people predict their future emotional states. And the core finding is consistent: we\'re wrong. Not randomly wrong. Systematically wrong in one direction. We overestimate the intensity and the duration of how events will affect us. They call it the impact bias.' },
      // T9 — Voice B (t=198s)
      { t: 198, role: 'b', text: 'So I imagine the promotion will make me happy for months, but actually I adapt in weeks. And I imagine the rejection will crush me, but my mind… reframes it faster than I expected.' },
      // T10 — Voice A (t=210s)
      { t: 210, role: 'a', text: 'That\'s it. Gilbert describes what he calls a psychological immune system — the mind\'s capacity to rationalize, reframe, find meaning. People are surprisingly resilient, but they don\'t predict their own resilience. They call that immune neglect. And there\'s a second mechanism — focalism. When you imagine a future event, you zoom in on that event alone and forget everything else that will still be true about your life when it arrives. The promotion looms large in imagination because you\'re not picturing the unchanged commute, the same Tuesday meetings.' },
      // T11 — Voice B (t=249s)
      { t: 249, role: 'b', text: 'Okay, so both traditions are pointing at the same structural problem — we build an emotional picture of the fruit of action, and that picture is distorted. But they\'re diagnosing it differently, aren\'t they?' },
      // T12 — Voice A (t=263s)
      { t: 263, role: 'a', text: 'Very differently. And this is where it matters. Gilbert and Wilson diagnose a cognitive bias. The recommendation is calibrational — know that you overestimate, adjust your predictions, make better decisions. It\'s an epistemic correction. You\'re still the same self aiming at outcomes; you just get more accurate about how those outcomes will land.' },
      // T13 — Voice B (t=287s)
      { t: 287, role: 'b', text: 'And the Gītā\'s diagnosis goes… deeper than that.' },
      // T14 — Voice A (t=291s) — niṣkāma karma introduced (first and only use)
      { t: 291, role: 'a', text: 'It goes to a different place entirely. The Gītā doesn\'t say the prediction is off — it says the whole orientation of grasping at the fruit is what generates suffering. The concept Krishna teaches is niṣkāma karma — action without grasping at outcome. Not better forecasting but a fundamentally different relationship between the one who acts and the act itself. Gilbert says: your mental model of the future is unreliable, so trust it less. Krishna says: the self that builds that model, the self that wraps itself around the imagined fruit — that self-structure is the problem. Release the grip, not just the prediction.' },
      // T15 — Voice B (t=334s)
      { t: 334, role: 'b', text: 'So the convergence is real — both see that anticipated payoff doesn\'t deliver what it promises. But the Gītā thinks the fix is in who you are when you act, and Gilbert thinks the fix is in how accurately you predict. One is about recalibrating the instrument. The other is about… recognizing that the instrument and the one holding it aren\'t two separate things.' },
      // T16 — Voice A (t=359s) — cited: Aṅguttara Nikāya 6.55
      { t: 359, role: 'a', text: 'That\'s well put. And there\'s a Buddhist angle that sharpens the contrast even further. In the Anguttara Nikāya, sutta 6.55, the Buddha visits a monk named Soṇa who is striving so hard he\'s about to quit. The Buddha asks him about his old life as a harp player. When the strings were too tight — resonant? No. Too slack? No. Only when the tension was even. And then the sutta describes what a person who\'s completed that path looks like: "Their mind is quite untainted. It is steady, imperturbable, observing disappearance." The image at the end is a mountain of solid rock — storms blow from every direction and it doesn\'t shake.', cite: 'Aṅguttara Nikāya 6.55 (Sujato)', citeShort: 'AN 6.55' },
      // T17 — Voice B (t=403s)
      { t: 403, role: 'b', text: 'That\'s almost identical to the Gītā\'s ocean image — everything arrives, nothing destabilizes. But neither tradition is saying don\'t feel anything. They\'re describing someone who feels fully but isn\'t… owned by what they feel.' },
      // T18 — Voice A (t=418s)
      { t: 418, role: 'a', text: 'And that\'s exactly what Gilbert\'s model can\'t reach. His framework stays inside the self-as-predictor — it improves the predictions. The contemplative traditions are asking whether you can stand somewhere that doesn\'t need the prediction at all. Not indifference. The Gītā is emphatic — you still act, you act fully, you act with care. But the imagined payoff isn\'t what\'s driving the action anymore.' },
      // T19 — Voice B (t=446s)
      { t: 446, role: 'b', text: 'So the next time I notice myself rehearsing how something will feel when I get it… what\'s the question to hold?' },
      // T20 — Voice A (t=454s)
      { t: 454, role: 'a', text: 'The question isn\'t whether your forecast is accurate. Gilbert already showed you it\'s not. The question is: who is the one building the forecast, and does that one need the fruit in order to act? The Gītā and the lab agree that the anticipated payoff is unreliable. They part ways on what to do about it — recalibrate the model, or release the grip that made you build it. That gap between them is where the real work starts.' },
      // T21 — Voice A closing (v4, 2026-05-09 — 498s / 8m18s)
      { t: 483, role: 'a', text: 'Thank you for sitting with this one today. Next time, we take up the self that isn\'t a thing — what the early Buddhist suttas call the not-self teaching, and what Thomas Metzinger calls the ego tunnel. Until then.' }
    ],
    citations: [
      {
        id: 'cite01',
        source: 'Bhagavad Gita 2.47',
        license: 'PD · Edwin Arnold',
        locator: '2.47–2.48',
        quote: 'Let right deeds be thy motive, not the fruit which comes from them. And live in action! Labour! Make thine acts thy piety, casting all self aside, contemning gain and merit; equable in good or evil: equability is Yog, is piety!',
        url: 'https://www.sacred-texts.com/hin/gita/bg02.htm',
        heardAt: 45
      },
      {
        id: 'cite02',
        source: 'Bhagavad Gita 2.56',
        license: 'PD · Edwin Arnold',
        locator: '2.56–2.57',
        quote: 'In sorrows not dejected, and in joys not overjoyed; dwelling outside the stress of passion, fear, and anger; fixed in calms of lofty contemplation.',
        url: 'https://www.sacred-texts.com/hin/gita/bg02.htm',
        heardAt: 86
      },
      {
        id: 'cite03',
        source: 'Yoga Sūtras 1.15',
        license: 'PD · Swami Vivekananda',
        locator: '1.15',
        quote: 'That effect which comes to those who have given up their thirst after objects, either seen or heard, and which wills to control the objects, is non-attachment.',
        url: 'https://www.sacred-texts.com/hin/yogasutr.htm',
        heardAt: 133
      },
      {
        id: 'cite04',
        source: 'Aṅguttara Nikāya 6.55 — With Soṇa',
        license: 'CC0 · Bhante Sujato',
        locator: 'AN 6.55',
        quote: 'Their mind is quite untainted. It is steady, imperturbable, observing disappearance.',
        url: 'https://suttacentral.net/an6.55/en/sujato',
        heardAt: 359
      }
    ],
    showNotes: {
      whatItExplores: 'The concept of vairāgya — dispassion or non-attachment — from the Yoga Sūtras and the Bhagavad Gītā, paired with contemporary research on affective forecasting from behavioural science (Gilbert & Wilson).',
      primarySources: [
        { label: 'Bhagavad Gita 2.47', detail: 'Edwin Arnold · License: PD', url: 'https://www.sacred-texts.com/hin/gita/bg02.htm' },
        { label: 'Bhagavad Gita 2.56', detail: 'Edwin Arnold · License: PD', url: 'https://www.sacred-texts.com/hin/gita/bg02.htm' },
        { label: 'Yoga Sūtras 1.15', detail: 'Swami Vivekananda · License: PD', url: 'https://www.sacred-texts.com/hin/yogasutr.htm' },
        { label: 'Aṅguttara Nikāya 6.55 — With Soṇa', detail: 'Bhante Sujato · License: CC0', url: 'https://suttacentral.net/an6.55/en/sujato' }
      ],
      modernThinkerContext: 'Daniel Gilbert & Timothy Wilson on Affective Forecasting. Public lectures and peer-reviewed papers. Core finding: humans systematically overestimate the emotional impact of future events (impact bias) and underestimate their own psychological immune system\'s capacity to adapt (immune neglect). Vairāgya and niṣkāma karma address this asymmetry from the inside — not by correcting the forecast, but by releasing the grip on outcome.',
      antiPatterns: [
        'No quantum-consciousness analogies',
        'No syncretic flattening (Patañjali ≠ Kastrup; vairāgya ≠ detachment-as-coldness)',
        '\'Consciousness\' used only with named referent (vṛtti, puruṣa, or phenomenal self-model)'
      ]
    }
  }
};
