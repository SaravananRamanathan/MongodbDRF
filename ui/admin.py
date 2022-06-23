
from django.contrib import admin
from ui import models
# Register your models here.
#linking dashboard with the database part

#admin.site.register(models.Product)
#since using a cusotm usermodel, making sure its visible in django admins
#from django.contrib.auth.admin import UserAdmin
#from userAccess.models import CustomUser 

#admin.site.register(CustomUser, UserAdmin)

class ImageView(admin.StackedInline):
    model = models.productImages
 
@admin.register(models.Product)
class PostAdmin(admin.ModelAdmin):
    inlines = [ImageView]
 
    class Meta:
       model = models.Product
 
@admin.register(models.productImages)
class ImageView(admin.ModelAdmin):
    pass