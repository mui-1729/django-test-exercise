from django.db import models
from django.utils import timezone

# Create your models here.


class Task(models.Model):
    PRIORITY_HIGH = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 3
    PRIORITY_CHOICES = (
        (PRIORITY_HIGH, '高'),
        (PRIORITY_MEDIUM, '中'),
        (PRIORITY_LOW, '低'),
    )

    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    priority = models.PositiveSmallIntegerField(
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt

    def mark_completed(self):
        self.completed = True
        self.save(update_fields=['completed'])
