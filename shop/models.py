from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

# Create your models here.
class Instrument(models.Model):
    instrument_id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=100, null=False)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    rating = models.FloatField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='instruments', null=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.model}"

class Category(models.Model):

    INSTRUMENT_TYPES = [
        ('ELECTRIC', 'Electric'),
        ('ACOUSTIC', 'Acoustic'),
        ('ELECTRO-ACOUSTIC', 'Electro-Acoustic'),
    ]
    
    category_id = models.AutoField(primary_key=True)
    instrument = models.CharField(max_length=50, null=False) # poate fi chitara, bas, tobe, etc.
    type = models.CharField(
        max_length=20, 
        choices=INSTRUMENT_TYPES,
        default='ACOUSTIC'
    )
    def __str__(self):
        return f"{self.instrument} - {self.get_type_display()}"

class InstrumentImage(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='images')
    path = models.ImageField(upload_to='instruments/')
    primary_image = models.BooleanField(default=False)      # pentru a marca imaginea principala
    order = models.IntegerField(default=0)                  # pentru a ordona imaginile
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.instrument.model} - {self.order}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)
    instrument = models.ManyToManyField(Instrument,related_name='orders')
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PROCESSING')

    def __str__(self):
        return f"{self.order_id} status: {self.status}"


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='order_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(null=False)

    def __str__(self):
        return f"{self.order_item_id} - {self.instrument.model} - {self.order.order_id}"
    

class Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='discounts')
    discount_value = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=False)

    def __str__(self):
        return f"{self.discount_id} - {self.instrument.model} - {self.discount_value}%"



