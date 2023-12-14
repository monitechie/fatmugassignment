from django.db import models

# Create your models here.


class Vendor(models.Model):
    name = models.CharField(max_length=30)
    contact_detail = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    vendor_code = models.CharField(max_length=100)
    on_time_delivery_rate = models.FloatField(blank=True, null=True)
    quality_rating_avg = models.FloatField(blank=True, null=True)
    average_response_time = models.FloatField(blank=True, null=True)
    fulfillment_rate = models.FloatField(blank=True, null=True)


status = (
    ('Pending', 'Pending'),
    ('completed', 'Completed'),
    ('Cancelled', 'Cancelled')
)


class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=100)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, default=1)
    order_date = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    items = models.JSONField()
    quantity = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=100, choices=status, default='Pending')
    quality_rating = models.FloatField(null=True)
    issue_date = models.DateTimeField(blank=True, null=True)
    acknowledgement_date = models.DateTimeField(blank=True, null=True)



class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, default=1)
    date = models.DateTimeField(blank=True, null=True)
    on_time_delivery_rate = models.FloatField(blank=True, null=True)
    quality_rating_avg = models.FloatField(blank=True, null=True)
    average_response_time = models.FloatField(blank=True, null=True)
    fulfillment_rate = models.FloatField(blank=True, null=True)
