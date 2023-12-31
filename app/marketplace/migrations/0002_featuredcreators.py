# Generated by Django 4.0.1 on 2022-12-29 04:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedCreators',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence_number', models.PositiveIntegerField()),
                ('creator', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='featured_creators', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
