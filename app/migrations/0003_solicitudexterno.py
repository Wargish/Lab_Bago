# Generated by Django 5.1.2 on 2024-11-29 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_tipo_informe_informe_categoría_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolicitudExterno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_externo', models.CharField(max_length=255)),
                ('correo_externo', models.EmailField(max_length=254)),
                ('descripcion', models.TextField()),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='peticiones_imagenes/')),
                ('pdf_peticion', models.FileField(blank=True, null=True, upload_to='peticiones/')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
