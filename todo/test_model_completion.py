from django.test import TestCase

from todo.models import Task


class TaskCompletionModelTestCase(TestCase):
    def test_mark_completed_updates_task(self):
        task = Task.objects.create(title='task1')

        task.mark_completed()

        task.refresh_from_db()
        self.assertTrue(task.completed)
