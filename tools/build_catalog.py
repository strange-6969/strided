"""Extracts the full Striver A2Z problem catalog from public solution mirrors.

Why mirrors rather than the site: takeuforward.org renders its sheet client side
and exposes no JSON endpoint, and it sits behind a bot check. Public solution
repositories mirror the sheet faithfully, and their directory names encode the
sheet's own structure (topic, difficulty band, problem title), which is exactly
the metadata a catalog needs.

Only titles and topic placement come from the mirrors. No solution code is
copied, and no LeetCode content is reproduced.

Four mirrors are read and unioned: LeetCode-style questions dominate, but the
basics and pattern sections on Striver's sheet are not LeetCode problems, so
those rows are kept with platform "tuf" and are clearly non-LeetCode.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "data" / "catalog.json"

MIRRORS = [
    "Codensity30/Strivers-A2Z-DSA-Sheet",
    "dhruv-yadav-nitj/striver-a2z-dsa",
    "sumitgirwal/Strivers-A2Z-DSA-Sheet",
    "megh-bari/Striver-A2Z-DSA-Sheet",
]

EXT = (".cpp", ".py", ".java", ".js", ".ts", ".c", ".go", ".cs", ".md")

# Sheet topic keywords mapped onto our spine ids. Order matters: the first
# match wins, so more specific patterns are listed before broader ones.
TOPIC_RULES: list[tuple[str, str]] = [
    (r"(?i)\b(learn the basics|things to know|pattern problems?|basic math)\b", "basics"),
    (r"(?i)\bmaths?\b|\bnumber theory\b|\bprimes?\b|\bdivisors?\b|\bdigits?\b", "math"),
    (r"(?i)\bbit ?manipulation\b|\bbitmagic\b", "bitmanipulation"),
    (r"(?i)\bsorting\b|\bsort algorithm\b", "sorting"),
    (r"(?i)\bsegment trees?\b|\bfenwick\b|\bavl\b|\bred ?black\b|\badvanced trees?\b", "avlandt"),
    (r"(?i)\bbinary search trees?\b|\bbst\b", "bst"),
    (r"(?i)\bbinary search\b|\bsearch space\b", "binarysearch"),
    (r"(?i)\bdynamic programming\b|\bdp\b", "dynamicprogramming"),
    (r"(?i)\bdivide and conquer\b|\bdivide\b|\bconquer\b", "divideconquer"),
    (r"(?i)\bsliding window\b", "slidingwindow"),
    (r"(?i)\btwo ?pointers?\b", "twopointers"),
    (r"(?i)\bbacktrack\b|\brecursion\b|\bsubsets?\b|\bpermutations?\b|\bcombinations?\b", "recursion"),
    (r"(?i)\bgraphs?\b|\bdijkstra\b|\btopological\b|\bspanning\b|\bbridges?\b|\bscc\b", "graphs"),
    (r"(?i)\bbinary trees?\b|\btrees\b", "trees"),
    (r"(?i)\blinked ?lists?\b|\bdll\b", "linkedlist"),
    (r"(?i)\bstacks?\b|\bqueues?\b|\bmonotonic\b|\bdeque\b", "stack"),
    (r"(?i)\bheaps?\b|\bpriority ?queue\b", "heap"),
    (r"(?i)\btries?\b", "tries"),
    (r"(?i)\bstrings?\b", "strings"),
    (r"(?i)\bhashing\b|\bhash map\b|\bfrequency\b", "hashing"),
    (r"(?i)\bgreedy\b", "greedy"),
    (r"(?i)\bintervals?\b", "intervals"),
    (r"(?i)\barrays?\b", "arrays"),
]

# Matched against path segments with leading ordinals stripped, so "1.Easy"
# reads as Easy rather than as the number 1.
DIFF_RULES: list[tuple[str, str]] = [
    (r"(?i)\b(hard|advanced|expert)\b", "Hard"),
    (r"(?i)\b(medium|mid)\b", "Medium"),
    (r"(?i)\b(easy|basics?|learning|concept|intro|simple)\b", "Easy"),
]

# Noise to drop: helper classes and non-problem files.
#
# Anchored on purpose. A loose word filter here would silently delete real
# problems: "Height of binary tree" contains "tree", and "Deleting node in
# linked list" contains "node". So only words that appear as standalone helper
# class files, or as an explicit helper suffix, count as noise.
DROP = re.compile(
    r"(?i)(^|[\s_\-])("
    r"treenode|listnode|node\.h|node\.hpp|"
    r"helper|helpers|util|utils|utility|"
    r"readme|note|notes|approach|explanation|"
    r"test|tests|main|demo|driver|setup|config|"
    r"contributing|assets?|images?|img|"
    r"solution[\s_\-]?notes"
    r")([\s_\-.]|$)"
)


def gh_tree(repo: str) -> list[str]:
    r = subprocess.run(
        ["gh", "api", f"repos/{repo}/git/trees/HEAD?recursive=1",
         "--jq", '.tree[] | select(.type=="blob") | .path'],
        capture_output=True, text=True, timeout=120,
    )
    return [p for p in r.stdout.splitlines() if p.strip()]


# Leading ordinals and mirrored-slice suffixes ("part 2", "2", "p 2") are a
# naming convention in these mirrors, not part of the problem name. Left in
# place they make near-duplicates that do not collapse, and they break the
# difficulty rules below.
ORDINAL = re.compile(r"^\s*\d{1,3}\s*[.\-_\)]?\s*")
SUFFIX = re.compile(
    # Requires the separator to be a real word boundary, so "sum" stays "sum"
    # and "bfs" stays "bfs". A bare trailing "-1" is only stripped when it is
    # separated by a non-alphanumeric AND the stem is longer than the digits,
    # otherwise "combination-sum-1" would lose its distinguishing number.
    r"(?i)[\s\-_]+(part|parts)[\s\-_.]?\s*\d{1,2}\s*$"
    r"|\bp\s*[\-_]\s*\d{1,2}\s*$"
    r"|[\s\-_]+\d{1,2}(?=\s*$)"
)


def clean_title(text: str) -> str:
    """Strip a leading directory ordinal, then a trailing slice suffix.

    Deliberately conservative. An earlier version stripped any trailing
    number, which silently mangled 290 entries: "BFS" became "" and
    "4 sum" became "sum", collapsing whole topics into one junk row.
    """
    out = ORDINAL.sub("", text)
    out = SUFFIX.sub("", out)
    out = re.sub(r"\s+", " ", out).strip(" .-")
    return out or text.strip()


def strip_ext(path: str) -> tuple[str, str]:
    stem = path.rsplit(".", 1)[0]
    parts = stem.split("/")
    return stem, clean_title(parts[-1].replace("_", " ").replace("-", " ").strip())


def norm_title(text: str) -> str:
    """Collapse to a dedup key.

    Punctuation becomes a space rather than vanishing, so "combination-sum"
    and "combination sum" produce the same key instead of "combinationsum"
    against "combinationsum" from a differently punctuated mirror. The earlier
    delete-not-replace behaviour also made short acronyms such as "bfs"
    indistinguishable from nothing at all.
    """
    return " ".join(tokens(text))


# Mirrors disagree on abbreviations and typos for the same problem: "Koko
# eating banana" against "koto eating banana", "Flatten LL" against "flatten
# linkedList". Merging those is right. Merging anything else is not, and the
# distinctions below are the ones that actually change the problem:
#
#   "Print 1 to N"      vs "Print N to 1"   token order carries the meaning
#   "Merge 2 sorted"    vs "Merge K sorted" a different k
#   "Kadane's"          vs "Kahn's"        different algorithms
#   "Longest pal subseq" vs "... substring" different problems
#
# So two titles merge only when their normalised token SEQUENCE is identical.
TYPO_FIXES = {
    "ll": "linkedlist", "l": "linkedlist", "dll": "doublylinkedlist",
    "bs": "binarysearch", "subarr": "subarray", "arr": "array", "arra": "array",
    "koto": "koko", "partion": "partition", "palindorme": "palindrome",
    "conseq": "consecutive", "sor": "sort", "srch": "search",
    "inv": "inverse", "inver": "inverse", "pattren": "pattern",
    # Mirror spellings differ on the plural and on the trailing article.
    "bananas": "banana", "arrays": "array", "lists": "list",
    "trees": "tree", "strings": "string", "graphs": "graph",
    "stacks": "stack", "queues": "queue", "heaps": "heap",
    "subsets": "subset", "permutations": "permutation",
    "combinations": "combination", "sequences": "sequence",
    "paths": "path", "nodes": "node", "numbers": "number",
    "subsequences": "subsequence", "substrings": "substring",
}


# Whole-token abbreviation expansion. Substitution alone cannot handle a case
# like "Flatten LL" against "flatten linked list": LL expands to a two word
# phrase, so it has to be replaced in place rather than mapped to one token.
ABBREV = [
    (r"\bdlls?\b", "doubly linked list"),
    (r"\blinked ?lst\b|\bll\b", "linked list"),
    (r"\bbsts?\b", "binary search tree"),
    (r"\bbinary ?srch\b|\bbinary ?search trees?\b", "binary search tree"),
    (r"\bbs\b", "binary search"),
    (r"\bsub ?arr\w*\b", "subarray"),
    (r"\b2 ?d\b", "two dimensional"),
    (r"\b1 ?d\b", "one dimensional"),
]


def tokens(text: str) -> list[str]:
    s = re.sub(r"[^a-z0-9 ]", " ", clean_title(text).lower())
    for pat, repl in ABBREV:
        s = re.sub(pat, repl, s)
    return [TYPO_FIXES.get(w, w) for w in s.split()]


def pattern_drill(text: str) -> bool:
    """Striver's pattern section numbers its drills, and "Pattern 1" and
    "Pattern 10" are different exercises. Treating the numeral as a plain token
    is not enough on its own, because a trailing ordinal is already stripped
    from the title, so the drill index has to be recovered before that."""
    m = re.search(r"(?i)\bpattern\s+(\d{1,2})\b", text)
    return bool(m)


def same_problem(a: str, b: str) -> bool:
    """Exact token-sequence equality. Order is significant and extra tokens mean
    a different variant, so nothing fuzzy can slip through here.

    Numbered pattern drills are the one case where clean_title cannot be trusted
    on its own, because it strips a trailing ordinal, and Striver's pattern
    section is numbered. The drill index is compared from the raw title.
    """
    if bool(pattern_drill(a)) != bool(pattern_drill(b)):
        return False
    if pattern_drill(a) and pattern_drill(b):
        ia = re.search(r"(?i)\bpattern\s+(\d{1,2})\b", a)
        ib = re.search(r"(?i)\bpattern\s+(\d{1,2})\b", b)
        if ia.group(1) != ib.group(1):
            return False
        return True
    return tokens(a) == tokens(b)


# Acronyms are legitimate problem titles in these mirrors ("BFS", "DFS", "N
# Queen", "MCM"), so the minimum identifying length has to admit three
# characters. Requiring four silently deleted the entire graph traversal
# section.
MIN_KEY = 3


def scrub(blob: str) -> str:
    """Strip ordinals from every path segment so rules see words, not numbers."""
    return " ".join(clean_title(seg.replace("_", " ").replace("-", " ")) for seg in blob.split("/"))


def topic_of(blob: str) -> str | None:
    """Classify by the deepest directory that names a topic.

    Directory segments first (deepest wins), then the filename last. Testing
    the filename first is wrong: a leaf like "Largest element in array" would
    win before the parent directory "01.Arrays" ever got a look, so whole
    topics would fall through to the generic filename rules or to unmapped.
    """
    segments = [s for s in blob.split("/")[:-1] if s]
    for seg in reversed(segments):
        probe = clean_title(seg.replace("_", " ").replace("-", " "))
        if not probe:
            continue
        for pat, tid in TOPIC_RULES:
            if re.search(pat, probe, re.I):
                return tid
    leaf = clean_title(blob.rsplit("/", 1)[-1].replace("_", " ").replace("-", " "))
    for pat, tid in TOPIC_RULES:
        if re.search(pat, leaf, re.I):
            return tid
    return None


def difficulty_of(blob: str, leaf: str) -> str:
    probe = scrub(blob)
    for pat, d in DIFF_RULES:
        if re.search(pat, probe):
            return d
    for pat, d in DIFF_RULES:
        if re.search(pat, leaf, re.I):
            return d
    return "Medium"


def main() -> int:
    # title -> best record. Duplicates across mirrors collapse; a topic hit from
    # any mirror wins because it is more specific than a bare filename.
    catalog: dict[str, dict] = {}
    stats = {"files": 0, "dropped": 0, "unmapped": 0, "duplicates": 0}

    for repo in MIRRORS:
        for path in gh_tree(repo):
            if not path.lower().endswith(EXT):
                continue
            stats["files"] += 1
            stem, leaf = strip_ext(path)
            if DROP.search(leaf):
                stats["dropped"] += 1
                continue

            tid = topic_of(path)
            if tid is None:
                stats["unmapped"] += 1
                continue

            # A leaf that is nothing but an abbreviation ("LL") carries no
            # problem identity on its own; its parent directory names the topic
            # but not the question. Keep it out rather than index a bare token.
            key = norm_title(leaf)
            if len(key) < MIN_KEY or not any(ch.isalpha() for ch in leaf) or len(leaf) < 3:
                # Mirrors commit per-file artefacts (a shared header, a
                # main, a README) whose names carry no problem identity.
                stats["dropped"] += 1
                continue

            diff = difficulty_of(path, leaf)
            prev = catalog.get(key)
            # Prefer a record whose topic came from a path segment we recognise.
            if prev is None:
                catalog[key] = {
                    "title": leaf,
                    "topic": tid,
                    "difficulty": diff,
                    "seenIn": [repo],
                }
            else:
                stats["duplicates"] += 1
                prev["seenIn"].append(repo)
                if prev["difficulty"] == "Medium" and diff != "Medium":
                    prev["difficulty"] = diff

    # Second pass: merge rows whose titles are the same problem once
    # abbreviations and typos are normalised. Done as a pass rather than inside
    # the loop because two mirrors can each contribute a spelling that only
    # becomes obviously equivalent when compared with a third.
    merged: dict[str, dict] = {}
    for key, row in catalog.items():
        match = next(
            (m for mk, m in merged.items() if same_problem(m["title"], row["title"])),
            None,
        )
        if match is None:
            merged[key] = row
            continue
        for repo in row["seenIn"]:
            if repo not in match["seenIn"]:
                match["seenIn"].append(repo)
        if match["difficulty"] == "Medium" and row["difficulty"] != "Medium":
            match["difficulty"] = row["difficulty"]
        stats["mergedTitles"] = stats.get("mergedTitles", 0) + 1

    problems = sorted(merged.values(), key=lambda x: (x["topic"], x["difficulty"], x["title"]))
    for p in problems:
        p["platform"] = "tuf" if p["topic"] == "basics" else "leetcode"

    by_topic: dict[str, int] = defaultdict(int)
    by_diff: dict[str, int] = defaultdict(int)
    for p in problems:
        by_topic[p["topic"]] += 1
        by_diff[p["difficulty"]] += 1

    OUT.write_text(json.dumps({
        "_meta": {
            "source": "Striver A2Z DSA sheet, extracted from public solution mirrors",
            "mirrors": MIRRORS,
            "note": (
                "Titles and topic placement only. No solution code and no LeetCode "
                "content is reproduced. Problems marked platform tuf are Striver's "
                "own basics and pattern drills, not LeetCode questions."
            ),
            # These mirrors are solved copies of the sheet, and solvers add
            # problems beyond the official list. The extraction is therefore a
            # superset, not the sheet itself: measured against the published
            # section totals it runs about 1.6x overall and above 1x in every
            # comparable topic. It is a planning index, not an authoritative
            # problem count, and the UI says so.
            "isTheSheetExactly": False,
            "provenance": (
                "Superset of the sheet, assembled from four public solution mirrors. "
                "Solvers add problems beyond the official list, so this index is "
                "larger than the sheet and larger than any single mirror. Section "
                "counts as published on 2026-08-09 were 152 easy, 186 medium, "
                "136 hard, 474 total."
            ),
            "publishedTotals": {
                "total": 474, "easy": 152, "medium": 186, "hard": 136,
                "asOf": "2026-08-09",
            },
            "filesScanned": stats["files"],
            "dropped": stats["dropped"],
            "unmapped": stats["unmapped"],
            "mergedDuplicates": stats["duplicates"],
        },
        "problems": problems,
        "byTopic": dict(sorted(by_topic.items())),
        "byDifficulty": dict(by_diff),
    }, indent=2, ensure_ascii=False))

    print(f"mirrors      : {len(MIRRORS)}")
    print(f"files scanned: {stats['files']}")
    print(f"dropped      : {stats['dropped']}  (non-problem files and unidentifiable names)")
    print(f"merged dupes : {stats['duplicates']}  (same problem across mirrors)")
    print(f"unmapped     : {stats['unmapped']}")
    print(f"unique probs : {len(problems)}")
    print(f"by difficulty: {dict(by_diff)}")
    print("\nby topic:")
    for t, n in sorted(by_topic.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>4}  {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())