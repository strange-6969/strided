"""Batch two: Sorting, Recursion, Tries, BST and Divide and Conquer.

Leaves only Learn the Basics and Advanced Trees unauthored after this, which are
the two least valuable to ladder: the first is syntax drills and the second is
advanced data structures that belong to a later stage.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "data" / "problems.json"

NEW_CARDS = [
    {
        "pattern": "sorting",
        "note": (
            "Java's Arrays.sort for primitives is a dual-pivot quicksort; for objects it is a "
            "tim sort, because you asked for stability by using a comparator. C++ std::sort is "
            "introsort: quicksort that falls back to heapsort on bad pivots, so it is never "
            "quadratic. std::stable_sort is mergesort and needs O(n) extra memory."
        ),
        "snippets": {
            "java": "Arrays.sort(arr);                    // primitives: dual-pivot quicksort\narr.sort((a, b) -> a - b);   // objects: tim sort, stable\nArrays.sort(arr, 2, 6);                // range only",
            "python": "nums.sort()                 # in place, tim sort, stable\nsorted(nums)                # returns a new list\nsorted(nums, key=lambda x: x[1], reverse=True)",
            "cpp": "#include <algorithm>\nstd::sort(a.begin(), a.end());              // introsort\nstd::stable_sort(a.begin(), a.end());     // mergesort, needs O(n) memory\nstd::sort(a.begin(), a.end(), greater<int>());  // descending",
        },
    },
    {
        "pattern": "recursion",
        "note": (
            "Every backtracking problem is the same three lines: choose, recurse, undo. "
            "The undo has to happen in the reverse order of the choose, or the next sibling "
            "branch inherits a corrupted state and you chase ghosts."
        ),
        "snippets": {
            "java": "private void backtrack(int[] a, int start, List<Integer> cur, List<List<Integer>> out) {\n  if (cur.size() == a.length) { out.add(new ArrayList<>(cur)); return; }\n  for (int i = start; i < a.length; i++) {\n    cur.add(a[i]);            // choose\n    backtrack(a, i + 1, cur, out);\n    cur.remove(cur.size() - 1); // undo\n  }\n}",
            "python": "def backtrack(path, start):\n    if len(path) == len(a):\n        out.append(path[:]); return\n    for i in range(start, len(a)):\n        path.append(a[i])      # choose\n        backtrack(path, i + 1)\n        path.pop()             # undo",
            "cpp": "void backtrack(vector<int>& cur, int start, vector<vector<int>>& out) {\n  if ((int)cur.size() == (int)a.size()) { out.push_back(cur); return; }\n  for (int i = start; i < (int)a.size(); ++i) {\n    cur.push_back(a[i]);\n    backtrack(cur, i + 1, out);\n    cur.pop_back();\n  }\n}",
        },
    },
    {
        "pattern": "tries",
        "note": (
            "Each node holds a fixed-size array indexed by character value, so lookup is a "
            "single array index per character rather than a hash of the whole prefix. "
            "Reserve 26 children when the input is known to be lowercase letters."
        ),
        "snippets": {
            "java": "class Trie {\n  private final Trie[] kids = new Trie[26];\n  private boolean isWord;\n  public void insert(String word) {\n    Trie node = this;\n    for (char c : word.toCharArray()) {\n      int i = c - 'a';\n      if (node.kids[i] == null) node.kids[i] = new Trie();\n      node = node.kids[i];\n    }\n    node.isWord = true;\n  }\n}",
            "python": "class Trie:\n    def __init__(self):\n        self.kids = {}\n        self.is_word = False\n\n    def insert(self, word):\n        node = self\n        for ch in word:\n            node = node.kids.setdefault(ch, Trie())\n        node.is_word = True",
            "cpp": "struct Trie {\n  Trie* kids[26]{};\n  bool isWord = false;\n  void insert(const string& word) {\n    Trie* node = this;\n    for (char c : word) {\n      int i = c - 'a';\n      if (!node->kids[i]) node->kids[i] = new Trie();\n      node = node->kids[i];\n    }\n    node->isWord = true;\n  }\n};",
        },
    },
    {
        "pattern": "bst",
        "note": (
            "The whole structure follows from one invariant: everything left is smaller, "
            "everything right is larger. Inorder traversal of a BST is therefore sorted, which "
            "is the property most BST problems are really asking you to exploit."
        ),
        "snippets": {
            "java": "// inorder is sorted for a valid BST\nvoid inorder(TreeNode n, List<Integer> out) {\n  if (n == null) return;\n  inorder(n.left, out);\n  out.add(n.val);\n  inorder(n.right, out);\n}\n\n// find floor: largest value <= target\nwhile (node != null) {\n  if (node.val == target) return node.val;\n  if (node.val < target) { ans = node.val; node = node.right; }\n  else node = node.left;\n}",
            "python": "def inorder(node, out):\n    if node is None: return\n    inorder(node.left, out)\n    out.append(node.val)\n    inorder(node.right, out)\n\ndef floor(root, target):\n    ans = None\n    node = root\n    while node:\n        if node.val == target: return node.val\n        if node.val < target:\n            ans = node.val\n            node = node.right\n        else:\n            node = node.left\n    return ans",
            "cpp": "void inorder(TreeNode* n, vector<int>& out) {\n  if (!n) return;\n  inorder(n->left, out);\n  out.push_back(n->val);\n  inorder(n->right, out);\n}\n\nint floor(TreeNode* root, int target) {\n  int ans = INT_MIN;\n  while (root) {\n    if (root->val == target) return root->val;\n    if (root->val < target) { ans = root->val; root = root->right; }\n    else root = root->left;\n  }\n  return ans;\n}",
        },
    },
    {
        "pattern": "divideconquer",
        "note": (
            "Binary search on the answer is the reusable shape: the predicate is monotonic, so "
            "you search the answer space instead of the data. Keep the predicate in its own "
            "function; that separation is the whole technique."
        ),
        "snippets": {
            "java": "// find the smallest x for which can(x) is true\nint lo = 0, hi = upper;\nwhile (lo < hi) {\n  int mid = lo + (hi - lo) / 2;\n  if (can(mid)) hi = mid; else lo = mid + 1;\n}\nreturn lo;",
            "python": "lo, hi = 0, upper\nwhile lo < hi:\n    mid = (lo + hi) // 2\n    if can(mid):\n        hi = mid\n    else:\n        lo = mid + 1\nreturn lo",
            "cpp": "int lo = 0, hi = upper;\nwhile (lo < hi) {\n  int mid = lo + (hi - lo) / 2;\n  if (can(mid)) hi = mid; else lo = mid + 1;\n}\nreturn lo;",
        },
    },
]

NEW_PROBLEMS = [
    # --------------------------------------------------------------- Sorting
    {
        "id": "912",
        "slug": "sort-an-array",
        "title": "Sort an Array",
        "difficulty": "Medium",
        "pattern": "sorting",
        "lists": ["striverSDE"],
        "platform": {
            "leetcode": "sort-an-array",
            "walkccc": "https://walkccc.me/leetcodeproblems/sort-an-array/",
        },
        "statement": "Given an integer array nums, return it sorted in ascending order. You must solve the problem without using any built-in sorting function.",
        "keyIdea": "Quicksort picks a pivot and partitions so that everything on one side is smaller than the pivot. The partition is the actual insight: once values land on the correct side you never have to look at them again.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Selection sort",
                "time": "O(n^2)",
                "space": "O(1)",
                "why": "Repeatedly find the smallest remaining value and swap it into place. Every comparison is used, which makes it instructive, and there are n squared of them regardless of the input, which makes it unusable.",
                "code": {
                    "java": "int[] a = nums.clone();\nfor (int i = 0; i < a.length; i++) {\n  int min = i;\n  for (int j = i + 1; j < a.length; j++) if (a[j] < a[min]) min = j;\n  int t = a[i]; a[i] = a[min]; a[min] = t;\n}\nreturn a;",
                    "python": "a = list(nums)\nfor i in range(len(a)):\n    lo = min(range(i, len(a)), key=lambda k: a[k])\n    a[i], a[lo] = a[lo], a[i]\nreturn a",
                    "cpp": "vector<int> a(nums);\nfor (int i = 0; i < n; ++i) {\n  int lo = i;\n  for (int j = i + 1; j < n; ++j) if (a[j] < a[lo]) lo = j;\n  swap(a[i], a[lo]);\n}\nreturn a;",
                },
            },
            {
                "tier": "better",
                "label": "Merge sort",
                "time": "O(n log n)",
                "space": "O(n)",
                "why": "Halve the array, sort each half, merge them in one linear pass. Guaranteed n log n on every input and stable, at the cost of an auxiliary buffer.",
                "code": {
                    "java": "int[] a = nums.clone(), buf = new int[a.length];\nmergeSort(a, buf, 0, a.length - 1);\nreturn a;\n\nprivate void mergeSort(int[] a, int[] buf, int lo, int hi) {\n  if (lo >= hi) return;\n  int mid = (lo + hi) / 2;\n  mergeSort(a, buf, lo, mid);\n  mergeSort(a, buf, mid + 1, hi);\n  int i = lo, j = mid + 1, k = lo;\n  while (i <= mid && j <= hi) buf[k++] = a[i] <= a[j] ? a[i++] : a[j++];\n  while (i <= mid) buf[k++] = a[i++];\n  while (j <= hi) buf[k++] = a[j++];\n  System.arraycopy(buf, lo, a, lo, hi - lo + 1);\n}",
                    "python": "a = list(nums)\ndef msort(lo, hi):\n    if lo >= hi: return\n    mid = (lo + hi) // 2\n    msort(lo, mid); msort(mid + 1, hi)\n    i, j, k = lo, mid + 1, lo\n    while i <= mid and j <= hi:\n        if a[i] <= a[j]: a[k] = a[i]; i += 1\n        else: a[k] = a[j]; j += 1\n        k += 1\n    while i <= mid: a[k] = a[i]; i += 1; k += 1\n    while j <= hi: a[k] = a[j]; j += 1; k += 1\nmsort(0, len(a) - 1)\nreturn a",
                    "cpp": "void msort(vector<int>& a, vector<int>& buf, int lo, int hi) {\n  if (lo >= hi) return;\n  int mid = (lo + hi) / 2;\n  msort(a, buf, lo, mid); msort(a, buf, mid + 1, hi);\n  int i = lo, j = mid + 1, k = lo;\n  while (i <= mid && j <= hi) buf[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];\n  while (i <= mid) buf[k++] = a[i++];\n  while (j <= hi) buf[k++] = a[j++];\n  for (int x = lo; x <= hi; ++x) a[x] = buf[x];\n}\nvector<int> sortArray(vector<int>& nums) {\n  vector<int> a = nums, buf(a.size());\n  msort(a, buf, 0, (int)a.size() - 1);\n  return a;\n}",
                },
            },
            {
                "tier": "optimal",
                "label": "Quicksort with median-of-three pivot",
                "time": "O(n log n) average",
                "space": "O(log n)",
                "why": "Partition around a pivot chosen as the median of first, middle and last. That single change is what stops the sorted input case, which is exactly the input that makes a naive pivot quadratic. No auxiliary buffer, and the sort happens in place.",
                "code": {
                    "java": "int[] a = nums.clone();\nquickSort(a, 0, a.length - 1);\nreturn a;\n\nprivate void quickSort(int[] a, int lo, int hi) {\n  while (lo < hi) {\n    int p = partition(a, lo, hi);\n    if (p - lo < hi - p) { quickSort(a, lo, p - 1); lo = p + 1; }\n    else { quickSort(a, p + 1, hi); hi = p - 1; }\n  }\n}\n\nprivate int partition(int[] a, int lo, int hi) {\n  int mid = lo + (hi - lo) / 2;\n  int pivot = Math.max(Math.min(a[lo], a[mid]), Math.min(Math.max(a[lo], a[mid]), a[hi]));\n  int i = lo, j = hi;\n  while (i <= j) {\n    while (a[i] < pivot) i++;\n    while (a[j] > pivot) j--;\n    if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n  }\n  return j;\n}",
                    "python": "a = list(nums)\ndef qsort(lo, hi):\n    while lo < hi:\n        mid = (lo + hi) // 2\n        pivot = sorted([a[lo], a[mid], a[hi]])[1]\n        i, j = lo, hi\n        while i <= j:\n            while a[i] < pivot: i += 1\n            while a[j] > pivot: j -= 1\n            if i <= j:\n                a[i], a[j] = a[j], a[i]\n                i += 1; j -= 1\n        # recurse on the smaller side so the stack stays logarithmic\n        if j - lo < hi - i:\n            qsort(lo, j); lo = i\n        else:\n            qsort(i, hi); hi = j\nqsort(0, len(a) - 1)\nreturn a",
                    "cpp": "int partition(vector<int>& a, int lo, int hi) {\n  int mid = lo + (hi - lo) / 2;\n  int pivot = std::max(std::min(a[lo], a[mid]), std::min(std::max(a[lo], a[mid]), a[hi]));\n  int i = lo, j = hi;\n  while (i <= j) {\n    while (a[i] < pivot) ++i;\n    while (a[j] > pivot) --j;\n    if (i <= j) { swap(a[i], a[j]); ++i; --j; }\n  }\n  return j;\n}\nvoid qsort(vector<int>& a, int lo, int hi) {\n  while (lo < hi) {\n    int p = partition(a, lo, hi);\n    if (p - lo < hi - p) { qsort(a, lo, p - 1); lo = p + 1; }\n    else { qsort(a, p + 1, hi); hi = p - 1; }\n  }\n}\nvector<int> sortArray(vector<int>& nums) {\n  vector<int> a = nums;\n  qsort(a, 0, (int)a.size() - 1);\n  return a;\n}",
                },
            },
        ],
        "hints": [
            "What is the one comparison pattern that appears in every n squared sort?",
            "It keeps comparing pairs that cannot both be the answer. Selection sort compares everything against the current minimum even after the minimum is already known.",
            "If you split the array in half and solve both halves, how do you get the whole thing back in order?",
            "Merge them. Both halves are sorted, so one linear pass interleaves them.",
            "Pseudocode for the merge: compare the front elements of both halves, take the smaller, repeat until one half is empty, then append the rest.",
        ],
    },
    # -------------------------------------------------------------- Recursion
    {
        "id": "78",
        "slug": "subsets",
        "title": "Subsets",
        "difficulty": "Medium",
        "pattern": "recursion",
        "lists": ["neetcode150", "striverSDE"],
        "platform": {
            "leetcode": "subsets",
            "neetcode": "https://neetcode.io/problems/subsets",
            "walkccc": "https://walkccc.me/leetcodeproblems/subsets/",
        },
        "statement": "Given an integer array nums of unique elements, return all possible subsets (the power set). The solution must not contain duplicate subsets. Return the subsets in any order.",
        "keyIdea": "Record the current path at every node of the search tree, not only at the leaves. Every prefix is itself a valid subset, so the recursion has no base case that stops early.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Enumerate all masks and test each one",
                "time": "O(n * 2^n)",
                "space": "O(2^n)",
                "why": "Treat the subset as a bitmask, so there are exactly 2 to the n of them and every mask is valid. Thorough and completely ignores the recursive structure that makes this problem teachable.",
                "code": {
                    "java": "List<List<Integer>> out = new ArrayList<>();\nfor (int mask = 0; mask < (1 << nums.length); mask++) {\n  List<Integer> sub = new ArrayList<>();\n  for (int i = 0; i < nums.length; i++) if ((mask & (1 << i)) != 0) sub.add(nums[i]);\n  out.add(sub);\n}\nreturn out;",
                    "python": "out = []\nn = len(nums)\nfor mask in range(1 << n):\n    out.append([nums[i] for i in range(n) if mask & (1 << i)])\nreturn out",
                    "cpp": "vector<vector<int>> out;\nfor (int mask = 0; mask < (1 << n); ++mask) {\n  vector<int> sub;\n  for (int i = 0; i < n; ++i) if (mask & (1 << i)) sub.push_back(a[i]);\n  out.push_back(sub);\n}\nreturn out;",
                },
            },
            {
                "tier": "better",
                "label": "Iterative doubling",
                "time": "O(n * 2^n)",
                "space": "O(2^n)",
                "why": "Start with the empty subset, then for each element add a copy of every subset with that element appended. No recursion, and the doubling structure is visible in the code.",
                "code": {
                    "java": "List<List<Integer>> out = new ArrayList<>();\nout.add(new ArrayList<>());\nfor (int v : nums) {\n  int size = out.size();\n  for (int i = 0; i < size; i++) {\n    List<Integer> copy = new ArrayList<>(out.get(i));\n    copy.add(v);\n    out.add(copy);\n  }\n}\nreturn out;",
                    "python": "out = [[]]\nfor v in nums:\n    out += [sub + [v] for sub in out]\nreturn out",
                    "cpp": "vector<vector<int>> out(1);\nfor (int v : nums) {\n  int size = out.size();\n  for (int i = 0; i < size; ++i) {\n    vector<int> copy = out[i];\n    copy.push_back(v);\n    out.push_back(copy);\n  }\n}\nreturn out;",
                },
            },
            {
                "tier": "optimal",
                "label": "Backtracking, record at every node",
                "time": "O(n * 2^n)",
                "space": "O(n)",
                "why": "Same asymptotics, because you must materialise 2 to the n subsets either way. The win is space: one shared path is mutated in place and copied on the way out, instead of allocating a fresh list per leaf. Recording at entry rather than at the leaf is what makes the empty subset appear without special-casing it.",
                "code": {
                    "java": "List<List<Integer>> out = new ArrayList<>();\nbacktrack(nums, 0, new ArrayList<>(), out);\nreturn out;\n\nprivate void backtrack(int[] a, int start, List<Integer> path, List<List<Integer>> out) {\n  out.add(new ArrayList<>(path));\n  for (int i = start; i < a.length; i++) {\n    path.add(a[i]);\n    backtrack(a, i + 1, path, out);\n    path.remove(path.size() - 1);\n  }\n}",
                    "python": "out, path = [], []\ndef backtrack(start):\n    out.append(path[:])\n    for i in range(start, len(nums)):\n        path.append(nums[i])\n        backtrack(i + 1)\n        path.pop()\nbacktrack(0)\nreturn out",
                    "cpp": "vector<vector<int>> out;\nvector<int> path;\nfunction<void(int)> bt = [&](int start) {\n  out.push_back(path);\n  for (int i = start; i < n; ++i) {\n    path.push_back(a[i]);\n    bt(i + 1);\n    path.pop_back();\n  }\n};\nbt(0);\nreturn out;",
                },
            },
        ],
        "hints": [
            "How many subsets does a set of n distinct elements have?",
            "Two to the n. Every element is either in or out, and that choice is independent for each one.",
            "In a recursive solution, is a subset only complete at the deepest call?",
            "No. Every partial path is already a valid subset, so record the current path at entry rather than at the exit.",
            "Pseudocode: record a copy of the current path. For each remaining element, add it, recurse from the next index, then remove it.",
        ],
    },
    # ------------------------------------------------------------------ Tries
    {
        "id": "208",
        "slug": "implement-trie-prefix-tree",
        "title": "Implement Trie (Prefix Tree)",
        "difficulty": "Medium",
        "pattern": "tries",
        "lists": ["neetcode150", "striverSDE"],
        "platform": {
            "leetcode": "implement-trie-prefix-tree",
            "neetcode": "https://neetcode.io/problems/implement-trie-prefix-tree",
            "walkccc": "https://walkccc.me/leetcodeproblems/implement-trie-prefix-tree/",
        },
        "statement": "Implement a trie with insert, search and startsWith. Each node represents a single character and holds links to its children, with a flag marking the end of a word.",
        "keyIdea": "A trie stores prefixes as shared path prefixes rather than whole strings. The word 'car' and 'cat' share the nodes for 'c' and 'a', so a prefix query walks the shared path and stops.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Store words in a list and scan",
                "time": "O(n * m) insert, O(n * m) search",
                "space": "O(n * m)",
                "why": "Keep every inserted word and check startsWith against each one with string comparison. Correct, and it re-reads the shared prefix on every single lookup, which is exactly the duplication a trie exists to remove.",
                "code": {
                    "java": "class Trie {\n  private final List<String> words = new ArrayList<>();\n  public void insert(String w) { words.add(w); }\n  public boolean search(String w) { return words.contains(w); }\n  public boolean startsWith(String p) {\n    for (String w : words) if (w.startsWith(p)) return true;\n    return false;\n  }\n}",
                    "python": "class Trie:\n    def __init__(self): self.words = []\n    def insert(self, w): self.words.append(w)\n    def search(self, w): return w in self.words\n    def startsWith(self, p): return any(w.startswith(p) for w in self.words)",
                    "cpp": "class Trie {\n  std::vector<std::string> words;\n public:\n  void insert(const std::string& w) { words.push_back(w); }\n  bool search(const std::string& w) {\n    return std::find(words.begin(), words.end(), w) != words.end();\n  }\n  bool startsWith(const std::string& p) {\n    for (auto& w : words) if (w.rfind(p, 0) == 0) return true;\n    return false;\n  }\n};",
                },
            },
            {
                "tier": "better",
                "label": "Nested hash maps",
                "time": "O(m) insert, O(m) search",
                "space": "O(n * m)",
                "why": "Each node is a dictionary from character to child node, which keeps the shared-prefix structure while avoiding the fixed alphabet array. Lookup is one hash per character.",
                "code": {
                    "java": "class Trie {\n  private final Map<Character, Trie> kids = new HashMap<>();\n  private boolean isWord;\n  public void insert(String w) {\n    Trie node = this;\n    for (char c : w.toCharArray()) {\n      Trie next = node.kids.get(c);\n      if (next == null) { next = new Trie(); node.kids.put(c, next); }\n      node = next;\n    }\n    node.isWord = true;\n  }\n  public boolean search(String w) {\n    Trie n = walk(w);\n    return n != null && n.isWord;\n  }\n  public boolean startsWith(String p) { return walk(p) != null; }\n  private Trie walk(String s) {\n    Trie node = this;\n    for (char c : s.toCharArray()) {\n      node = node.kids.get(c);\n      if (node == null) return null;\n    }\n    return node;\n  }\n}",
                    "python": "class Trie:\n    def __init__(self):\n        self.kids = {}\n        self.is_word = False\n\n    def _walk(self, s):\n        node = self\n        for ch in s:\n            if ch not in node.kids: return None\n            node = node.kids[ch]\n        return node\n\n    def insert(self, w):\n        node = self\n        for ch in w:\n            node = node.kids.setdefault(ch, Trie())\n        node.is_word = True\n\n    def search(self, w):\n        node = self._walk(w)\n        return node is not None and node.is_word\n\n    def startsWith(self, p):\n        return self._walk(p) is not None",
                    "cpp": "class Trie {\n  std::map<char, Trie*> kids;\n  bool isWord = false;\n public:\n  ~Trie() { for (auto& kv : kids) delete kv.second; }\n  void insert(const std::string& w) {\n    Trie* node = this;\n    for (char c : w) {\n      if (!node->kids.count(c)) node->kids[c] = new Trie();\n      node = node->kids[c];\n    }\n    node->isWord = true;\n  }\n  Trie* walk(const std::string& s) {\n    Trie* node = this;\n    for (char c : s) {\n      if (!node->kids.count(c)) return nullptr;\n      node = node->kids[c];\n    }\n    return node;\n  }\n  bool search(const std::string& w) { Trie* n = walk(w); return n && n->isWord; }\n  bool startsWith(const std::string& p) { return walk(p) != nullptr; }\n};",
                },
            },
            {
                "tier": "optimal",
                "label": "Fixed alphabet array per node",
                "time": "O(m) insert, O(m) search",
                "space": "O(n * sigma)",
                "why": "Same linear behaviour, but a child is a direct array index rather than a hash lookup, so each character costs one bounds check and one load. For a known alphabet that is measurably faster, at the price of allocating 26 slots for nodes that hold far fewer.",
                "code": {
                    "java": "class Trie {\n  private final Trie[] kids = new Trie[26];\n  private boolean isWord;\n  public void insert(String w) {\n    Trie node = this;\n    for (char c : w.toCharArray()) {\n      int i = c - 'a';\n      if (node.kids[i] == null) node.kids[i] = new Trie();\n      node = node.kids[i];\n    }\n    node.isWord = true;\n  }\n  public boolean search(String w) {\n    Trie n = walk(w);\n    return n != null && n.isWord;\n  }\n  public boolean startsWith(String p) { return walk(p) != null; }\n  private Trie walk(String s) {\n    Trie node = this;\n    for (char c : s.toCharArray()) {\n      node = node.kids[c - 'a'];\n      if (node == null) return null;\n    }\n    return node;\n  }\n}",
                    "python": "class Trie:\n    def __init__(self):\n        self.kids = [None] * 26\n        self.is_word = False\n\n    def _walk(self, s):\n        node = self\n        for ch in s:\n            node = node.kids[ord(ch) - ord('a')]\n            if node is None: return None\n        return node\n\n    def insert(self, w):\n        node = self\n        for ch in w:\n            i = ord(ch) - ord('a')\n            if node.kids[i] is None: node.kids[i] = Trie()\n            node = node.kids[i]\n        node.is_word = True\n\n    def search(self, w):\n        node = self._walk(w)\n        return node is not None and node.is_word\n\n    def startsWith(self, p):\n        return self._walk(p) is not None",
                    "cpp": "class Trie {\n  Trie* kids[26]{};\n  bool isWord = false;\n public:\n  ~Trie() { for (auto* k : kids) delete k; }\n  void insert(const std::string& w) {\n    Trie* node = this;\n    for (char c : w) {\n      int i = c - 'a';\n      if (!node->kids[i]) node->kids[i] = new Trie();\n      node = node->kids[i];\n    }\n    node->isWord = true;\n  }\n  Trie* walk(const std::string& s) {\n    Trie* node = this;\n    for (char c : s) {\n      node = node->kids[c - 'a'];\n      if (!node) return nullptr;\n    }\n    return node;\n  }\n  bool search(const std::string& w) { Trie* n = walk(w); return n && n->isWord; }\n  bool startsWith(const std::string& p) { return walk(p) != nullptr; }\n};",
                },
            },
        ],
        "hints": [
            "What do two words with a common prefix have in common that you could store once?",
            "The path of nodes spelling that prefix. Every word through 'car' shares the same nodes for 'c', 'a' and 'r'.",
            "What does a single trie node need to hold?",
            "Links to its children, and a flag saying whether a word ends exactly here. That flag is what separates a prefix from a complete word.",
            "Pseudocode: for each character, follow or create the child for it, then set a flag marking the final node as a word end.",
        ],
    },
    # -------------------------------------------------------------------- BST
    {
        "id": "700",
        "slug": "search-in-a-binary-search-tree",
        "title": "Search in a Binary Search Tree",
        "difficulty": "Easy",
        "pattern": "bst",
        "lists": ["striverSDE"],
        "platform": {
            "leetcode": "search-in-a-binary-search-tree",
            "walkccc": "https://walkccc.me/leetcodeproblems/search-in-a-binary-search-tree/",
        },
        "statement": "Given the root node of a binary search tree and a target integer, return the node where the target is found, or null if it is not present. A BST has the property that all values in the left subtree are smaller and all values in the right subtree are larger.",
        "keyIdea": "The ordering invariant tells you which side can possibly contain the target, so you never visit the other subtree. That halves the search space at every step.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Recursive search of both subtrees",
                "time": "O(n)",
                "space": "O(h)",
                "why": "Walk both subtrees looking for the value. It works, and it makes no use of the BST property, so on a balanced tree it visits nodes a logarithmic search would have skipped.",
                "code": {
                    "java": "public TreeNode searchBST(TreeNode root, int val) {\n  if (root == null) return null;\n  if (root.val == val) return root;\n  TreeNode left = searchBST(root.left, val);\n  return left != null ? left : searchBST(root.right, val);\n}",
                    "python": "def search_bst(root, val):\n    if root is None: return None\n    if root.val == val: return root\n    left = search_bst(root.left, val)\n    return left if left is not None else search_bst(root.right, val)",
                    "cpp": "TreeNode* searchBST(TreeNode* root, int val) {\n  if (!root) return nullptr;\n  if (root->val == val) return root;\n  TreeNode* l = searchBST(root->left, val);\n  return l ? l : searchBST(root->right, val);\n}",
                },
            },
            {
                "tier": "better",
                "label": "Recursive, use the ordering invariant",
                "time": "O(h)",
                "space": "O(h)",
                "why": "Only recurse into the subtree that can hold the target. The tree height h bounds the work, which on a balanced tree is logarithmic.",
                "code": {
                    "java": "public TreeNode searchBST(TreeNode root, int val) {\n  if (root == null) return null;\n  if (val < root.val) return searchBST(root.left, val);\n  if (val > root.val) return searchBST(root.right, val);\n  return root;\n}",
                    "python": "def search_bst(root, val):\n    if root is None: return None\n    if val < root.val: return search_bst(root.left, val)\n    if val > root.val: return search_bst(root.right, val)\n    return root",
                    "cpp": "TreeNode* searchBST(TreeNode* root, int val) {\n  if (!root) return nullptr;\n  if (val < root->val) return searchBST(root->left, val);\n  if (val > root->val) return searchBST(root->right, val);\n  return root;\n}",
                },
            },
            {
                "tier": "optimal",
                "label": "Iterative descent",
                "time": "O(h)",
                "space": "O(1)",
                "why": "The same halving, but as a loop with one cursor, so no stack frames are pushed. Removes the recursion depth limit, which is the only reason to prefer this over the recursive form.",
                "code": {
                    "java": "TreeNode cur = root;\nwhile (cur != null) {\n  if (val == cur.val) return cur;\n  if (val < cur.val) cur = cur.left; else cur = cur.right;\n}\nreturn null;",
                    "python": "cur = root\nwhile cur:\n    if val == cur.val: return cur\n    if val < cur.val: cur = cur.left\n    else: cur = cur.right\nreturn None",
                    "cpp": "TreeNode* cur = root;\nwhile (cur) {\n  if (val == cur->val) return cur;\n  if (val < cur->val) cur = cur->left; else cur = cur->right;\n}\nreturn nullptr;",
                },
            },
        ],
        "hints": [
            "What does the BST invariant tell you about which subtree can contain a value smaller than the root?",
            "Only the left one. So the right subtree can be skipped entirely rather than searched and found wanting.",
            "Compare the target against the current node, then which direction do you move?",
            "Left when the target is smaller, right when it is larger, and stop when they are equal.",
            "Pseudocode: while the node exists, if it matches return it, otherwise step left or right according to the comparison.",
        ],
    },
    # ------------------------------------------------- Divide and conquer
    {
        "id": "875",
        "slug": "koko-eating-bananas",
        "title": "Koko Eating Bananas",
        "difficulty": "Medium",
        "pattern": "divideconquer",
        "lists": ["striverSDE"],
        "platform": {
            "leetcode": "koko-eating-bananas",
            "walkccc": "https://walkccc.me/leetcodeproblems/koko-eating-bananas/",
        },
        "statement": "Koko can eat a pile of bananas in one hour if the pile has at most x bananas. She can choose any eating speed x, and eats at the same rate. Given piles, find the minimum x such that Koko can finish all piles within h hours.",
        "keyIdea": "The predicate 'can Koko finish at speed x' is monotonic: if she can finish at speed x, she can finish at any higher speed. So binary search over the answer space, not over the piles.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Try every speed from 1 upward",
                "time": "O(p * m)",
                "space": "O(1)",
                "why": "Test each candidate speed and take the first that works. Linear in the maximum pile, which for large piles means testing hundreds of thousands of speeds one at a time.",
                "code": {
                    "java": "for (int speed = 1; speed <= max; speed++) {\n  long hours = 0;\n  for (int pile : piles) hours += (pile + speed - 1) / speed;\n  if (hours <= h) return speed;\n}\nreturn max;",
                    "python": "for speed in range(1, max(piles) + 1):\n    hours = sum((p + speed - 1) // speed for p in piles)\n    if hours <= h:\n        return speed\nreturn max(piles)",
                    "cpp": "for (int speed = 1; speed <= mx; ++speed) {\n  long long hours = 0;\n  for (int p : piles) hours += (p + speed - 1) / speed;\n  if (hours <= h) return speed;\n}\nreturn mx;",
                },
            },
            {
                "tier": "better",
                "label": "Binary search the answer with a separate predicate",
                "time": "O(p log m)",
                "space": "O(1)",
                "why": "Extract the feasibility test into its own function and binary search the smallest speed that passes. The monotonicity guarantees no passing speed is skipped, because speed up the pile times only ever decrease.",
                "code": {
                    "java": "int lo = 1, hi = max;\nwhile (lo < hi) {\n  int mid = lo + (hi - lo) / 2;\n  if (canFinish(piles, mid, h)) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n\nprivate boolean canFinish(int[] piles, int speed, int h) {\n  long hours = 0;\n  for (int p : piles) {\n    hours += (p + speed - 1) / speed;\n    if (hours > h) return false;\n  }\n  return true;\n}",
                    "python": "def can_finish(speed):\n    hours = 0\n    for p in piles:\n        hours += (p + speed - 1) // speed\n        if hours > h: return False\n    return True\n\nlo, hi = 1, max(piles)\nwhile lo < hi:\n    mid = (lo + hi) // 2\n    if can_finish(mid): hi = mid\n    else: lo = mid + 1\nreturn lo",
                    "cpp": "auto canFinish = [&](int speed) {\n  long long hours = 0;\n  for (int p : piles) {\n    hours += (p + speed - 1) / speed;\n    if (hours > h) return false;\n  }\n  return true;\n};\nint lo = 1, hi = mx;\nwhile (lo < hi) {\n  int mid = lo + (hi - lo) / 2;\n  if (canFinish(mid)) hi = mid; else lo = mid + 1;\n}\nreturn lo;",
                },
            },
            {
                "tier": "optimal",
                "label": "Binary search with early exit in the predicate",
                "time": "O(p log m)",
                "space": "O(1)",
                "why": "Same asymptotics, but the predicate bails out the moment accumulated hours exceed the budget. On a failing candidate that often saves most of the scan, and because the predicate is checked more often than the binary search steps, that saving dominates in practice.",
                "code": {
                    "java": "int lo = 1, hi = max;\nwhile (lo < hi) {\n  int mid = lo + (hi - lo) / 2;\n  long hours = 0;\n  boolean ok = true;\n  for (int p : piles) {\n    hours += (p + mid - 1) / mid;\n    if (hours > h) { ok = false; break; }\n  }\n  if (ok) hi = mid; else lo = mid + 1;\n}\nreturn lo;",
                    "python": "lo, hi = 1, max(piles)\nwhile lo < hi:\n    mid = (lo + hi) // 2\n    hours = 0\n    for p in piles:\n        hours += (p + mid - 1) // mid\n        if hours > h: break\n    else:\n        hi = mid\n        continue\n    lo = mid + 1\nreturn lo",
                    "cpp": "int lo = 1, hi = mx;\nwhile (lo < hi) {\n  int mid = lo + (hi - lo) / 2;\n  long long hours = 0;\n  bool ok = true;\n  for (int p : piles) {\n    hours += (p + mid - 1) / mid;\n    if (hours > h) { ok = false; break; }\n  }\n  if (ok) hi = mid; else lo = mid + 1;\n}\nreturn lo;",
                },
            },
        ],
        "hints": [
            "If Koko can finish at speed x, what can she say about speed x plus one?",
            "She can certainly finish at x plus one too. Faster speed never increases the hours needed, so the predicate is monotonic.",
            "What does a monotonic predicate over a numeric range invite?",
            "A binary search for the smallest value that passes. You are searching the answer, not the data.",
            "Pseudocode: lo starts at 1, hi at the largest pile. Take the midpoint, test feasibility, and on success move hi down to it, otherwise move lo up past it.",
        ],
    },
]


def main():
    data = json.loads(DATA.read_text())

    # register any pattern these problems introduce but the dataset lacks
    have = {p["id"] for p in data["patterns"]}
    new_patterns = {
        "sorting": {"id": "sorting", "name": "Sorting Techniques",
                    "blurb": "Insertion, selection, bubble, merge and quick sort.",
                    "drill": "A naive pivot makes quicksort quadratic on already sorted input. What single choice of pivot removes that worst case?"},
        "recursion": {"id": "recursion", "name": "Recursion and Backtracking",
                      "blurb": "Subsets, combinations, permutations, grid search.",
                      "drill": "Every backtracking problem is choose, recurse, undo. What breaks if you forget the third step?"},
        "tries": {"id": "tries", "name": "Tries",
                  "blurb": "Prefix search and counting across a key space.",
                  "drill": "What does one trie node need to store to tell a complete word apart from a mere prefix?"},
        "bst": {"id": "bst", "name": "Binary Search Trees",
                "blurb": "Inorder ordering, insert, delete, floor and ceil.",
                "drill": "Inorder traversal of a valid BST is sorted. Which problems does that single fact let you solve without recursion?"},
        "divideconquer": {"id": "divideconquer", "name": "Divide and Conquer",
                          "blurb": "Binary search on answer, median, inversion count.",
                          "drill": "Your predicate is monotonic. Why does that let you search the answer instead of enumerating candidates?"},
    }
    for pid, meta in new_patterns.items():
        if pid not in have:
            data["patterns"].append(meta)
            have.add(pid)

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
    print("total patterns:", len(data["patterns"]))


if __name__ == "__main__":
    main()