"""Adds seven hand-authored problems and two syntax cards to the Strided dataset.

Every approach is original teaching material: brute first, then a genuinely
intermediate strategy, then the optimal one, each labelled with its time and
space cost plus a note on why the trade was worth making.
"""

import json
import pathlib

DATA = pathlib.Path("/home/strange/Projects/strided/app/data/problems.json")

NEW_SYNTAX_CARDS = [
    {
        "pattern": "linkedlist",
        "note": "There is no index, so every operation needs a saved pointer. When you remove or reverse a node, capture next before you overwrite it.",
        "snippets": {
            "java": "ListNode prev = null, cur = head;\nwhile (cur != null) {\n  ListNode next = cur.next;\n  cur.next = prev;\n  prev = cur;\n  cur = next;\n}\nreturn prev;",
            "python": "prev, cur = None, head\nwhile cur:\n    cur.next, prev, cur = prev, cur, cur.next\nreturn prev",
            "cpp": "ListNode* prev = nullptr;\nListNode* cur = head;\nwhile (cur) {\n  ListNode* next = cur->next;\n  cur->next = prev;\n  prev = cur;\n  cur = next;\n}\nreturn prev;",
        },
    },
    {
        "pattern": "math",
        "note": "Sum without the plus operator is XOR plus carry. The carry comes from AND, shifted one place left. Keep adding the carry until it is zero.",
        "snippets": {
            "java": "int sum = a ^ b;\nint carry = a & b;\nwhile (carry != 0) {\n  int next = (sum & carry) << 1;\n  sum ^= carry;\n  carry = next;\n}\nreturn sum;",
            "python": "MASK = 0xFFFFFFFF\ns = (a ^ b) & MASK\ncarry = ((a & b) << 1) & MASK\nwhile carry:\n    s = (s ^ carry) & MASK\n    carry = ((s & carry) << 1) & MASK\nreturn s - (1 << 32) if s >> 31 else s",
            "cpp": "int sum = a ^ b;\nint carry = a & b;\nwhile (carry != 0) {\n  int next = (sum & carry) << 1;\n  sum ^= carry;\n  carry = next;\n}\nreturn sum;",
        },
    },
]

NEW_PROBLEMS = [
    {
        "id": "206",
        "slug": "reverse-linked-list",
        "title": "Reverse Linked List",
        "difficulty": "Easy",
        "pattern": "linkedlist",
        "lists": ["neetcode150", "blind75"],
        "platform": {
            "leetcode": "reverse-linked-list",
            "neetcode": "https://neetcode.io/problems/reverse-linked-list",
            "walkccc": "https://walkccc.me/leetcodeproblems/reverse-linked-list/",
        },
        "statement": "Given the head of a singly linked list, reverse the list and return its new head.",
        "keyIdea": "Reversing is the same local pointer swap repeated along the whole list. Keep one pointer to the part already reversed so nothing is lost on the way.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Copy through an array",
                "time": "O(n)",
                "space": "O(n)",
                "why": "Read every node into an array, reverse the array, then build a second list from it. Correct, but it allocates two extra n sized structures and never touches the original pointers.",
                "code": {
                    "java": "List<Integer> vals = new ArrayList<>();\nfor (ListNode c = head; c != null; c = c.next) vals.add(c.val);\nListNode dummy = new ListNode(0);\nfor (int i = vals.size() - 1; i >= 0; i--)\n  dummy.next = new ListNode(vals.get(i), dummy.next);\nreturn dummy.next;",
                    "python": "vals = []\ncur = head\nwhile cur:\n    vals.append(cur.val)\n    cur = cur.next\n\ndummy = ListNode(0)\nfor v in reversed(vals):\n    dummy.next = ListNode(v, dummy.next)\nreturn dummy.next",
                    "cpp": "vector<int> vals;\nfor (auto* c = head; c; c = c->next) vals.push_back(c->val);\nListNode* dummy = new ListNode(0);\nfor (int i = (int)vals.size() - 1; i >= 0; --i)\n  dummy->next = new ListNode(vals[i], dummy->next);\nreturn dummy->next;",
                },
            },
            {
                "tier": "better",
                "label": "Recursive reversal",
                "time": "O(n)",
                "space": "O(n)",
                "why": "The recursion stack holds the rest of the list for you, so the code reads as three lines. It costs one stack frame per node, so a list longer than the stack limit will overflow.",
                "code": {
                    "java": "if (head == null || head.next == null) return head;\nListNode newHead = reverse(head.next);\nhead.next.next = head;\nhead.next = null;\nreturn newHead;",
                    "python": "def reverse(head):\n    if head is None or head.next is None:\n        return head\n    new_head = reverse(head.next)\n    head.next.next = head\n    head.next = None\n    return new_head",
                    "cpp": "ListNode* reverse(ListNode* head) {\n  if (!head || !head->next) return head;\n  ListNode* nh = reverse(head->next);\n  head->next->next = head;\n  head->next = nullptr;\n  return nh;\n}",
                },
            },
            {
                "tier": "optimal",
                "label": "Iterative three pointers",
                "time": "O(n)",
                "space": "O(1)",
                "why": "The same pointer surgery with no recursion, so the stack never grows with the list. Three pointers and the reversal is done in a single pass.",
                "code": {
                    "java": "ListNode prev = null, cur = head;\nwhile (cur != null) {\n  ListNode next = cur.next;\n  cur.next = prev;\n  prev = cur;\n  cur = next;\n}\nreturn prev;",
                    "python": "prev, cur = None, head\nwhile cur:\n    cur.next, prev, cur = prev, cur, cur.next\nreturn prev",
                    "cpp": "ListNode* prev = nullptr;\nListNode* cur = head;\nwhile (cur) {\n  ListNode* next = cur->next;\n  cur->next = prev;\n  prev = cur;\n  cur = next;\n}\nreturn prev;",
                },
            },
        ],
        "hints": [
            "What single pointer change reverses a two node list?",
            "Reversal is local: if a points to b, you want b to point back to a. Each node needs exactly one rewire.",
            "You need a pointer to the node you already reversed, so the next iteration does not lose the finished part.",
            "Keep prev (already reversed), cur (current node) and next (saved before the overwrite).",
            "Pseudocode: while cur: save next, set cur.next to prev, advance prev to cur, advance cur to next. Return prev.",
        ],
    },
    {
        "id": "104",
        "slug": "maximum-depth-of-binary-tree",
        "title": "Maximum Depth of Binary Tree",
        "difficulty": "Easy",
        "pattern": "trees",
        "lists": ["neetcode150", "blind75"],
        "platform": {
            "leetcode": "maximum-depth-of-binary-tree",
            "neetcode": "https://neetcode.io/problems/maximum-depth-of-binary-tree",
            "walkccc": "https://walkccc.me/leetcodeproblems/maximum-depth-of-binary-tree/",
        },
        "statement": "Given the root of a binary tree, return its maximum depth. The maximum depth is the number of nodes along the longest path from the root down to a leaf.",
        "keyIdea": "The depth of a node is one more than the deeper of its two subtrees. That single recurrence is the entire problem; every approach is just a different way of walking it.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Level order with a queue",
                "time": "O(n)",
                "space": "O(w)",
                "why": "Walk the tree one level at a time and count the levels. Simple and immune to recursion limits, but a wide tree holds an entire level in memory at once.",
                "code": {
                    "java": "if (root == null) return 0;\nQueue<TreeNode> q = new ArrayDeque<>();\nq.add(root);\nint depth = 0;\nwhile (!q.isEmpty()) {\n  int size = q.size();\n  for (int i = 0; i < size; i++) {\n    TreeNode n = q.poll();\n    if (n.left != null) q.add(n.left);\n    if (n.right != null) q.add(n.right);\n  }\n  depth++;\n}\nreturn depth;",
                    "python": "from collections import deque\n\nif root is None:\n    return 0\nq = deque([root])\ndepth = 0\nwhile q:\n    for _ in range(len(q)):\n        n = q.popleft()\n        if n.left:\n            q.append(n.left)\n        if n.right:\n            q.append(n.right)\n    depth += 1\nreturn depth",
                    "cpp": "if (!root) return 0;\nqueue<TreeNode*> q; q.push(root);\nint depth = 0;\nwhile (!q.empty()) {\n  int size = q.size();\n  while (size--) {\n    TreeNode* n = q.front(); q.pop();\n    if (n->left) q.push(n->left);\n    if (n->right) q.push(n->right);\n  }\n  ++depth;\n}\nreturn depth;",
                },
            },
            {
                "tier": "better",
                "label": "Recursive depth of the taller side",
                "time": "O(n)",
                "space": "O(h)",
                "why": "One plus the deeper child is the whole recurrence. It reads as three lines and costs one stack frame per level.",
                "code": {
                    "java": "if (root == null) return 0;\nreturn 1 + Math.max(depth(root.left), depth(root.right));",
                    "python": "def max_depth(root):\n    if root is None:\n        return 0\n    return 1 + max(max_depth(root.left), max_depth(root.right))",
                    "cpp": "int depth(TreeNode* node) {\n  if (!node) return 0;\n  return 1 + max(depth(node->left), depth(node->right));\n}",
                },
            },
            {
                "tier": "optimal",
                "label": "Iterative DFS with an explicit stack",
                "time": "O(n)",
                "space": "O(h)",
                "why": "Same recurrence, but the depth is tracked explicitly instead of living in the call stack. A skewed tree of a hundred thousand nodes will not overflow.",
                "code": {
                    "java": "if (root == null) return 0;\nDeque<TreeNode> stack = new ArrayDeque<>();\nDeque<Integer> depths = new ArrayDeque<>();\nstack.push(root);\ndepths.push(1);\nint best = 0;\nwhile (!stack.isEmpty()) {\n  TreeNode n = stack.pop();\n  int d = depths.pop();\n  best = Math.max(best, d);\n  if (n.left != null) { stack.push(n.left); depths.push(d + 1); }\n  if (n.right != null) { stack.push(n.right); depths.push(d + 1); }\n}\nreturn best;",
                    "python": "if root is None:\n    return 0\nstack = [(root, 1)]\nbest = 0\nwhile stack:\n    node, d = stack.pop()\n    best = max(best, d)\n    if node.left:\n        stack.append((node.left, d + 1))\n    if node.right:\n        stack.append((node.right, d + 1))\nreturn best",
                    "cpp": "if (!root) return 0;\nstack<pair<TreeNode*,int>> st;\nst.push({root, 1});\nint best = 0;\nwhile (!st.empty()) {\n  auto [node, d] = st.top(); st.pop();\n  best = max(best, d);\n  if (node->left) st.push({node->left, d + 1});\n  if (node->right) st.push({node->right, d + 1});\n}\nreturn best;",
                },
            },
        ],
        "hints": [
            "How do you get from the two subtree depths to the depth of their parent?",
            "The path through a node goes through whichever child is deeper. The other child is irrelevant to the answer.",
            "Try writing the answer as one plus the maximum of two recursive calls.",
            "What is the depth of an empty tree? That gives you the base case.",
            "Pseudocode: if node is empty return 0, else return 1 + max(depth(left), depth(right)).",
        ],
    },
    {
        "id": "215",
        "slug": "kth-largest-element-in-an-array",
        "title": "Kth Largest Element in an Array",
        "difficulty": "Medium",
        "pattern": "heap",
        "lists": ["neetcode150"],
        "platform": {
            "leetcode": "kth-largest-element-in-an-array",
            "neetcode": "https://neetcode.io/problems/kth-largest-element-in-an-array",
            "walkccc": "https://walkccc.me/leetcodeproblems/kth-largest-element-in-an-array/",
        },
        "statement": "Given an integer array nums and an integer k, return the kth largest element in the array. It is not necessarily the kth distinct element.",
        "keyIdea": "You only ever need the top k values, so anything outside that set is dead weight. Discarding the rest is what turns a full sort into a partial one.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Sort and index from the end",
                "time": "O(n log n)",
                "space": "O(1)",
                "why": "Sort ascending and read index n minus k. Always correct, but it totally orders every element in order to use k of them.",
                "code": {
                    "java": "int[] a = nums.clone();\nArrays.sort(a);\nreturn a[a.length - k];",
                    "python": "return sorted(nums, reverse=True)[k - 1]",
                    "cpp": "vector<int> a(nums);\nsort(a.begin(), a.end());\nreturn a[a.size() - k];",
                },
            },
            {
                "tier": "better",
                "label": "Quickselect around a pivot",
                "time": "O(n)",
                "space": "O(1)",
                "why": "Partition around a pivot so everything larger goes to one side, then recurse only into the side holding position k. Average linear, but the worst case degenerates to n squared when the pivot keeps landing on an extreme.",
                "code": {
                    "java": "int[] a = nums.clone();\nint target = a.length - k;\nquickSelect(a, 0, a.length - 1, target);\nreturn a[target];\n\nprivate void quickSelect(int[] a, int lo, int hi, int target) {\n  while (lo < hi) {\n    int pivot = a[lo + (hi - lo) / 2];\n    int i = lo, j = hi;\n    while (i <= j) {\n      while (a[i] < pivot) i++;\n      while (a[j] > pivot) j--;\n      if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }\n    }\n    if (target <= j) hi = j;\n    else if (target >= i) lo = i;\n    else return;\n  }\n}",
                    "python": "def quick_select(a, lo, hi, target):\n    while lo < hi:\n        pivot = a[(lo + hi) // 2]\n        i, j = lo, hi\n        while i <= j:\n            while a[i] < pivot: i += 1\n            while a[j] > pivot: j -= 1\n            if i <= j:\n                a[i], a[j] = a[j], a[i]\n                i += 1; j -= 1\n        if target <= j: hi = j\n        elif target >= i: lo = i\n        else: return\n\na = list(nums)\nquick_select(a, 0, len(a) - 1, len(a) - k)\nreturn a[len(a) - k]",
                    "cpp": "vector<int> a(nums);\nint target = (int)a.size() - k;\nint lo = 0, hi = (int)a.size() - 1;\nwhile (lo < hi) {\n  int pivot = a[lo + (hi - lo) / 2];\n  int i = lo, j = hi;\n  while (i <= j) {\n    while (a[i] < pivot) ++i;\n    while (a[j] > pivot) --j;\n    if (i <= j) { swap(a[i], a[j]); ++i; --j; }\n  }\n  if (target <= j) hi = j;\n  else if (target >= i) lo = i;\n  else break;\n}\nreturn a[target];",
                },
            },
            {
                "tier": "optimal",
                "label": "Min-heap of size k",
                "time": "O(n log k)",
                "space": "O(k)",
                "why": "Keep only the k largest in a min-heap. The heap top is always the smallest of the current top k, so it is exactly the next value to evict. Cost depends on k, not on n.",
                "code": {
                    "java": "PriorityQueue<Integer> pq = new PriorityQueue<>();\nfor (int v : nums) {\n  pq.offer(v);\n  if (pq.size() > k) pq.poll();\n}\nreturn pq.peek();",
                    "python": "import heapq\n\npq = []\nfor v in nums:\n    heapq.heappush(pq, v)\n    if len(pq) > k:\n        heapq.heappop(pq)\nreturn pq[0]",
                    "cpp": "priority_queue<int, vector<int>, greater<int>> pq;\nfor (int v : nums) {\n  pq.push(v);\n  if ((int)pq.size() > k) pq.pop();\n}\nreturn pq.top();",
                },
            },
        ],
        "hints": [
            "How many values do you actually need to remember at any moment?",
            "Only k. Every other element is irrelevant the moment you read it.",
            "If you kept the k largest seen so far, what structure answers which one to throw away?",
            "A min-heap of size k. Its top is the smallest of the k largest, so that is the one that gets evicted.",
            "Pseudocode: push each value, and whenever the heap size exceeds k, pop it. The heap top at the end is the answer.",
        ],
    },
    {
        "id": "55",
        "slug": "jump-game",
        "title": "Jump Game",
        "difficulty": "Medium",
        "pattern": "greedy",
        "lists": ["neetcode150"],
        "platform": {
            "leetcode": "jump-game",
            "neetcode": "https://neetcode.io/problems/jump-game",
            "walkccc": "https://walkccc.me/leetcodeproblems/jump-game/",
        },
        "statement": "You are given an integer array nums. Each element nums[i] represents the maximum jump length available at that position. Start at index 0 and return true if you can reach the last index, or false if it is not possible.",
        "keyIdea": "Track the furthest index reachable so far. If the current index passes that frontier, no choice of path could have helped, because the frontier is the best any earlier jump could have bought.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Try every path",
                "time": "O(2^n)",
                "space": "O(n)",
                "why": "Recursively try every jump length from every position. Exponential, because the same suffix is re-explored exponentially many times.",
                "code": {
                    "java": "private boolean reach(int[] nums, int i) {\n  if (i >= nums.length - 1) return true;\n  for (int step = 1; step <= nums[i]; step++)\n    if (reach(nums, i + step)) return true;\n  return false;\n}",
                    "python": "def can_reach(nums, i):\n    if i >= len(nums) - 1:\n        return True\n    for step in range(1, nums[i] + 1):\n        if can_reach(nums, i + step):\n            return True\n    return False\n\ndef canJump(nums):\n    return can_reach(nums, 0)",
                    "cpp": "bool reach(const vector<int>& nums, int i) {\n  if (i >= (int)nums.size() - 1) return true;\n  for (int s = 1; s <= nums[i]; ++s)\n    if (reach(nums, i + s)) return true;\n  return false;\n}\nbool canJump(vector<int>& nums) { return reach(nums, 0); }",
                },
            },
            {
                "tier": "better",
                "label": "Dynamic programming from the end",
                "time": "O(n)",
                "space": "O(n)",
                "why": "Mark every index you can reach, working backwards. Linear time, but it keeps a boolean per index when the answer only ever needs one running number.",
                "code": {
                    "java": "boolean[] good = new boolean[nums.length];\ngood[nums.length - 1] = true;\nfor (int i = nums.length - 2; i >= 0; i--)\n  for (int s = 1; s <= nums[i] && i + s < nums.length; s++)\n    if (good[i + s]) { good[i] = true; break; }\nreturn good[0];",
                    "python": "good = [False] * len(nums)\ngood[-1] = True\nfor i in range(len(nums) - 2, -1, -1):\n    for s in range(1, nums[i] + 1):\n        if i + s < len(nums) and good[i + s]:\n            good[i] = True\n            break\nreturn good[0]",
                    "cpp": "vector<bool> good(nums.size(), false);\ngood[nums.size() - 1] = true;\nfor (int i = (int)nums.size() - 2; i >= 0; --i)\n  for (int s = 1; s <= nums[i] && i + s < (int)nums.size(); ++s)\n    if (good[i + s]) { good[i] = true; break; }\nreturn good[0];",
                },
            },
            {
                "tier": "optimal",
                "label": "Greedy furthest reach",
                "time": "O(n)",
                "space": "O(1)",
                "why": "One variable holds the furthest index reachable. If the current index ever passes it, the answer is no. Constant space, single pass, and no array of states.",
                "code": {
                    "java": "int reach = 0;\nfor (int i = 0; i < nums.length; i++) {\n  if (i > reach) return false;\n  reach = Math.max(reach, i + nums[i]);\n  if (reach >= nums.length - 1) return true;\n}\nreturn false;",
                    "python": "reach = 0\nfor i, v in enumerate(nums):\n    if i > reach:\n        return False\n    reach = max(reach, i + v)\n    if reach >= len(nums) - 1:\n        return True\nreturn False",
                    "cpp": "int reach = 0;\nfor (int i = 0; i < (int)nums.size(); ++i) {\n  if (i > reach) return false;\n  reach = max(reach, i + nums[i]);\n  if (reach >= (int)nums.size() - 1) return true;\n}\nreturn false;",
                },
            },
        ],
        "hints": [
            "Do you need to know every reachable position, or just the furthest one?",
            "If you can reach index 9, every index up to 9 is also reachable. Reachability is a prefix, not a scattered set.",
            "Keep a single number: the furthest index anything so far can jump to.",
            "At each index, extend the frontier with i plus nums[i]. If the frontier falls behind the current index, you are stuck.",
            "Pseudocode: reach = 0. For each i, if i > reach return false, else reach = max(reach, i + nums[i]).",
        ],
    },
    {
        "id": "56",
        "slug": "merge-intervals",
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "pattern": "intervals",
        "lists": ["neetcode150", "blind75"],
        "platform": {
            "leetcode": "merge-intervals",
            "neetcode": "https://neetcode.io/problems/merge-intervals",
            "walkccc": "https://walkccc.me/leetcodeproblems/merge-intervals/",
        },
        "statement": "Given an array of intervals where intervals[i] equals start i and end i, merge all overlapping intervals and return an array of the non-overlapping intervals that cover all the input ranges.",
        "keyIdea": "Sort by start time, then sweep once. Each interval either extends the run you are building or has to begin a new one, and no interval can ever overlap something more than one position behind.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Repeated pairwise merging until stable",
                "time": "O(n^3)",
                "space": "O(n)",
                "why": "Keep merging any two overlapping intervals until nothing changes. Correct, but it rescans the entire list after every single merge.",
                "code": {
                    "java": "List<int[]> out = new ArrayList<>();\nfor (int[] iv : intervals) out.add(new int[]{iv[0], iv[1]});\nboolean changed = true;\nwhile (changed) {\n  changed = false;\n  for (int i = 0; i < out.size() && !changed; i++)\n    for (int j = i + 1; j < out.size(); j++)\n      if (out.get(i)[0] <= out.get(j)[1] && out.get(j)[0] <= out.get(i)[1]) {\n        out.get(i)[0] = Math.min(out.get(i)[0], out.get(j)[0]);\n        out.get(i)[1] = Math.max(out.get(i)[1], out.get(j)[1]);\n        out.remove(j); changed = true; break;\n      }\n}\nreturn out;",
                    "python": "out = [[a, b] for a, b in intervals]\nchanged = True\nwhile changed:\n    changed = False\n    for i in range(len(out)):\n        for j in range(i + 1, len(out)):\n            if out[i][0] <= out[j][1] and out[j][0] <= out[i][1]:\n                out[i][0] = min(out[i][0], out[j][0])\n                out[i][1] = max(out[i][1], out[j][1])\n                out.pop(j)\n                changed = True\n                break\n        if changed:\n            break\nreturn out",
                    "cpp": "vector<vector<int>> out;\nfor (auto& iv : intervals) out.push_back({iv[0], iv[1]});\nbool changed = true;\nwhile (changed) {\n  changed = false;\n  for (int i = 0; i < (int)out.size() && !changed; ++i)\n    for (int j = i + 1; j < (int)out.size(); ++j)\n      if (out[i][0] <= out[j][1] && out[j][0] <= out[i][1]) {\n        out[i][0] = min(out[i][0], out[j][0]);\n        out[i][1] = max(out[i][1], out[j][1]);\n        out.erase(out.begin() + j);\n        changed = true; break;\n      }\n}\nreturn out;",
                },
            },
            {
                "tier": "better",
                "label": "Sort by start, then one merge pass",
                "time": "O(n log n)",
                "space": "O(n)",
                "why": "Sorting by start makes every overlap adjacent, so a single left to right pass finishes the job. It still allocates a second n sized array.",
                "code": {
                    "java": "int[][] sorted = intervals.clone();\nArrays.sort(sorted, (a, b) -> a[0] - b[0]);\nList<int[]> out = new ArrayList<>();\nfor (int[] iv : sorted) {\n  if (out.isEmpty() || iv[0] > out.get(out.size() - 1)[1]) out.add(new int[]{iv[0], iv[1]});\n  else out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], iv[1]);\n}\nreturn out.toArray(new int[0][]);",
                    "python": "merged = []\nfor start, end in sorted(intervals):\n    if merged and start <= merged[-1][1]:\n        merged[-1][1] = max(merged[-1][1], end)\n    else:\n        merged.append([start, end])\nreturn merged",
                    "cpp": "sort(iv.begin(), iv.end(), [](auto& a, auto& b){ return a[0] < b[0]; });\nvector<vector<int>> merged;\nfor (auto& p : iv) {\n  if (merged.empty() || p[0] > merged.back()[1]) merged.push_back(p);\n  else merged.back()[1] = max(merged.back()[1], p[1]);\n}\nreturn merged;",
                },
            },
            {
                "tier": "optimal",
                "label": "In-place merge into the same array",
                "time": "O(n log n)",
                "space": "O(log n)",
                "why": "Same sorted sweep, but the result is written back over the input as it goes. The only extra memory is whatever the sort itself needs.",
                "code": {
                    "java": "Arrays.sort(intervals, (a, b) -> a[0] - b[0]);\nint write = 0;\nfor (int i = 0; i < intervals.length; i++) {\n  if (write == 0 || intervals[i][0] > intervals[write - 1][1]) intervals[write++] = intervals[i];\n  else intervals[write - 1][1] = Math.max(intervals[write - 1][1], intervals[i][1]);\n}\nreturn Arrays.copyOf(intervals, write);",
                    "python": "intervals.sort(key=lambda p: p[0])\nwrite = 0\nfor iv in intervals:\n    if write == 0 or iv[0] > intervals[write - 1][1]:\n        intervals[write] = iv\n        write += 1\n    else:\n        intervals[write - 1][1] = max(intervals[write - 1][1], iv[1])\nreturn intervals[:write]",
                    "cpp": "sort(iv.begin(), iv.end(), [](auto& a, auto& b){ return a[0] < b[0]; });\nint write = 0;\nfor (int i = 0; i < (int)iv.size(); ++i) {\n  if (write == 0 || iv[i][0] > iv[write - 1][1]) iv[write++] = iv[i];\n  else iv[write - 1][1] = max(iv[write - 1][1], iv[i][1]);\n}\niv.resize(write);\nreturn iv;",
                },
            },
        ],
        "hints": [
            "What makes two intervals adjacent in the list rather than scattered?",
            "Sorting. Once intervals are ordered by start, an interval can only overlap the one you are currently building or the one right after it.",
            "Sort by start time, then walk once comparing each start against the current run's end.",
            "If start is at or before the current end, extend the end. Otherwise push a new interval.",
            "Pseudocode: sort by start. For each interval, if it overlaps the last merged one, extend that one's end, else append it.",
        ],
    },
    {
        "id": "191",
        "slug": "number-of-1-bits",
        "title": "Number of 1 Bits",
        "difficulty": "Easy",
        "pattern": "bitmanipulation",
        "lists": ["neetcode150", "blind75"],
        "platform": {
            "leetcode": "number-of-1-bits",
            "neetcode": "https://neetcode.io/problems/number-of-1-bits",
            "walkccc": "https://walkccc.me/leetcodeproblems/number-of-1-bits/",
        },
        "statement": "Write a function that takes an unsigned integer n and returns the number of set bits it has, also called the population count. Assume n is a non-negative 32-bit integer.",
        "keyIdea": "x AND (x minus 1) clears the lowest set bit in a single operation. Counting how many times you can do that before the number reaches zero is exactly counting the set bits.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Convert to binary and count characters",
                "time": "O(log n)",
                "space": "O(log n)",
                "why": "Write the number out in base two and count the ones. Understandable, but it allocates a string to answer a question about a fixed 32 bit word.",
                "code": {
                    "java": "return (int) Integer.toBinaryString(n).chars().filter(c -> c == '1').count();",
                    "python": "return bin(n).count('1')",
                    "cpp": "string s;\nfor (int i = 31; i >= 0; --i) s += ((n >> i) & 1) ? '1' : '0';\nreturn (int) count(s.begin(), s.end(), '1');",
                },
            },
            {
                "tier": "better",
                "label": "Kernighan's trick",
                "time": "O(k)",
                "space": "O(1)",
                "why": "Each x AND (x minus 1) removes exactly one set bit, so the loop runs once per set bit rather than once per bit. No allocation, and it skips every zero position.",
                "code": {
                    "java": "int count = 0;\nwhile (n != 0) {\n  n &= n - 1;\n  count++;\n}\nreturn count;",
                    "python": "count = 0\nwhile n:\n    n &= n - 1\n    count += 1\nreturn count",
                    "cpp": "int count = 0;\nwhile (n) { n &= n - 1; ++count; }\nreturn count;",
                },
            },
            {
                "tier": "optimal",
                "label": "SWAR popcount with fixed masks",
                "time": "O(1)",
                "space": "O(1)",
                "why": "Add, subtract and mask in fixed width steps so each operation accounts for two bits, then four, then eight, then sixteen at once. The count takes a handful of arithmetic steps regardless of the input.",
                "code": {
                    "java": "n = n - ((n >> 1) & 0x55555555);\nn = (n & 0x33333333) + ((n >> 2) & 0x33333333);\nn = (n + (n >> 4)) & 0x0f0f0f0f;\nreturn (n * 0x01010101) >> 24;",
                    "python": "n &= 0xFFFFFFFF\nn = n - ((n >> 1) & 0x55555555)\nn = (n & 0x33333333) + ((n >> 2) & 0x33333333)\nn = (n + (n >> 4)) & 0x0F0F0F0F\nreturn ((n * 0x01010101) >> 24) & 0xFF",
                    "cpp": "uint32_t x = n;\nx = x - ((x >> 1) & 0x55555555u);\nx = (x & 0x33333333u) + ((x >> 2) & 0x33333333u);\nx = (x + (x >> 4)) & 0x0F0F0F0Fu;\nreturn (int) ((x * 0x01010101u) >> 24);",
                },
            },
        ],
        "hints": [
            "How do you remove exactly one set bit from a number in a single operation?",
            "Subtracting one flips the lowest set bit to zero and everything below it to one. AND with that result keeps only the cleared bit.",
            "If you AND a number with itself minus one, what happens to the number of set bits?",
            "It loses exactly one set bit. So loop that operation and count how many times you can before reaching zero.",
            "Pseudocode: while n is not zero, set n = n AND (n - 1) and increment the counter.",
        ],
    },
    {
        "id": "371",
        "slug": "sum-of-two-integers",
        "title": "Sum of Two Integers",
        "difficulty": "Medium",
        "pattern": "math",
        "lists": ["neetcode150"],
        "platform": {
            "leetcode": "sum-of-two-integers",
            "neetcode": "https://neetcode.io/problems/sum-of-two-integers",
            "walkccc": "https://walkccc.me/leetcodeproblems/sum-of-two-integers/",
        },
        "statement": "Given two integers a and b, return the sum of the two integers without using the plus or minus operators.",
        "keyIdea": "XOR gives the sum without any carry. AND identifies exactly the positions that produce a carry, and shifting that left by one moves the carry into the next position.",
        "ladder": [
            {
                "tier": "brute",
                "label": "Add one bit position at a time",
                "time": "O(32)",
                "space": "O(1)",
                "why": "Walk all 32 positions individually, writing the sum bit into the result and shifting the carry up by hand each round. Correct but mechanical, and it always does exactly 32 iterations.",
                "code": {
                    "java": "int result = 0, carry = 0;\nfor (int i = 0; i < 32; i++) {\n  int aBit = (a >> i) & 1;\n  int bBit = (b >> i) & 1;\n  int sumBit = aBit ^ bBit ^ carry;\n  carry = aBit & bBit | (aBit & carry) | (bBit & carry);\n  result |= sumBit << i;\n}\nreturn result;",
                    "python": "result = 0\ncarry = 0\nfor i in range(32):\n    a_bit = (a >> i) & 1\n    b_bit = (b >> i) & 1\n    sum_bit = a_bit ^ b_bit ^ carry\n    carry = a_bit & b_bit | (a_bit & carry) | (b_bit & carry)\n    result |= sum_bit << i\nreturn result",
                    "cpp": "int result = 0, carry = 0;\nfor (int i = 0; i < 32; ++i) {\n  int ab = (a >> i) & 1, bb = (b >> i) & 1;\n  int s = ab ^ bb ^ carry;\n  carry = (ab & bb) | (ab & carry) | (bb & carry);\n  result |= s << i;\n}\nreturn result;",
                },
            },
            {
                "tier": "better",
                "label": "XOR for the sum, AND for the carry",
                "time": "O(1)",
                "space": "O(1)",
                "why": "XOR already computes the sum of each bit pair ignoring carries, and AND marks exactly the positions that carry. Shift the carry left and feed it back until it disappears. Usually converges in two or three rounds.",
                "code": {
                    "java": "int sum = a ^ b;\nint carry = a & b;\nwhile (carry != 0) {\n  int next = (sum & carry) << 1;\n  sum ^= carry;\n  carry = next;\n}\nreturn sum;",
                    "python": "MASK = 0xFFFFFFFF\n\ntotal = (a ^ b) & MASK\ncarry = ((a & b) << 1) & MASK\nwhile carry:\n    total = (total ^ carry) & MASK\n    carry = ((total & carry) << 1) & MASK\n\nreturn total - (1 << 32) if total >> 31 else total",
                    "cpp": "int sum = a ^ b;\nint carry = (a & b) << 1;\nwhile (carry != 0) {\n  int next = (sum & carry) << 1;\n  sum ^= carry;\n  carry = next;\n}\nreturn sum;",
                },
            },
            {
                "tier": "optimal",
                "label": "Branchless fixed-width carry propagation",
                "time": "O(1)",
                "space": "O(1)",
                "why": "Identical arithmetic, but the loop always runs 32 times with no data dependent exit. On a fixed width word the answer is identical while the branch becomes fully predictable, which is what you want in hot code.",
                "code": {
                    "java": "int sum = a ^ b;\nint carry = a & b;\nfor (int i = 0; i < 32; i++) {\n  int next = (sum & carry) << 1;\n  sum ^= carry;\n  carry = next;\n}\nreturn sum;",
                    "python": "MASK = 0xFFFFFFFF\n\ntotal = (a ^ b) & MASK\ncarry = (a & b) & MASK\nfor _ in range(32):\n    total, carry = (total ^ carry) & MASK, ((total & carry) << 1) & MASK\n\nreturn total - (1 << 32) if total >> 31 else total",
                    "cpp": "int sum = a ^ b;\nint carry = a & b;\nfor (int i = 0; i < 32; ++i) {\n  int next = (sum & carry) << 1;\n  sum ^= carry;\n  carry = next;\n}\nreturn sum;",
                },
            },
        ],
        "hints": [
            "Which bitwise operator gives you 1 only where exactly one input bit is 1?",
            "XOR. That is the sum of a bit pair when you ignore carrying entirely.",
            "Which operator identifies the positions where a carry will actually be produced?",
            "AND, shifted one place left. That carry then has to be added back into the sum, which means feeding it through the same XOR step again.",
            "Pseudocode: sum = a XOR b, carry = a AND b. While carry is nonzero: next = (sum AND carry) shifted left, sum = sum XOR carry, carry = next.",
        ],
    },
]


def main():
    data = json.loads(DATA.read_text())

    have_cards = {c["pattern"] for c in data["syntaxCards"]}
    added_cards = [c for c in NEW_SYNTAX_CARDS if c["pattern"] not in have_cards]
    data["syntaxCards"].extend(added_cards)

    have_ids = {p["id"] for p in data["problems"]}
    added_problems = [p for p in NEW_PROBLEMS if p["id"] not in have_ids]
    data["problems"].extend(added_problems)

    # order by difficulty then id so the Learn list reads sensibly
    order = {"Easy": 0, "Medium": 1, "Hard": 2}
    data["problems"].sort(key=lambda p: (order.get(p["difficulty"], 3), int(p["id"])))

    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    print("syntax cards added:", [c["pattern"] for c in added_cards])
    print("problems added   :", [p["id"] for p in added_problems])
    print("problems total   :", len(data["problems"]))
    print("cards total      :", len(data["syntaxCards"]))


if __name__ == "__main__":
    main()