from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from tracker.models import Topic, Problem, Attempt, RevisionSchedule


class Command(BaseCommand):
    help = "Populates sample DSA problems, attempts, and SM-2 schedules for testing and demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="demo",
            help="Username for sample data owner (default: demo)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com", "is_staff": True}
        )
        if created:
            user.set_password("demo1234")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created demo user '{username}' (password: demo1234)"))
        else:
            self.stdout.write(f"Using existing user '{username}'")

        sample_problems = [
            {
                "title": "Two Sum",
                "topic": "Arrays",
                "pattern": Problem.Pattern.TWO_POINTER,
                "difficulty": Problem.Difficulty.EASY,
                "link": "https://leetcode.com/problems/two-sum/",
                "notes": "Hash map lookup in O(N) time and O(N) space. Store value -> index mapping. Complement is target - num.",
                "is_mastered": True,
                "attempts": [
                    {"mins": 14, "success": True, "notes": "One-pass hash table with instant lookup."},
                    {"mins": 25, "success": True, "notes": "Initial brute force O(N^2) before optimizing."},
                ],
                "due_today": True,
                "reps": 3,
                "interval": 1,
            },
            {
                "title": "Longest Substring Without Repeating Characters",
                "topic": "Strings",
                "pattern": Problem.Pattern.SLIDING_WINDOW,
                "difficulty": Problem.Difficulty.MEDIUM,
                "link": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
                "notes": "Sliding window with character index hash table. Move right pointer, jump left pointer to max(left, last_seen[char] + 1).",
                "is_mastered": True,
                "attempts": [
                    {"mins": 28, "success": True, "notes": "Handled duplicate jumping pointer condition cleanly."},
                    {"mins": 35, "success": False, "notes": "Forgot max(left, ...) leading to backward pointer jumps."},
                ],
                "due_today": True,
                "reps": 2,
                "interval": 6,
            },
            {
                "title": "Reverse Linked List",
                "topic": "Linked Lists",
                "pattern": Problem.Pattern.OTHER,
                "difficulty": Problem.Difficulty.EASY,
                "link": "https://leetcode.com/problems/reverse-linked-list/",
                "notes": "Iterative three-pointer approach (prev, curr, nxt). Maintain prev = None initially. Can also be done recursively.",
                "is_mastered": True,
                "attempts": [
                    {"mins": 8, "success": True, "notes": "Clean iterative 3-pointer swap in O(1) space."},
                ],
                "due_today": False,
                "reps": 4,
                "interval": 14,
            },
            {
                "title": "Course Schedule (Cycle Detection)",
                "topic": "Graphs",
                "pattern": Problem.Pattern.GRAPH,
                "difficulty": Problem.Difficulty.MEDIUM,
                "link": "https://leetcode.com/problems/course-schedule/",
                "notes": "Topological sort via Kahn's algorithm (in-degrees array + queue) or DFS 3-state coloring (unvisited=0, visiting=1, visited=2).",
                "is_mastered": False,
                "attempts": [
                    {"mins": 42, "success": True, "notes": "Kahn's algorithm with queue felt easier to avoid recursion stack."},
                    {"mins": 55, "success": False, "notes": "Missed disconnected component cycle detection in DFS."},
                ],
                "due_today": True,
                "reps": 1,
                "interval": 1,
            },
            {
                "title": "Coin Change",
                "topic": "Dynamic Programming",
                "pattern": Problem.Pattern.DP,
                "difficulty": Problem.Difficulty.MEDIUM,
                "link": "https://leetcode.com/problems/coin-change/",
                "notes": "Bottom-up 1D DP table. dp[a] = min(dp[a], dp[a - c] + 1) for each coin c. Initialize with float('inf') and dp[0] = 0.",
                "is_mastered": False,
                "attempts": [
                    {"mins": 38, "success": True, "notes": "Bottom-up tabulation worked smoothly once base case dp[0]=0 was set."},
                ],
                "due_today": False,
                "reps": 1,
                "interval": 3,
            },
            {
                "title": "Trapping Rain Water",
                "topic": "Arrays",
                "pattern": Problem.Pattern.TWO_POINTER,
                "difficulty": Problem.Difficulty.HARD,
                "link": "https://leetcode.com/problems/trapping-rain-water/",
                "notes": "Two-pointer approach with left_max and right_max tracking. Move the pointer on the smaller max side. O(N) time, O(1) space.",
                "is_mastered": False,
                "attempts": [
                    {"mins": 48, "success": True, "notes": "Understood the two-pointer invariant: water level trapped is bounded by the lower boundary."},
                    {"mins": 60, "success": False, "notes": "Struggled with the monotonic stack approach initially."},
                ],
                "due_today": True,
                "reps": 1,
                "interval": 1,
            },
            {
                "title": "Binary Tree Maximum Path Sum",
                "topic": "Trees",
                "pattern": Problem.Pattern.OTHER,
                "difficulty": Problem.Difficulty.HARD,
                "link": "https://leetcode.com/problems/binary-tree-maximum-path-sum/",
                "notes": "Post-order traversal returning max path down one branch (clamped to 0). Update global max with left_gain + right_gain + node.val.",
                "is_mastered": False,
                "attempts": [
                    {"mins": 45, "success": True, "notes": "Critical insight: return max branch sum up, but calculate inverted-V path sum at each node."},
                ],
                "due_today": False,
                "reps": 2,
                "interval": 6,
            },
            {
                "title": "Search in Rotated Sorted Array",
                "topic": "Binary Search",
                "pattern": Problem.Pattern.BINARY_SEARCH,
                "difficulty": Problem.Difficulty.MEDIUM,
                "link": "https://leetcode.com/problems/search-in-rotated-sorted-array/",
                "notes": "Modified binary search: determine which half is normally sorted, then check if target lies within that sorted range. O(log N).",
                "is_mastered": True,
                "attempts": [
                    {"mins": 22, "success": True, "notes": "Clean edge-case handling on <= and >= boundaries."},
                ],
                "due_today": False,
                "reps": 3,
                "interval": 12,
            },
            {
                "title": "Word Search",
                "topic": "Backtracking",
                "pattern": Problem.Pattern.BACKTRACKING,
                "difficulty": Problem.Difficulty.MEDIUM,
                "link": "https://leetcode.com/problems/word-search/",
                "notes": "DFS with grid backtracking. Mark visited in-place by temporarily mutating board[r][c] = '#' and restoring on return.",
                "is_mastered": False,
                "attempts": [
                    {"mins": 36, "success": True, "notes": "In-place board mutation avoids extra O(M*N) memory set allocation."},
                ],
                "due_today": False,
                "reps": 1,
                "interval": 2,
            },
        ]

        today = timezone.now().date()
        created_count = 0

        for p_data in sample_problems:
            topic, _ = Topic.objects.get_or_create(
                name=p_data["topic"],
                defaults={"slug": p_data["topic"].lower().replace(" ", "-")}
            )
            problem, prob_created = Problem.objects.get_or_create(
                user=user,
                title=p_data["title"],
                defaults={
                    "topic": topic,
                    "pattern": p_data["pattern"],
                    "difficulty": p_data["difficulty"],
                    "link": p_data["link"],
                    "notes": p_data["notes"],
                    "is_mastered": p_data["is_mastered"],
                }
            )
            if prob_created:
                created_count += 1
                # Seed attempts
                for att in p_data["attempts"]:
                    Attempt.objects.create(
                        problem=problem,
                        time_taken_minutes=att["mins"],
                        was_successful=att["success"],
                        approach_notes=att["notes"],
                    )

                # Seed revision schedule
                next_date = today if p_data["due_today"] else today + timedelta(days=p_data["interval"])
                RevisionSchedule.objects.create(
                    problem=problem,
                    ease_factor=2.5,
                    interval_days=p_data["interval"],
                    repetitions=p_data["reps"],
                    next_review_date=next_date,
                )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully populated {created_count} sample problems with attempts and SM-2 schedules for user '{username}'.")
        )
