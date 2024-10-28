from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group

def create_groups(sender, **kwargs):
    Group.objects.get_or_create(name='Operarios')
    Group.objects.get_or_create(name='Técnicos')

def ready(app_config):
    post_migrate.connect(create_groups, sender=app_config)