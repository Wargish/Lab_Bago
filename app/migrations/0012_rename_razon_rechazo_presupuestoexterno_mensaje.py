# Generated by Django 5.1.2 on 2024-12-04 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_presupuestoexterno_fecha_creacion_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='presupuestoexterno',
            old_name='razon_rechazo',
            new_name='mensaje',
        ),
    ]