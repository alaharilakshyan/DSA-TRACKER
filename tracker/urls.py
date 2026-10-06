from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("welcome/", views.landing_page, name="welcome"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("problems/", views.problem_list, name="problem_list"),
    path("problems/new/", views.problem_create, name="problem_create"),
    path("problems/<int:problem_id>/", views.problem_detail, name="problem_detail"),
    path("problems/<int:problem_id>/edit/", views.problem_update, name="problem_update"),
    path("problems/<int:problem_id>/delete/", views.problem_delete, name="problem_delete"),
    path("problems/<int:problem_id>/attempt/", views.log_attempt, name="log_attempt"),
    path("problems/<int:problem_id>/toggle-mastery/", views.toggle_mastery, name="toggle_mastery"),
    path("revision/today/", views.revision_today, name="revision_today"),
    path("revision/<int:problem_id>/", views.submit_revision, name="submit_revision"),
    path("problems/fetch-leetcode/", views.fetch_leetcode, name="fetch_leetcode"),
    path("export/report/", views.export_report, name="export_report"),
    path("export/markdown/", views.export_markdown, name="export_markdown"),
    path("sync/leetcode/", views.sync_leetcode_view, name="sync_leetcode"),
    path("skill-graph/", views.skill_graph_view, name="skill_graph"),
    path("api/skill-graph/", views.skill_graph_api, name="skill_graph_api"),
    path("interview/", views.interview_hub, name="interview_hub"),
    path("interview/start/", views.interview_start, name="interview_start"),
    path("interview/<int:session_id>/", views.interview_console, name="interview_console"),
    path("interview/<int:session_id>/question/<int:question_id>/submit/", views.interview_submit_question, name="interview_submit_question"),
    path("interview/<int:session_id>/complete/", views.interview_complete, name="interview_complete"),
    path("interview/<int:session_id>/report/", views.interview_report_view, name="interview_report"),
]
