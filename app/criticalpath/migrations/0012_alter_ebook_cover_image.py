# Generated by Django 4.0.1 on 2023-03-31 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('criticalpath', '0011_alter_ebook_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebook',
            name='cover_image',
            field=models.ImageField(blank=True, default='seo-card-image.png', null=True, upload_to='ebooks/cover_images/'),
        ),
    ]