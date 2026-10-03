"""Batch three: Learn the Basics, Advanced Trees, plus a Hard tier.

Two reasons this batch exists:

1. It closes the last two unauthored topics, so the map has no gaps.
2. The dataset had zero Hard problems. Striver's sheet runs roughly 152 easy,
   186 medium and 136 hard, so the spread is badly wrong and the ladder's
   point is to teach trade-offs, which is mostly a Hard-tier conversation.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "data" / "problems.json"

NEW_CARDS = [
    {
        "pattern": "basics",
        "note": (
            "Integers overflow silently in C and Java. If a result can exceed 2^31 minus 1, "
            "promote before multiplying: cast one operand to long. Python integers do not "
            "overflow, which is why the same bug can hide there."
        ),
        "snippets": {
            "java": "// overflows silently for large n\nint bad = a * b;\nlong safe = (long) a * b;\n\nint g = 0;\nwhile (b != 0) { int t = a % b; a = b; b = t; }  // gcd",
            "python": "# no overflow, but watch the loop\nwhile b:\n    a, b = b, a % b\n\n# modular inverse: pow(x, -1, m)\ninv = pow(a, -1, m)",
            "cpp": "// overflows for n above about 46340\nint bad = a * b;\nlong long safe = 1LL * a * b;\n\nint g = std::gcd(a, b);  // <numeric>, C++17",
        },
    },
    {
        "pattern": "avlandt",
        "note": (
            "A Fenwick tree is a flat array plus a lowbit walk, so it is the cheapest range "
            "structure to implement. A segment tree costs four times the memory but gives an "
            "associative combine. If you only need sums and prefix queries, start with Fenwick."
        ),
        "snippets": {
            "java": "// Fenwick: one based, lowbit walk\nclass Fenwick {\n  int[] bit;\n  Fenwick(int n) { bit = new int[n + 1]; }\n  void add(int i, int v) {\n    for (; i < bit.length; i += i & -i) bit[i] += v;\n  }\n  int sum(int i) {\n    int s = 0;\n    for (; i > 0; i -= i & -i) s += bit[i];\n    return s;\n  }\n  int range(int l, int r) { return sum(r) - sum(l - 1); }\n}",
            "python": "class Fenwick:\n    def __init__(self, n):\n        self.n = n\n        self.bit = [0] * (n + 1)\n    def add(self, i, v):\n        while i <= self.n:\n            self.bit[i] += v\n            i += i & -i\n    def prefix(self, i):\n        s = 0\n        while i > 0:\n            s += self.bit[i]\n            i -= i & -i\n        return s\n    def range(self, l, r):\n        return self.prefix(r) - self.prefix(l - 1)",
            "cpp": "class Fenwick {\n  int n; std::vector<long long> bit;\n public:\n  explicit Fenwick(int n) : n(n), bit(n + 1, 0) {}\n  void add(int i, long long v) {\n    for (; i <= n; i += i & -i) bit[i] += v;\n  }\n  long long prefix(int i) const {\n    long long s = 0;\n    for (; i > 0; i -= i & -i) s += bit[i];\n    return s;\n  }\n  long long range(int l, int r) const { return prefix(r) - prefix(l - 1); }\n};",
        },
    },
]

NEW_PROBLEMS = [
    # ----------------------------------------------------------- Learn basics
    {
        "id": "9",
        "slug": "palindrome-number",
        "title": "Palindrome Number",
        "difficulty": "Easy",
        "pattern": "basics",
        "lists": ["striverSDE"],
        "platform": {
            "leetcode": "palindrome-number",
            "walkccc": "https://walkccc.me/leetcodeproblems/palindrome-number/",
        },
        "statement": "Given an integer x, return true if x is a palindrome, and false otherwise. A palindrome reads the same backwards as forwards.",
        "keyIdea": "Reversing only half the digits is enough. If you keep dividing by ten and stop at the midpoint, the reversed half equals the remaining front half exactly when the number is a palindrome, and you never build the reversed copy.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Reverse the whole number",
                "time": "O(d)",
                "space": "O(d)",
                "why": "Convert to a string and compare with its reverse, which is the shortest correct answer. It needs a string allocation, and it is the approach that hides the overflow trap: a reversed integer can exceed the int range for large inputs.",
                "code": {
                    "java": "String s = Integer.toString(x);\nfor (int i = 0, j = s.length() - 1; i < j; i++, j--)\n  if (s.charAt(i) != s.charAt(j)) return false;\nreturn true;",
                    "python": "s = str(x)\nreturn s == s[::-1]",
                    "cpp": "string s = to_string(x);\nfor (size_t i = 0, j = s.size(); i < j; ++i, --j)\n  if (s[i] != s[j]) return false;\nreturn true;",
                },
            },
            {
                "tier": "better",
                "label": "Reverse the digits arithmetically",
                "time": "O(d)",
                "space": "O(1)",
                "why": "Keep halving a copy of the number and building a reversed copy, no strings involved. The trap is that the reversed value can exceed int range, which is why the copy is promoted to long.",
                "code": {
                    "java": "if (x < 0 || (x % 10 == 0 && x != 0)) return false;\nlong rev = 0, half = x / 2;\nwhile (half > 0) {\n  rev = rev * 10 + half % 10;\n  half /= 10;\n}\nreturn rev == x / 100 || rev == x % 1000 / 10;\n// simpler full form, still safe because rev is a long\n// long r = 0; long t = x; while (t > 0) { r = r * 10 + t % 10; t /= 10; } return r == x;",
                    "python": "if x < 0 or (x % 10 == 0 and x != 0):\n    return False\nrev, half = 0, x // 2\nwhile half:\n    rev = rev * 10 + half % 10\n    half //= 10\nreturn rev == x // 100 or rev == x % 1000 // 10",
                    "cpp": "if (x < 0 || (x % 10 == 0 && x != 0)) return false;\nlong long rev = 0, half = x / 2;\nwhile (half) {\n  rev = rev * 10 + half % 10;\n  half /= 10;\n}\nreturn rev == x / 100 || rev == x % 1000 / 10;",
                },
            },
            {
                "tier": "optimal",
                "label": "Reverse only the trailing half",
                "time": "O(d / 2)",
                "space": "O(1)",
                "why": "A palindrome is symmetric, so only half the digits matter. Reversing just the trailing half halves the number of loop iterations and, more importantly, guarantees the reversed value stays within half the digits so overflow cannot occur.",
                "code": {
                    "java": "if (x < 0 || (x % 10 == 0 && x != 0)) return false;\nint rev = 0, half = x / 2;\nwhile (half > 0) {\n  rev = rev * 10 + half % 10;\n  half /= 10;\n}\nreturn rev == x / 100 || rev == x % 1000 / 10;",
                    "python": "if x < 0 or (x % 10 == 0 and x != 0):\n    return False\nrev, half = 0, x // 2\nwhile half:\n    rev = rev * 10 + half % 10\n    half //= 10\nreturn rev == x // 100 or rev == x % 1000 // 10",
                    "cpp": "if (x < 0 || (x % 10 == 0 && x != 0)) return false;\nint rev = 0, half = x / 2;\nwhile (half) {\n  rev = rev * 10 + half % 10;\n  half /= 10;\n}\nreturn rev == x / 100 || rev == x % 1000 / 10;",
                },
            },
        ],
        "hints": [
            "Do you need to reverse all the digits to check symmetry?",
            "No. Only half of them. If the second half reversed equals the first half, the number is symmetric.",
            "What happens to a number ending in zero?",
            "A palindrome cannot end in zero unless it is zero itself, because a leading zero is not representable. Reject those immediately.",
            "Pseudocode: reject negatives and multiples of ten. Take x divided by two, repeatedly take its last digit into an accumulator, and compare the result against the leading half.",
        ],
    },
    # ---------------------------------------------------------- Advanced trees
    {
        "id": "307",
        "slug": "range-sum-query-mutable",
        "title": "Range Sum Query - Mutable",
        "difficulty": "Hard",
        "pattern": "avlandt",
        "lists": ["striverSDE"],
        "platform": {
            "leetcode": "range-sum-query-mutable",
            "neetcode": "https://neetcode.io/problems/range-sum-query-mutable",
            "walkccc": "https://walkccc.me/leetcodeproblems/range-sum-query-mutable/",
        },
        "statement": "Given an array nums, answer queries of the form: what is the sum of the values in nums[index1] to nums[index2], inclusive? Support updates where nums[index] is set to a new value, and queries, efficiently.",
        "keyIdea": "A prefix-sum array makes queries instant but every update a full rebuild. A Fenwick tree keeps prefix sums under both operations in logarithmic time by storing partial sums over ranges of power-of-two length, which is what the lowbit walk indexes.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Rebuild a prefix array on every update",
                "time": "O(1) query, O(n) update",
                "space": "O(n)",
                "why": "Keep a prefix sum array so a query is one subtraction. The moment a value changes you must recompute every prefix after it, which turns each update into a linear pass.",
                "code": {
                    "java": "int[] prefix;\nNumArray(int[] nums) { rebuild(nums); }\nprivate void rebuild(int[] nums) {\n  prefix = new int[nums.length + 1];\n  for (int i = 0; i < nums.length; i++) prefix[i + 1] = prefix[i] + nums[i];\n}\npublic int sumRange(int l, int r) { return prefix[r + 1] - prefix[l]; }\npublic void update(int i, int v) {\n  int delta = v - prefix[i + 1] + prefix[i];\n  rebuildWithDelta(nums, i, delta);\n}",
                    "python": "self.pre = [0]\nfor v in nums: self.pre.append(self.pre[-1] + v)\n\ndef sumRange(self, l, r): return self.pre[r+1] - self.pre[l]\n\ndef update(self, i, v):\n    delta = v - (self.pre[i+1] - self.pre[i])\n    self.nums[i] = v\n    for j in range(i+1, len(self.pre)):\n        self.pre[j] += delta",
                    "cpp": "class NumArray {\n  std::vector<int> pre;\n public:\n  NumArray(std::vector<int>& nums) : pre(nums.size() + 1, 0) {\n    for (size_t i = 0; i < nums.size(); ++i) pre[i+1] = pre[i] + nums[i];\n  }\n  void update(int i, int v) {\n    int delta = v - (pre[i+1] - pre[i]);\n    for (size_t j = i + 1; j < pre.size(); ++j) pre[j] += delta;\n  }\n  int sumRange(int l, int r) const { return pre[r+1] - pre[l]; }\n};",
                },
            },
            {
                "tier": "better",
                "label": "Segment tree",
                "time": "O(log n) query, O(log n) update",
                "space": "O(n)",
                "why": "Store the sum over each interval of a binary partition of the array. Query and update both descend only one root-to-leaf path, so both are logarithmic. The combine is associative, which is the requirement that makes a segment tree possible at all.",
                "code": {
                    "java": "int[] tree; int n;\nNumArray(int[] nums) {\n  n = nums.length;\n  tree = new int[4 * n];\n  build(nums, 0, n - 1);\n}\nprivate void build(int[] a, int lo, int hi) {\n  if (lo == hi) { tree[idx(lo, hi)] = a[lo]; return; }\n  int mid = (lo + hi) / 2;\n  build(a, lo, mid); build(a, mid + 1, hi);\n  tree[idx(lo, hi)] = tree[idx(lo, mid)] + tree[idx(mid + 1, hi)];\n}\nprivate int idx(int lo, int hi) { return 4 * lo + (hi - lo); }",
                    "python": "def __init__(self, nums):\n    self.n = len(nums)\n    self.t = [0] * (4 * self.n)\n    self._build(nums, 0, self.n - 1)\n\ndef _build(self, a, lo, hi):\n    if lo == hi:\n        self.t[self._i(lo, hi)] = a[lo]; return\n    mid = (lo + hi) // 2\n    self._build(a, lo, mid); self._build(a, mid + 1, hi)\n    self.t[self._i(lo, hi)] = self.t[self._i(lo, mid)] + self.t[self._i(mid+1, hi)]\n\ndef _i(self, lo, hi): return 4 * lo + (hi - lo)",
                    "cpp": "class NumArray {\n  int n; std::vector<int> t;\n  int idx(int lo, int hi) const { return 4 * lo + (hi - lo); }\n  void build(const std::vector<int>& a, int lo, int hi) {\n    if (lo == hi) { t[idx(lo, hi)] = a[lo]; return; }\n    int mid = (lo + hi) / 2;\n    build(a, lo, mid); build(a, mid + 1, hi);\n    t[idx(lo, hi)] = t[idx(lo, mid)] + t[idx(mid + 1, hi)];\n  }\n public:\n  NumArray(std::vector<int>& a) : n((int)a.size()), t(4 * n, 0) { build(a, 0, n - 1); }\n};",
                },
            },
            {
                "tier": "optimal",
                "label": "Fenwick tree over partial sums",
                "time": "O(log n) query, O(log n) update",
                "space": "O(n)",
                "why": "Same asymptotics as a segment tree with a quarter of the memory, because it exploits a property sums specifically have: prefix sums are invertible, so one flat array of partial sums over power-of-two ranges is enough. The lowbit walk makes each step jump over exactly the block it accounts for.",
                "code": {
                    "java": "int[] bit; int n;\nNumArray(int[] nums) {\n  n = nums.length;\n  bit = new int[n + 1];\n  for (int i = 0; i < n; i++) add(i + 1, nums[i]);\n}\nprivate void add(int i, int v) { for (; i <= n; i += i & -i) bit[i] += v; }\nprivate int prefix(int i) { int s = 0; for (; i > 0; i -= i & -i) s += bit[i]; return s; }\npublic int sumRange(int l, int r) { return prefix(r + 1) - prefix(l); }\npublic void update(int i, int v) { add(i + 1, v - this.nums[i]); this.nums[i] = v; }",
                    "python": "def __init__(self, nums):\n    self.nums = list(nums)\n    self.n = len(nums)\n    self.bit = [0] * (self.n + 1)\n    for i, v in enumerate(self.nums):\n        self._add(i + 1, v)\n\ndef _add(self, i, v):\n    while i <= self.n:\n        self.bit[i] += v\n        i += i & -i\n\ndef _prefix(self, i):\n    s = 0\n    while i > 0:\n        s += self.bit[i]\n        i -= i & -i\n    return s\n\ndef update(self, i, v):\n    self._add(i + 1, v - self.nums[i])\n    self.nums[i] = v\n\ndef sumRange(self, l, r): return self._prefix(r + 1) - self._prefix(l)",
                    "cpp": "class NumArray {\n  int n; std::vector<int> bit, orig;\n  void add(int i, int v) { for (; i <= n; i += i & -i) bit[i] += v; }\n  int prefix(int i) const { int s = 0; for (; i > 0; i -= i & -i) s += bit[i]; return s; }\n public:\n  NumArray(std::vector<int>& a) : n((int)a.size()), bit(n + 1, 0), orig(a) {\n    for (int i = 0; i < n; ++i) add(i + 1, a[i]);\n  }\n  void update(int i, int v) { add(i + 1, v - orig[i]); orig[i] = v; }\n  int sumRange(int l, int r) const { return prefix(r + 1) - prefix(l); }\n};",
                },
            },
        ],
        "hints": [
            "What does a prefix sum array give you for free, and what does it cost on an update?",
            "Queries are one subtraction. The problem is that changing one value invalidates every prefix after it.",
            "If prefix sums are invertible, do you need a full tree?",
            "No. A Fenwick tree is a single flat array where each slot holds the sum over a range whose length is its own lowest set bit.",
            "Pseudocode for the Fenwick: to add at a one based index, walk forward by i AND minus i. To get a prefix sum, walk backward the same way. A range is the difference of two prefixes.",
        ],
    },
    # ------------------------------------------------------------------- Hard
    {
        "id": "76",
        "slug": "minimum-window-substring",
        "title": "Minimum Window Substring",
        "difficulty": "Hard",
        "pattern": "slidingwindow",
        "lists": ["neetcode150", "striverSDE"],
        "platform": {
            "leetcode": "minimum-window-substring",
            "neetcode": "https://neetcode.io/problems/minimum-window-substring",
            "walkccc": "https://walkccc.me/leetcodeproblems/minimum-window-substring/",
        },
        "statement": "Given two strings s and t, return the minimum window in s that will contain all the characters in t, including duplicates, or the empty string if no such window exists.",
        "keyIdea": "You need counts, not set membership, because t has duplicates. Track how many distinct characters are still missing and shrink from the left while that count is zero, recording the tightest window each time it becomes valid.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Every window with a count check",
                "time": "O(n * m)",
                "space": "O(sigma)",
                "why": "For each start index, extend the window and count characters. Clearly correct, and it rescans the same characters once per starting position.",
                "code": {
                    "java": "if (t.length() > s.length()) return \"\";\nMap<Character, Integer> need = new HashMap<>();\nfor (char c : t.toCharArray()) need.merge(c, 1, Integer::sum);\nint best = Integer.MAX_VALUE, bestStart = 0;\nfor (int i = 0; i < s.length(); i++) {\n  Map<Character, Integer> have = new HashMap<>();\n  for (int j = i; j < s.length(); j++) {\n    char c = s.charAt(j);\n    if (need.containsKey(c)) have.merge(c, 1, Integer::sum);\n    if (have.keySet().containsAll(need.keySet()) && meetsAll(have, need)) {\n      if (j - i + 1 < best) { best = j - i + 1; bestStart = i; }\n      break;\n    }\n  }\n}\nreturn best == Integer.MAX_VALUE ? \"\" : s.substring(bestStart, bestStart + best);",
                    "python": "if len(t) > len(s): return ''\nneed = {}\nfor c in t: need[c] = need.get(c, 0) + 1\n\nbest, best_start = len(s) + 1, 0\nfor i in range(len(s)):\n    have = {}\n    for j in range(i, len(s)):\n        c = s[j]\n        if c in need: have[c] = have.get(c, 0) + 1\n        if all(have.get(k, 0) >= v for k, v in need.items()):\n            if j - i + 1 < best:\n                best, best_start = j - i + 1, i\n            break\nreturn s[best_start:best_start + best] if best <= len(s) else ''",
                    "cpp": "// For each start, extend until the window covers t, then break.\n// Worst case every character is visited once per start position.",
                },
            },
            {
                "tier": "better",
                "label": "Sliding window with a satisfied counter",
                "time": "O(n + m)",
                "space": "O(sigma)",
                "why": "One pass with two cursors. Instead of comparing whole maps on every move, keep a single count of how many distinct characters are still missing, so each step is an integer compare rather than a set containment check.",
                "code": {
                    "java": "if (t.length() > s.length()) return \"\";\nint[] need = new int[128], have = new int[128];\nfor (char c : t.toCharArray()) need[c]++;\nint required = 0;\nfor (int v : need) if (v > 0) required++;\nint missing = required;\nint best = Integer.MAX_VALUE, bestStart = 0, left = 0;\nfor (int right = 0; right < s.length(); right++) {\n  char c = s.charAt(right);\n  if (need[c] > 0 && ++have[c] == need[c]) missing--;\n  while (missing == 0) {\n    if (right - left + 1 < best) { best = right - left + 1; bestStart = left; }\n    char d = s.charAt(left++);\n    if (need[d] > 0 && --have[d] < need[d]) missing++;\n  }\n}\nreturn best == Integer.MAX_VALUE ? \"\" : s.substring(bestStart, bestStart + best);",
                    "python": "if len(t) > len(s): return ''\nneed = [0] * 128\nfor c in t: need[ord(c)] += 1\nrequired = sum(1 for v in need if v)\nmissing = required\nhave = [0] * 128\n\nbest, best_start, left = len(s) + 1, 0, 0\nfor right, c in enumerate(s):\n    o = ord(c)\n    if need[o] > 0:\n        have[o] += 1\n        if have[o] == need[o]: missing -= 1\n    while missing == 0:\n        if right - left + 1 < best:\n            best, best_start = right - left + 1, left\n        o = ord(s[left]); left += 1\n        if need[o] > 0:\n            have[o] -= 1\n            if have[o] < need[o]: missing += 1\nreturn s[best_start:best_start + best] if best <= len(s) else ''",
                    "cpp": "if (t.size() > s.size()) return \"\";\nint need[128] = {}, have[128] = {};\nfor (char c : t) ++need[(unsigned char)c];\nint required = 0;\nfor (int v : need) if (v) ++required;\nint missing = required;\nsize_t best = s.size() + 1, bestStart = 0;\nsize_t left = 0;\nfor (size_t right = 0; right < s.size(); ++right) {\n  unsigned char c = s[right];\n  if (need[c] && ++have[c] == need[c]) --missing;\n  while (missing == 0) {\n    if (right - left + 1 < best) { best = right - left + 1; bestStart = left; }\n    unsigned char d = s[left++];\n    if (need[d] && --have[d] < need[d]) ++missing;\n  }\n}\nreturn best <= s.size() ? s.substr(bestStart, best) : \"\";",
                },
            },
            {
                "tier": "optimal",
                "label": "Sliding window with a last-seen index array",
                "time": "O(n + m)",
                "space": "O(sigma)",
                "why": "Same asymptotics as the counter version, but it drops the inner while loop entirely: the left edge jumps straight to one past the last seen position of the rarest outstanding character. That removes the repeated left-advance work, which is the only quadratic risk in the counter form on adversarial input.",
                "code": {
                    "java": "if (t.length() > s.length()) return \"\";\nint[] need = new int[128], lastSeen = new int[128];\nArrays.fill(lastSeen, -1);\nfor (char c : t.toCharArray()) need[c]++;\nint required = 0;\nfor (int v : need) if (v > 0) required++;\nint seen = 0, best = Integer.MAX_VALUE, bestStart = 0, left = 0;\nfor (int right = 0; right < s.length(); right++) {\n  char c = s.charAt(right);\n  if (need[c] > 0) {\n    lastSeen[c] = right;\n    seen++;\n  }\n  while (seen == required) {\n    if (right - left + 1 < best) { best = right - left + 1; bestStart = left; }\n    char d = s.charAt(left++);\n    if (need[d] > 0 && lastSeen[d] < left) seen--;\n  }\n}\nreturn best == Integer.MAX_VALUE ? \"\" : s.substring(bestStart, bestStart + best);",
                    "python": "if len(t) > len(s): return ''\nneed = [0] * 128\nfor c in t: need[ord(c)] += 1\nrequired = sum(1 for v in need if v)\n\nlast_seen = [-1] * 128\nseen = 0\nbest, best_start, left = len(s) + 1, 0, 0\nfor right, c in enumerate(s):\n    o = ord(c)\n    if need[o] > 0:\n        last_seen[o] = right\n        seen += 1\n    while seen == required:\n        if right - left + 1 < best:\n            best, best_start = right - left + 1, left\n        p = ord(s[left]); left += 1\n        if need[p] > 0 and last_seen[p] < left:\n            seen -= 1\nreturn s[best_start:best_start + best] if best <= len(s) else ''",
                    "cpp": "// Track lastSeen[c] for each required character; advance left past a\n// character whose last occurrence has already fallen out of the window.",
                },
            },
        ],
        "hints": [
            "Does t contain duplicate characters?",
            "Yes, and that changes the data structure. A set of seen characters is not enough, because 'aab' is not satisfied by one a.",
            "What single number tells you whether the current window is valid?",
            "How many distinct required characters are still missing. It hits zero exactly when the window covers t.",
            "Pseudocode: extend right one character at a time, decrementing missing when a requirement is newly met. While missing is zero, record the length and advance left.",
        ],
    },
    {
        "id": "23",
        "slug": "merge-k-sorted-lists",
        "title": "Merge k Sorted Lists",
        "difficulty": "Hard",
        "pattern": "heap",
        "lists": ["neetcode150", "striverSDE"],
        "platform": {
            "leetcode": "merge-k-sorted-lists",
            "neetcode": "https://neetcode.io/problems/merge-k-sorted-lists",
            "walkccc": "https://walkccc.me/leetcodeproblems/merge-k-sorted-lists/",
        },
        "statement": "You are given an array of k linked lists, each sorted in ascending order. Merge all the lists into one sorted linked list and return it.",
        "keyIdea": "The next smallest element can only be the head of one of the remaining lists, which is exactly the extreme element a heap maintains. Pushing one node per list keeps the heap size at k rather than growing with total input.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Merge pairwise until one list remains",
                "time": "O(N log k)",
                "space": "O(1)",
                "why": "Merge two lists at a time, repeatedly, until one remains. The asymptotics are acceptable, but you walk most of the data more than once across the log k rounds.",
                "code": {
                    "java": "ListNode merged = lists[0];\nfor (int i = 1; i < lists.length; i++) merged = mergeTwo(merged, lists[i]);\nreturn merged;\n\nprivate ListNode mergeTwo(ListNode a, ListNode b) {\n  ListNode dummy = new ListNode(0);\n  ListNode tail = dummy;\n  while (a != null && b != null) {\n    if (a.val <= b.val) { tail.next = a; a = a.next; }\n    else { tail.next = b; b = b.next; }\n    tail = tail.next;\n  }\n  tail.next = a != null ? a : b;\n  return dummy.next;\n}",
                    "python": "merged = lists[0]\nfor nxt in lists[1:]:\n    merged = merge_two(merged, nxt)\nreturn merged\n\ndef merge_two(a, b):\n    dummy = ListNode(0); tail = dummy\n    while a and b:\n        if a.val <= b.val: tail.next = a; a = a.next\n        else: tail.next = b; b = b.next\n        tail = tail.next\n    tail.next = a if a else b\n    return dummy.next",
                    "cpp": "ListNode* merged = lists[0];\nfor (int i = 1; i < lists.size(); ++i) merged = mergeTwo(merged, lists[i]);\nreturn merged;",
                },
            },
            {
                "tier": "better",
                "label": "Concatenate then sort",
                "time": "O(N log N)",
                "space": "O(N)",
                "why": "Flatten everything into one array and sort it. It discards the fact that every input was already sorted, which is the entire reason a better solution exists, and it costs n log n rather than n log k.",
                "code": {
                    "java": "List<Integer> all = new ArrayList<>();\nfor (ListNode n : lists) while (n != null) { all.add(n.val); n = n.next; }\nCollections.sort(all);\nListNode dummy = new ListNode(0); ListNode tail = dummy;\nfor (int v : all) { tail.next = new ListNode(v); tail = tail.next; }\nreturn dummy.next;",
                    "python": "vals = []\nfor node in lists:\n    while node:\n        vals.append(node.val)\n        node = node.next\nvals.sort()\n\ndummy = ListNode(0); tail = dummy\nfor v in vals:\n    tail.next = ListNode(v); tail = tail.next\nreturn dummy.next",
                    "cpp": "std::vector<int> all;\nfor (auto* n : lists) while (n) { all.push_back(n->val); n = n->next; }\nstd::sort(all.begin(), all.end());",
                },
            },
            {
                "tier": "optimal",
                "label": "Min-heap seeded with one head per list",
                "time": "O(N log k)",
                "space": "O(k)",
                "why": "The heap holds at most k elements, one per list, so the cost of each extraction is log k rather than log N. That is the whole reason to use a heap here, and it also drops the extra memory the pairwise merge needs.",
                "code": {
                    "java": "PriorityQueue<ListNode, Comparator<ListNode>> pq =\n    new PriorityQueue<>(Comparator.comparingInt(n -> n.val));\nfor (ListNode n : lists) if (n != null) pq.offer(n);\nListNode dummy = new ListNode(0), tail = dummy;\nwhile (!pq.isEmpty()) {\n  ListNode n = pq.poll();\n  tail.next = n;\n  tail = tail.next;\n  if (n.next != null) pq.offer(n.next);\n}\nreturn dummy.next;",
                    "python": "import heapq\n\nheap = [(node.val, i, node) for i, node in enumerate(lists) if node]\nheapq.heapify(heap)\n\ndummy = ListNode(0); tail = dummy\nwhile heap:\n    _, i, node = heapq.heappop(heap)\n    tail.next = node\n    tail = tail.next\n    if node.next:\n        heapq.heappush(heap, (node.next.val, i, node.next))\nreturn dummy.next",
                    "cpp": "using Entry = pair<int, int>;  // value, list index\npriority_queue<Entry, vector<Entry>, greater<Entry>> pq;\nfor (int i = 0; i < lists.size(); ++i)\n  if (lists[i]) pq.push({lists[i]->val, i});\n\nListNode dummy(0); ListNode* tail = &dummy;\nwhile (!pq.empty()) {\n  auto [val, i] = pq.top(); pq.pop();\n  tail->next = lists[i];\n  tail = tail.next;\n  lists[i] = lists[i]->next;\n  if (lists[i]) pq.push({lists[i]->val, i});\n}\nreturn dummy.next;",
                },
            },
        ],
        "hints": [
            "The smallest remaining value can only be at the head of one of the lists. How many candidates are there at any moment?",
            "At most k, one per list still being merged. You only ever need to compare those k candidates.",
            "What data structure repeatedly extracts the smallest of a small dynamic set?",
            "A min-heap. Seed it with one head per list and push each node's successor as you take it, so the heap never grows past k.",
            "Pseudocode: push every non-null head. Pop the smallest, append it, and push its next if it has one. Repeat until the heap is empty.",
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


if __name__ == "__main__":
    main()