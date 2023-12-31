# Generated by Django 4.0.1 on 2022-12-24 00:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('criticalpath', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000)),
                ('amount', models.PositiveIntegerField()),
                ('status', models.CharField(max_length=1000)),
                ('unit', models.CharField(max_length=50)),
                ('internal_id', models.CharField(max_length=1000)),
                ('external_id', models.CharField(max_length=1000)),
                ('callback_url', models.URLField()),
                ('charge_encoded', models.CharField(max_length=1000)),
                ('uri', models.CharField(max_length=1000)),
                ('fee', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.CharField(max_length=1000)),
                ('expires_at', models.CharField(max_length=1000)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('user_credited', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type_text', models.IntegerField(choices=[(0, 'Debit'), (1, 'Credit')])),
            ],
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('unit', models.CharField(max_length=1000)),
                ('status', models.CharField(blank=True, max_length=500, null=True)),
                ('external_id', models.CharField(max_length=1000)),
                ('internal_id', models.CharField(max_length=1000)),
                ('description', models.TextField()),
                ('callback_url', models.URLField()),
                ('lnurl_withdrawal_encoded', models.CharField(max_length=1000)),
                ('uri', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.CharField(max_length=1000)),
                ('user_credited', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.PositiveIntegerField(default=0)),
                ('is_locked', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lightning_address', models.EmailField(blank=True, max_length=254, null=True)),
                ('creator', models.BooleanField(default=False, null=True)),
                ('bio', models.TextField()),
                ('profile_pic', models.ImageField(default='img1.jpg', null=True, upload_to='resource/profile_pics/%Y/%m/%D/')),
                ('tiktok_username', models.CharField(blank=True, max_length=255, null=True)),
                ('youtube_username', models.CharField(blank=True, max_length=255, null=True)),
                ('twitter_username', models.CharField(blank=True, max_length=255, null=True)),
                ('twitch_username', models.CharField(blank=True, max_length=255, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_code_text', models.CharField(max_length=1000)),
                ('transaction_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='marketplace.transactiontype')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000)),
                ('amount', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('transaction_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='marketplace.transactioncode')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid_at', models.DateField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('charge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='marketplace.charge')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='criticalpath.course')),
                ('journey', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='criticalpath.journey')),
                ('resource', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='criticalpath.resource')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
