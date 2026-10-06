"""
Multi-Factor DSA Pattern Mastery Engine & Algorithmic Diagnostics.

Calculates true algorithmic mastery across 5 distinct dimensions:
1. Difficulty-Weighted Volume Depth
2. First-Attempt Accuracy (anti-brute-force)
3. Speed Velocity (vs target interview benchmarks)
4. SM-2 Spaced Repetition Retention Decay
5. Bayesian Confidence Damping (eliminates the 1-problem 100% mastery cold-start anomaly)
"""

from collections import defaultdict
from django.utils import timezone
from tracker.models import Problem, Attempt, RevisionSchedule
from .skill_graph import SKILL_NODES, SKILL_GRAPH_BRANCHES, get_unlocked_frontiers


def calculate_user_mastery_matrix(user) -> dict:
    """
    Computes comprehensive pattern mastery and diagnostic classifications
    for all 16 algorithmic patterns in a single highly-optimized pass.

    Returns:
        {
            "patterns": {
                "TWO_POINTER": {
                    "key": "TWO_POINTER",
                    "name": "Two Pointers",
                    "mastery_score": 78.4,
                    "status": "STRONG",  # STRONG, WEAK, FORGOTTEN, OVER_RELIANCE, DEVELOPING, UNEXPLORED
                    "status_label": "Strong Pattern",
                    "status_color": "#10b981",
                    "total_solved": 14,
                    "easy_count": 6,
                    "med_count": 7,
                    "hard_count": 1,
                    "first_attempt_accuracy": 71.4,
                    "avg_solve_time": 21.3,
                    "benchmark_time": 25,
                    "retention_score": 82.0,
                    "confidence": 1.0,
                    "branch": "arrays_strings",
                },
                ...
            },
            "diagnostics": {
                "strong": [...],
                "weak": [...],
                "forgotten": [...],
                "over_reliance": [...],
                "next_frontiers": [...],
            },
            "branches": [
                {
                    "id": "arrays_strings",
                    "name": "Arrays & Sequence Processing",
                    "mastery_score": 64.2,
                    "patterns_count": 6,
                    "mastered_count": 3,
                },
                ...
            ],
            "overall_readiness_score": 58.7,
            "total_solved": 45,
            "mastered_patterns_count": 4,
        }
    """
    now = timezone.now()
    today = now.date()

    # 1. Single query for all problems of this user with related revision and attempts
    problems = (
        Problem.objects.filter(user=user)
        .select_related("revision", "topic")
        .prefetch_related("attempts")
    )

    # Group problems and attempts in memory by pattern
    pattern_problems = defaultdict(list)
    branch_counts = defaultdict(int)
    total_solved_all = 0

    for p in problems:
        pattern_problems[p.pattern].append(p)
        total_solved_all += 1
        node = SKILL_NODES.get(p.pattern)
        if node:
            branch_counts[node["branch"]] += 1

    patterns_result = {}
    strong_list = []
    weak_list = []
    forgotten_list = []
    over_reliance_list = []
    mastered_keys = set()

    for pattern_key, node in SKILL_NODES.items():
        plist = pattern_problems.get(pattern_key, [])
        total_solved = len(plist)

        easy_count = sum(1 for p in plist if p.difficulty == Problem.Difficulty.EASY)
        med_count = sum(1 for p in plist if p.difficulty == Problem.Difficulty.MEDIUM)
        hard_count = sum(1 for p in plist if p.difficulty == Problem.Difficulty.HARD)

        # 1. Depth Score (Weighted difficulty: Easy=1, Med=2.5, Hard=5; target = 25 pts)
        depth_points = (easy_count * 1.0) + (med_count * 2.5) + (hard_count * 5.0)
        depth_score = min(100.0, (depth_points / 25.0) * 100.0)

        # 2. First-Attempt Accuracy
        first_success_count = 0
        all_attempts = []
        solve_times = []
        revision_ease_factors = []
        overdue_days_max = 0
        latest_solved_at = None

        for p in plist:
            p_attempts = list(p.attempts.all())
            all_attempts.extend(p_attempts)

            if p_attempts:
                # Chronologically first attempt
                earliest_att = min(p_attempts, key=lambda a: a.solved_at)
                if earliest_att.was_successful:
                    first_success_count += 1

                for att in p_attempts:
                    if att.was_successful:
                        solve_times.append(att.time_taken_minutes)
                        if not latest_solved_at or att.solved_at > latest_solved_at:
                            latest_solved_at = att.solved_at

            # SM-2 Revision metrics
            if hasattr(p, "revision"):
                rev = p.revision
                revision_ease_factors.append(rev.ease_factor)
                if rev.next_review_date < today:
                    delta_overdue = (today - rev.next_review_date).days
                    if delta_overdue > overdue_days_max:
                        overdue_days_max = delta_overdue

        if total_solved > 0:
            first_attempt_acc = (first_success_count / total_solved) * 100.0
        else:
            first_attempt_acc = 50.0

        # 3. Solve Speed Velocity
        avg_solve_time = (sum(solve_times) / len(solve_times)) if solve_times else 0
        benchmarks = node.get("benchmarks", {"EASY": 15, "MEDIUM": 25, "HARD": 45})
        # Weighted benchmark based on problems solved
        if total_solved > 0:
            expected_bench = (
                (easy_count * benchmarks.get("EASY", 15)) +
                (med_count * benchmarks.get("MEDIUM", 25)) +
                (hard_count * benchmarks.get("HARD", 45))
            ) / total_solved
        else:
            expected_bench = benchmarks.get("MEDIUM", 25)

        if avg_solve_time <= 0:
            speed_score = 50.0
        elif avg_solve_time <= expected_bench:
            speed_score = min(100.0, 80.0 + (1.0 - (avg_solve_time / expected_bench)) * 20.0)
        else:
            ratio = (avg_solve_time - expected_bench) / expected_bench
            speed_score = max(15.0, 80.0 - ratio * 50.0)

        # 4. SM-2 Spaced Repetition Retention Score
        if revision_ease_factors:
            avg_ef = sum(revision_ease_factors) / len(revision_ease_factors)
            # EF ranges from 1.3 to 2.5+ -> map to 0..100
            base_retention = max(0.0, min(100.0, ((avg_ef - 1.3) / 1.2) * 100.0))
        else:
            base_retention = 60.0

        # Inactivity & Overdue penalty
        overdue_penalty = min(35.0, overdue_days_max * 1.5)
        inactivity_days = (now - latest_solved_at).days if latest_solved_at else 0
        inactivity_penalty = min(30.0, max(0, inactivity_days - 30) * 0.75) if total_solved > 0 else 0

        retention_score = max(10.0, min(100.0, base_retention - overdue_penalty - inactivity_penalty))

        # 5. Bayesian Confidence Damping
        # Full confidence achieved at 5+ problems
        confidence = min(1.0, total_solved / 5.0)

        raw_mastery = (
            (0.35 * depth_score) +
            (0.25 * first_attempt_acc) +
            (0.20 * speed_score) +
            (0.20 * retention_score)
        )
        composite_mastery = round(raw_mastery * confidence, 1)

        # Classify status
        branch_key = node["branch"]
        branch_total = branch_counts.get(branch_key, 0)
        is_over_reliant = (
            total_solved >= 8 and
            branch_total > 0 and
            (total_solved / branch_total) >= 0.55
        )

        if total_solved == 0:
            status = "UNEXPLORED"
            status_label = "Unexplored"
            status_color = "#6b7280"
        elif composite_mastery >= 70.0 and retention_score >= 60.0:
            status = "STRONG"
            status_label = "Strong Mastery"
            status_color = "#10b981"
            strong_list.append(pattern_key)
            mastered_keys.add(pattern_key)
        elif (retention_score < 45.0 or overdue_days_max >= 10 or inactivity_days > 45) and total_solved >= 2:
            status = "FORGOTTEN"
            status_label = "Decayed / Needs Review"
            status_color = "#eab308"
            forgotten_list.append(pattern_key)
        elif is_over_reliant:
            status = "OVER_RELIANCE"
            status_label = "Over-Reliance"
            status_color = "#f97316"
            over_reliance_list.append(pattern_key)
            if composite_mastery >= 70.0:
                mastered_keys.add(pattern_key)
        elif first_attempt_acc < 50.0 or speed_score < 45.0 or composite_mastery < 45.0:
            status = "WEAK"
            status_label = "Needs Practice"
            status_color = "#ef4444"
            weak_list.append(pattern_key)
        else:
            status = "DEVELOPING"
            status_label = "Developing"
            status_color = "#3b82f6"

        patterns_result[pattern_key] = {
            "key": pattern_key,
            "name": node["name"],
            "branch": node["branch"],
            "difficulty_baseline": node["difficulty_baseline"],
            "interview_weight": node["interview_weight"],
            "description": node["description"],
            "why_it_matters": node["why_it_matters"],
            "mastery_score": composite_mastery,
            "status": status,
            "status_label": status_label,
            "status_color": status_color,
            "total_solved": total_solved,
            "easy_count": easy_count,
            "med_count": med_count,
            "hard_count": hard_count,
            "first_attempt_accuracy": round(first_attempt_acc, 1),
            "avg_solve_time": round(avg_solve_time, 1),
            "benchmark_time": round(expected_bench, 1),
            "retention_score": round(retention_score, 1),
            "confidence_pct": round(confidence * 100, 0),
            "overdue_days": overdue_days_max,
        }

    # Branch Mastery Rollups
    branches_result = []
    total_branch_mastery = 0.0

    for b in SKILL_GRAPH_BRANCHES:
        b_patterns = [patterns_result[pk] for pk in b["patterns"] if pk in patterns_result]
        b_count = len(b_patterns)
        b_mastery = round(sum(p["mastery_score"] for p in b_patterns) / b_count, 1) if b_count else 0.0
        b_mastered_count = sum(1 for p in b_patterns if p["status"] == "STRONG")
        total_branch_mastery += b_mastery

        branches_result.append({
            "id": b["id"],
            "name": b["name"],
            "icon": b["icon"],
            "color": b["color"],
            "mastery_score": b_mastery,
            "patterns": b_patterns,
            "patterns_count": b_count,
            "mastered_count": b_mastered_count,
        })

    overall_readiness = round(total_branch_mastery / len(SKILL_GRAPH_BRANCHES), 1) if SKILL_GRAPH_BRANCHES else 0.0

    # Calculate Next Frontier patterns
    unlocked_frontiers = get_unlocked_frontiers(mastered_keys)

    return {
        "patterns": patterns_result,
        "diagnostics": {
            "strong": [patterns_result[k] for k in strong_list],
            "weak": [patterns_result[k] for k in weak_list],
            "forgotten": [patterns_result[k] for k in forgotten_list],
            "over_reliance": [patterns_result[k] for k in over_reliance_list],
            "next_frontiers": unlocked_frontiers[:4],
        },
        "branches": branches_result,
        "overall_readiness_score": overall_readiness,
        "total_solved": total_solved_all,
        "mastered_patterns_count": len(mastered_keys),
    }
