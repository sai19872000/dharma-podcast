/* Shared episode data — consumed by per-episode pages via window.EPISODES.
   Source of truth for episode metadata; app.jsx also carries EP1 inline
   for the landing page (no changes needed there). */

/*
  Transcript timestamp heuristic (v3, 2026-05-09):
  Total duration = 517s (8m37s, v3 audio).
  v3 changes: closing turn added (Voice A), IPA phoneme substitution,
  Voice B pause beats, realism levers (stability 0.40, style 0.35,
  per-turn speed jitter), jittered inter-turn gaps.
  Timestamps carried forward from v2 distribution; closing turn appended
  at t=510 (3 turns from end in v3 script).
*/

window.EPISODES = {
  EP1: {
    id: '001',
    slug: 'vairagya',
    roman: 'Vairāgya',
    deva: 'वैराग्य',
    gloss: 'the loosening of the grip',
    duration: 517, // 8:37 — v3 audio (closing turn + IPA + realism levers; ffprobe 517.25s)
    publishedAt: 'May 8, 2026',
    audioSrc: '/audio/001.mp3',
    chapters: [
      { t: 0,   label: 'Cold open — the question worth sitting with' },
      { t: 66,  label: 'Gītā 2.47–56 — let right deeds be thy motive' },
      { t: 161, label: 'Affective forecasting — impact bias & immune neglect' },
      { t: 295, label: 'The fault line — calibration vs. niṣkāma karma' },
      { t: 405, label: 'Buddhist parallel — AN 5.30 & Soṇa' },
      { t: 499, label: 'Closing — two questions' }
    ],
    transcript: [
      // T0 — Voice A (0 chars before = t 0)
      { t: 0,   role: 'a', text: 'This is Dharma — two voices, one careful question per episode. Today: the Bhagavad Gītā\'s teaching on non-attachment to the fruit of action, held against the modern psychology of how badly we mispredict what the fruit will actually feel like.' },
      // T1 — Voice B (243 chars before = t 17)
      { t: 17,  role: 'b', text: 'So here\'s the thing that caught me. Krishna tells Arjuna to act without grasping at the outcome. And then twenty-five centuries later, Dan Gilbert\'s lab at Harvard finds that people are systematically wrong about how outcomes will make them feel. Are they noticing the same problem… or just rhyming?' },
      // T2 — Voice A (543 chars before = t 37)
      { t: 37,  role: 'a', text: 'That\'s the question worth sitting with. Let\'s start with the Gītā\'s side. The concept is vairāgya — non-attachment, sometimes translated as dispassion, though dispassion makes it sound cold and it isn\'t. Krishna\'s argument in Chapter Two is surprisingly specific. He doesn\'t say stop acting. He says stop letting the imagined reward be the reason you act.' },
      // T3 — Voice B (900 chars before = t 61)
      { t: 61,  role: 'b', text: 'Can you read the passage? I want to hear exactly how Arnold renders it.' },
      // T4 — Voice A (971 chars before = t 66) — cited: Bhagavad Gita 2.47
      { t: 66,  role: 'a', text: 'This is Edwin Arnold\'s 1885 translation, from roughly verse 2.47 onward. Krishna says: "But thou, want not! ask not! Find full reward of doing right in right! Let right deeds be thy motive, not the fruit which comes from them. And live in action! Labour! Make thine acts thy piety, casting all self aside, contemning gain and merit; equable in good or evil: equability is Yog, is piety!" Notice what he\'s not saying. He\'s not saying outcomes don\'t matter. He\'s saying the attachment to outcomes — the way we grip the imagined fruit before we\'ve even acted — that\'s what distorts both the action and the actor.', cite: 'Bhagavad Gita 2.47', citeShort: 'BG 2.47' },
      // T5 — Voice B (1585 chars before = t 108)
      { t: 108, role: 'b', text: 'And then Arjuna pushes back. He asks what that person actually looks like — the one who\'s managed this. He calls it the one of steady insight, the sthitaprajña — the one of steady insight. How does that person sit, move, speak?' },
      // T6 — Voice A (1815 chars before = t 123) — cited: Bhagavad Gita 2.56
      { t: 123, role: 'a', text: 'Right, and Krishna\'s description is remarkable. Arnold renders it: "In sorrows not dejected, and in joys not overjoyed; dwelling outside the stress of passion, fear, and anger; fixed in calms of lofty contemplation — such an one is Muni, is the Sage, the true Recluse!" That\'s not numbness. The person still encounters sorrow and joy. They\'re just not thrown by either one. And then the ocean image at the end of Chapter Two — the person of steady insight is like the ocean receiving rivers without overflowing. Floods come in. The boundary holds.', cite: 'Bhagavad Gita 2.56', citeShort: 'BG 2.56' },
      // T7 — Voice B (2371 chars before = t 161)
      { t: 161, role: 'b', text: 'Okay, so that\'s the Gītā\'s picture. Now, Gilbert and Wilson — they\'re working a completely different problem, right? They\'re not asking how to relate to outcomes. They\'re asking why our predictions about outcomes are so consistently wrong.' },
      // T8 — Voice A (2610 chars before = t 177)
      { t: 177, role: 'a', text: 'Exactly. Starting in the late nineties, they documented what they call impact bias — the systematic tendency to overestimate how intensely and how long a future event will affect your wellbeing. You get the promotion, and it matters less than you thought. You lose the relationship, and you recover faster than you predicted. The direction of the prediction is usually right — good things feel good, bad things feel bad — but the magnitude and duration are inflated.' },
      // T9 — Voice B (3075 chars before = t 209)
      { t: 209, role: 'b', text: 'And they found specific mechanisms behind this?' },
      // T10 — Voice A (3123 chars before = t 212)
      { t: 212, role: 'a', text: 'Three main ones. First, focalism — when you imagine a future event, you zoom in on it and forget that the rest of your life will still be happening around it. Second, what they call immune neglect — you have a psychological immune system that rationalizes, reframes, finds meaning in bad outcomes, but you consistently forget it exists when you\'re predicting. And third, the durability bias — adaptation happens faster than you expect. Gilbert\'s TED talk puts it simply: people can synthesize happiness from almost any outcome, yet they routinely believe they can\'t.' },
      // T11 — Voice B (3688 chars before = t 250)
      { t: 250, role: 'b', text: 'So both the Gītā and the lab are saying… the fruit isn\'t what you think it is. The payoff you\'re gripping doesn\'t arrive the way you imagined.' },
      // T12 — Voice A (3832 chars before = t 260)
      { t: 260, role: 'a', text: 'That\'s the convergence, and it\'s genuine. Both traditions observe that the anticipated emotional payoff of attainment is not what gets delivered. The Gītā watches Arjuna agonize over outcomes that haven\'t happened yet, and Krishna says the agonizing itself is the problem. Gilbert watches experimental subjects overestimate the impact of outcomes that have happened, and he says the prediction mechanism is the problem. Same phenomenon — the mind inflates the fruit — noticed from two completely different angles.' },
      // T13 — Voice B (4343 chars before = t 295)
      { t: 295, role: 'b', text: 'But the prescriptions diverge. Gilbert says correct your prediction. Krishna says… something deeper than that.' },
      // T14 — Voice A (4454 chars before = t 302) — cited: AN 5.30 (via turn_idx in JSONL)
      { t: 302, role: 'a', text: 'That\'s exactly the fault line. Gilbert\'s recommendation is calibrational — know your bias, adjust your forecast, expect that the promotion will matter less than you think. It\'s an epistemic fix. The Gītā\'s move is different in kind. It\'s not saying predict better. It\'s saying the whole stance of acting-for-the-sake-of-the-outcome is where suffering takes root. The concept Krishna introduces is niṣkāma karma — action without grasping at outcome. That\'s not improved forecasting. That\'s a different relationship to action itself. You act because the action is right, not because you\'ve calculated what the fruit will feel like.', cite: 'Anguttara Nikāya 5.30 — With Nāgita', citeShort: 'AN 5.30' },
      // T15 — Voice B (5086 chars before = t 345)
      { t: 345, role: 'b', text: 'So one is adjusting the lens and the other is… questioning why you\'re looking through a lens at all.' },
      // T16 — Voice A (5187 chars before = t 352)
      { t: 352, role: 'a', text: 'Yes. And there\'s a structural reason for that difference. Gilbert is doing empirical psychology. His question is descriptive: how does this cognitive mechanism work, and where does it go wrong? The Gītā is embedded in a whole account of the self-as-doer. Krishna\'s diagnosis is that the problem isn\'t just a miscalibrated prediction — it\'s the identification with being the one who reaps the fruit. Patañjali makes the same point in the Yoga Sūtras: non-attachment isn\'t a technique for feeling better. It\'s what happens when you stop mistaking mental activity for your identity.' },
      // T17 — Voice B (5765 chars before = t 391)
      { t: 391, role: 'b', text: 'There\'s a Buddhist parallel too, isn\'t there? The Buddha in AN 5.30 draws a sharp line between… I think he calls it the pleasure of renunciation and the filthy pleasure of possessions and popularity.' },
      // T18 — Voice A (5966 chars before = t 405)
      { t: 405, role: 'a', text: 'He does. He\'s sitting in a forest near Icchānaṅgala and a crowd arrives with food and fanfare, and the Buddha says to his attendant Nāgita: "May I never become famous. May fame not come to me. There are those who can\'t get the pleasure of renunciation, the pleasure of seclusion, the pleasure of peace, the pleasure of awakening when they want, without trouble or difficulty like I can. Let them enjoy the filthy, lazy pleasure of possessions, honor, and popularity." And then he runs through a sequence: what you eat ends as excrement, loved ones perish and grief follows, impermanence is visible everywhere. He\'s not moralizing. He\'s describing what the outcome actually is when you trace it to completion.' },
      // T19 — Voice B (6676 chars before = t 453)
      { t: 453, role: 'b', text: 'Which is almost what Gilbert is doing with data — tracing the outcome to completion and showing it doesn\'t match the forecast.' },
      // T20 — Voice A (6802 chars before = t 461)
      { t: 461, role: 'a', text: 'Almost. But the Buddha\'s version ends somewhere Gilbert\'s doesn\'t. The Buddha\'s sequence leads to a trained seeing-through — not a corrected prediction but a release of the grip itself. And Soṇa\'s story in AN 6.55 shows what that looks like in practice: the lute strings tuned neither too tight nor too slack, effort and serenity in balance. And when Soṇa reaches that balance, he describes himself as steady, imperturbable — like a solid rock that the wind cannot stir. That\'s the same image as the Gītā\'s ocean. Not numb. Not indifferent. Just… not thrown.' },
      // T21 — Voice B (7363 chars before = t 499)
      { t: 499, role: 'b', text: 'So what\'s the takeaway? If I\'m listening and I find both of these compelling — the lab data and the Gītā — where does that leave me?' },
      // T22 — Voice A (7497 chars before = t 509)
      { t: 509, role: 'a', text: 'Here. Next time you notice yourself rehearsing how good something will feel when you get it — or how bad it\'ll feel if you don\'t — you\'ve got two different questions available. Gilbert\'s question is: am I overestimating this? And that\'s a useful question. But the Gītā\'s question goes one step further: why am I gripping the forecast at all? The first question corrects the lens. The second asks whether the act of forecasting your happiness is itself the thing pulling you off balance. They\'re not the same question. And you don\'t have to choose between them — but it matters that you know which one you\'re asking.' },
      // T23 — Voice A closing (v3, rendered 2026-05-09 — 8m37s total)
      { t: 497, role: 'a', text: 'Thank you for sitting with this one today. Next time, we take up the self that isn\'t a thing — what the early Buddhist suttas call the not-self teaching, and what Thomas Metzinger calls the ego tunnel. Until then.' }
    ],
    citations: [
      {
        id: 'cite01',
        source: 'Bhagavad Gita 2.47',
        license: 'PD · Edwin Arnold',
        locator: '2.47–2.48',
        quote: 'But thou, want not! ask not! Find full reward of doing right in right! Let right deeds be thy motive, not the fruit which comes from them. And live in action! Labour! Make thine acts thy piety, casting all self aside, contemning gain and merit; equable in good or evil: equability is Yog, is piety!',
        url: 'https://www.sacred-texts.com/hin/gita/bg02.htm',
        heardAt: 66
      },
      {
        id: 'cite02',
        source: 'Bhagavad Gita 2.56',
        license: 'PD · Edwin Arnold',
        locator: '2.56',
        quote: 'In sorrows not dejected, and in joys not overjoyed; dwelling outside the stress of passion, fear, and anger; fixed in calms of lofty contemplation — such an one is Muni, is the Sage, the true Recluse!',
        url: 'https://www.sacred-texts.com/hin/gita/bg02.htm',
        heardAt: 123
      },
      {
        id: 'cite03',
        source: 'Anguttara Nikāya 5.30 — With Nāgita',
        license: 'CC0 · Bhante Sujato',
        locator: 'AN 5.30',
        quote: 'May I never become famous. May fame not come to me. There are those who can\'t get the pleasure of renunciation, the pleasure of seclusion, the pleasure of peace, the pleasure of awakening when they want, without trouble or difficulty like I can. Let them enjoy the filthy, lazy pleasure of possessions, honor, and popularity.',
        url: 'https://suttacentral.net/an5.30/en/sujato',
        heardAt: 302
      }
    ],
    showNotes: {
      whatItExplores: 'The concept of vairāgya — dispassion or non-attachment — from the Yoga Sūtras and the Bhagavad Gītā, paired with contemporary research on affective forecasting from behavioural science (Gilbert & Wilson).',
      primarySources: [
        { label: 'Bhagavad Gita 2.47', detail: 'Edwin Arnold · License: PD', url: 'https://www.sacred-texts.com/hin/gita/bg02.htm' },
        { label: 'Bhagavad Gita 2.56', detail: 'Edwin Arnold · License: PD', url: 'https://www.sacred-texts.com/hin/gita/bg02.htm' },
        { label: 'Anguttara Nikāya 5.30 — With Nāgita', detail: 'Bhante Sujato · License: CC0', url: 'https://suttacentral.net/an5.30/en/sujato' }
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
