from uuid import uuid4
from django.contrib import admin

from bot.models import Post, Region, User

# Register your models here.



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id','media', 'comment')
    

    def has_add_permission(self, request) -> bool:
        return not Post.objects.count()


admin.site.register(Region)
admin.site.register(User)