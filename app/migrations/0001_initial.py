# Generated by Django 5.1.2 on 2024-11-19 16:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ubicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Informe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('objetivo', models.TextField(blank=True, null=True)),
                ('mensaje', models.TextField(blank=True, null=True)),
                ('imagen', models.ImageField(upload_to='imagenes/informes/')),
                ('tipo_informe', models.CharField(choices=[('INF', 'Infraestructura'), ('MAQ', 'Maquinaria')], default='INF', max_length=3)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='informes', to=settings.AUTH_USER_MODEL)),
                ('ubicacion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.ubicacion')),
            ],
            options={
                'ordering': ['-creado_en'],
            },
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leido', models.BooleanField(default=False)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('mensaje', models.TextField(blank=True, null=True)),
                ('informe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.informe')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('objetivo', models.TextField(blank=True, null=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('asignado_a', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tareas', to=settings.AUTH_USER_MODEL)),
                ('estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.estado')),
                ('informe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.informe')),
            ],
        ),
        migrations.CreateModel(
            name='ReporteTarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField(blank=True, null=True)),
                ('imagen', models.ImageField(upload_to='imagenes/reportes_tarea/')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('tarea', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reporte_tarea', to='app.tarea')),
            ],
        ),
        migrations.CreateModel(
            name='FeedbackTarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aprobado', models.BooleanField()),
                ('comentarios', models.TextField(blank=True, null=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('tarea', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.tarea')),
            ],
        ),
    ]
