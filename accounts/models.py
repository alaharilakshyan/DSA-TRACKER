from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    leetcode_username = models.CharField(max_length=100, blank=True)
    leetcode_ranking = models.PositiveIntegerField(null=True, blank=True)
    leetcode_solved_count = models.PositiveIntegerField(default=0)
    leetcode_easy_count = models.PositiveIntegerField(default=0)
    leetcode_medium_count = models.PositiveIntegerField(default=0)
    leetcode_hard_count = models.PositiveIntegerField(default=0)
    leetcode_profile_url = models.URLField(max_length=255, blank=True)
    leetcode_avatar_url = models.URLField(max_length=500, blank=True)
    leetcode_real_name = models.CharField(max_length=150, blank=True)
    leetcode_topic_stats = models.JSONField(default=list, blank=True)
    leetcode_last_synced = models.DateTimeField(null=True, blank=True)

    @property
    def effective_profile_url(self):
        if self.leetcode_profile_url:
            return self.leetcode_profile_url
        if self.leetcode_username:
            return f"https://leetcode.com/u/{self.leetcode_username}/"
        return ""

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
