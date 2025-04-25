from django.db import models
import datetime

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=13,null = True)
    is_admin = models.BooleanField(default=False)

class Menu(models.Model):
    item_name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=2,max_digits=6)
    description = models.TextField()
    image = models.ImageField(upload_to='media/')

    def __str__(self):
        return f"{self.item_name}"


class Order(models.Model):
    made_by = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="orders")
    status = models.CharField(default = "placing",max_length=30)
    created_at = models.DateTimeField(null=True)
    menu_items = models.ManyToManyField(Menu,through='OrderItem')
    grand_total = models.DecimalField(decimal_places=2,max_digits=10,default=0)
    payment_method = models.CharField(max_length=30,default='cash')
    
    def calculate_grand_total(self):
        return sum(item.subtotal for item in self.order_items.all())

    def __str__(self):
        return f"Order #{self.id}, by {self.made_by}"
    
    

class ShippingDetails(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="shipping_address")
    houseNo = models.CharField(max_length=10)
    flatNo = models.CharField(max_length=10)
    street =  models.CharField(max_length=30)
    additional = models.CharField(max_length=30,default=None,null=True)

    def __str__(self):
        return  f"""House #{self.houseNo} , Flat #{self.flatNo}
{self.street}

Additional Instructions: {self.additional}"""

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name="order_items")
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)  
    subtotal = models.DecimalField(decimal_places=2, max_digits=8,default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.menu_item.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.menu_item} ( x{self.quantity} )"

class Configuration(models.Model):
    title = models.CharField(max_length=30,default=None)
    logo = models.ImageField(upload_to='media/',default = None)