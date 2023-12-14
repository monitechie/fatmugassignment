from django.urls import path

from apis.views import PerformanceMetricsView, PurchaseOrderAcknowledgeView, PurchaseOrderDetailView, PurchaseOrderViewSet, VendorViewSet, VendorDetailView


urlpatterns = [
    path('vendors/', VendorViewSet.as_view(), name='vendorprofile'),
    path('vendors/<int:pk>/', VendorDetailView.as_view(), name='vendordetail'),
    # Purchase Order
    path('purchase_orders/', PurchaseOrderViewSet.as_view(), name='purchaseorder'),
    path('purchase_orders/<int:pk>/',
         PurchaseOrderDetailView.as_view(), name='purchasedetail'),
    path('vendors/<int:pk>/performance/',
         PerformanceMetricsView.as_view(), name='performance'),
    path('purchase_orders/<int:pk>/acknowledge/',
         PurchaseOrderAcknowledgeView.as_view(), name='purchase-order-acknowledge'),
]
