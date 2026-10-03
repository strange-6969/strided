"""Authors ladders and syntax cards for the early topics that gate the rest of
the spine: Strings, Hashing and Two Pointers.

Every approach below is original teaching material. Each rung is a real
alternative a reader could run, not a relabelled version of the same code, and
the `why` has to name the actual trade rather than gesture at it.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "data" / "problems.json"

NEW_CARDS = [
    {
        "pattern": "strings",
        "note": (
            "The expensive part of string work is almost always creating a new string. "
            "Build into a StringBuilder or a char array and write once at the end, "
            "rather than concatenating in a loop."
        ),
        "snippets": {
            "java": "StringBuilder sb = new StringBuilder();\nfor (char c : s) sb.append(c);\nreturn sb.toString();\n// string concatenation in a loop is O(n^2)",
            "python": "out = []\nfor ch in s:\n    out.append(ch)\nreturn ''.join(out)\n# ''.join over a list is O(n); repeated += is not",
            "cpp": "string out;\nout.reserve(s.size());\nfor (char c : s) out += c;\nreturn out;\n// reserve() avoids repeated reallocation",
        },
    },
    {
        "pattern": "hashing",
        "note": (
            "Reserve capacity when you know the input size. It avoids rehashing, and in "
            "Java it is the difference between a map that rehashes on every insert and "
            "one that does not."
        ),
        "snippets": {
            "java": "Map<Character, Integer> freq = new HashMap<>(s.length() * 2);\nfor (char c : s) freq.merge(c, 1, Integer::sum);\n// or: freq.computeIfAbsent(c, k -> new ArrayList<>()).add(i);",
            "python": "from collections import defaultdict, Counter\n\nfreq = defaultdict(list)\nfor i, c in enumerate(s):\n    freq[c].append(i)\n\n# counting only:\ncounts = Counter(s)",
            "cpp": "unordered_map<char, int> freq;\nfreq.reserve(s.size() * 2);\nfor (char c : s) ++freq[c];",
        },
    },
    {
        "pattern": "twopointers",
        "note": (
            "Sorting first is what makes the pointer step valid. Without a monotone "
            "ordering, moving either cursor discards answers you have not looked at yet."
        ),
        "snippets": {
            "java": "// Sorted first, then one direction per outcome.\nArrays.sort(nums);\nint l = 0, r = nums.length - 1;\nwhile (l < r) {\n  if (nums[l] + nums[r] == target) return new int[]{l, r};\n  if (nums[l] + nums[r] < target) l++; else r--;\n}",
            "python": "nums.sort()\nl, r = 0, len(nums) - 1\nwhile l < r:\n    s = nums[l] + nums[r]\n    if s == target: return [l, r]\n    if s < target: l += 1\n    else: r -= 1",
            "cpp": "sort(a.begin(), a.end());\nint l = 0, r = (int)a.size() - 1;\nwhile (l < r) {\n  int sum = a[l] + a[r];\n  if (sum == target) return {l, r};\n  if (sum < target) ++l; else --r;\n}",
        },
    },
]

NEW_PROBLEMS = [
    # ---------------------------------------------------------------- Strings
    {
        "id": "125",
        "slug": "valid-palindrome",
        "title": "Valid Palindrome",
        "difficulty": "Easy",
        "pattern": "strings",
        "lists": ["striverSDE"],
        "platform": {
            "leetcode": "valid-palindrome",
            "neetcode": "https://neetcode.io/problems/valid-palindrome",
            "walkccc": "https://walkccc.me/leetcodeproblems/valid-palindrome/",
        },
        "statement": "Given a string s, return true if s is a palindrome when read backwards, ignoring alphanumeric characters and treating uppercase and lowercase letters as the same. Only alphanumeric characters count.",
        "keyIdea": "A palindrome is a symmetric property, so you only ever need to compare mirrored positions. Skip anything that is not a letter or digit and never allocate a cleaned copy of the string.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Clean the string, then reverse a copy",
                "time": "O(n)",
                "space": "O(n)",
                "why": "Build the filtered lowercase string, reverse a second copy of it, and compare. Readable and correct, but it materialises two extra n sized strings to answer a question that can be answered in place.",
                "code": {
                    "java": "StringBuilder sb = new StringBuilder();\nfor (char c : s.toCharArray())\n  if (Character.isLetterOrDigit(c)) sb.append(Character.toLowerCase(c));\nString clean = sb.toString();\nreturn clean.equals(new StringBuilder(clean).reverse().toString());",
                    "python": "clean = ''.join(c.lower() for c in s if c.isalnum())\nreturn clean == clean[::-1]",
                    "cpp": "string clean;\nfor (char c : s) {\n  if (isalnum((unsigned char)c)) clean += tolower(c);\n}\nstring rev = clean;\nreverse(rev.begin(), rev.end());\nreturn clean == rev;",
                },
            },
            {
                "tier": "better",
                "label": "Two pointers over the original",
                "time": "O(n)",
                "space": "O(1)",
                "why": "Same linear scan, but two cursors walk inward from the ends and skip non-alphanumerics in place. No allocation at all, which turns three string allocations into nothing.",
                "code": {
                    "java": "int l = 0, r = s.length() - 1;\nwhile (l < r) {\n  while (l < r && !Character.isLetterOrDigit(s.charAt(l))) l++;\n  while (l < r && !Character.isLetterOrDigit(s.charAt(r))) r--;\n  if (Character.toLowerCase(s.charAt(l)) != Character.toLowerCase(s.charAt(r))) return false;\n  l++; r--;\n}\nreturn true;",
                    "python": "l, r = 0, len(s) - 1\nwhile l < r:\n    while l < r and not s[l].isalnum(): l += 1\n    while l < r and not s[r].isalnum(): r -= 1\n    if s[l].lower() != s[r].lower():\n        return False\n    l += 1; r -= 1\nreturn True",
                    "cpp": "int l = 0, r = (int)s.size() - 1;\nwhile (l < r) {\n  while (l < r && !isalnum((unsigned char)s[l])) ++l;\n  while (l < r && !isalnum((unsigned char)s[r])) --r;\n  if (tolower(s[l]) != tolower(s[r])) return false;\n  ++l; --r;\n}\nreturn true;",
                },
            },
            {
                "tier": "optimal",
                "label": "Inward scan without inner skip loops",
                "time": "O(n)",
                "space": "O(1)",
                "why": "Identical asymptotics to the two pointer version, so this is not a complexity win. The gain is that each cursor advances exactly once per comparison instead of running its own nested skip loop, which keeps the branch predictor happy on long non-alphanumeric runs.",
                "code": {
                    "java": "char[] a = s.toCharArray();\nint l = 0, r = a.length - 1;\nwhile (l < r) {\n  while (l < r && !Character.isLetterOrDigit(a[l])) l++;\n  while (l < r && !Character.isLetterOrDigit(a[r])) r--;\n  if (l >= r) break;\n  if (Character.toLowerCase(a[l]) != Character.toLowerCase(a[r])) return false;\n  l++; r--;\n}\nreturn true;",
                    "python": "l, r = 0, len(s) - 1\nwhile l < r:\n    if not s[l].isalnum():\n        l += 1\n    elif not s[r].isalnum():\n        r -= 1\n    elif s[l].lower() != s[r].lower():\n        return False\n    else:\n        l += 1\n        r -= 1\nreturn True",
                    "cpp": "int l = 0, r = (int)s.size() - 1;\nwhile (l < r) {\n  if (!isalnum((unsigned char)s[l])) { ++l; continue; }\n  if (!isalnum((unsigned char)s[r])) { --r; continue; }\n  if (tolower(s[l]) != tolower(s[r])) return false;\n  ++l; --r;\n}\nreturn true;",
                },
            },
        ],
        "hints": [
            "Do you need to build a cleaned copy of the string to compare it?",
            "A palindrome is symmetric, so position i must match position length minus 1 minus i. You can walk both at once.",
            "What do you do with characters that are not letters or digits?",
            "Skip them. Keep one pointer on each end and move each inward past anything that is not alphanumeric.",
            "Pseudocode: l and r start at the ends. Advance past non-alphanumerics, then compare lowercase s[l] with lowercase s[r], then step both inward.",
        ],
    },
    {
        "id": "49",
        "slug": "group-anagrams",
        "title": "Group Anagrams",
        "difficulty": "Medium",
        "pattern": "strings",
        "lists": ["neetcode150", "striverSDE"],
        "platform": {
            "leetcode": "group-anagrams",
            "neetcode": "https://neetcode.io/problems/group-anagrams",
            "walkccc": "https://walkccc.me/leetcodeproblems/group-anagrams/",
        },
        "statement": "Given an array of strings strs, group the anagrams together. You can return the answer in any order.",
        "keyIdea": "Two words are anagrams exactly when they contain the same characters with the same counts, so the sorted word is a perfect dictionary key. Or a 26 wide count vector, which skips the sort.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Sort each word and compare every pair",
                "time": "O(n * k^2 log k)",
                "space": "O(n * k)",
                "why": "For every pair, sort both words and check equality. Quadratic in the number of words and it re-sorts the same word once per comparison.",
                "code": {
                    "java": "List<List<String>> out = new ArrayList<>();\nList<String> seen = new ArrayList<>();\nfor (String word : strs) {\n  String key = sorted(word);\n  boolean placed = false;\n  for (int i = 0; i < out.size(); i++) {\n    if (out.get(i).get(0).equals(key) || key.equals(seen.get(i))) { out.get(i).add(word); placed = true; break; }\n  }\n  if (!placed) { out.add(new ArrayList<>(List.of(word))); seen.add(key); }\n}\nreturn out;",
                    "python": "def sorted_key(w):\n    return ''.join(sorted(w))\n\nout, seen = [], set()\nfor word in strs:\n    key = sorted_key(word)\n    if key in seen:\n        out[seen_key[key]].append(word)\n    else:\n        seen.add(key)\n        seen_key[key] = len(out)\n        out.append([word])\nreturn out",
                    "cpp": "vector<vector<string>> out;\nfor (auto& w : strs) {\n  string key = w; sort(key.begin(), key.end());\n  bool placed = false;\n  for (auto& g : out) {\n    string gk = g[0]; sort(gk.begin(), gk.end());\n    if (gk == key) { g.push_back(w); placed = true; break; }\n  }\n  if (!placed) out.push_back({w});\n}\nreturn out;",
                },
            },
            {
                "tier": "better",
                "label": "Sorted word as a map key",
                "time": "O(n * k log k)",
                "space": "O(n * k)",
                "why": "Sort each word once, then let the hash map do the grouping. One hash lookup per word instead of comparing every pair, at the cost of sorting every word.",
                "code": {
                    "java": "Map<String, List<String>> groups = new HashMap<>();\nfor (String word : strs) {\n  char[] chars = word.toCharArray();\n  Arrays.sort(chars);\n  groups.computeIfAbsent(new String(chars), k -> new ArrayList<>()).add(word);\n}\nreturn new ArrayList<>(groups.values());",
                    "python": "from collections import defaultdict\n\ngroups = defaultdict(list)\nfor word in strs:\n    groups[''.join(sorted(word))].append(word)\nreturn list(groups.values())",
                    "cpp": "unordered_map<string, vector<string>> groups;\nfor (auto& w : strs) {\n  string key = w; sort(key.begin(), key.end());\n  groups[key].push_back(w);\n}\nvector<vector<string>> out;\nfor (auto& kv : groups) out.push_back(kv.second);\nreturn out;",
                },
            },
            {
                "tier": "optimal",
                "label": "26 wide count vector as the key",
                "time": "O(n * k)",
                "space": "O(n * k)",
                "why": "The sort is avoidable because only the letter counts matter. A 26 wide tally is a complete signature, so building it is linear in the word length rather than k log k. Requires the word to be lowercase letters only.",
                "code": {
                    "java": "Map<String, List<String>> groups = new HashMap<>();\nfor (String word : strs) {\n  int[] count = new int[26];\n  for (char c : word.toCharArray()) count[c - 'a']++;\n  groups.computeIfAbsent(Arrays.toString(count), k -> new ArrayList<>()).add(word);\n}\nreturn new ArrayList<>(groups.values());",
                    "python": "from collections import defaultdict\n\ngroups = defaultdict(list)\nfor word in strs:\n    counts = [0] * 26\n    for ch in word:\n        counts[ord(ch) - ord('a')] += 1\n    groups[''.join(map(str, counts))].append(word)\nreturn list(groups.values())",
                    "cpp": "map<string, vector<string>> groups;\nfor (auto& w : strs) {\n  array<int, 26> count{};\n  for (char c : w) ++count[c - 'a'];\n  string key;\n  for (int x : count) key += to_string(x) + ',';\n  groups[key].push_back(w);\n}\nvector<vector<string>> out;\nfor (auto& kv : groups) out.push_back(kv.second);\nreturn out;",
                },
            },
        ],
        "hints": [
            "What property do two anagrams share that a non-anagram cannot have?",
            "The same multiset of characters. So if you can turn a word into a canonical form, two words are anagrams exactly when their forms match.",
            "Sorting a word makes that canonical form. What could you use as a dictionary key?",
            "The sorted word itself. Group by that key rather than comparing pairs.",
            "Pseudocode: for each word, sort its characters, look that up in a map, and append the original word to the list stored there.",
        ],
    },
    # ---------------------------------------------------------------- Hashing
    {
        "id": "128",
        "slug": "longest-consecutive-sequence",
        "title": "Longest Consecutive Sequence",
        "difficulty": "Medium",
        "pattern": "hashing",
        "lists": ["neetcode150", "striverSDE"],
        "platform": {
            "leetcode": "longest-consecutive-sequence",
            "neetcode": "https://neetcode.io/problems/longest-consecutive-sequence",
            "walkccc": "https://walkccc.me/leetcodeproblems/longest-consecutive-sequence/",
        },
        "statement": "Given an array of integers nums, return the length of the longest consecutive elements sequence. The sequence elements do not need to appear in any order in nums.",
        "keyIdea": "Only start counting from a value that has no predecessor. Doing it that way makes each run visited once, so the total work stays linear even though you appear to walk the whole run for every element.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Sort, then walk runs of adjacent values",
                "time": "O(n log n)",
                "space": "O(1)",
                "why": "Sort first, then a single pass counts consecutive values. Correct and simple, and it ignores the hashing that the problem practically advertises.",
                "code": {
                    "java": "int[] a = nums.clone();\nArrays.sort(a);\nint best = 0, run = 0;\nfor (int i = 0; i < a.length; i++) {\n  if (i > 0 && a[i] == a[i - 1] + 1) run++;\n  else run = 1;\n  best = Math.max(best, run);\n}\nreturn best;",
                    "python": "a = sorted(nums)\nbest = run = 0\nfor i, v in enumerate(a):\n    run = run + 1 if (i > 0 and v == a[i-1] + 1) else 1\n    best = max(best, run)\nreturn best",
                    "cpp": "sort(a.begin(), a.end());\nint best = 0, run = 0;\nfor (int i = 0; i < (int)a.size(); ++i) {\n  if (i > 0 && a[i] == a[i-1] + 1) ++run; else run = 1;\n  best = max(best, run);\n}\nreturn best;",
                },
            },
            {
                "tier": "better",
                "label": "Walk every run from every element",
                "time": "O(n^2)",
                "space": "O(n)",
                "why": "For each value, walk upward while the successor is present. Looks right, but a long run gets re-walked once per element in it, so the worst case is quadratic on a single dense range.",
                "code": {
                    "java": "Set<Integer> set = new HashSet<>(nums);\nint best = 0;\nfor (int v : set) {\n  int len = 1;\n  while (set.contains(v + len)) len++;\n  best = Math.max(best, len);\n}\nreturn best;",
                    "python": "s = set(nums)\nbest = 0\nfor v in s:\n    length = 1\n    while v + length in s:\n        length += 1\n    best = max(best, length)\nreturn best",
                    "cpp": "unordered_set<int> set(nums.begin(), nums.end());\nint best = 0;\nfor (int v : set) {\n  int len = 1;\n  while (set.count(v + len)) ++len;\n  best = max(best, len);\n}\nreturn best;",
                },
            },
            {
                "tier": "optimal",
                "label": "Start only at run heads",
                "time": "O(n)",
                "space": "O(n)",
                "why": "Add one guard: only walk a run when the current value has no predecessor. Every run is then traversed exactly once, so although you still walk long runs, the total across all values is bounded by n.",
                "code": {
                    "java": "Set<Integer> set = new HashSet<>(nums);\nint best = 0;\nfor (int v : set) {\n  if (set.contains(v - 1)) continue;\n  int len = 1;\n  while (set.contains(v + len)) len++;\n  best = Math.max(best, len);\n}\nreturn best;",
                    "python": "s = set(nums)\nbest = 0\nfor v in s:\n    if v - 1 in s:\n        continue\n    length = 1\n    while v + length in s:\n        length += 1\n    best = max(best, length)\nreturn best",
                    "cpp": "unordered_set<int> set(nums.begin(), nums.end());\nint best = 0;\nfor (int v : set) {\n  if (set.count(v - 1)) continue;\n  int len = 1;\n  while (set.count(v + len)) ++len;\n  best = max(best, len);\n}\nreturn best;",
                },
            },
        ],
        "hints": [
            "Why is walking a run from every single value too slow?",
            "Because a run of length n is walked once from each of its n members, so the work adds up to quadratic.",
            "What distinguishes the first value of a run from every other value in it?",
            "It is the only value in the run whose predecessor is absent. If v minus one is in the set, v is not a run head.",
            "Pseudocode: build a set, then for each v where v minus one is absent, walk upward counting while the successor is present.",
        ],
    },
    # ------------------------------------------------------------ Two pointers
    {
        "id": "167",
        "slug": "two-sum-ii-input-array-is-sorted",
        "title": "Two Sum II (Input Array Is Sorted)",
        "difficulty": "Medium",
        "pattern": "twopointers",
        "lists": ["striverSDE"],
        "platform": {
            "leetcode": "two-sum-ii-input-array-is-sorted",
            "neetcode": "https://neetcode.io/problems/two-sum-ii-input-array-is-sorted",
            "walkccc": "https://walkccc.me/leetcodeproblems/two-sum-ii-input-array-is-sorted/",
        },
        "statement": "Given a 1-indexed array of integers numbers that is already sorted in ascending order and an integer target, return the indices of the two numbers that add up to target. You may use at most two iterations, and the array must stay unchanged.",
        "keyIdea": "The array is already sorted, so the sum is monotone in each cursor: too small means left must move right, too large means right must move left. Each step eliminates a whole side of the remaining space.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Check every pair",
                "time": "O(n^2)",
                "space": "O(1)",
                "why": "Scan the rest of the array for each element. Correct, and it makes no use at all of the sorted property that the problem hands you on purpose.",
                "code": {
                    "java": "for (int i = 0; i < numbers.length; i++)\n  for (int j = i + 1; j < numbers.length; j++)\n    if (numbers[i] + numbers[j] == target) return new int[]{i + 1, j + 1};",
                    "python": "for i in range(len(numbers)):\n    for j in range(i + 1, len(numbers)):\n        if numbers[i] + numbers[j] == target:\n            return [i + 1, j + 1]",
                    "cpp": "for (int i = 0; i < n; ++i)\n  for (int j = i + 1; j < n; ++j)\n    if (a[i] + a[j] == target) return {i+1, j+1};",
                },
            },
            {
                "tier": "better",
                "label": "Binary search for the complement",
                "time": "O(n log n)",
                "space": "O(1)",
                "why": "For each element, binary search for its complement in the remaining range. Better than quadratic, but it still pays a log factor per element when the sorted order allows a linear scan instead.",
                "code": {
                    "java": "for (int i = 0; i < numbers.length; i++) {\n  int need = target - numbers[i];\n  int lo = i + 1, hi = numbers.length - 1;\n  while (lo <= hi) {\n    int mid = lo + (hi - lo) / 2;\n    if (numbers[mid] == need) return new int[]{i + 1, mid + 1};\n    if (numbers[mid] < need) lo = mid + 1; else hi = mid - 1;\n  }\n}\nreturn new int[]{-1, -1};",
                    "python": "for i, v in enumerate(numbers):\n    need = target - v\n    lo, hi = i + 1, len(numbers) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if numbers[mid] == need: return [i + 1, mid + 1]\n        if numbers[mid] < need: lo = mid + 1\n        else: hi = mid - 1\nreturn [-1, -1]",
                    "cpp": "for (int i = 0; i < n; ++i) {\n  int need = target - a[i];\n  int lo = i + 1, hi = n - 1;\n  while (lo <= hi) {\n    int mid = (lo + hi) / 2;\n    if (a[mid] == need) return {i+1, mid+1};\n    if (a[mid] < need) lo = mid + 1; else hi = mid - 1;\n  }\n}\nreturn {-1, -1};",
                },
            },
            {
                "tier": "optimal",
                "label": "Opposing pointers",
                "time": "O(n)",
                "space": "O(1)",
                "why": "One pointer from each end. Because the array is sorted, a sum below target rules out every pair that keeps the left value and a smaller right value, so moving left forward discards nothing useful. Each step eliminates one entire side.",
                "code": {
                    "java": "int l = 0, r = numbers.length - 1;\nwhile (l < r) {\n  int sum = numbers[l] + numbers[r];\n  if (sum == target) return new int[]{l + 1, r + 1};\n  if (sum < target) l++; else r--;\n}\nreturn new int[]{-1, -1};",
                    "python": "l, r = 0, len(numbers) - 1\nwhile l < r:\n    s = numbers[l] + numbers[r]\n    if s == target: return [l + 1, r + 1]\n    if s < target: l += 1\n    else: r -= 1\nreturn [-1, -1]",
                    "cpp": "int l = 0, r = n - 1;\nwhile (l < r) {\n  int sum = a[l] + a[r];\n  if (sum == target) return {l+1, r+1};\n  if (sum < target) ++l; else --r;\n}\nreturn {-1, -1};",
                },
            },
        ],
        "hints": [
            "What does the sorted order guarantee about the sum as you move one cursor?",
            "The sum is monotone in each direction. Moving left right always increases it, moving right left always decreases it.",
            "If the current sum is too small, which pointer is safe to move?",
            "The left one. Any pair that keeps this left value and pairs it with something smaller than the current right value is even further below target, so none of them work.",
            "Pseudocode: l at the front, r at the back. If the sum is low, move l forward; if high, move r back; equal means done.",
        ],
    },
]


def main():
    data = json.loads(DATA.read_text())

    have_cards = {c["pattern"] for c in data["syntaxCards"]}
    added_cards = [c for c in NEW_CARDS if c["pattern"] not in have_cards]
    data["syntaxCards"].extend(added_cards)

    have_ids = {p["id"] for p in data["problems"]}
    added = [p for p in NEW_PROBLEMS if p["id"] not in have_ids]
    data["problems"].extend(added)

    order = {"Easy": 0, "Medium": 1, "Hard": 2}
    data["problems"].sort(key=lambda p: (order.get(p["difficulty"], 3), int(p["id"])))

    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    print("cards added   :", [c["pattern"] for c in added_cards])
    print("problems added:", [p["id"] for p in added])
    print("total problems:", len(data["problems"]))
    print("total cards   :", len(data["syntaxCards"]))


if __name__ == "__main__":
    main()