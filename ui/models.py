from django.db import models
#from django.contrib.auth.models import User
#from byteCipher.settings import AUTH_USER_MODEL
from userAccess.models import CustomUser
from django.core.files import File
import os
import  urllib.request 
import tempfile


class Product(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="product",null=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    price = models.PositiveIntegerField(blank=False, null=False)
    color = models.CharField(max_length=50, blank=False, default="N/A")
    
    def __str__(self):
        return self.name

class productImages(models.Model):
    product = models.ForeignKey(Product, related_name='productimages' , on_delete=models.CASCADE)
    images = models.ImageField(upload_to = 'images/')
    image_url = models.URLField(blank=True)
    class Meta:
        unique_together = ('product', 'id')
        ordering = ['id']

    def save(self, *args, **kwargs):
        ""
        super().save(*args, **kwargs) 

    """def __str__(self):
        return self.product.name
        """
def get_remote_image(self):
    print("get_remote_image starting")
    if self.image_url and self.images:
        print("saving remote images")
        img_temp = tempfile.NamedTemporaryFile(delete=True)
        img_temp.write(urllib.request.urlopen(self.image_url).read())
        img_temp.flush()
        self.images.save(f"image_{self.pk}", File(img_temp))
        self.save()
    #else:
    #    self.save()
"""def get_remote_image(self):
    if self.image_url and not self.images:
        result = urllib.urlretrieve(self.image_url)
        self.images.save(
                os.path.basename(self.image_url),
                File(open(result[0]))
                )
        self.save()
"""