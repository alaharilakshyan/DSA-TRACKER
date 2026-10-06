"""
Topological DSA Skill Graph Taxonomy & Knowledge Architecture.

Defines the hierarchical relationship between algorithmic patterns,
directed prerequisite dependencies, and interview time benchmarks.
"""

SKILL_GRAPH_BRANCHES = [
    {
        "id": "arrays_strings",
        "name": "Arrays & Sequence Processing",
        "icon": "bi-view-list",
        "color": "#3b82f6",
        "patterns": [
            "TWO_POINTER",
            "FAST_SLOW",
            "SLIDING_WINDOW",
            "INTERVALS",
            "MONOTONIC_STACK",
            "BINARY_SEARCH",
        ],
    },
    {
        "id": "trees_tries",
        "name": "Hierarchical & Tree Structures",
        "icon": "bi-diagram-3",
        "color": "#10b981",
        "patterns": [
            "TREE_TRAVERSAL",
            "TRIE",
            "HEAP_TOP_K",
        ],
    },
    {
        "id": "graphs_networks",
        "name": "Graphs & Connected Components",
        "icon": "bi-share-fill",
        "color": "#8b5cf6",
        "patterns": [
            "GRAPH",
            "UNION_FIND",
        ],
    },
    {
        "id": "dp_optimization",
        "name": "Optimization & State Search",
        "icon": "bi-lightning-charge-fill",
        "color": "#f59e0b",
        "patterns": [
            "GREEDY",
            "BACKTRACKING",
            "DP",
            "BIT_MANIPULATION",
            "OTHER",
        ],
    },
]

SKILL_NODES = {
    "TWO_POINTER": {
        "key": "TWO_POINTER",
        "name": "Two Pointers",
        "branch": "arrays_strings",
        "prerequisites": [],
        "difficulty_baseline": "EASY",
        "interview_weight": 95,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 40},
        "description": "Pointers moving in tandem or opposite directions to search pairs or partition in linear time.",
        "why_it_matters": "Eliminates nested loops to bring O(N^2) brute force down to O(N) linear time.",
    },
    "FAST_SLOW": {
        "key": "FAST_SLOW",
        "name": "Fast & Slow Pointers",
        "branch": "arrays_strings",
        "prerequisites": ["TWO_POINTER"],
        "difficulty_baseline": "EASY",
        "interview_weight": 75,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 40},
        "description": "Floyd's Tortoise and Hare algorithm for cycle detection, midpoint location, and cyclic arrays.",
        "why_it_matters": "Enables cycle detection in O(1) auxiliary space without hash sets.",
    },
    "SLIDING_WINDOW": {
        "key": "SLIDING_WINDOW",
        "name": "Sliding Window",
        "branch": "arrays_strings",
        "prerequisites": ["TWO_POINTER"],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 95,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 45},
        "description": "Expanding and contracting subarray bounds to track contiguous state without recomputation.",
        "why_it_matters": "Massively popular in Big Tech interviews for substring/subarray optimization problems.",
    },
    "INTERVALS": {
        "key": "INTERVALS",
        "name": "Merge Intervals",
        "branch": "arrays_strings",
        "prerequisites": ["TWO_POINTER"],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 85,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 45},
        "description": "Sorting and scanning overlapping interval ranges to insert, merge, or eliminate conflicts.",
        "why_it_matters": "Core building block for calendar scheduling, memory allocation, and range problems.",
    },
    "MONOTONIC_STACK": {
        "key": "MONOTONIC_STACK",
        "name": "Monotonic Stack / Queue",
        "branch": "arrays_strings",
        "prerequisites": ["TWO_POINTER"],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 80,
        "benchmarks": {"EASY": 20, "MEDIUM": 30, "HARD": 50},
        "description": "Maintaining an ordered stack or deque to answer 'next greater/smaller element' in O(N).",
        "why_it_matters": "Solves complex range extrema (e.g. histogram rectangles, daily temperatures) in linear time.",
    },
    "BINARY_SEARCH": {
        "key": "BINARY_SEARCH",
        "name": "Binary Search",
        "branch": "arrays_strings",
        "prerequisites": [],
        "difficulty_baseline": "EASY",
        "interview_weight": 90,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 45},
        "description": "Logarithmic search over sorted arrays, rotated arrays, and monotonic predicate search spaces.",
        "why_it_matters": "Reduces O(N) search to O(log N). Critical for search-the-answer optimization techniques.",
    },
    "TREE_TRAVERSAL": {
        "key": "TREE_TRAVERSAL",
        "name": "Tree BFS / DFS",
        "branch": "trees_tries",
        "prerequisites": [],
        "difficulty_baseline": "EASY",
        "interview_weight": 95,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 45},
        "description": "Recursive post/pre/in-order depth exploration and queue-based level-order breadth traversal.",
        "why_it_matters": "Fundamental recursive foundation for almost all advanced graph and backtracking algorithms.",
    },
    "TRIE": {
        "key": "TRIE",
        "name": "Trie / Prefix Tree",
        "branch": "trees_tries",
        "prerequisites": ["TREE_TRAVERSAL"],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 70,
        "benchmarks": {"EASY": 20, "MEDIUM": 30, "HARD": 45},
        "description": "N-ary tree structure for fast string prefix searching, auto-complete, and IP routing tables.",
        "why_it_matters": "Provides O(L) prefix search regardless of the number of dictionary keys.",
    },
    "HEAP_TOP_K": {
        "key": "HEAP_TOP_K",
        "name": "Top 'K' Elements (Heap)",
        "branch": "trees_tries",
        "prerequisites": [],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 85,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 45},
        "description": "Min-heap and max-heap prioritization for streaming medians, task scheduling, and top K items.",
        "why_it_matters": "Avoids O(N log N) full sorting when only K elements or extreme values are needed in O(N log K).",
    },
    "GRAPH": {
        "key": "GRAPH",
        "name": "Graph Traversal (BFS/DFS)",
        "branch": "graphs_networks",
        "prerequisites": ["TREE_TRAVERSAL"],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 95,
        "benchmarks": {"EASY": 20, "MEDIUM": 30, "HARD": 50},
        "description": "Exploration of vertex-edge topologies with visited sets, cycle detection, and topological sorting.",
        "why_it_matters": "Models dependency resolution, networks, social graphs, and maze pathfinding.",
    },
    "UNION_FIND": {
        "key": "UNION_FIND",
        "name": "Union Find / Disjoint Set",
        "branch": "graphs_networks",
        "prerequisites": ["GRAPH"],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 75,
        "benchmarks": {"EASY": 20, "MEDIUM": 30, "HARD": 50},
        "description": "Path compression and union-by-rank for near-constant time connected component tracking.",
        "why_it_matters": "Solves dynamic connectivity and Kruskal's Minimum Spanning Tree in nearly O(1) amortized time.",
    },
    "GREEDY": {
        "key": "GREEDY",
        "name": "Greedy",
        "branch": "dp_optimization",
        "prerequisites": ["TWO_POINTER"],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 80,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 45},
        "description": "Making the locally optimal choice at each step to reach a global optimum.",
        "why_it_matters": "Yields simple O(N) or O(N log N) solutions when optimal substructure and greedy choice hold.",
    },
    "BACKTRACKING": {
        "key": "BACKTRACKING",
        "name": "Backtracking",
        "branch": "dp_optimization",
        "prerequisites": ["TREE_TRAVERSAL"],
        "difficulty_baseline": "MEDIUM",
        "interview_weight": 85,
        "benchmarks": {"EASY": 20, "MEDIUM": 30, "HARD": 50},
        "description": "Exhaustive state-space tree traversal with pruning for permutations, combinations, and N-Queens.",
        "why_it_matters": "The gateway to understanding search space trees and transitioning into Dynamic Programming.",
    },
    "DP": {
        "key": "DP",
        "name": "Dynamic Programming",
        "branch": "dp_optimization",
        "prerequisites": ["BACKTRACKING"],
        "difficulty_baseline": "HARD",
        "interview_weight": 95,
        "benchmarks": {"EASY": 20, "MEDIUM": 35, "HARD": 55},
        "description": "Breaking problems into overlapping subproblems solved via memoization or bottom-up tabulation.",
        "why_it_matters": "The ultimate differentiator in technical interviews for proving algorithmic maturity.",
    },
    "BIT_MANIPULATION": {
        "key": "BIT_MANIPULATION",
        "name": "Bit Manipulation",
        "branch": "dp_optimization",
        "prerequisites": [],
        "difficulty_baseline": "EASY",
        "interview_weight": 65,
        "benchmarks": {"EASY": 15, "MEDIUM": 20, "HARD": 40},
        "description": "Bitwise XOR, AND, OR bitmask state encoding for subset representations and space reduction.",
        "why_it_matters": "Enables state compression in advanced DP and O(1) mathematical trickery.",
    },
    "OTHER": {
        "key": "OTHER",
        "name": "Other / General",
        "branch": "dp_optimization",
        "prerequisites": [],
        "difficulty_baseline": "EASY",
        "interview_weight": 60,
        "benchmarks": {"EASY": 15, "MEDIUM": 25, "HARD": 45},
        "description": "Composite problem types, mathematical calculations, and custom OOP data structure design.",
        "why_it_matters": "Tests software engineering hygiene and clean implementation of custom constraints.",
    },
}


def get_skill_graph_nodes() -> dict:
    """Returns all nodes in the skill graph."""
    return SKILL_NODES


def get_skill_graph_edges() -> list:
    """
    Returns list of directed prerequisite edges:
    [{ 'from': 'TWO_POINTER', 'to': 'SLIDING_WINDOW' }, ...]
    """
    edges = []
    for target_key, node in SKILL_NODES.items():
        for source_key in node.get("prerequisites", []):
            edges.append({
                "from": source_key,
                "to": target_key,
                "from_name": SKILL_NODES.get(source_key, {}).get("name", source_key),
                "to_name": node.get("name", target_key),
            })
    return edges


def get_pattern_meta(pattern_key: str) -> dict:
    """Returns metadata for a given pattern key or default OTHER."""
    return SKILL_NODES.get(pattern_key, SKILL_NODES["OTHER"])


def get_unlocked_frontiers(mastered_patterns: set) -> list:
    """
    Calculates the 'Next Frontier' of patterns a candidate should learn.
    A pattern is unlocked if all its prerequisites are mastered,
    but the pattern itself is not yet mastered.
    """
    frontiers = []
    for key, node in SKILL_NODES.items():
        if key in mastered_patterns:
            continue
        prereqs = node.get("prerequisites", [])
        if not prereqs or all(p in mastered_patterns for p in prereqs):
            frontiers.append({
                "key": key,
                "name": node["name"],
                "branch": node["branch"],
                "description": node["description"],
                "interview_weight": node["interview_weight"],
                "difficulty_baseline": node["difficulty_baseline"],
            })
    # Sort by interview importance descending
    frontiers.sort(key=lambda x: x["interview_weight"], reverse=True)
    return frontiers
