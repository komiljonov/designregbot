# Generated by Django 4.0.5 on 2022-06-08 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_post_mediatype_alter_post_comment_alter_post_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='chat_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
