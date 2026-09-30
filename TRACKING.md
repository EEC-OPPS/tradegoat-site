# Site tracking

Every public page carries one inline script block, "Site beacon", just before
`</body>`. It sends one page view per load and a few funnel events. There is
no backend change: an event is an ordinary beacon row whose `page` starts with
`evt:` (the field keeps 120 characters). No personal data is sent: the row is
the page or event string, the referrer on page views only, and the anonymous
per-browser token that page views already used.

## How it sends

- Body: `{page, ref, visitor}`, sent with `navigator.sendBeacon` as `text/plain`
  (no preflight, survives the page closing), falling back to a `keepalive`
  fetch. Fail-silent: a lost beacon never shows an error.
- Visitor: the same `tg_vid` token in localStorage as before. A device opened
  once with `?goat=me` sends `founder` instead, and reports leave it out.
- Where it goes: `thetradegoat.com` and `www.thetradegoat.com` send to the live
  beacon. `localhost` / `127.0.0.1` send to `/__tg_sink` on the same local
  server, so a local test never reaches production. Any other host (a preview
  deploy, a copy) sends nothing. `file://` sends nothing.

## Page views (every page)

| Row `page` | Fires |
|---|---|
| the path, e.g. `/index`, `/demo.html`, `/blog/what-tradegoat-is.html` (plus `?ref` when the URL carries a referral code) | once per page load. Blog pages and `updates.html` / `privacy.html` are new; the other pages already sent this and still send exactly the same value. |

## Events

`<page>` below is the path without the leading slash or `.html`:
`index`, `demo`, `tour`, `pricing`, `features`, `kaufman`, `updates`,
`privacy`, `blog/index`, `blog/<article>`.

| Row `page` | Fires | Where |
|---|---|---|
| `evt:cta:<page>:<kind>-<zone>` | a click on a call to action. `kind`: `start` (any Start free / waitlist button, or anything pointing at `#beta`, `#waitlist` or `/sign-up`), `demo` (a link to the demo), `pricing`, `tour`, `login`. `zone`: `nav` (top bar), `menu` (the phone menu), `hero`, `guide` (the demo's Try-this box), `foot`, `body`. | every page |
| `evt:form:<page>:invalid` | the browser refused the waitlist form (empty or bad email, no answer picked); once per attempt | home page form |
| `evt:form:<page>:submit` | the waitlist form was submitted | home page form |
| `evt:form:<page>:ok` | the thank-you appeared after the signup engine saved it | home page form |
| `evt:form:<page>:fallback` | the thank-you appeared, but the engine was unreachable and the backup form service took it | home page form |
| `evt:form:<page>:fail` | the "Something went wrong" message appeared | home page form |
| `evt:home:scroll:25` / `50` / `75` / `100` | the reader scrolled far enough that that share of the page has been on screen; once each per view | `index.html` |
| `evt:demo:scene:<id>` | each time the demo's screen changes (`dash`, `calc`, `drive`, `props`, `tmpl`, `maint`, `ticket`, `map`, `jmoney`, `cust`, `wl`, `score`, `team`), including the first screen on load | `demo.html` |
| `evt:demo:guide:<n>` | the first time Try-this step `n` shows (1–13 are the steps; 14 is the closing "That's the whole loop" card) | `demo.html` |
| `evt:demo:end:s=<seconds>:deep=<n>:last=<id>` | once, when the demo page is left (`pagehide`): seconds the page was on screen (hidden-tab time not counted), the deepest Try-this step reached, the screen it was left on | `demo.html` |
| `evt:tour:step:<chapter id>` | the first time each chapter is reached (`ch1`, `ch2`, `ch3`, `ch4`, `ch-owner`, `ch5`, `ch6`, `ch-lang`, `ch7`, `ch-history`, `ch8`): in the scrolling tour when it crosses the middle of the screen, in `?tv=1` mode when its slide shows | `tour.html` |
| `evt:tour:end:s=<seconds>:deep=<n>:last=<chapter id>` | once, when the tour page is left: seconds on screen, the furthest chapter by position (1–11), the chapter it was left on | `tour.html` |

## Known limits

- A phone that is backgrounded and then closed by the system may never fire
  `pagehide`, so it sends no closing row. Its screen and step rows are still
  there; only its time is missing.
- A browser that blocks storage sends rows with no visitor token; they cannot
  be counted as people.
- The demo and tour hooks watch the page itself (the `.scene` / `#guideSteps`
  markup and the `section.ch[id]` chapters). If those are renamed, update the
  matching block at the bottom of `demo.html` / `tour.html`.
