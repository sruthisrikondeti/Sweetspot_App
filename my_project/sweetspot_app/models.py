from django.db import models
from django.contrib.auth.hashers import make_password



class Customer(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.email

    class Meta:
        db_table = 'customer'



class Cake(models.Model):
    name = models.CharField(max_length=255)
    flavour = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='cakes/',null=True, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cake'


class CakeCustomization(models.Model):
    message = models.TextField(blank=True, null=True)  # Made optional
    egg_version = models.CharField(max_length=50, blank=True, null=True)  # Made optional
    toppings = models.TextField(blank=True, null=True)  # Made optional
    shape = models.CharField(max_length=100, blank=True, null=True)  # Made optional
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)  # Links to Cake model
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Links to Customer model
    
    def __str__(self):
        return f"Customization for {self.cake.name} by {self.customer}"

    class Meta:
        db_table = 'cake_customization'
        unique_together = ('cake', 'customer') 


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cake = models.ManyToManyField(Cake)
    quantity = models.IntegerField()
    customization = models.ForeignKey(CakeCustomization, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'cart'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cake_customization = models.ForeignKey(CakeCustomization, null=False, default=1, on_delete=models.CASCADE)
    items = models.ManyToManyField(Cake)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField()
    order_status = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50)

    class Meta:
        db_table = 'order'