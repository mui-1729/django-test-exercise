from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from todo.models import Task

class Command(BaseCommand):
    help = '期限が24時間以内の未完了タスクを確認する'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        tomorrow = now + timedelta(days=1)
        
        tasks = Task.objects.filter(completed=False, due_at__range=(now, tomorrow))
        
        if tasks.exists():
            self.stdout.write(self.style.WARNING('以下のタスクの期限が迫っています:'))
            for task in tasks:
                self.stdout.write(f'- {task.title} (期限: {task.due_at})')
        else:
            self.stdout.write(self.style.SUCCESS('期限が24時間以内のタスクはありません。'))