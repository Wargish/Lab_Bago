# Generated by Django 5.1.2 on 2024-12-20 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internal_workers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbacktarea',
            name='comentarios',
            field=models.TextField(blank=True, default='Trabajo aprobado'),
        ),
    ]
