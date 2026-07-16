from django.test import TestCase, Client
from django.utils import timezone
from datetime import datetime
from todo.models import Task

# Create your tests here.


class SampleTestCase(TestCase):
    def test_sample(self):
        self.assertEqual(1 + 2, 3)


class TaskModelTestCase(TestCase):
    def test_create_task1(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        task = Task(title='task1', due_at=due)
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task1')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, due)

    def test_create_task2(self):
        task = Task(title='task2')
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task2')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, None)
        self.assertEqual(task.notes, '')
        self.assertEqual(task.priority, Task.PRIORITY_MEDIUM)

    def test_create_task_with_notes(self):
        task = Task.objects.create(title='task with notes', notes='Remember this')

        self.assertEqual(task.notes, 'Remember this')

    def test_create_task_with_priority(self):
        task = Task(title='urgent task', priority=Task.PRIORITY_HIGH)
        task.save()

        self.assertEqual(Task.objects.get(pk=task.pk).priority, Task.PRIORITY_HIGH)

    def test_is_overdue_future(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()

        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_past(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()

        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task1')
        task.save()

        self.assertFalse(task.is_overdue(current))


class TodoViewTestCase(TestCase):
    def test_index_get(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)

    def test_index_task_shows_priority(self):
        Task.objects.create(title='urgent task', priority=Task.PRIORITY_HIGH)

        response = Client().get('/')

        self.assertContains(response, 'Priority: 高')

    def test_index_post(self):
        client = Client()
        data = {
            'title': 'Test Task',
            'due_at': '2024-06-30 23:59:59',
            'notes': 'Task details',
            'priority': Task.PRIORITY_HIGH,
        }
        response = client.post('/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].notes, 'Task details')
        self.assertEqual(response.context['tasks'][0].priority, Task.PRIORITY_HIGH)

    def test_index_post_without_notes(self):
        response = Client().post('/', {'title': 'No notes'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.get(title='No notes').notes, '')

    def test_index_get_order_priority(self):
        low = Task.objects.create(title='low', priority=Task.PRIORITY_LOW)
        high = Task.objects.create(title='high', priority=Task.PRIORITY_HIGH)
        medium = Task.objects.create(title='medium', priority=Task.PRIORITY_MEDIUM)

        response = Client().get('/?order=priority')

        self.assertEqual(list(response.context['tasks']), [high, medium, low])

    def test_index_get_order_post(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=post')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task2)
        self.assertEqual(response.context['tasks'][1], task1)

    def test_index_get_order_due(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=due')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task1)
        self.assertEqual(response.context['tasks'][1], task2)

    def test_detail_get_success(self):
        task = Task(
            title='task1',
            due_at=timezone.make_aware(datetime(2024, 7, 1)),
            notes='Detailed note',
            priority=Task.PRIORITY_HIGH,
        )
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)
        self.assertContains(response, 'Notes: Detailed note')
        self.assertContains(response, 'Priority: 高')

    def test_detail_get_fail(self):
        client = Client()
        response = client.get('/1/')

        self.assertEqual(response.status_code, 404)

    def test_close_post_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.post('/{}/close/'.format(task.pk))

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(pk=task.pk)
        self.assertTrue(task.completed)

    def test_close_post_fail(self):
        client = Client()
        response = client.post('/999/close/')

        self.assertEqual(response.status_code, 404)

    def test_index_incomplete_task_shows_close_action(self):
        task = Task(title='task1')
        task.save()
        client = Client()
        response = client.get('/')

        self.assertContains(response, 'Status: Not Completed')
        self.assertContains(response, '/{}/close/'.format(task.pk))
        self.assertContains(response, '<button type="submit">終了</button>', html=True)

    def test_index_completed_task_hides_close_action(self):
        task = Task(title='task1', completed=True)
        task.save()
        client = Client()
        response = client.get('/')

        self.assertContains(response, 'Status: Completed')
        self.assertNotContains(response, '/{}/close/'.format(task.pk))
        self.assertNotContains(response, '<button type="submit">終了</button>', html=True)

    def test_delete_get_shows_confirmation(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/delete'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/delete_confirm.html')
        self.assertEqual(response.context['task'], task)
        self.assertContains(response, task.title)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_delete_post_success(self):
        task = Task.objects.create(title='task1')

        response = Client().post('/{}/delete'.format(task.pk))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_confirmation_cancel(self):
        task = Task.objects.create(title='task1')

        response = Client().get('/{}/delete'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<a href="/{}/">キャンセル</a>'.format(task.pk),
            html=True,
        )
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_update_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/update'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/edit.html')
        self.assertEqual(response.context['task'], task)

    def test_update_get_fail(self):
        client = Client()
        response = client.get('/999/update')

        self.assertEqual(response.status_code, 404)

    def test_update_post_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        data = {
            'title': 'task2',
            'due_at': '2024-08-01 12:00:00',
            'notes': 'Updated note',
            'priority': Task.PRIORITY_LOW,
        }
        response = client.post('/{}/update'.format(task.pk), data)

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task2')
        self.assertEqual(task.due_at, timezone.make_aware(datetime(2024, 8, 1, 12, 0, 0)))
        self.assertEqual(task.notes, 'Updated note')
        self.assertEqual(task.priority, Task.PRIORITY_LOW)

    def test_delete_get_fail(self):
        client = Client()
        response = client.get('/1/delete')

        self.assertEqual(response.status_code, 404)

    def test_delete_post_fail(self):
        response = Client().post('/999/delete')

        self.assertEqual(response.status_code, 404)

    def test_delete_post_requires_csrf_token(self):
        task = Task.objects.create(title='task1')

        response = Client(enforce_csrf_checks=True).post(
            '/{}/delete'.format(task.pk)
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_update_post_fail(self):
        client = Client()
        data = {'title': 'task2', 'due_at': '2024-08-01 12:00:00'}
        response = client.post('/999/update', data)

        self.assertEqual(response.status_code, 404)
