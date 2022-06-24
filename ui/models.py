from django.db import models
#from django.contrib.auth.models import User
#from byteCipher.settings import AUTH_USER_MODEL
from userAccess.models import CustomUser
class Product(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="product",null=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    price = models.PositiveIntegerField(blank=False, null=False)
    color = models.CharField(max_length=50, blank=False, default="N/A")
    
    def __str__(self):
        return self.name

class productImages(models.Model):
    product = models.ForeignKey(Product, related_name='productimages' , on_delete=models.CASCADE)
    images = models.FileField(upload_to = 'images/')
 
    class Meta:
        unique_together = ('product', 'id')
        ordering = ['id']

    """def __str__(self):
        return self.product.name
        """