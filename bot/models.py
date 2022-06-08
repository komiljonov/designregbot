from uuid import uuid4
from django.db import models
from ckeditor.fields import RichTextField
from django.db.models.fields.files import FieldFile


class Region(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class User(models.Model):
    id: int
    chat_id = models.IntegerField()
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    region: Region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    is_admin: bool = models.BooleanField(default=False)


class Post(models.Model):
    media: FieldFile = models.FileField(upload_to="post", null=True, blank=True)
    comment: str = RichTextField()
    mediatype: int = models.IntegerField(choices=[
        (0, 'text'),
        (1, 'image'),
        (2, 'video'),
    ])
    @property
    def com(self) -> str:
        return self.comment.replace("<p>", "").replace("</p>", "").replace("<strong>", "<b>").replace("</strong>", "</b>").replace("<em>", "<i>").replace("</em>", "</i>").replace("<br />","\n").replace("\r\n\r\n", "\n").replace("&nbsp;", " ")
    
    @property
    def file(self):
        return open(f"{self.media.path}", 'rb')
