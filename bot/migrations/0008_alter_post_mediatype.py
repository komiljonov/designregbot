# Generated by Django 4.0.5 on 2022-07-06 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_started'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='mediatype',
            field=models.IntegerField(choices=[(0, 'text'), (1, 'image'), (2, 'video'), (3, 'doc')]),
        ),
    ]