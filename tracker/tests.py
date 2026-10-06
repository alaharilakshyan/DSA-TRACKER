from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Topic, Problem, RevisionSchedule
from .services.revision_engine import update_revision_schedule
from .services.stats import get_weak_patterns, get_dashboard_kpis


class RevisionEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.topic, _ = Topic.objects.get_or_create(slug="arrays", defaults={"name": "Arrays"})
        self.problem = Problem.objects.create(
            user=self.user,
            title="Two Sum",
            topic=self.topic,
            pattern=Problem.Pattern.TWO_POINTER,
            difficulty=Problem.Difficulty.EASY,
        )
        self.revision, _ = RevisionSchedule.objects.get_or_create(problem=self.problem)

    def test_low_quality_resets_repetitions(self):
        """Quality < 3 resets repetitions and sets interval to 1 day."""
        self.revision.repetitions = 4
        self.revision.interval_days = 20
        self.revision.save()

        update_revision_schedule(self.revision, quality=1)
        self.assertEqual(self.revision.repetitions, 0)
        self.assertEqual(self.revision.interval_days, 1)

    def test_high_quality_grows_interval(self):
        """Successive ratings >= 3 scale interval: 1 -> 6 -> round(6 * EF)."""
        update_revision_schedule(self.revision, quality=5)  # rep 1
        self.assertEqual(self.revision.repetitions, 1)
        self.assertEqual(self.revision.interval_days, 1)

        update_revision_schedule(self.revision, quality=5)  # rep 2
        self.assertEqual(self.revision.repetitions, 2)
        self.assertEqual(self.revision.interval_days, 6)

        update_revision_schedule(self.revision, quality=5)  # rep 3
        self.assertEqual(self.revision.repetitions, 3)
        self.assertGreaterEqual(self.revision.interval_days, 15)

    def test_ease_factor_bounded_at_minimum(self):
        """Ease factor must never drop below 1.3 even after repeated poor ratings."""
        self.revision.ease_factor = 1.35
        self.revision.save()
        for _ in range(5):
            update_revision_schedule(self.revision, quality=0)
        self.assertGreaterEqual(self.revision.ease_factor, 1.3)


class TrackerViewsAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="alice", password="password123")
        self.user2 = User.objects.create_user(username="bob", password="password123")
        self.topic, _ = Topic.objects.get_or_create(
            slug="dynamic-programming",
            defaults={"name": "Dynamic Programming"}
        )

        self.problem1 = Problem.objects.create(
            user=self.user1,
            title="Climbing Stairs",
            topic=self.topic,
            pattern=Problem.Pattern.DP,
            difficulty=Problem.Difficulty.EASY,
        )
        RevisionSchedule.objects.get_or_create(problem=self.problem1)

    def test_login_required_protection(self):
        """Unauthenticated requests must be redirected to login."""
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_user_data_isolation(self):
        """User Bob must not see or access Alice's problems."""
        self.client.login(username="bob", password="password123")

        # Bob views problem list — Alice's problem should not appear
        response = self.client.get(reverse("problem_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Climbing Stairs")

        # Bob directly requests Alice's problem detail — should get 404
        detail_response = self.client.get(reverse("problem_detail", args=[self.problem1.id]))
        self.assertEqual(detail_response.status_code, 404)

    def test_problem_create_auto_creates_revision(self):
        """Creating a problem via the form must automatically initialize a RevisionSchedule."""
        self.client.login(username="alice", password="password123")
        response = self.client.post(reverse("problem_create"), {
            "title": "Coin Change",
            "topic": self.topic.id,
            "pattern": Problem.Pattern.DP,
            "difficulty": Problem.Difficulty.MEDIUM,
            "link": "https://leetcode.com/problems/coin-change/",
            "notes": "Classic unbounded knapsack pattern.",
        })
        self.assertEqual(response.status_code, 302)
        problem = Problem.objects.get(title="Coin Change")
        self.assertEqual(problem.user, self.user1)
        self.assertTrue(hasattr(problem, "revision"))
        self.assertEqual(problem.revision.interval_days, 1)

    def test_toggle_mastery(self):
        """Toggle mastery switches the is_mastered boolean."""
        self.client.login(username="alice", password="password123")
        self.assertFalse(self.problem1.is_mastered)

        self.client.post(reverse("toggle_mastery", args=[self.problem1.id]))
        self.problem1.refresh_from_db()
        self.assertTrue(self.problem1.is_mastered)

    def test_log_attempt_and_stats(self):
        """Logging an attempt recalculates KPIs and weak pattern detection correctly."""
        self.client.login(username="alice", password="password123")
        self.client.post(reverse("log_attempt", args=[self.problem1.id]), {
            "time_taken_minutes": 35,
            "was_successful": True,
            "approach_notes": "Tabulation method worked well.",
        })
        self.assertEqual(self.problem1.attempts.count(), 1)
        kpis = get_dashboard_kpis(self.user1)
        self.assertEqual(kpis["total_attempts"], 1)
        self.assertEqual(kpis["total_time_minutes"], 35)

        weak_patterns = get_weak_patterns(self.user1)
        self.assertEqual(len(weak_patterns), 1)
        self.assertEqual(weak_patterns[0]["pattern"], Problem.Pattern.DP)

    def test_expanded_patterns(self):
        """Problems can be created and saved with newly expanded patterns."""
        p = Problem.objects.create(
            user=self.user1,
            title="Daily Temperatures",
            topic=self.topic,
            pattern=Problem.Pattern.MONOTONIC_STACK,
            difficulty=Problem.Difficulty.MEDIUM,
        )
        self.assertEqual(p.pattern, Problem.Pattern.MONOTONIC_STACK)
        self.assertEqual(p.get_pattern_display(), "Monotonic Stack / Queue")

    def test_leetcode_slug_extraction(self):
        """Slug extractor handles URLs, trailing slashes, and raw slugs."""
        from .services.leetcode import extract_slug
        self.assertEqual(extract_slug("https://leetcode.com/problems/trapping-rain-water/"), "trapping-rain-water")
        self.assertEqual(extract_slug("https://leetcode.com/problems/two-sum"), "two-sum")
        self.assertEqual(extract_slug("lru-cache"), "lru-cache")

    def test_fetch_leetcode_endpoint_validation(self):
        """Fetch endpoint requires a query parameter."""
        self.client.login(username="alice", password="password123")
        res = self.client.get(reverse("fetch_leetcode"))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data.get("success"))

    def test_export_views(self):
        """Export report and Markdown dossier return valid responses."""
        self.client.login(username="alice", password="password123")
        res_report = self.client.get(reverse("export_report"))
        self.assertEqual(res_report.status_code, 200)
        self.assertContains(res_report, "Readiness Dossier")
        self.assertContains(res_report, "Climbing Stairs")

        res_md = self.client.get(reverse("export_markdown"))
        self.assertEqual(res_md.status_code, 200)
        self.assertEqual(res_md["Content-Type"], "text/markdown; charset=utf-8")
        self.assertIn("Climbing Stairs", res_md.content.decode("utf-8"))

    def test_user_profile_auto_created(self):
        """Creating a User automatically creates an associated UserProfile."""
        self.assertTrue(hasattr(self.user1, "profile"))
        self.assertEqual(self.user1.profile.leetcode_username, "")

    def test_sync_leetcode_empty_validation(self):
        """Sync view rejects empty URL or username with error message."""
        self.client.login(username="alice", password="password123")
        res = self.client.post(reverse("sync_leetcode"), {"leetcode_url": ""})
        self.assertEqual(res.status_code, 302)

    def test_extract_username_from_url(self):
        """extract_username_from_url accurately parses profile URLs, handles, and query params."""
        from .services.leetcode import extract_username_from_url
        self.assertEqual(extract_username_from_url("https://leetcode.com/u/lee215/"), "lee215")
        self.assertEqual(extract_username_from_url("https://leetcode.com/u/john_doe-99"), "john_doe-99")
        self.assertEqual(extract_username_from_url("leetcode.com/u/test_user?tab=submissions"), "test_user")
        self.assertEqual(extract_username_from_url("https://leetcode.com/alice/"), "alice")
        self.assertEqual(extract_username_from_url("@bob123"), "bob123")
        self.assertEqual(extract_username_from_url("claudia"), "claudia")
        self.assertEqual(extract_username_from_url(""), "")

    def test_user_profile_effective_profile_url(self):
        """UserProfile effective_profile_url property generates canonical URL."""
        self.user1.profile.leetcode_username = "lee215"
        self.assertEqual(self.user1.profile.effective_profile_url, "https://leetcode.com/u/lee215/")
        self.user1.profile.leetcode_profile_url = "https://leetcode.com/u/custom-handle/"
        self.assertEqual(self.user1.profile.effective_profile_url, "https://leetcode.com/u/custom-handle/")

    def test_skill_graph_taxonomy(self):
        """Skill graph returns 16 nodes and valid directed prerequisite edges."""
        from .services.skill_graph import get_skill_graph_nodes, get_skill_graph_edges, get_unlocked_frontiers
        nodes = get_skill_graph_nodes()
        self.assertEqual(len(nodes), 16)
        edges = get_skill_graph_edges()
        self.assertTrue(len(edges) >= 10)
        frontiers = get_unlocked_frontiers(set())
        self.assertTrue(any(f["key"] == "TWO_POINTER" for f in frontiers))

    def test_mastery_matrix_calculation(self):
        """Mastery engine computes multi-factor metrics with Bayesian damping."""
        from .services.mastery_engine import calculate_user_mastery_matrix
        matrix = calculate_user_mastery_matrix(self.user1)
        self.assertIn("patterns", matrix)
        self.assertIn("diagnostics", matrix)
        self.assertIn("branches", matrix)
        self.assertEqual(len(matrix["branches"]), 4)
        # Check DP pattern for alice (Climbing Stairs is logged)
        dp_stat = matrix["patterns"]["DP"]
        self.assertEqual(dp_stat["total_solved"], 1)
        self.assertIn(dp_stat["status"], ["WEAK", "DEVELOPING", "STRONG"])

    def test_skill_graph_endpoints(self):
        """Skill graph page and JSON API return successful responses."""
        self.client.login(username="alice", password="password123")
        res_page = self.client.get(reverse("skill_graph"))
        self.assertEqual(res_page.status_code, 200)
        self.assertContains(res_page, "Skill Graph")

        res_api = self.client.get(reverse("skill_graph_api"))
        self.assertEqual(res_api.status_code, 200)
        data = res_api.json()
        self.assertTrue(data.get("success"))
        self.assertIn("matrix", data)

    def test_interview_simulator_lifecycle(self):
        """Simulator creates session, evaluates across 5 dimensions, and injects into SM-2 queue."""
        from .services.interview_simulator import create_interview_session, evaluate_interview_session
        from tracker.models import RevisionSchedule

        # 1. Ensure canonical questions exist
        from django.core.management import call_command
        call_command("seed_canonical_questions")

        # 2. Create session
        session = create_interview_session(self.user1, track="GENERAL", difficulty="MEDIUM", duration_minutes=45)
        self.assertFalse(session.is_completed)
        self.assertEqual(session.questions.count(), 2)

        # 3. Simulate answering a question with hints
        q1 = session.questions.first()
        q1.hints_revealed = 1
        q1.time_taken_seconds = 1200
        q1.was_passed = False
        q1.candidate_approach = "Tried two pointers but struggled with edge cases."
        q1.save()

        # 4. Evaluate session
        report = evaluate_interview_session(session)
        self.assertTrue(session.is_completed)
        self.assertGreater(report.overall_score, 0)
        self.assertIn("Needs Reinforcement", report.weak_area)
        self.assertEqual(len(report.revision_roadmap), 3)

        # 5. Verify bi-directional SM-2 queue injection
        q1_title = q1.canonical_question.title
        injected_rev = RevisionSchedule.objects.filter(problem__user=self.user1, problem__title=q1_title).first()
        self.assertIsNotNone(injected_rev)
        self.assertEqual(injected_rev.interval_days, 1)

    def test_interview_views(self):
        """Interview hub and simulator views render without error."""
        from django.core.management import call_command
        call_command("seed_canonical_questions")

        self.client.login(username="alice", password="password123")
        res_hub = self.client.get(reverse("interview_hub"))
        self.assertEqual(res_hub.status_code, 200)
        self.assertContains(res_hub, "Technical Interview Simulator")

        # Start interview via POST
        res_start = self.client.post(reverse("interview_start"), {
            "track": "PRODUCT",
            "difficulty": "MEDIUM",
            "duration": 45,
        })
        self.assertEqual(res_start.status_code, 302)
        session_id = res_start.url.split("/")[2]

        # View console
        res_console = self.client.get(reverse("interview_console", args=[session_id]))
        self.assertEqual(res_console.status_code, 200)

        # Complete interview
        res_comp = self.client.get(reverse("interview_complete", args=[session_id]))
        self.assertEqual(res_comp.status_code, 302)

        # View report
        res_report = self.client.get(reverse("interview_report", args=[session_id]))
        self.assertEqual(res_report.status_code, 200)
        self.assertContains(res_report, "Performance Report")

    def test_landing_page_and_guest_navbar(self):
        """Unauthenticated visitor sees landing hero page with login, sign up, and features."""
        # Unauthenticated request to / (landing)
        res_landing = self.client.get(reverse("landing"))
        self.assertEqual(res_landing.status_code, 200)
        self.assertContains(res_landing, "Stop Grinding Random DSA")
        self.assertContains(res_landing, "Log In")
        self.assertContains(res_landing, "Get Started")
        self.assertContains(res_landing, "Topological Skill Graph")
        self.assertContains(res_landing, "SuperMemo-2")

        # Authenticated user visiting / is redirected to dashboard
        self.client.login(username="alice", password="password123")
        res_auth = self.client.get(reverse("landing"))
        self.assertEqual(res_auth.status_code, 302)
        self.assertIn(reverse("dashboard"), res_auth.url)

        # Authenticated user with ?preview=1 can preview landing page
        res_preview = self.client.get(reverse("welcome") + "?preview=1")
        self.assertEqual(res_preview.status_code, 200)
        self.assertContains(res_preview, "Stop Grinding Random DSA")

