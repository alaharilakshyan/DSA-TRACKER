import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import (
    Problem, RevisionSchedule, Attempt, Topic,
    InterviewSession, InterviewQuestionAttempt, InterviewReport
)
from .forms import ProblemForm, AttemptForm, RevisionQualityForm
from .services.stats import (
    get_topic_progress,
    get_weak_patterns,
    get_difficulty_breakdown,
    get_dashboard_kpis,
)
from .services.revision_engine import update_revision_schedule


def landing_page(request):
    """
    Public-facing Hero / Welcome landing page showcasing:
    - Topological DSA Skill Graph & Pattern Mastery
    - History-Aware Mock Interview Readiness Simulator
    - SuperMemo-2 Spaced Repetition Active Recall Engine
    - 1-Click Official LeetCode Profile URL Sync
    """
    if request.user.is_authenticated and request.GET.get("preview") != "1":
        return redirect("dashboard")
    return render(request, "tracker/landing.html", {
        "is_authenticated": request.user.is_authenticated,
    })


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    # KPI summary cards
    kpis = get_dashboard_kpis(user)

    # Topic progress
    topic_progress = get_topic_progress(user)
    topic_labels = [tp["topic__name"] for tp in topic_progress]
    topic_totals = [tp["total"] for tp in topic_progress]
    topic_mastered = [tp["mastered"] for tp in topic_progress]

    # Weak patterns
    weak_patterns = get_weak_patterns(user, limit=5)
    pattern_labels = [p["pattern"].replace("_", " ").title() for p in weak_patterns]
    pattern_avg_times = [round(p["avg_time"], 1) for p in weak_patterns]

    # Difficulty breakdown
    diff_data = get_difficulty_breakdown(user)
    diff_counts = {"EASY": 0, "MEDIUM": 0, "HARD": 0}
    for d in diff_data:
        diff_counts[d["difficulty"]] = d["total"]

    # Today's due revisions
    today_revisions = (
        RevisionSchedule.objects.filter(
            problem__user=user,
            next_review_date__lte=today,
        )
        .select_related("problem", "problem__topic")
        .order_by("next_review_date")
    )

    # Recent attempts
    recent_attempts = (
        Attempt.objects.filter(problem__user=user)
        .select_related("problem", "problem__topic")
        .order_by("-solved_at")[:6]
    )

    from .services.mastery_engine import calculate_user_mastery_matrix
    mastery_matrix = calculate_user_mastery_matrix(user)

    context = {
        "kpis": kpis,
        "topic_progress": topic_progress,
        "weak_patterns": weak_patterns,
        "today_revisions": today_revisions,
        "recent_attempts": recent_attempts,
        "mastery_matrix": mastery_matrix,
        # JSON serialized data for Chart.js
        "topic_labels_json": json.dumps(topic_labels),
        "topic_totals_json": json.dumps(topic_totals),
        "topic_mastered_json": json.dumps(topic_mastered),
        "diff_counts_json": json.dumps([
            diff_counts["EASY"],
            diff_counts["MEDIUM"],
            diff_counts["HARD"]
        ]),
        "pattern_labels_json": json.dumps(pattern_labels),
        "pattern_avg_times_json": json.dumps(pattern_avg_times),
        "user_profile": getattr(user, "profile", None),
    }
    return render(request, "tracker/dashboard.html", context)


@login_required
def problem_list(request):
    problems = Problem.objects.filter(user=request.user).select_related("topic", "revision")

    topic_slug = request.GET.get("topic", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    pattern = request.GET.get("pattern", "").strip()
    mastered = request.GET.get("mastered", "").strip()
    query = request.GET.get("q", "").strip()

    if topic_slug:
        problems = problems.filter(topic__slug=topic_slug)
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    if pattern:
        problems = problems.filter(pattern=pattern)
    if mastered:
        if mastered == "yes":
            problems = problems.filter(is_mastered=True)
        elif mastered == "no":
            problems = problems.filter(is_mastered=False)
    if query:
        problems = problems.filter(
            Q(title__icontains=query) | Q(notes__icontains=query)
        )

    all_topics = Topic.objects.all()
    difficulties = Problem.Difficulty.choices
    patterns = Problem.Pattern.choices

    return render(
        request,
        "tracker/problem_list.html",
        {
            "problems": problems,
            "topics": all_topics,
            "difficulties": difficulties,
            "patterns": patterns,
            "selected_topic": topic_slug,
            "selected_difficulty": difficulty,
            "selected_pattern": pattern,
            "selected_mastered": mastered,
            "query": query,
            "total_count": problems.count(),
        },
    )


@login_required
def problem_create(request):
    if request.method == "POST":
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.user = request.user
            problem.save()
            # Initialize SM-2 revision schedule
            RevisionSchedule.objects.get_or_create(problem=problem)
            messages.success(request, f"Problem '{problem.title}' added successfully!")
            return redirect("problem_detail", problem_id=problem.id)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        # Prepopulate topic if provided in GET query param
        initial = {}
        topic_slug = request.GET.get("topic")
        if topic_slug:
            topic = Topic.objects.filter(slug=topic_slug).first()
            if topic:
                initial["topic"] = topic
        form = ProblemForm(initial=initial)

    return render(request, "tracker/problem_form.html", {"form": form, "action": "Add Problem"})


@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(
        Problem.objects.select_related("topic", "revision"),
        id=problem_id,
        user=request.user,
    )
    attempts = problem.attempts.all()
    attempt_form = AttemptForm()

    return render(
        request,
        "tracker/problem_detail.html",
        {
            "problem": problem,
            "attempts": attempts,
            "attempt_form": attempt_form,
        },
    )


@login_required
def problem_update(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id, user=request.user)
    if request.method == "POST":
        form = ProblemForm(request.POST, instance=problem)
        if form.is_valid():
            form.save()
            messages.success(request, f"Problem '{problem.title}' updated successfully.")
            return redirect("problem_detail", problem_id=problem.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProblemForm(instance=problem)

    return render(
        request,
        "tracker/problem_form.html",
        {"form": form, "problem": problem, "action": "Edit Problem"},
    )


@login_required
@require_POST
def problem_delete(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id, user=request.user)
    title = problem.title
    problem.delete()
    messages.success(request, f"Problem '{title}' has been deleted.")
    return redirect("problem_list")


@login_required
@require_POST
def log_attempt(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id, user=request.user)
    form = AttemptForm(request.POST)
    if form.is_valid():
        attempt = form.save(commit=False)
        attempt.problem = problem
        attempt.save()
        messages.success(request, f"New attempt logged ({attempt.time_taken_minutes} mins). Keep up the momentum!")
    else:
        messages.error(request, "Failed to log attempt. Please verify the time entered.")
    return redirect("problem_detail", problem_id=problem.id)


@login_required
@require_POST
def toggle_mastery(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id, user=request.user)
    problem.is_mastered = not problem.is_mastered
    problem.save()

    status_msg = "mastered" if problem.is_mastered else "marked as needs practice"
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "is_mastered": problem.is_mastered,
            "message": f"Problem '{problem.title}' is now {status_msg}."
        })

    messages.info(request, f"Problem '{problem.title}' {status_msg}.")
    return redirect(request.META.get("HTTP_REFERER", "problem_list"))


@login_required
def revision_today(request):
    today = timezone.now().date()
    revisions = (
        RevisionSchedule.objects.filter(
            problem__user=request.user,
            next_review_date__lte=today,
        )
        .select_related("problem", "problem__topic")
        .order_by("next_review_date")
    )
    return render(request, "tracker/revision_today.html", {"revisions": revisions, "today": today})


@login_required
def submit_revision(request, problem_id):
    revision = get_object_or_404(
        RevisionSchedule.objects.select_related("problem", "problem__topic"),
        problem__id=problem_id,
        problem__user=request.user,
    )

    if request.method == "POST":
        form = RevisionQualityForm(request.POST)
        if form.is_valid():
            quality = int(form.cleaned_data["quality"])
            update_revision_schedule(revision, quality)
            messages.success(
                request,
                f"Recorded revision for '{revision.problem.title}' (Rating: {quality}/5). "
                f"Next review in {revision.interval_days} day(s) on {revision.next_review_date}!"
            )
            # If user came from today's revision queue, send them back there
            if "revision_today" in request.META.get("HTTP_REFERER", ""):
                return redirect("revision_today")
            return redirect("dashboard")
    else:
        form = RevisionQualityForm()

    return render(
        request,
        "tracker/revision_today.html",
        {
            "form": form,
            "revision": revision,
            "active_problem": revision.problem,
            "is_submitting_single": True,
        },
    )


@login_required
def fetch_leetcode(request):
    """API endpoint to fetch LeetCode question details by URL or slug."""
    url_or_slug = request.GET.get("url", "").strip()
    if not url_or_slug:
        return JsonResponse({"success": False, "error": "Please provide a LeetCode problem URL or slug."})

    from .services.leetcode import fetch_leetcode_problem
    result = fetch_leetcode_problem(url_or_slug)
    return JsonResponse(result)


@login_required
def export_report(request):
    """Renders a printable interview readiness dossier."""
    user = request.user
    problems = Problem.objects.filter(user=user).select_related("topic", "revision")
    kpis = get_dashboard_kpis(user)
    topic_progress = get_topic_progress(user)
    weak_patterns = get_weak_patterns(user, limit=5)
    mastered_problems = problems.filter(is_mastered=True)
    in_progress_problems = problems.filter(is_mastered=False)

    context = {
        "user": user,
        "generated_at": timezone.now(),
        "kpis": kpis,
        "topic_progress": topic_progress,
        "weak_patterns": weak_patterns,
        "mastered_problems": mastered_problems,
        "in_progress_problems": in_progress_problems,
        "total_count": problems.count(),
    }
    return render(request, "tracker/export_report.html", context)


@login_required
def export_markdown(request):
    """Generates a downloadable Markdown dossier of personal DSA prep notes and problems."""
    from django.http import HttpResponse
    user = request.user
    problems = Problem.objects.filter(user=user).select_related("topic", "revision")
    kpis = get_dashboard_kpis(user)

    lines = [
        f"# DSA Interview Readiness Dossier — {user.username}",
        f"*Generated on {timezone.now().strftime('%B %d, %Y')} via Smart DSA Tracker*\n",
        "## 📊 Executive Summary",
        f"- **Total Problems Logged**: {kpis['total_problems']}",
        f"- **Mastered Problems**: {kpis['mastered_problems']} ({kpis['mastery_rate']}%)",
        f"- **Total Practice Time**: {kpis['total_time_minutes']} minutes",
        f"- **Overall Attempt Success Rate**: {kpis['success_rate']}%\n",
        "## 📚 Problem Bank & Takeaways\n",
    ]

    for p in problems:
        status = "⭐ Mastered" if p.is_mastered else "⏳ Needs Practice"
        lines.append(f"### {p.title} ({p.get_difficulty_display()} • {p.topic.name})")
        lines.append(f"- **Pattern**: {p.get_pattern_display()}")
        lines.append(f"- **Status**: {status}")
        if p.link:
            lines.append(f"- **Link**: [{p.title}]({p.link})")
        if p.notes:
            lines.append(f"\n**Approach Notes & Intuition:**\n```\n{p.notes}\n```\n")
        lines.append("---\n")

    md_content = "\n".join(lines)
    response = HttpResponse(md_content, content_type="text/markdown; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{user.username}_dsa_dossier.md"'
    return response


@login_required
@require_POST
def sync_leetcode_view(request):
    """
    Triggers an automatic synchronization of the user's official LeetCode profile,
    extracting profile statistics, problem counts, solved topics breakdown, and recent accepted submissions.
    """
    account_input = (
        request.POST.get("leetcode_url", "").strip() or
        request.POST.get("leetcode_username", "").strip()
    )

    if not account_input and hasattr(request.user, "profile"):
        account_input = (
            request.user.profile.leetcode_profile_url or
            request.user.profile.leetcode_username
        )

    if not account_input:
        error_msg = "Please provide your LeetCode account URL (e.g. https://leetcode.com/u/your-username/) or handle."
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": error_msg})
        messages.error(request, error_msg)
        return redirect(request.META.get("HTTP_REFERER", "dashboard"))

    from .services.leetcode import sync_leetcode_for_user
    result = sync_leetcode_for_user(request.user, account_input, limit=20)

    if not result.get("success"):
        error_msg = result.get("error", "Failed to sync with official LeetCode.")
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": error_msg})
        messages.error(request, error_msg)
        return redirect(request.META.get("HTTP_REFERER", "dashboard"))

    # Craft an informative success notification highlighting problems and topics synced
    topics_count = result.get("topics_count", 0)
    total_solved = result.get("total_solved", 0)
    easy = result.get("easy", 0)
    med = result.get("medium", 0)
    hard = result.get("hard", 0)
    new_probs = result.get("new_problems_added", 0)

    success_msg = (
        f"Synced with official LeetCode @{result['username']}! "
        f"Extracted {total_solved} solved problems ({easy} Easy, {med} Med, {hard} Hard) "
        f"across {topics_count} topics, and imported {new_probs} recent submission(s) into your revision queue."
    )
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "message": success_msg, "data": result})

    messages.success(request, success_msg)
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


@login_required
def skill_graph_view(request):
    """
    Renders the interactive Topological DSA Skill Graph & Pattern Mastery Dashboard.
    """
    from .services.mastery_engine import calculate_user_mastery_matrix
    from .services.skill_graph import get_skill_graph_edges, get_skill_graph_nodes

    matrix = calculate_user_mastery_matrix(request.user)
    edges = get_skill_graph_edges()
    nodes = get_skill_graph_nodes()

    context = {
        "matrix": matrix,
        "edges_json": json.dumps(edges),
        "nodes_json": json.dumps(nodes),
        "patterns_json": json.dumps(matrix["patterns"]),
    }
    return render(request, "tracker/skill_graph.html", context)


@login_required
def skill_graph_api(request):
    """
    JSON API returning complete skill graph topology and user mastery metrics.
    """
    from .services.mastery_engine import calculate_user_mastery_matrix
    from .services.skill_graph import get_skill_graph_edges, get_skill_graph_nodes

    matrix = calculate_user_mastery_matrix(request.user)
    edges = get_skill_graph_edges()
    nodes = get_skill_graph_nodes()

    return JsonResponse({
        "success": True,
        "matrix": matrix,
        "edges": edges,
        "nodes": nodes,
    })


# ---------------------------------------------------------
# INTERVIEW SIMULATOR VIEWS
# ---------------------------------------------------------

@login_required
def interview_hub(request):
    """
    Landing hub for the Technical Interview Simulator.
    Displays previous session history, average scores, and configuration launcher.
    """
    sessions = (
        request.user.interview_sessions
        .select_related("report")
        .prefetch_related("questions")
        .order_by("-started_at")
    )
    completed_sessions = [s for s in sessions if s.is_completed]
    avg_score = round(sum(s.score for s in completed_sessions) / len(completed_sessions), 1) if completed_sessions else 0.0

    context = {
        "sessions": sessions,
        "completed_count": len(completed_sessions),
        "avg_score": avg_score,
    }
    return render(request, "tracker/interview_hub.html", context)


@login_required
@require_POST
def interview_start(request):
    """
    Starts a new history-aware technical interview simulation session.
    """
    from .services.interview_simulator import create_interview_session

    track = request.POST.get("track", "GENERAL").strip()
    difficulty = request.POST.get("difficulty", "MEDIUM").strip()
    duration = int(request.POST.get("duration", 45))

    session = create_interview_session(
        user=request.user,
        track=track,
        difficulty=difficulty,
        duration_minutes=duration,
    )
    return redirect("interview_console", session_id=session.id)


@login_required
def interview_console(request, session_id):
    """
    Live interactive mock interview console.
    """
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    if session.is_completed:
        return redirect("interview_report", session_id=session.id)

    questions = list(session.questions.select_related("canonical_question", "user_problem").all())
    
    # Active question determination (by query param ?q=order, or first unanswered)
    q_param = request.GET.get("q")
    active_question = None
    if q_param and q_param.isdigit():
        q_order = int(q_param)
        for q in questions:
            if q.question_order == q_order:
                active_question = q
                break
    if not active_question:
        active_question = next((q for q in questions if not q.was_passed and not q.candidate_approach), questions[0] if questions else None)

    # Time remaining calculation
    elapsed_seconds = (timezone.now() - session.started_at).total_seconds()
    total_seconds = session.duration_minutes * 60
    remaining_seconds = max(0, int(total_seconds - elapsed_seconds))

    context = {
        "session": session,
        "questions": questions,
        "active_question": active_question,
        "remaining_seconds": remaining_seconds,
    }
    return render(request, "tracker/interview_console.html", context)


@login_required
@require_POST
def interview_submit_question(request, session_id, question_id):
    """
    Saves candidate's approach notes, code, hint count, follow-up answer, and passed status.
    """
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    question = get_object_or_404(session.questions, id=question_id)

    time_spent = int(request.POST.get("time_taken_seconds", 0))
    hints_used = int(request.POST.get("hints_revealed", 0))
    approach = request.POST.get("candidate_approach", "").strip()
    code = request.POST.get("candidate_code", "").strip()
    follow_up = request.POST.get("follow_up_answer", "").strip()
    was_passed = request.POST.get("was_passed", "false").lower() in ["true", "1", "yes"]

    question.time_taken_seconds = max(question.time_taken_seconds, time_spent)
    question.hints_revealed = max(question.hints_revealed, hints_used)
    question.candidate_approach = approach
    question.candidate_code = code
    question.follow_up_answer = follow_up
    question.was_passed = was_passed
    question.save()

    next_order = question.question_order + 1
    has_next = session.questions.filter(question_order=next_order).exists()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "has_next": has_next,
            "next_order": next_order if has_next else None,
        })

    if has_next:
        return redirect(f"{redirect('interview_console', session_id=session.id).url}?q={next_order}")
    return redirect("interview_complete", session_id=session.id)


@login_required
def interview_complete(request, session_id):
    """
    Finalizes interview session, computes 5-dimension scorecard, and redirects to report.
    """
    from .services.interview_simulator import evaluate_interview_session

    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    if not session.is_completed:
        evaluate_interview_session(session)

    return redirect("interview_report", session_id=session.id)


@login_required
def interview_report_view(request, session_id):
    """
    Displays the detailed Interview Performance Report and Diagnostic Scorecard.
    """
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    if not hasattr(session, "report"):
        from .services.interview_simulator import evaluate_interview_session
        evaluate_interview_session(session)

    report = session.report
    questions = session.questions.select_related("canonical_question", "user_problem").all()

    context = {
        "session": session,
        "report": report,
        "questions": questions,
    }
    return render(request, "tracker/interview_report.html", context)

