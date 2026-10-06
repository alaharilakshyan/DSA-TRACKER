from django.db import migrations
from django.utils.text import slugify

TOPICS = [
    "Arrays",
    "Strings",
    "Linked Lists",
    "Stacks & Queues",
    "Trees",
    "Binary Search Trees",
    "Heaps",
    "Graphs",
    "Dynamic Programming",
    "Backtracking",
    "Greedy",
    "Binary Search",
    "Bit Manipulation",
    "Tries",
    "Two Pointers",
    "Sliding Window",
]


def seed_topics(apps, schema_editor):
    Topic = apps.get_model("tracker", "Topic")
    for name in TOPICS:
        Topic.objects.get_or_create(
            name=name,
            defaults={"slug": slugify(name)}
        )


def reverse_topics(apps, schema_editor):
    Topic = apps.get_model("tracker", "Topic")
    Topic.objects.filter(name__in=TOPICS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_topics, reverse_code=reverse_topics),
    ]
