from django.db import models
from django.contrib.auth.models import User

STATE_CHOICES = (
    ('Alaminos', 'Alaminos'),
    ('Bay', 'Bay'),
    ('Biñan', 'Biñan'),
    ('Cabuyao', 'Cabuyao'),
    ('Calamba', 'Calamba'),
    ('Calauan', 'Calauan'),
    ('Cavinti', 'Cavinti'),
    ('Famy', 'Famy'),
    ('Kalayaan', 'Kalayaan'),
    ('Liliw', 'Liliw'),
    ('Los Baños', 'Los Baños'),
    ('Luisiana', 'Luisiana'),
    ('Lumban', 'Lumban'),
    ('Mabitac', 'Mabitac'),
    ('Magdalena', 'Magdalena'),
    ('Majayjay', 'Majayjay'),
    ('Nagcarlan', 'Nagcarlan'),
    ('Paete', 'Paete'),
    ('Pagsanjan', 'Pagsanjan'),
    ('Pakil', 'Pakil'),
    ('Pangil', 'Pangil'),
    ('Pila', 'Pila'),
    ('Rizal', 'Rizal'),
    ('San Pablo', 'San Pablo'),
    ('San Pedro', 'San Pedro'),
    ('Santa Cruz', 'Santa Cruz'),
    ('Santa Maria', 'Santa Maria'),
    ('Santa Rosa', 'Santa Rosa'),
    ('Siniloan', 'Siniloan'),
    ('Victoria', 'Victoria'),
)


CATEGORY_CHOICES = (
    ('AR', 'Armani'),
    ('CD', 'Creed'),
    ('YSL', 'Yves Saint Laurent'),
    ('DR', 'Dior'),
    ('MM', 'Maison Margiela'),
    ('PDM', 'Parfumes De Marley'),
    ('VT','Valentino'),
    ('LV','Louis Vuitton')
)

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    composition = models.TextField(default='', blank=True)
    prodapp = models.TextField(default='', blank=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    product_image = models.ImageField(upload_to='product')

    def __str__(self):
        return self.title
    
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=100)
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel'),
    ('Pending','Pending'),
)

class Payment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)

class OrderPlaced(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("To Ship", "To Ship"),
        ("To Deliver", "To Deliver"),
        ("To Receive", "To Receive"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    ordered_date = models.DateTimeField(auto_now_add=True)
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
