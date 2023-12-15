from datetime import timezone
from django.shortcuts import render
from rest_framework import viewsets
from apis.models import HistoricalPerformance, Vendor, PurchaseOrder
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from apis.serializers import HistoricalPerformanceSerializer, PurchaseOrderAcknowledgeSerializer, PurchaseOrderSerializer, VendorSerializer
from rest_framework import status, generics
from django.db import models
# Create your views here.


class VendorViewSet(ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class VendorDetailView(APIView):
    def get(self, request, pk):
        try:
            vendor_profile = Vendor.objects.get(pk=pk)

            serializer = VendorSerializer(vendor_profile)
            return Response(serializer.data)
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            vendor_profile = Vendor.objects.get(pk=pk)
            serializer = VendorSerializer(vendor_profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except vendor_profile.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            vendor_profile = Vendor.objects.get(pk=pk)
            vendor_profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except vendor_profile.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

# Purchase Order

# Create and List


class PurchaseOrderViewSet(ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
# Get,Put and Delete


class PurchaseOrderDetailView(APIView):
    def get(self, request, pk):
        try:
            order = PurchaseOrder.objects.get(pk=pk)
            serializer = PurchaseOrderSerializer(order)
            return Response(serializer.data)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "Order detail not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            order = PurchaseOrder.objects.get(pk=pk)
            serializer = PurchaseOrderSerializer(order, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except order.DoesNotExist:
            return Response({"error": "Order detail not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            order = PurchaseOrder.objects.get(pk=pk)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except order.DoesNotExist:
            return Response({"error": "Order Detail vnot found"}, status=status.HTTP_404_NOT_FOUND)


class PerformanceMetricsView(APIView):
    def get(self, request, pk):
        try:
            vendor_detail = HistoricalPerformance.objects.get(pk=pk)
            serializer = HistoricalPerformanceSerializer(vendor_detail)
            return Response(serializer.data)
        except:
            return Response({"error": "Performance of Vendor Detail vnot found"}, status=status.HTTP_404_NOT_FOUND)


class PurchaseOrderAcknowledgeView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def perform_update(self, serializer):
        instance = serializer.save(acknowledgement_date=timezone.now())
        instance.vendor.average_response_time = instance.vendor.purchaseorder_set.filter(acknowledgement_date__isnull=False).aggregate(
            avg_response_time=models.Avg(models.F('acknowledgement_date') - models.F('issue_date')))['avg_response_time']
        instance.vendor.save()
# PurchaseOrder Acknowledgement


class PurchaseOrderAcknowledgeView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderAcknowledgeSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if 'acknowledgement_date' in request.data:
            acknowledgement_date = request.data['acknowledgement_date']

            instance.acknowledgement_date = acknowledgement_date
            instance.save()

            return Response({'message': 'Purchase order acknowledged successfully.'}, status=status.HTTP_200_OK)
