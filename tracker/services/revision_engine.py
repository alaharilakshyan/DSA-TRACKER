from datetime import timedelta
from django.utils import timezone


def update_revision_schedule(revision, quality: int):
    """
    Update a RevisionSchedule after the user self-rates recall quality (0-5),
    using a simplified version of the SM-2 algorithm (the same family Anki uses).

    quality:
        0-2 -> forgot / struggled badly -> reset repetitions, review again tomorrow
        3-5 -> recalled it -> interval grows based on ease_factor
    """
    quality = int(quality)

    if quality < 3:
        revision.repetitions = 0
        revision.interval_days = 1
    else:
        revision.repetitions += 1
        if revision.repetitions == 1:
            revision.interval_days = 1
        elif revision.repetitions == 2:
            revision.interval_days = 6
        else:
            revision.interval_days = max(1, round(revision.interval_days * revision.ease_factor))

    # Ease factor adjustment (bounded so it never drops below 1.3)
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    factor_adjustment = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    revision.ease_factor = max(1.3, round(revision.ease_factor + factor_adjustment, 3))
    
    revision.next_review_date = timezone.now().date() + timedelta(days=revision.interval_days)
    revision.save()
    return revision
