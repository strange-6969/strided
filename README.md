# Strided

A DSA practice tracker built around one idea the existing trackers do not have:
show the improvement. Every problem carries a complexity ladder, brute force
first, then a better approach, then the optimal, each labelled with its time
and space cost and a note on why the trade was worth making.

## What is here

- **Complexity ladder** per problem, in Java, Python and C++
- **Syntax cards** per pattern, so the incantation you forget sits next to the idea
- **Escalating hints** that unlock one at a time, from a nudge to a full skeleton
- **External practice links** to LeetCode, NeetCode and Walkccc
- **Spaced review** with an inspectable interval ladder, a streak freeze, XP decay
  and mastery freezing
- Responsive, dark, no backend, no account

## Run it

```bash
npm start              # serves app/ on http://localhost:8788
npm test               # 16 spaced-repetition tests
```

## Layout

```
app/
  index.html
  css/app.css
  data/problems.json     static dataset: problems, ladders, hints, syntax cards
  js/srs.js              scheduling, streak, XP (unit tested)
  js/store.js            localStorage persistence, export and import
  js/main.js             views and events
  assets/fonts/          self-hosted Space Grotesk and JetBrains Mono
tools/
  test_srs.py            runs the SRS suite in node
  shots.js               viewport screenshots and overflow checks
```

## Data and independence

Problem titles, ids and difficulty mirror public LeetCode listings. Approach
ladders, syntax cards and hints are original material written for this project.
Strided is an independent study aid: not affiliated with, endorsed by, or
sponsored by LeetCode, and it hosts none of LeetCode content.

LeetCode has no public API and its GraphQL endpoint rejects unauthenticated
requests, so the dataset ships as static JSON and the app links out rather than
scraping. Progress lives in `localStorage` only. Export a backup before clearing
site data.
