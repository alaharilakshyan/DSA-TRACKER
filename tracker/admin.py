from django.contrib import admin
from .models import Topic, Problem, Attempt, RevisionSchedule


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "problem_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def problem_count(self, obj):
        return obj.problems.count()
    problem_count.short_description = "Problems"


class AttemptInline(admin.TabularInline):
    model = Attempt
    extra = 0
    readonly_fields = ("solved_at",)


class RevisionScheduleInline(admin.StackedInline):
    model = RevisionSchedule
    extra = 0


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "topic", "difficulty", "pattern", "is_mastered", "created_at")
    list_filter = ("difficulty", "pattern", "is_mastered", "topic")
    search_fields = ("title", "notes", "user__username")
    inlines = [RevisionScheduleInline, AttemptInline]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("problem", "solved_at", "time_taken_minutes", "was_successful")
    list_filter = ("was_successful", "solved_at")
    search_fields = ("problem__title", "approach_notes")


@admin.register(RevisionSchedule)
class RevisionScheduleAdmin(admin.ModelAdmin):
    list_display = ("problem", "next_review_date", "interval_days", "repetitions", "ease_factor")
    list_filter = ("next_review_date",)
    search_fields = ("problem__title",)
