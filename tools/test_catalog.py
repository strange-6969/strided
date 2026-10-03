"""Regression tests for the catalog extractor.

Each of these reproduces a bug that actually shipped in an earlier revision:

  1. clean_title collapsed acronyms. "BFS" became "" and "4 sum" became "sum",
     which merged 290 distinct entries into one junk key and silently deleted
     most of the graph section.
  2. norm_title deleted punctuation instead of replacing it with a space, so
     differently punctuated mirrors produced different keys.
  3. The minimum key length of 4 rejected "BFS", "DFS" and "MCM".
  4. The noise filter matched bare "tree" and "node", deleting real problems
     such as "Height of binary tree" and "Deleting node in linked list".
  5. topic_of tested the filename before the directory, so a whole topic fell
     through to unmapped.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_catalog as bc  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main() -> int:
    # 1. acronyms survive
    for t, want in [("BFS", "BFS"), ("DFS", "DFS"), ("MCM", "MCM"),
                    ("03. BFS", "BFS"), ("01. MCM", "MCM"),
                    ("Largest Rectangle in Histogram", "Largest Rectangle in Histogram")]:
        got = bc.clean_title(t)
        check(got == want, f"clean_title keeps {t!r} -> {got!r}")

    # 2. nothing collapses to an empty key
    empties = ["BFS", "DFS", "MCM", "PRINT-N-UP-TRIANGLE", "N Queen", "LIS"]
    bad = [t for t in empties if len(bc.norm_title(bc.clean_title(t))) < bc.MIN_KEY]
    check(not bad, f"no title collapses below the minimum key length ({bad})")

    # 3. punctuation is a separator, not a deletion
    a = bc.norm_title("combination-sum-1")
    b = bc.norm_title("Combination Sum 1")
    check(a == b, f"punctuation normalises ({a!r} == {b!r})")
    check("combination sum" in a, f"words survive normalisation ({a!r})")

    # 4. the noise filter must not eat real problems
    for t in ["Height of binary tree", "Deleting node in linked list",
              "Number of nodes", "Insert node in DLL", "Binary tree representation"]:
        check(not bc.DROP.search(t), f"noise filter keeps the real problem {t!r}")
    for t in ["TreeNode", "README", "main", "utils", "helper"]:
        check(bool(bc.DROP.search(t)), f"noise filter drops {t!r}")

    # 5. directory beats filename when classifying
    #
    # The decisive cases are leaves whose own words name a different topic. A
    # file under "13. Graphs" called "Binary Search Tree Insertion" must stay a
    # graphs problem, because the directory is the authoritative placement on
    # the sheet. Testing only unambiguous leaves would not catch a regression
    # that consults the filename first.
    cases = [
        ("01.Arrays/1.Easy/03.Move_0's_to_end.cpp", "arrays"),
        ("12. Binary Search Trees/08. Build BST from Preorder.cpp", "bst"),
        ("13. Graphs/1. Learning/03. BFS.cpp", "graphs"),
        ("14. Dynamic Programming/2. 1D DP/05. House Robber 2.cpp", "dynamicprogramming"),
        ("08. Sliding Window/3. Hard/1. Sliding Window Maximum.cpp", "slidingwindow"),
        ("11. Binary Trees/1. Traversals/01. Inorder Traversal.cpp", "trees"),
        # ambiguous: the leaf names bst, the directory says graphs
        ("13. Graphs/1.Learning/Binary Search Tree Insertion.cpp", "graphs"),
        # ambiguous: the leaf names arrays, the directory says sliding window
        ("08. Sliding Window/2.Medium/Maximum Subarray.cpp", "slidingwindow"),
        # ambiguous: the leaf names recursion, the directory says arrays
        ("01.Arrays/2.Medium/Backtracking Subsets.cpp", "arrays"),
        # These are real placements on the sheet, where the directory and the
        # filename genuinely disagree. Each one is a regression case: the sheet
        # files "Sliding window maximum" under Stack and Queues, and "Implement
        # stack using linked list" under Stack and Queues too. Consulting the
        # filename first would silently move 74 of the real entries.
        ("07. Stack and Queues/4. Implementation/01. Sliding window maximum.cpp", "stack"),
        ("07. Stack and Queues/1. Learning/05. Implement stack using linked list.cpp", "stack"),
        ("01.Arrays/2.Medium/08.Next_permutation.cpp", "arrays"),
        ("03.Strings/2.Medium/01.Sort_characters_by_frequency.cpp", "strings"),
        ("02. Binary Search/In Search Space/10.Split_array_largest.cpp", "binarysearch"),
    ]
    for path, want in cases:
        got = bc.topic_of(path)
        check(got == want, f"topic_of({path.rsplit('/', 1)[-1]}) -> {got} (want {want})")

    # 6. difficulty comes from the band directory, not the index
    diffs = [
        ("01.Arrays/1.Easy/01.Largest_element_in_array.cpp", "Easy"),
        ("01.Arrays/3.Hard/03.3_sum.cpp", "Hard"),
        ("01.Arrays/2.Medium/05.Maximum_subarray.cpp", "Medium"),
    ]
    for path, want in diffs:
        leaf = bc.clean_title(path.rsplit("/", 1)[-1].rsplit(".", 1)[0])
        got = bc.difficulty_of(path, leaf)
        check(got == want, f"difficulty_of({path.split('/')[1]}) -> {got} (want {want})")

    # 7. the built artifact is coherent
    cat_path = bc.ROOT / "app" / "data" / "catalog.json"
    if not cat_path.exists():
        check(False, "catalog.json exists")
        return 1
    import json
    cat = json.loads(cat_path.read_text())
    problems = cat["problems"]

    check(len(problems) > 400, f"catalog is substantial ({len(problems)} problems)")
    check(len({p["title"] for p in problems}) == len(problems),
          "no duplicate titles in the built catalog")
    check(all(len(p["title"].strip()) >= 3 for p in problems),
          "no truncated titles in the built catalog")

    keys = [bc.norm_title(p["title"]) for p in problems]
    check(len(set(keys)) == len(keys), "dedup keys are unique in the built catalog")

    by_topic = cat["byTopic"]
    check(by_topic.get("graphs", 0) > 40, f"graph section recovered ({by_topic.get('graphs')} problems)")
    check(by_topic.get("dynamicprogramming", 0) > 60,
          f"dp section recovered ({by_topic.get('dynamicprogramming')} problems)")
    check(cat["_meta"]["unmapped"] < 20, f"few unmapped files ({cat['_meta']['unmapped']})")

    diffs = cat["byDifficulty"]
    for band in ("Easy", "Medium", "Hard"):
        check(diffs.get(band, 0) > 50, f"{band} band populated ({diffs.get(band, 0)})")

    # 8. every catalog topic must exist on the spine
    spine = json.loads((cat_path.parent / "spine.json").read_text())
    topic_ids = {t["id"] for t in spine["topics"]}
    unknown = sorted(set(by_topic) - topic_ids)
    check(not unknown, f"every catalog topic exists on the spine ({unknown})")

    print(f"\n{len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())