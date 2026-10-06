"""
Management command to seed the Canonical Interview Question Bank.
Populates standard, high-yield interview questions equipped with tiered hints,
interviewer follow-up questions, and complexity benchmarks.
"""

from django.core.management.base import BaseCommand
from tracker.models import CanonicalInterviewQuestion, Problem, Topic


CANONICAL_QUESTIONS_DATA = [
    # 1. TWO POINTERS
    {
        "title": "Two Sum II - Input Array Is Sorted",
        "slug": "two-sum-ii-input-array-is-sorted",
        "topic_slug": "two-pointers",
        "pattern": Problem.Pattern.TWO_POINTER,
        "supporting_concepts": "Array, Binary Search",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,FRONTEND,BACKEND,PRODUCT",
        "company_tags": "Amazon, Apple, Meta, Google",
        "description": "Given a 1-indexed array of integers numbers that is already sorted in non-decreasing order, find two numbers such that they add up to a specific target number. Return the indices of the two numbers, index1 and index2, added by one as an integer array [index1, index2] of length 2.",
        "examples": "Input: numbers = [2,7,11,15], target = 9 -> Output: [1,2]\nInput: numbers = [2,3,4], target = 6 -> Output: [1,3]",
        "constraints": "2 <= numbers.length <= 3 * 10^4\n-1000 <= numbers[i] <= 1000\nnumbers is sorted in non-decreasing order.",
        "hints": [
            "Since the array is sorted, how does moving the left pointer right or right pointer left change the current sum?",
            "Start with left at 0 and right at len - 1. If sum < target, increment left. If sum > target, decrement right.",
            "Maintain O(1) space with two convergence pointers."
        ],
        "follow_ups": [
            {
                "question": "Why is Two Pointers preferable to a Hash Map in this specific problem?",
                "options": ["It reduces time from O(N) to O(log N)", "It reduces auxiliary space from O(N) to O(1)", "It handles duplicate values without sets"],
                "correct": "It reduces auxiliary space from O(N) to O(1)",
                "explanation": "Because the input array is already sorted, Two Pointers achieves O(1) extra space compared to HashMap's O(N)."
            }
        ],
        "optimal_time": "O(N)",
        "optimal_space": "O(1)",
        "url": "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/"
    },
    {
        "title": "3Sum",
        "slug": "3sum",
        "topic_slug": "two-pointers",
        "pattern": Problem.Pattern.TWO_POINTER,
        "supporting_concepts": "Sorting, Two Pointers, Duplicate Elimination",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Google, Meta, Microsoft, Amazon",
        "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0. Notice that the solution set must not contain duplicate triplets.",
        "examples": "Input: nums = [-1,0,1,2,-1,-4] -> Output: [[-1,-1,2],[-1,0,1]]",
        "constraints": "3 <= nums.length <= 3000\n-10^5 <= nums[i] <= 10^5",
        "hints": [
            "Sorting the array first makes it easy to avoid duplicate triplets and reduces 3Sum to N instances of Two Sum II.",
            "Iterate with index i from 0 to N-3. Skip duplicates if nums[i] == nums[i-1]. Use two pointers (left=i+1, right=N-1) to find sum == -nums[i].",
            "When a valid triplet is found, advance both left and right past duplicate values to avoid duplicate sets."
        ],
        "follow_ups": [
            {
                "question": "Can 3Sum be solved in sub-quadratic O(N log N) time?",
                "options": ["Yes, using 3 parallel pointers", "No, 3Sum is provably Omega(N^2) under comparison-based models", "Yes, using a multi-index Trie"],
                "correct": "No, 3Sum is provably Omega(N^2) under comparison-based models",
                "explanation": "The 3SUM conjecture posits that no algorithm can solve 3SUM in O(N^(2-eps)) time without special word-RAM tricks."
            }
        ],
        "optimal_time": "O(N^2)",
        "optimal_space": "O(1) auxiliary",
        "url": "https://leetcode.com/problems/3sum/"
    },
    {
        "title": "Container With Most Water",
        "slug": "container-with-most-water",
        "topic_slug": "two-pointers",
        "pattern": Problem.Pattern.TWO_POINTER,
        "supporting_concepts": "Greedy Choice, Area Maximization",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,FRONTEND,PRODUCT",
        "company_tags": "Meta, Amazon, Google",
        "description": "You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]). Find two lines that together with the x-axis form a container, such that the container contains the most water. Return the maximum amount of water a container can store.",
        "examples": "Input: height = [1,8,6,2,5,4,8,3,7] -> Output: 49",
        "constraints": "n == height.length\n2 <= n <= 10^5\n0 <= height[i] <= 10^4",
        "hints": [
            "Area is bounded by min(height[left], height[right]) * (right - left).",
            "To have any chance of finding a larger area as the width shrinks, you must move the pointer at the shorter bar.",
            "Initialize left=0, right=n-1, compute area, and advance the smaller bar inward."
        ],
        "follow_ups": [
            {
                "question": "What is the invariant proving that moving the shorter line will never skip the global maximum?",
                "options": ["Width is strictly increasing", "Keeping the shorter line can only result in smaller areas because width decreases", "Both lines have equal heights"],
                "correct": "Keeping the shorter line can only result in smaller areas because width decreases",
                "explanation": "Any other container using the current shorter line would have a strictly smaller width and at most the same height, so it cannot exceed the current area."
            }
        ],
        "optimal_time": "O(N)",
        "optimal_space": "O(1)",
        "url": "https://leetcode.com/problems/container-with-most-water/"
    },

    # 2. FAST & SLOW POINTERS
    {
        "title": "Linked List Cycle",
        "slug": "linked-list-cycle",
        "topic_slug": "linked-lists",
        "pattern": Problem.Pattern.FAST_SLOW,
        "supporting_concepts": "Linked List, Cycle Detection",
        "difficulty": Problem.Difficulty.EASY,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Microsoft, Amazon, Spotify",
        "description": "Given head, the head of a linked list, determine if the linked list has a cycle in it. Return true if there is a cycle in the linked list, otherwise return false.",
        "examples": "Input: head = [3,2,0,-4], pos = 1 -> Output: true",
        "constraints": "The number of the nodes in the list is in the range [0, 10^4].\n-10^5 <= Node.val <= 10^5",
        "hints": [
            "Two runners on a circular track moving at different speeds will eventually meet.",
            "Use slow pointer moving 1 step and fast pointer moving 2 steps.",
            "If fast or fast.next reaches null, there is no cycle."
        ],
        "follow_ups": [
            {
                "question": "If the cycle length is C, at most how many iterations does it take for fast to catch slow after slow enters the cycle?",
                "options": ["C - 1 iterations", "2 * C iterations", "log(C) iterations"],
                "correct": "C - 1 iterations",
                "explanation": "The distance between fast and slow decreases by 1 on each step, so they meet in at most C steps."
            }
        ],
        "optimal_time": "O(N)",
        "optimal_space": "O(1)",
        "url": "https://leetcode.com/problems/linked-list-cycle/"
    },

    # 3. SLIDING WINDOW
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring-without-repeating-characters",
        "topic_slug": "sliding-window",
        "pattern": Problem.Pattern.SLIDING_WINDOW,
        "supporting_concepts": "HashMap, Two Pointers, String",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,FRONTEND,BACKEND,PRODUCT",
        "company_tags": "Google, Meta, Amazon, Microsoft, Uber",
        "description": "Given a string s, find the length of the longest substring without repeating characters.",
        "examples": "Input: s = 'abcabcbb' -> Output: 3 ('abc')\nInput: s = 'bbbbb' -> Output: 1 ('b')",
        "constraints": "0 <= s.length <= 5 * 10^4\ns consists of English letters, digits, symbols and spaces.",
        "hints": [
            "Use a sliding window [left, right] and a hash map storing the most recent index of each character seen.",
            "When s[right] has been seen inside the current window (index >= left), jump left pointer to map[s[right]] + 1.",
            "Update max_len = max(max_len, right - left + 1) at every step."
        ],
        "follow_ups": [
            {
                "question": "Can this be solved with an array instead of a hash map to reduce memory overhead?",
                "options": ["No, UTF-8 requires dynamic hash tables", "Yes, an ASCII array of size 128 or 256 yields direct O(1) index lookups", "Only if the string contains digits"],
                "correct": "Yes, an ASCII array of size 128 or 256 yields direct O(1) index lookups",
                "explanation": "If the character alphabet is standard ASCII, an integer array of size 128 avoids all hash map collision and heap allocation overhead."
            }
        ],
        "optimal_time": "O(N)",
        "optimal_space": "O(min(N, alphabet_size))",
        "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/"
    },
    {
        "title": "Minimum Window Substring",
        "slug": "minimum-window-substring",
        "topic_slug": "sliding-window",
        "pattern": Problem.Pattern.SLIDING_WINDOW,
        "supporting_concepts": "Hash Table, Frequency Count, Two Pointers",
        "difficulty": Problem.Difficulty.HARD,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Meta, Airbnb, Google, LinkedIn",
        "description": "Given two strings s and t of lengths m and n respectively, return the minimum window substring of s such that every character in t (including duplicates) is included in the window. If there is no such substring, return the empty string ''.",
        "examples": "Input: s = 'ADOBECODEBANC', t = 'ABC' -> Output: 'BANC'",
        "constraints": "m == s.length, n == t.length\n1 <= m, n <= 10^5\ns and t consist of uppercase and lowercase English letters.",
        "hints": [
            "Track character frequency needed from t in a map. Maintain a count of characters currently matched.",
            "Expand right until all characters in t are satisfied in the window.",
            "Once valid, contract left as much as possible while maintaining all characters to find the minimum length."
        ],
        "follow_ups": [
            {
                "question": "How can you verify if a window satisfies string t in O(1) time per character expansion?",
                "options": ["Compare two 256-element arrays every iteration", "Maintain a 'formed' variable tracking how many unique characters match required counts", "Compute a rolling polynomial hash"],
                "correct": "Maintain a 'formed' variable tracking how many unique characters match required counts",
                "explanation": "Incrementing 'formed' only when a char's count equals the required count allows O(1) window validity checks."
            }
        ],
        "optimal_time": "O(N + M)",
        "optimal_space": "O(alphabet_size)",
        "url": "https://leetcode.com/problems/minimum-window-substring/"
    },

    # 4. MERGE INTERVALS
    {
        "title": "Merge Intervals",
        "slug": "merge-intervals",
        "topic_slug": "arrays",
        "pattern": Problem.Pattern.INTERVALS,
        "supporting_concepts": "Sorting, Array, Intervals",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Google, Meta, Microsoft, Bloomberg",
        "description": "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
        "examples": "Input: intervals = [[1,3],[2,6],[8,10],[15,18]] -> Output: [[1,6],[8,10],[15,18]]",
        "constraints": "1 <= intervals.length <= 10^4\nintervals[i].length == 2\n0 <= starti <= endi <= 10^4",
        "hints": [
            "Sort intervals by start time. Once sorted, overlapping intervals will always be adjacent.",
            "Iterate through intervals. If the current interval overlaps with the previous one in your output list, merge them by updating end = max(prev.end, curr.end).",
            "Otherwise, append the current interval as a new non-overlapping range."
        ],
        "follow_ups": [
            {
                "question": "What if the intervals are arriving continuously as an infinite data stream?",
                "options": ["Sort the entire list on every arrival", "Maintain an Interval Tree or Segment Tree to query and merge in O(log N)", "Use Quickselect on start points"],
                "correct": "Maintain an Interval Tree or Segment Tree to query and merge in O(log N)",
                "explanation": "A self-balancing interval search tree or treap supports O(log N) dynamic insertions and overlap queries."
            }
        ],
        "optimal_time": "O(N log N)",
        "optimal_space": "O(N) for output",
        "url": "https://leetcode.com/problems/merge-intervals/"
    },

    # 5. MONOTONIC STACK
    {
        "title": "Daily Temperatures",
        "slug": "daily-temperatures",
        "topic_slug": "stacks-queues",
        "pattern": Problem.Pattern.MONOTONIC_STACK,
        "supporting_concepts": "Stack, Monotonic Decreasing, Array",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,FRONTEND,BACKEND,PRODUCT",
        "company_tags": "Amazon, Meta, Google",
        "description": "Given an array of integers temperatures represents the daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature. If there is no future day for which this is possible, keep answer[i] == 0 instead.",
        "examples": "Input: temperatures = [73,74,75,71,69,72,76,73] -> Output: [1,1,4,2,1,1,0,0]",
        "constraints": "1 <= temperatures.length <= 10^5\n30 <= temperatures[i] <= 100",
        "hints": [
            "To find the next greater element efficiently, maintain indices in a monotonic decreasing stack.",
            "Iterate through temperatures. While stack is not empty and current temp > temperatures[stack.top()], pop index and answer[idx] = curr_idx - idx.",
            "Push the current index onto the stack."
        ],
        "follow_ups": [
            {
                "question": "What is the total number of push and pop operations across the entire array of length N?",
                "options": ["O(N^2) in worst case", "Exactly 2N operations total, making it strictly O(N) amortized", "O(N log N)"],
                "correct": "Exactly 2N operations total, making it strictly O(N) amortized",
                "explanation": "Every element is pushed onto the stack exactly once and popped at most once."
            }
        ],
        "optimal_time": "O(N)",
        "optimal_space": "O(N)",
        "url": "https://leetcode.com/problems/daily-temperatures/"
    },

    # 6. BINARY SEARCH
    {
        "title": "Search in Rotated Sorted Array",
        "slug": "search-in-rotated-sorted-array",
        "topic_slug": "binary-search",
        "pattern": Problem.Pattern.BINARY_SEARCH,
        "supporting_concepts": "Array, Partitioning, Binary Search",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Meta, Google, Apple, Microsoft",
        "description": "There is an integer array nums sorted in ascending order (with distinct values). Prior to being passed to your function, nums is possibly rotated at an unknown pivot index k. Given the array nums after the possible rotation and an integer target, return the index of target if it is in nums, or -1 if it is not in nums.",
        "examples": "Input: nums = [4,5,6,7,0,1,2], target = 0 -> Output: 4\nInput: nums = [4,5,6,7,0,1,2], target = 3 -> Output: -1",
        "constraints": "1 <= nums.length <= 5000\n-10^4 <= nums[i] <= 10^4\nAll values of nums are unique.\nnums is an ascending array that is possibly rotated.",
        "hints": [
            "In any rotated sorted array, splitting at midpoint mid divides the array into at least one normally sorted half and one rotated half.",
            "Compare nums[left] with nums[mid] to determine which half is normally sorted.",
            "Check if target falls within the bounds of the sorted half. If yes, search that half; otherwise search the other half."
        ],
        "follow_ups": [
            {
                "question": "What happens to the time complexity if the array contains duplicate elements (e.g. [1,0,1,1,1])?",
                "options": ["Remains O(log N)", "Degrades to O(N) worst case because nums[left] == nums[mid] == nums[right] obscures which half is sorted", "Becomes O(1)"],
                "correct": "Degrades to O(N) worst case because nums[left] == nums[mid] == nums[right] obscures which half is sorted",
                "explanation": "When endpoints match mid, we must linearly decrement right or increment left, causing O(N) worst-case time."
            }
        ],
        "optimal_time": "O(log N)",
        "optimal_space": "O(1)",
        "url": "https://leetcode.com/problems/search-in-rotated-sorted-array/"
    },

    # 7. TREE BFS / DFS
    {
        "title": "Lowest Common Ancestor of a Binary Tree",
        "slug": "lowest-common-ancestor-of-a-binary-tree",
        "topic_slug": "trees",
        "pattern": Problem.Pattern.TREE_TRAVERSAL,
        "supporting_concepts": "Recursion, Tree DFS, Binary Tree",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Meta, Amazon, Microsoft, LinkedIn",
        "description": "Given a binary tree, find the lowest common ancestor (LCA) of two given nodes in the tree. According to the definition of LCA: The lowest common ancestor is defined between two nodes p and q as the lowest node in T that has both p and q as descendants (where we allow a node to be a descendant of itself).",
        "examples": "Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1 -> Output: 3",
        "constraints": "The number of nodes in the tree is in the range [2, 10^5].\n-10^9 <= Node.val <= 10^9\nAll Node.val are unique.\np != q\np and q will exist in the tree.",
        "hints": [
            "Use post-order DFS traversal. If root is null, p, or q, return root.",
            "Recursively search the left subtree and right subtree.",
            "If both left and right return non-null, the current root is the LCA. If only one returns non-null, pass that result up."
        ],
        "follow_ups": [
            {
                "question": "What if nodes p or q might NOT exist in the tree?",
                "options": ["The standard DFS still works unchanged", "We need a two-pass algorithm or a count accumulator to confirm both nodes were visited", "Tree traversal cannot solve it"],
                "correct": "We need a two-pass algorithm or a count accumulator to confirm both nodes were visited",
                "explanation": "If a node is missing, returning non-null upon finding p might falsely label p as LCA even if q doesn't exist."
            }
        ],
        "optimal_time": "O(N)",
        "optimal_space": "O(H) where H is tree height",
        "url": "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/"
    },

    # 8. TOP K ELEMENTS (HEAP)
    {
        "title": "Top K Frequent Elements",
        "slug": "top-k-frequent-elements",
        "topic_slug": "heaps",
        "pattern": Problem.Pattern.HEAP_TOP_K,
        "supporting_concepts": "Hash Table, Min-Heap, Bucket Sort",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Amazon, Meta, Google, Microsoft",
        "description": "Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.",
        "examples": "Input: nums = [1,1,1,2,2,3], k = 2 -> Output: [1,2]\nInput: nums = [1], k = 1 -> Output: [1]",
        "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4\nk is in the range [1, the number of unique elements in the array].",
        "hints": [
            "First build a frequency map of each number's count.",
            "Keep a min-heap of size k storing (count, num). When the heap exceeds size k, pop the smallest count.",
            "Alternatively, use Bucket Sort where the index represents frequency to achieve O(N) linear time."
        ],
        "follow_ups": [
            {
                "question": "How does Bucket Sort achieve O(N) compared to Heap's O(N log K)?",
                "options": ["By hashing the array", "By creating an array of buckets where index = frequency, bounded by array length N", "By using Radix Sort"],
                "correct": "By creating an array of buckets where index = frequency, bounded by array length N",
                "explanation": "Since maximum frequency is N, we can place items into buckets 1..N and collect the top k items from right to left in O(N)."
            }
        ],
        "optimal_time": "O(N) with Bucket Sort or O(N log K) with Heap",
        "optimal_space": "O(N)",
        "url": "https://leetcode.com/problems/top-k-frequent-elements/"
    },

    # 9. GRAPH TRAVERSAL (BFS/DFS)
    {
        "title": "Course Schedule",
        "slug": "course-schedule",
        "topic_slug": "graphs",
        "pattern": Problem.Pattern.GRAPH,
        "supporting_concepts": "Topological Sort, Kahn's BFS, Cycle Detection",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Google, Meta, Amazon, Microsoft",
        "description": "There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1. You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you must take course bi first if you want to take course ai. Return true if you can finish all courses, otherwise return false.",
        "examples": "Input: numCourses = 2, prerequisites = [[1,0]] -> Output: true\nInput: numCourses = 2, prerequisites = [[1,0],[0,1]] -> Output: false",
        "constraints": "1 <= numCourses <= 2000\n0 <= prerequisites.length <= 5000\nprerequisites[i].length == 2\n0 <= ai, bi < numCourses\nAll the pairs prerequisites[i] are unique.",
        "hints": [
            "This problem is equivalent to detecting if a directed graph has a cycle.",
            "Build an adjacency list and calculate the in-degree of every vertex.",
            "Use Kahn's Algorithm (BFS): Add vertices with in-degree 0 to a queue. For each popped vertex, reduce neighbors' in-degree. If total popped equals numCourses, no cycle exists."
        ],
        "follow_ups": [
            {
                "question": "If we also need to return the exact sequence of courses to take, what algorithm should we use?",
                "options": ["Dijkstra's Shortest Path", "Kahn's Topological Sort (recording popped order) or Post-order DFS reversal", "Bellman-Ford"],
                "correct": "Kahn's Topological Sort (recording popped order) or Post-order DFS reversal",
                "explanation": "Recording the order of nodes as they reach 0 in-degree yields a valid topological sort (Course Schedule II)."
            }
        ],
        "optimal_time": "O(V + E)",
        "optimal_space": "O(V + E)",
        "url": "https://leetcode.com/problems/course-schedule/"
    },

    # 10. DYNAMIC PROGRAMMING
    {
        "title": "Coin Change",
        "slug": "coin-change",
        "topic_slug": "dynamic-programming",
        "pattern": Problem.Pattern.DP,
        "supporting_concepts": "Bottom-Up Tabulation, Unbounded Knapsack, BFS",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Amazon, Google, Meta, Bloomberg",
        "description": "You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.",
        "examples": "Input: coins = [1,2,5], amount = 11 -> Output: 3 (5 + 5 + 1)\nInput: coins = [2], amount = 3 -> Output: -1",
        "constraints": "1 <= coins.length <= 12\n1 <= coins[i] <= 2^31 - 1\n0 <= amount <= 10^4",
        "hints": [
            "Define dp[i] as the minimum coins needed to make amount i.",
            "Base case: dp[0] = 0, and all other dp[i] = infinity.",
            "Transition: For each amount i from 1 to amount, for each coin c: if i - c >= 0, dp[i] = min(dp[i], dp[i - c] + 1)."
        ],
        "follow_ups": [
            {
                "question": "Why does a greedy approach (always taking the largest coin first) fail here?",
                "options": ["It doesn't fail, greedy is always optimal", "Counterexample: coins = [1, 3, 4], amount = 6. Greedy takes 4+1+1 (3 coins), optimal is 3+3 (2 coins)", "Because coins can be negative"],
                "correct": "Counterexample: coins = [1, 3, 4], amount = 6. Greedy takes 4+1+1 (3 coins), optimal is 3+3 (2 coins)",
                "explanation": "Standard coin systems (like US currency) are canonical systems where greedy works, but arbitrary coin systems lack the greedy-choice property."
            }
        ],
        "optimal_time": "O(amount * len(coins))",
        "optimal_space": "O(amount)",
        "url": "https://leetcode.com/problems/coin-change/"
    },
    {
        "title": "Word Break",
        "slug": "word-break",
        "topic_slug": "dynamic-programming",
        "pattern": Problem.Pattern.DP,
        "supporting_concepts": "Hash Set, Memoization, Trie",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Meta, Amazon, Google, Uber",
        "description": "Given a string s and a dictionary of strings wordDict, return true if s can be segmented into a space-separated sequence of one or more dictionary words. Note that the same word in the dictionary may be reused multiple times in the segmentation.",
        "examples": "Input: s = 'leetcode', wordDict = ['leet','code'] -> Output: true\nInput: s = 'applepenapple', wordDict = ['apple','pen'] -> Output: true",
        "constraints": "1 <= s.length <= 300\n1 <= wordDict.length <= 1000\n1 <= wordDict[i].length <= 20\ns and wordDict[i] consist of only lowercase English letters.",
        "hints": [
            "Store wordDict in a hash set for O(1) lookups.",
            "Define dp[i] = true if substring s[0...i] can be segmented.",
            "For each index i, check all previous indices j: if dp[j] is true and s[j...i] is in the word set, set dp[i] = true and break."
        ],
        "follow_ups": [
            {
                "question": "How can you optimize the inner loop if words have a maximum length max_len?",
                "options": ["Check all N indices regardless", "Only test j down to max(0, i - max_len), reducing transitions from O(N) to O(max_len)", "Sort the wordDict alphabetically"],
                "correct": "Only test j down to max(0, i - max_len), reducing transitions from O(N) to O(max_len)",
                "explanation": "Since no word exceeds max_len, checking j beyond max_len is guaranteed to fail, reducing time to O(N * max_len)."
            }
        ],
        "optimal_time": "O(N^2) or O(N * max_len)",
        "optimal_space": "O(N) + O(dictionary_words)",
        "url": "https://leetcode.com/problems/word-break/"
    },

    # 11. BACKTRACKING
    {
        "title": "Subsets",
        "slug": "subsets",
        "topic_slug": "backtracking",
        "pattern": Problem.Pattern.BACKTRACKING,
        "supporting_concepts": "Recursion, Cascading, Bitmasking",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Meta, Amazon, Microsoft",
        "description": "Given an integer array nums of unique elements, return all possible subsets (the power set). The solution set must not contain duplicate subsets. Return the solution in any order.",
        "examples": "Input: nums = [1,2,3] -> Output: [[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]",
        "constraints": "1 <= nums.length <= 10\n-10 <= nums[i] <= 10\nAll the numbers of nums are unique.",
        "hints": [
            "For every element, you have two choices: include it in the current subset, or exclude it.",
            "Implement a recursive backtrack(start_idx, current_subset) function.",
            "At each step, append a copy of current_subset to results, then loop i from start_idx to end, append nums[i], recurse with i + 1, and pop."
        ],
        "follow_ups": [
            {
                "question": "How many total subsets exist for an array of size N, and what is the exact time complexity?",
                "options": ["N! subsets, O(N!)", "2^N subsets, O(N * 2^N) time to copy subsets", "2^N subsets, O(2^N)"],
                "correct": "2^N subsets, O(N * 2^N) time to copy subsets",
                "explanation": "There are 2^N subsets and creating/copying each takes on average O(N) time, giving O(N * 2^N)."
            }
        ],
        "optimal_time": "O(N * 2^N)",
        "optimal_space": "O(N) recursion stack",
        "url": "https://leetcode.com/problems/subsets/"
    },

    # 12. OTHER / DESIGN
    {
        "title": "LRU Cache",
        "slug": "lru-cache",
        "topic_slug": "stacks-queues",
        "pattern": Problem.Pattern.OTHER,
        "supporting_concepts": "Doubly Linked List, Hash Table, System Design",
        "difficulty": Problem.Difficulty.MEDIUM,
        "target_tracks": "GENERAL,BACKEND,PRODUCT",
        "company_tags": "Amazon, Google, Meta, Apple, Microsoft, Netflix",
        "description": "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache. Implement the LRUCache class with get(key) and put(key, value) in O(1) average time complexity.",
        "examples": "LRUCache lRUCache = new LRUCache(2);\nlRUCache.put(1, 1);\nlRUCache.put(2, 2);\nlRUCache.get(1); // returns 1\nlRUCache.put(3, 3); // evicts key 2\nlRUCache.get(2); // returns -1 (not found)",
        "constraints": "1 <= capacity <= 3000\n0 <= key <= 10^4\n0 <= value <= 10^5\nAt most 2 * 10^5 calls to get and put.",
        "hints": [
            "To achieve O(1) get and put, you need fast key lookup (Hash Map) and fast node reordering (Doubly Linked List).",
            "Store Map<Key, Node>. The doubly linked list maintains usage order: MRU at head, LRU at tail.",
            "Use pseudo head and tail dummy nodes to eliminate edge cases when inserting and deleting."
        ],
        "follow_ups": [
            {
                "question": "How would you make this LRU Cache thread-safe for a high-concurrency production backend service?",
                "options": ["Synchronize the entire get and put methods with a global lock", "Use ReadWriteLock with concurrent lock striping or segmented hashing", "Thread safety is unnecessary in caches"],
                "correct": "Use ReadWriteLock with concurrent lock striping or segmented hashing",
                "explanation": "A single global lock creates a severe bottleneck; segmented striping (like ConcurrentHashMap or Guava Cache) allows concurrent reads and writes."
            }
        ],
        "optimal_time": "O(1) for get and put",
        "optimal_space": "O(capacity)",
        "url": "https://leetcode.com/problems/lru-cache/"
    }
]


class Command(BaseCommand):
    help = "Seeds the Canonical Interview Question Bank with high-yield classic problems."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Canonical Interview Question Bank..."))
        seeded_count = 0
        updated_count = 0

        for item in CANONICAL_QUESTIONS_DATA:
            topic = Topic.objects.filter(slug=item.get("topic_slug", "")).first()
            if not topic:
                topic = Topic.objects.first()

            obj, created = CanonicalInterviewQuestion.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "topic": topic,
                    "pattern": item["pattern"],
                    "supporting_concepts": item.get("supporting_concepts", ""),
                    "difficulty": item["difficulty"],
                    "target_tracks": item.get("target_tracks", "GENERAL,BACKEND,PRODUCT"),
                    "company_tags": item.get("company_tags", ""),
                    "description": item["description"],
                    "examples": item.get("examples", ""),
                    "constraints": item.get("constraints", ""),
                    "hints": item.get("hints", []),
                    "follow_ups": item.get("follow_ups", []),
                    "optimal_time_complexity": item.get("optimal_time", ""),
                    "optimal_space_complexity": item.get("optimal_space", ""),
                    "leetcode_url": item.get("url", ""),
                }
            )
            if created:
                seeded_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded Canonical Questions! Added {seeded_count} new, updated {updated_count} existing."
        ))
