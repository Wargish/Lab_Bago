# Generated by Django 5.1.2 on 2024-12-03 15:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_solicitudexterno_correo_externo_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='presupuestoexterno',
            old_name='archivo_pdf',
            new_name='archivo',
        ),
        migrations.RemoveField(
            model_name='presupuestoexterno',
            name='actualizado_en',
        ),
        migrations.RemoveField(
            model_name='presupuestoexterno',
            name='aprobado',
        ),
        migrations.RemoveField(
            model_name='presupuestoexterno',
            name='creado_en',
        ),
        migrations.AddField(
            model_name='presupuestoexterno',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], default='pendiente', max_length=20),
        ),
        migrations.AddField(
            model_name='presupuestoexterno',
            name='razon_rechazo',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='presupuestoexterno',
            name='solicitud',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='presupuesto', to='app.solicitudexterno'),
        ),
    ]
