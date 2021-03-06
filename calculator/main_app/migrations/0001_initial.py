# Generated by Django 2.1.7 on 2019-04-20 10:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('role', models.IntegerField(choices=[(1, 'admin'), (2, 'investor')], default=1, verbose_name='Role')),
                ('first_name', models.CharField(blank=True, max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DownloadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField()),
                ('percent', models.DecimalField(decimal_places=2, max_digits=7)),
                ('project_name', models.CharField(max_length=255)),
                ('irr', models.CharField(max_length=255)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IncomeOutgo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.IntegerField()),
                ('income', models.DecimalField(decimal_places=2, max_digits=16)),
                ('outgo', models.DecimalField(decimal_places=2, max_digits=16)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.DownloadedFile')),
            ],
        ),
    ]
