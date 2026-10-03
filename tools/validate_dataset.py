"""Integrity checks for the Strided dataset.

Every problem must carry a real pattern, exactly three ladder rungs in the
order brute, better, optimal, a code sample per supported language, an
explanation for why the rung is an improvement, and five escalating hints.
Every pattern referenced by a problem needs a syntax card.
"""

import json
import pathlib
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / "app" / "data" / "problems.json"
LANGS = ("java", "python", "cpp")
TIERS = ["brute", "better", "optimal"]


def main():
    data = json.loads(DATA.read_text())
    problems = data["problems"]
    patterns = {p["id"] for p in data["patterns"]}
    card_patterns = {c["pattern"] for c in data["syntaxCards"]}

    errors = []
    warnings = []

    if len(problems) != len({p["id"] for p in problems}):
        errors.append("duplicate problem ids")

    for p in problems:
        pid = p.get("id", "?")

        if p.get("pattern") not in patterns:
            errors.append(f"{pid}: unknown pattern {p.get('pattern')!r}")

        if not p.get("statement") or len(p["statement"]) < 40:
            errors.append(f"{pid}: statement too thin")
        if not p.get("keyIdea") or len(p["keyIdea"]) < 40:
            errors.append(f"{pid}: keyIdea too thin")

        ladder = p.get("ladder", [])
        if [r["tier"] for r in ladder] != TIERS:
            errors.append(f"{pid}: ladder tiers are {[r['tier'] for r in ladder]}, expected {TIERS}")

        for rung in ladder:
            tag = f"{pid}/{rung.get('tier')}"
            if not rung.get("why") or len(rung["why"]) < 30:
                errors.append(f"{tag}: why is missing or too thin")
            for field in ("time", "space"):
                if not rung.get(field):
                    errors.append(f"{tag}: missing {field}")
            for lang in LANGS:
                code = (rung.get("code") or {}).get(lang)
                if not code or len(code.strip()) < 10:
                    errors.append(f"{tag}: missing or trivial {lang} code")

        hints = p.get("hints", [])
        if len(hints) != 5:
            errors.append(f"{pid}: expected 5 hints, found {len(hints)}")
        for i, h in enumerate(hints):
            if len(h) < 20:
                errors.append(f"{pid}: hint {i + 1} too thin")

        plat = p.get("platform", {})
        if not plat.get("leetcode"):
            errors.append(f"{pid}: no leetcode slug")
        for host in ("neetcode", "walkccc"):
            url = plat.get(host)
            if url and not url.startswith("https://"):
                errors.append(f"{pid}: {host} url is not https")

        # A ladder whose ends are identical is not a ladder. Where no
        # asymptotic win exists (n! outputs, for instance) the rung must say so
        # explicitly rather than implying an improvement that is not there.
        if len(ladder) == 3:
            first, last = ladder[0], ladder[-1]
            if first.get("time") == last.get("time") and first.get("space") == last.get("space"):
                says_so = any(
                    w in last.get("why", "").lower()
                    for w in ("no asymptotic win", "same asymptotics", "allocation", "no win left")
                )
                if not says_so:
                    errors.append(
                        f"{pid}: optimal rung has the same cost as brute and does not explain why"
                    )

    covered = {p["pattern"] for p in problems}
    missing_cards = covered - card_patterns
    if missing_cards:
        errors.append(f"patterns without a syntax card: {sorted(missing_cards)}")

    for c in data["syntaxCards"]:
        if c["pattern"] not in patterns:
            errors.append(f"syntax card for unknown pattern: {c['pattern']}")
        if not c.get("note") or len(c["note"]) < 40:
            errors.append(f"{c['pattern']}: syntax note too thin")
        for lang in LANGS:
            if not (c.get("snippets") or {}).get(lang):
                errors.append(f"{c['pattern']}: syntax card missing {lang}")

    # report
    print(f"problems      : {len(problems)}")
    print(f"patterns      : {len(data['patterns'])}")
    print(f"syntax cards  : {len(data['syntaxCards'])}")
    print(f"sources       : {len(data.get('sources', []))}")
    by_diff = {}
    for p in problems:
        by_diff[p["difficulty"]] = by_diff.get(p["difficulty"], 0) + 1
    print(f"difficulty    : {by_diff}")
    print(f"patterns used : {len(covered)} of {len(data['patterns'])}")

    if warnings:
        print("\nwarnings:")
        for w in warnings:
            print("  -", w)

    # ---------- dependency spine ----------
    spine_path = DATA.parent / "spine.json"
    if not spine_path.exists():
        errors.append("spine.json is missing, run tools/build_spine.py")
    else:
        spine = json.loads(spine_path.read_text())
        topics = spine["topics"]
        ids = [x["id"] for x in topics]
        idset = set(ids)

        if len(ids) != len(idset):
            errors.append("spine: duplicate topic ids")

        orders = sorted(x["order"] for x in topics)
        if orders != list(range(len(topics))):
            errors.append("spine: order values are not a dense sequence, so the graph may be cyclic")

        order_of = {x["id"]: x["order"] for x in topics}
        for e in spine["edges"]:
            if e["from"] not in idset or e["to"] not in idset:
                errors.append(f"spine: dangling edge {e}")
            elif order_of[e["to"]] <= order_of[e["from"]]:
                errors.append(
                    f"spine: {e['to']} is not ordered after its prerequisite {e['from']}"
                )

        for x in topics:
            for dep in x["needs"]:
                if dep not in idset:
                    errors.append(f"spine: {x['id']} needs unknown topic {dep}")

        # every authored problem must be represented, or the map hides content
        linked = {l["id"] for l in spine["links"]}
        authored_ids = {p["id"] for p in problems}
        for pid in sorted(authored_ids - linked):
            errors.append(f"spine: authored problem {pid} is not on the spine")

        for l in spine["links"]:
            if l["topic"] not in idset:
                errors.append(f"spine: link {l['id']} points at unknown topic {l['topic']}")

        # a link promising three rungs must have three rungs in the source data
        by_id = {p["id"]: p for p in problems}
        for l in spine["links"]:
            p = by_id.get(l["id"])
            if p and len(p.get("ladder", [])) != 3:
                errors.append(f"spine: link {l['id']} claims 3 rungs but has {len(p.get('ladder', []))}")

        print(f"spine topics     : {len(topics)}")
        print(f"spine edges      : {len(spine['edges'])}")
        print(f"spine links      : {len(spine['links'])}")

    if errors:
        print(f"\n{len(errors)} ERROR(S):")
        for e in errors[:40]:
            print("  x", e)
        return 1

    print("\nOK: dataset integrity clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())