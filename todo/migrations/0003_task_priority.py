from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_task_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.PositiveSmallIntegerField(
                choices=[(1, '高'), (2, '中'), (3, '低')],
                default=2,
            ),
        ),
    ]
