# # from django.db.models.signals import post_save
# # from django.dispatch import receiver
# # from apis.models import vendor, PurchaseOrder, HistoricalPerformance
# # from django.utils import timezone


# # @receiver(post_save, sender=PurchaseOrder)
# # def calculate_on_time_delivery_rate(sender, instance, **kwargs):
# #     if instance.status == 'Completed':
# #         try:
# #             product_performance = HistoricalPerformance.objects.get(vendor=instance.vendo)
# #         except HistoricalPerformance.DoesNotExist:
# #             performance = HistoricalPerformance(
# #                 vendor=instance.vendor, date=instance.order_date)
# #         # Calculate on time delivery rate
# #         on_time_deliveries = instance.vendor.PurchaseOrder.filter(
# #             delivery_date__lte=instance.delivery_date, status='Completed').count()
# #         total_deliveries = instance.vendor.PurchaseOrder.filter(
# #             delivery_date__lte=instance.delivery_date).count()
# #         on_time_delivery_rate = on_time_deliveries / total_deliveries * 100
# #         performance.delivery_rate = on_time_delivery_rate
# #         performance.save()
# # signals.py

# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from django.utils import timezone
# from .models import HistoricalPerformance, PurchaseOrder
# from django.db import models


# @receiver(pre_save, sender=PurchaseOrder)
# def update_HistoricalPerformance(sender, instance, **kwargs):
#     # Check if the status is changing to 'completed'
#     if instance.pk:
#         previous_status = PurchaseOrder.objects.get(pk=instance.pk).status
#         if previous_status != 'completed' and instance.status == 'completed':
#             # Update historical performance when status changes to 'completed'
#             completed_orders = instance.vendor.purchaseorder_set.filter(
#                 status='completed', quality_rating__isnull=False)
#             total_quality_ratings = completed_orders.count()
#             sum_quality_ratings = completed_orders.aggregate(
#                 sum_rating=models.Sum('quality_rating'))['sum_rating']
#             instance.vendor.quality_rating_avg = sum_quality_ratings / \
#                 total_quality_ratings if total_quality_ratings != 0 else 0
#         # Calculate average_response_time
#         previous_ack_date = PurchaseOrder.objects.get(
#             pk=instance.pk).acknowledgement_date
#         if previous_ack_date is None and instance.acknowledgement_date is not None:

#             response_times = instance.vendor.purchaseorder_set.filter(
#                 acknowledgement_date__isnull=False).values_list('acknowledgement_date', 'issue_date')
#             total_response_times = sum(
#                 (po.acknowledgement_date - po.issue_date).seconds for po in vendor.purchaseorder_set.filter(acknowledgement_date__isnull=False))

#             total_orders = instance.vendor.purchaseorder_set.filter(
#                 acknowledgement_date__isnull=False).count()

#             instance.vendor.average_response_time = total_response_times / \
#                 total_orders if total_orders != 0 else 0
#             HistoricalPerformance.objects.create(
#                 vendor=instance.vendor,
#                 date=timezone.now(),
#                 on_time_delivery_rate=instance.vendor.on_time_delivery_rate,
#                 quality_rating_avg=instance.vendor.quality_rating_avg,
#                 average_response_time=instance.vendor.average_response_time,
#                 fulfillment_rate=instance.vendor.fulfillment_rate
#             )


# signals.py
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
        HistoricalPerformance.objects.create(
            vendor=vendor,
            on_time_delivery_rate=on_time_delivery_rate,
            quality_rating_avg=quality_rating_avg,
            average_response_time=avg_response_time_seconds,
            fulfillment_rate=fulfillment_rate
        )
