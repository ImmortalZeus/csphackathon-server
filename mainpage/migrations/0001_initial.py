# Generated by Django 4.0.3 on 2022-09-09 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contestant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('members', models.JSONField(blank=True, default=dict, null=True)),
                ('firstac', models.JSONField(blank=True, default=dict, null=True)),
                ('score', models.JSONField(blank=True, default=dict, null=True)),
                ('penalty', models.JSONField(blank=True, default=dict, null=True)),
                ('submissions', models.JSONField(blank=True, default=dict, null=True)),
                ('submitted', models.BooleanField(default=False)),
                ('tscore', models.IntegerField(default=0)),
                ('tpenalty', models.IntegerField(default=0)),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('testnum', models.IntegerField(default=1)),
                ('answer', models.JSONField(default=list)),
                ('mscore', models.IntegerField(default=100)),
                ('submissions', models.JSONField(blank=True, default=list, null=True)),
                ('ordered', models.BooleanField(default=True)),
                ('unsolved', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='LeaderBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='rankingsave', max_length=255, unique=True)),
                ('value', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]
