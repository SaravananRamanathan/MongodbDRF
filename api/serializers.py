from rest_framework import serializers 
from ui.models import Product,productImages
from userAccess.models import CustomUser  


class customUserSerializer(serializers.ModelSerializer):
    ""
    class Meta:
        model=CustomUser
        fields=['id','username','email','password']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    def create(self,validated_data):
        password=validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password) #hashing password
        instance.save()
        return instance

class productImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=productImages
        fields=['images']

class productSerializer(serializers.ModelSerializer):
    
    productimages=productImageSerializer(many=True,read_only=True)
    class Meta:
        model = Product
        #fields = '__all__' 
        fields = ('id','user_id','name','price','color','productimages')
        #exclude=['user']

