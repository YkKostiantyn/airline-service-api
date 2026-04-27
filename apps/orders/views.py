from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer
from drf_spectacular.utils import extend_schema

# Create your views here.

class OrderListCreateAPIView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(request=OrderCreateSerializer, responses=OrderDetailSerializer)
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            response_serializer = OrderDetailSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Order, pk=pk)

    def get(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

    @extend_schema(request=OrderDetailSerializer, responses=OrderDetailSerializer)
    def put(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderDetailSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=OrderDetailSerializer, responses=OrderDetailSerializer)
    def patch(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderDetailSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

