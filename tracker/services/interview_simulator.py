"""
Interview Readiness Simulator & Diagnostic Evaluation Engine.

Provides history-aware problem selection, tiered hints with score penalties,
realistic interviewer follow-up questions, and 5-dimensional candidate scoring.
Automatically connects with SM-2 Spaced Repetition Queue for failed patterns.
"""

from datetime import timedelta
import random
from django.utils import timezone
from tracker.models import (
    CanonicalInterviewQuestion,
    InterviewSession,
    InterviewQuestionAttempt,
    InterviewReport,
    Problem,
    RevisionSchedule,
    Topic,
)
from .mastery_engine import calculate_user_mastery_matrix


def create_interview_session(user, track="GENERAL", difficulty="MEDIUM", duration_minutes=45) -> InterviewSession:
    """
    Creates a new history-aware interview session.
    Analyzes user's LeetCode history and Skill Graph diagnostics to pick
    questions targeting weak, forgotten, or high-yield interview patterns.
    """
    duration_minutes = int(duration_minutes)
    if duration_minutes <= 30:
        question_count = 2
    elif duration_minutes <= 45:
        question_count = 2
    else:
        question_count = 3

    # 1. Inspect user mastery diagnostics
    mastery_matrix = calculate_user_mastery_matrix(user)
    diagnostics = mastery_matrix.get("diagnostics", {})

    target_pattern_keys = []
    # Prioritize weak patterns
    for p in diagnostics.get("weak", []):
        target_pattern_keys.append(p["key"])
    # Then forgotten patterns
    for p in diagnostics.get("forgotten", []):
        if p["key"] not in target_pattern_keys:
            target_pattern_keys.append(p["key"])

    # Fallback to high-frequency core patterns if user has few weak patterns
    high_freq_defaults = ["TWO_POINTER", "SLIDING_WINDOW", "TREE_TRAVERSAL", "GRAPH", "DP", "BINARY_SEARCH"]
    for hf in high_freq_defaults:
        if hf not in target_pattern_keys:
            target_pattern_keys.append(hf)

    # 2. Query Canonical Questions matching difficulty & track
    selected_canonical = []
    diff_pool = [difficulty.upper()]
    if difficulty.upper() == "MEDIUM":
        diff_pool = ["MEDIUM", "EASY"]
    elif difficulty.upper() == "HARD":
        diff_pool = ["HARD", "MEDIUM"]
    elif difficulty.upper() == "MIXED":
        diff_pool = ["EASY", "MEDIUM", "HARD"]

    # First attempt: pick from target patterns
    matched_questions = list(
        CanonicalInterviewQuestion.objects.filter(
            pattern__in=target_pattern_keys,
            difficulty__in=diff_pool,
        )
    )
    random.shuffle(matched_questions)

    # Ensure diversity of patterns
    used_patterns = set()
    for q in matched_questions:
        if q.pattern not in used_patterns:
            selected_canonical.append(q)
            used_patterns.add(q.pattern)
            if len(selected_canonical) >= question_count:
                break

    # If still need more questions, broaden search
    if len(selected_canonical) < question_count:
        remaining_pool = list(
            CanonicalInterviewQuestion.objects.exclude(id__in=[q.id for q in selected_canonical])
        )
        random.shuffle(remaining_pool)
        for q in remaining_pool:
            selected_canonical.append(q)
            if len(selected_canonical) >= question_count:
                break

    # 3. Create Session in Database
    session = InterviewSession.objects.create(
        user=user,
        track=track,
        difficulty=difficulty,
        duration_minutes=duration_minutes,
        started_at=timezone.now(),
        is_completed=False,
    )

    for order, q in enumerate(selected_canonical, start=1):
        InterviewQuestionAttempt.objects.create(
            session=session,
            canonical_question=q,
            question_order=order,
        )

    return session


def evaluate_interview_session(session: InterviewSession) -> InterviewReport:
    """
    Evaluates completed interview session across 5 dimensions:
      1. Problem Solving (Correctness & approach quality)
      2. Pattern Recognition (Identifying optimal algorithmic pattern)
      3. Time Management (Time spent vs allotted interview time)
      4. Optimization (Handling follow-up questions & complexities)
      5. Consistency / Independence (Penalty for hints revealed)

    Generates report and injects struggled patterns into SM-2 Revision Queue.
    """
    questions = list(session.questions.select_related("canonical_question", "user_problem").all())
    total_q = len(questions)
    if total_q == 0:
        total_q = 1

    passed_count = sum(1 for q in questions if q.was_passed)
    total_hints_revealed = sum(q.hints_revealed for q in questions)
    total_time_spent = sum(q.time_taken_seconds for q in questions)

    # 1. Problem Solving Score (0 - 100)
    problem_solving_score = (passed_count / total_q) * 100.0

    # 2. Pattern Recognition Score (0 - 100)
    # Assesses approach notes and passed status
    pattern_recognition_score = 0.0
    for q in questions:
        q_score = 50.0 if q.was_passed else 20.0
        # If candidate wrote a solid approach with keywords
        approach_text = (q.candidate_approach or "").lower()
        if any(term in approach_text for term in ["pointer", "window", "dfs", "bfs", "dp", "memo", "heap", "stack", "hash"]):
            q_score += 30.0
        if q.was_passed:
            q_score += 20.0
        pattern_recognition_score += min(100.0, q_score)
    pattern_recognition_score = round(pattern_recognition_score / total_q, 1)

    # 3. Time Management Score (0 - 100)
    max_allowed_seconds = session.duration_minutes * 60
    if total_time_spent <= 0:
        time_management_score = 75.0
    elif total_time_spent <= max_allowed_seconds:
        # Finished within time limit
        time_management_score = round(min(100.0, 70.0 + ((max_allowed_seconds - total_time_spent) / max_allowed_seconds) * 30.0), 1)
    else:
        # Overtime penalty
        overtime = total_time_spent - max_allowed_seconds
        time_management_score = round(max(20.0, 70.0 - (overtime / max_allowed_seconds) * 50.0), 1)

    # 4. Optimization Score (0 - 100)
    # Evaluates answers to interviewer follow-ups
    correct_follow_ups = 0
    total_follow_ups = 0
    for q in questions:
        c_q = q.canonical_question
        if c_q and c_q.follow_ups:
            total_follow_ups += 1
            expected = c_q.follow_ups[0].get("correct", "").strip().lower()
            actual = (q.follow_up_answer or "").strip().lower()
            if actual and (expected in actual or actual in expected or len(actual) > 10):
                correct_follow_ups += 1
    if total_follow_ups > 0:
        optimization_score = round((correct_follow_ups / total_follow_ups) * 100.0, 1)
    else:
        optimization_score = 80.0 if passed_count == total_q else 60.0

    # 5. Consistency & Independence Score (0 - 100)
    # Hint penalties: 1 hint = -8%, 2 hints = -18%, 3 hints = -30%
    hint_penalty_total = sum(min(35.0, q.hints_revealed * 12.0) for q in questions)
    consistency_score = round(max(15.0, 100.0 - (hint_penalty_total / total_q)), 1)

    # Composite Overall Score (Weighted: PS: 35%, PR: 20%, TM: 20%, Opt: 15%, Indep: 10%)
    overall_score = round(
        (0.35 * problem_solving_score) +
        (0.20 * pattern_recognition_score) +
        (0.20 * time_management_score) +
        (0.15 * optimization_score) +
        (0.10 * consistency_score),
        1
    )

    # Detect weak areas and formulate 3-Day Action Plan
    weak_patterns = []
    struggled_questions = [q for q in questions if not q.was_passed or q.hints_revealed >= 2]
    for q in struggled_questions:
        if q.canonical_question and q.canonical_question.pattern:
            weak_patterns.append(q.canonical_question.get_pattern_display())

    if weak_patterns:
        weak_area_str = f"Needs Reinforcement: {', '.join(set(weak_patterns))}"
    elif overall_score >= 80.0:
        weak_area_str = "None. Strong performance across tested patterns."
    else:
        weak_area_str = "Time management and edge-case handling under timer pressure."

    # 3-Day Action Plan
    revision_roadmap = [
        {"day": "Day 1", "task": f"Active recall intuition review for {weak_patterns[0] if weak_patterns else 'Two Pointers & Hash Maps'}"},
        {"day": "Day 2", "task": "Time-boxed practice: solve 2 Medium problems within 25 min each without hints"},
        {"day": "Day 3", "task": "Full simulation re-test targeting previously missed follow-up optimizations"},
    ]

    # BI-DIRECTIONAL SM-2 INTEGRATION:
    # Inject struggled questions into the user's active SM-2 queue for tomorrow!
    for q in struggled_questions:
        c_q = q.canonical_question
        if c_q:
            # Find or create corresponding Problem record for the user
            topic = c_q.topic or Topic.objects.first()
            user_problem, _ = Problem.objects.get_or_create(
                user=session.user,
                title=c_q.title,
                defaults={
                    "topic": topic,
                    "pattern": c_q.pattern,
                    "difficulty": c_q.difficulty,
                    "link": c_q.leetcode_url,
                    "notes": f"Flagged in Mock Interview #{session.id}. Review intuition and follow-up.",
                    "is_mastered": False,
                }
            )
            rev, _ = RevisionSchedule.objects.get_or_create(problem=user_problem)
            # Reset schedule so it surfaces tomorrow
            rev.next_review_date = timezone.now().date() + timedelta(days=1)
            rev.ease_factor = max(1.3, rev.ease_factor - 0.2)
            rev.repetitions = 0
            rev.interval_days = 1
            rev.save()

    # Finalize Session & Create Report
    session.is_completed = True
    session.completed_at = timezone.now()
    session.score = overall_score
    session.save()

    report, _ = InterviewReport.objects.update_or_create(
        session=session,
        defaults={
            "overall_score": overall_score,
            "problem_solving_score": problem_solving_score,
            "pattern_recognition_score": pattern_recognition_score,
            "time_management_score": time_management_score,
            "optimization_score": optimization_score,
            "consistency_score": consistency_score,
            "weak_area": weak_area_str,
            "recommended_patterns": weak_patterns,
            "revision_roadmap": revision_roadmap,
        }
    )

    return report
