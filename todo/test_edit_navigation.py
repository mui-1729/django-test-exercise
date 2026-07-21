from django.test import Client, TestCase

from todo.models import Task


class EditNavigationTestCase(TestCase):
    def test_edit_page_has_cancel_link(self):
        task = Task.objects.create(title='task1')

        response = Client().get('/{}/update'.format(task.pk))

        self.assertContains(response, 'href="/{}/"'.format(task.pk))
        self.assertContains(response, '>Cancel</a>')
