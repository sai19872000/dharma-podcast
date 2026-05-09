/**
 * dharma-podcast-rss Worker
 * Serves the static site via [assets] binding.
 * /feed.xml is served as a static asset from web/feed.xml.template
 * (devops will iterate when R2 binding lands for dynamic feed generation).
 */

export default {
  async fetch(request, env) {
    // Pass all requests through to the static asset binding.
    // Wrangler [assets] handles SPA routing and 404 pages automatically.
    return env.ASSETS.fetch(request);
  },
};
