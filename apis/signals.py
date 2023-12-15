from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from .models import Vendor, PurchaseOrder, HistoricalPerformance


@receiver(post_save, sender=PurchaseOrder)
def update_performance_metrics(sender, instance, **kwargs):
    with transaction.atomic():
        vendor = instance.vendor

        # On-Time Delivery Rate
        completed_orders = vendor.purchaseorder_set.filter(status='completed')
        total_completed_orders = completed_orders.count()
        on_time_delivery_rate = (completed_orders.filter(delivery_date__lte=instance.delivery_date).count(
        ) / total_completed_orders) * 100 if total_completed_orders != 0 else 0

        # Quality Rating Average
        quality_rating_avg = completed_orders.aggregate(
            avg_rating=models.Avg('quality_rating'))['avg_rating'] or 0

        # Average Response Time
        avg_response_time_seconds = (vendor.purchaseorder_set.filter(acknowledgement_date__isnull=False)
                                     .aggregate(avg_time=models.Avg(models.F('acknowledgement_date') - models.F('issue_date')))['avg_time']
                                     or timezone.timedelta()).total_seconds()

        # Fulfilment Rate
        total_orders = vendor.purchaseorder_set.filter(
            status='completed').count()
        fulfillment_rate = (completed_orders.filter(
            status='completed').count() / total_orders) * 100 if total_orders != 0 else 0

        # Update HistoricalPerformance model
        HistoricalPerformance.objects.update_or_create(
            vendor=vendor,
            on_time_delivery_rate=on_time_delivery_rate,
            quality_rating_avg=quality_rating_avg,
            average_response_time=avg_response_time_seconds,
            fulfillment_rate=fulfillment_rate
        )
