/**
 * dharma-podcast-rss Worker
 * - /audio/* → served from R2 bucket with proper HTTP 206 Partial Content support,
 *   enabling browser seek (±15s/±30s, waveform click+drag, transcript-row click).
 * - Everything else → static site via [assets] binding.
 *
 * Root cause of v4.1 seek bug: Wrangler [assets] does not reliably honor Range
 * headers, and CF cache had served a stale HTTP 200 (no Accept-Ranges) for
 * audio files. Without 206, <audio> elements reset to 0:00 on every seek.
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith('/audio/') && (request.method === 'GET' || request.method === 'HEAD')) {
      const key = url.pathname.replace(/^\/audio\//, '');
      const range = request.headers.get('Range');

      // HEAD: lightweight metadata lookup; advertise Accept-Ranges so browsers
      // know they can seek before issuing a full GET.
      if (request.method === 'HEAD') {
        const obj = await env.AUDIO.head(key);
        if (!obj) return new Response('Not Found', { status: 404 });
        return new Response(null, {
          status: 200,
          headers: {
            'Content-Type': 'audio/mpeg',
            'Content-Length': String(obj.size),
            'Accept-Ranges': 'bytes',
            'Cache-Control': 'public, max-age=31536000, immutable',
            'ETag': obj.httpEtag,
          },
        });
      }

      if (range) {
        // Parse 'bytes=start-end' or 'bytes=start-' (open-ended).
        const m = /^bytes=(\d+)-(\d*)$/.exec(range);
        if (!m) return new Response('Range Not Satisfiable', { status: 416 });
        const head = await env.AUDIO.head(key);
        if (!head) return new Response('Not Found', { status: 404 });
        const total = head.size;
        const start = parseInt(m[1], 10);
        const end = m[2] ? Math.min(parseInt(m[2], 10), total - 1) : total - 1;
        if (start >= total || start > end) {
          return new Response('Range Not Satisfiable', {
            status: 416,
            headers: { 'Content-Range': `bytes */${total}` },
          });
        }
        const length = end - start + 1;
        const obj = await env.AUDIO.get(key, { range: { offset: start, length } });
        if (!obj) return new Response('Not Found', { status: 404 });
        return new Response(obj.body, {
          status: 206,
          headers: {
            'Content-Type': 'audio/mpeg',
            'Content-Length': String(length),
            'Content-Range': `bytes ${start}-${end}/${total}`,
            'Accept-Ranges': 'bytes',
            'Cache-Control': 'public, max-age=31536000, immutable',
            'ETag': obj.httpEtag,
          },
        });
      }

      // No Range header — return whole file, but advertise Accept-Ranges so the
      // browser can issue range requests on subsequent seeks.
      const obj = await env.AUDIO.get(key);
      if (!obj) return new Response('Not Found', { status: 404 });
      return new Response(obj.body, {
        status: 200,
        headers: {
          'Content-Type': 'audio/mpeg',
          'Content-Length': String(obj.size),
          'Accept-Ranges': 'bytes',
          'Cache-Control': 'public, max-age=31536000, immutable',
          'ETag': obj.httpEtag,
        },
      });
    }

    // All other paths (/, /e/*, /feed.xml, etc.) → static [assets] binding.
    return env.ASSETS.fetch(request);
  },
};
