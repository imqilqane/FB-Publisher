# Generated by Django 3.1.4 on 2020-12-09 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settingmodel2',
            name='group_join_per_time',
            field=models.IntegerField(default=6),
        ),
        migrations.AlterField(
            model_name='settingmodel2',
            name='post_per_time',
            field=models.IntegerField(default=6),
        ),
        migrations.AlterField(
            model_name='settingmodel2',
            name='to_wait_after_each_join',
            field=models.IntegerField(default=12),
        ),
    ]
