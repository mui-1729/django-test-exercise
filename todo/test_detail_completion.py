from django.test import Client, TestCase

from todo.models import Task


class DetailCompletionTestCase(TestCase):
    def test_incomplete_detail_shows_close_button(self):
        task = Task.objects.create(title='task1')

        response = Client().get('/{}/'.format(task.pk))

        self.assertContains(response, "action=\"/{}/close/\"".format(task.pk))
        self.assertContains(response, '<button type="submit">終了</button>', html=True)
