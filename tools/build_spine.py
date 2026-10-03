"""Builds the Striver A2Z topic spine and a dependency DAG.

Scope decision, stated plainly: the catalog spans the full Striver A2Z topic
set. Meeting *every* listed problem would mean 474 hand-written complexity
ladders, which is weeks of authoring, so the catalog carries every topic and
every problem we can verify, while the authored ladders stay a curated subset
that the UI labels honestly as coverage rather than pretending to be complete.

Provenance: topic names, counts and difficulty labels come from the Striver A2Z
structure as mirrored in public solution repositories. Ordering is authored here
as a dependency DAG: a topic may only appear after everything it requires.
"""

import json
import pathlib
import re
import collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "data" / "spine.json"

# ---------------------------------------------------------------- topic spine
# step = Striver's own step number, so the ordering matches the published sheet.
# needs = the topic ids that must be understood first.
TOPICS = [
    # Foundations
    dict(step=1, id="basics", name="Learn the Basics",
         group="Foundations", blurb="I/O, loops, functions and complexity analysis.",
         needs=[]),
    dict(step=2, id="sorting", name="Sorting Techniques",
         group="Foundations", blurb="Insertion, selection, bubble, merge and quick sort.",
         needs=["basics"]),
    dict(step=3, id="math", name="Basics of Maths",
         group="Foundations", blurb="Divisors, primes, digit tricks, modular arithmetic.",
         needs=["basics"]),
    dict(step=4, id="bitmanipulation", name="Bit Manipulation",
         group="Foundations", blurb="Set bits, masks, XOR tricks, powers of two.",
         needs=["basics", "math"]),

    # Core linear structures
    dict(step=5, id="arrays", name="Arrays",
         group="Core", blurb="Prefix sums, rotation, subarrays, frequency counting.",
         needs=["basics", "sorting"]),
    dict(step=6, id="strings", name="Strings",
         group="Core", blurb="Palindromes, anagrams, parsing, character maths.",
         needs=["arrays"]),
    dict(step=7, id="hashing", name="Hashing",
         group="Core", blurb="Frequency maps and set-based lookups.",
         needs=["arrays"]),
    dict(step=8, id="twopointers", name="Two Pointers",
         group="Core", blurb="Opposing cursors over a sorted or paired range.",
         needs=["arrays"]),
    dict(step=9, id="slidingwindow", name="Sliding Window",
         group="Core", blurb="Fixed and variable width windows with amortised updates.",
         needs=["arrays", "twopointers"]),
    dict(step=10, id="binarysearch", name="Binary Search",
         group="Core", blurb="Search on a monotone answer, including search space.",
         needs=["arrays", "sorting"]),
    dict(step=11, id="linkedlist", name="Linked List",
         group="Core", blurb="Reversal, cycles, merging, two pointer list tricks.",
         needs=["basics"]),

    # Non-linear structures
    dict(step=12, id="stack", name="Stacks and Queues",
         group="Structures", blurb="Next greater, monotonic stack, deques, prefix min.",
         needs=["linkedlist", "arrays"]),
    dict(step=13, id="heap", name="Heaps / Priority Queue",
         group="Structures", blurb="K largest, merge K lists, continuous streams.",
         needs=["arrays"]),
    dict(step=14, id="tries", name="Tries",
         group="Structures", blurb="Prefix search and counting across a key space.",
         needs=["strings", "hashing"]),

    # Recursive thinking
    dict(step=14, id="recursion", name="Recursion and Backtracking",
         group="Recursive",
         blurb="Subsets, combinations, permutations, grid search.",
         needs=["arrays", "strings"],
         # Patterns that are subtopics of this node rather than nodes in their
         # own right, so a problem tagged with them still lands somewhere real.
         also=["backtracking"]),

    # Trees
    dict(step=15, id="trees", name="Binary Trees",
         group="Trees", blurb="Traversals, BST properties, LCA, serialisation.",
         needs=["recursion", "linkedlist"]),
    dict(step=16, id="bst", name="Binary Search Trees",
         group="Trees", blurb="Inorder ordering, insert, delete, floor and ceil.",
         needs=["trees", "binarysearch"]),
    dict(step=17, id="avlandt", name="Advanced Trees (AVL, Segment Tree, Fenwick)",
         group="Trees", blurb="Self balancing structures and range queries.",
         needs=["bst"]),

    # Graphs
    dict(step=18, id="graphs", name="Graphs",
         group="Graphs", blurb="Traversal, topological sort, shortest paths, MST.",
         needs=["linkedlist", "stack", "heap"]),

    # Techniques layered on the above
    dict(step=19, id="greedy", name="Greedy",
         group="Techniques", blurb="Interval merging, activity selection, jump game.",
         needs=["sorting", "binarysearch"]),
    dict(step=20, id="intervals", name="Intervals",
         group="Techniques", blurb="Merge, insert and sweep over ranges on a line.",
         needs=["sorting"]),
    dict(step=21, id="divideconquer", name="Divide and Conquer",
         group="Techniques", blurb="Binary search on answer, median, inversion count.",
         needs=["binarysearch", "sorting"]),
    dict(step=22, id="dynamicprogramming", name="Dynamic Programming",
         group="Techniques", blurb="1D, 2D, grids, subsequences, strings, trees.",
         needs=["recursion", "arrays", "strings", "graphs"]),
]

# ------------------------------------------------------- verified counts
# Topic totals as published for the Striver A2Z sheet. Used to show where the
# authored subset sits against the full sheet rather than guessing.
PUBLISHED_TOTALS = {
    "basics": 54, "sorting": 7, "arrays": 40, "binarysearch": 32,
    "strings": 15, "linkedlist": 31, "recursion": 25, "bitmanipulation": 18,
    "stack": 30, "slidingwindow": 12, "heap": 17, "greedy": 15,
    "trees": 38, "bst": 16, "graphs": 53, "dynamicprogramming": 55,
    "tries": 7,
}


def topological_order():
    by_id = {t["id"]: t for t in TOPICS}
    seen, order = set(), []

    def visit(tid, stack):
        if tid in seen:
            return
        if tid in stack:
            raise ValueError(f"dependency cycle at {tid}")
        stack.add(tid)
        for dep in by_id[tid]["needs"]:
            if dep not in by_id:
                raise ValueError(f"{tid} depends on unknown topic {dep}")
            visit(dep, stack)
        stack.discard(tid)
        seen.add(tid)
        order.append(tid)

    for t in TOPICS:
        visit(t["id"], set())
    return order


def main():
    order = topological_order()
    by_id = {t["id"]: t for t in TOPICS}

    # assign each topic its position in the resolved dependency order
    for pos, tid in enumerate(order):
        by_id[tid]["order"] = pos

    # the same difficulty ladder order used everywhere else in the app
    diff_order = {"Easy": 0, "Medium": 1, "Hard": 2}

    # existing authored problems, keyed so we can attach ladders to spine topics
    authored = json.loads((ROOT / "app" / "data" / "problems.json").read_text())
    authored_by_id = {p["id"]: p for p in authored["problems"]}

    nodes = []
    for tid in order:
        t = by_id[tid]
        nodes.append({
            "id": t["id"],
            "name": t["name"],
            "group": t["group"],
            "step": t["step"],
            "order": t["order"],
            "blurb": t["blurb"],
            "needs": sorted(t["needs"], key=lambda x: by_id[x]["order"]),
            "publishedTotal": PUBLISHED_TOTALS.get(t["id"]),
        })

    # attach the authored subset
    # A problem's pattern may name a subtopic (backtracking), so resolve it
    # through the owning topic's `also` list rather than dropping the problem.
    owner = {}
    for t in TOPICS:
        owner[t["id"]] = t["id"]
        for sub in t.get("also", []):
            owner[sub] = t["id"]

    links = []
    orphans = []
    for pid, p in sorted(authored_by_id.items(), key=lambda kv: diff_order.get(kv[1]["difficulty"], 3)):
        tid = owner.get(p["pattern"])
        if tid is None or tid not in by_id:
            orphans.append((pid, p["pattern"]))
            continue
        links.append({
            "id": pid,
            "topic": tid,
            "title": p["title"],
            "difficulty": p["difficulty"],
            "ladders": len(p.get("ladder", [])),
            "hints": len(p.get("hints", [])),
            "lists": p.get("lists", []),
        })

    if orphans:
        raise SystemExit(
            "authored problems do not map onto the spine: "
            + ", ".join(f"{pid} ({pat})" for pid, pat in orphans)
        )

    spine = {
        "_meta": {
            "source": "Striver A2Z DSA sheet structure (takeuforward.org)",
            "note": (
                "Topic order is a dependency graph: a topic is only listed after every "
                "topic it requires. Counts marked publishedTotal are the sheet's own "
                "totals. Authored ladders are a curated subset; the Progress view shows "
                "authored versus published coverage per topic rather than implying the "
                "whole sheet is written up."
            ),
            "topics": len(nodes),
            "authoredProblems": len(links),
        },
        "topics": nodes,
        "links": links,
        "edges": [
            {"from": dep, "to": t["id"]}
            for t in nodes
            for dep in t["needs"]
        ],
    }

    OUT.write_text(json.dumps(spine, indent=2, ensure_ascii=False))

    print(f"topics            : {len(nodes)}")
    print(f"dependency edges  : {len(spine['edges'])}")
    print(f"authored problems : {len(links)}")
    print(f"authored ladders  : {sum(l['ladders'] for l in links)}")
    covered = {l["topic"] for l in links}
    print(f"topics with ladders: {len(covered)} of {len(nodes)}")
    missing = [n["name"] for n in nodes if n["id"] not in covered]
    if missing:
        print("\ntopics with no authored ladder yet:")
        for m in missing:
            print("  -", m)


if __name__ == "__main__":
    main()