# Generated by Django 4.0.1 on 2023-03-30 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_purchase_ebook_featuredebooks'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_text', models.CharField(max_length=500)),
                ('iso_code', models.CharField(max_length=3)),
            ],
        ),
    ]
