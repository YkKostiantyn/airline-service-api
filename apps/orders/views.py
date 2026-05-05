from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOrderOwnerOrAdmin
from apps.common.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

# Create your views here.

class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ["status", "user"]

    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]

    ordering_fields = [
        "id",
        "status",
        "created_at",
    ]

    ordering = ["-created_at"]

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Order.objects.select_related("user")
        user = self.request.user

        if getattr(user, "role", None) == "admin":
            return queryset.all()

        return queryset.filter(user=user)

    def filter_queryset(self, queryset):
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def paginate_queryset(self, queryset):
        paginator = self.pagination_class()
        return paginator.paginate_queryset(queryset, self.request, view=self), paginator

    @extend_schema(
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("ordering", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        responses=OrderListSerializer,
    )

    def get(self, request):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        page, paginator = self.paginate_queryset(queryset)

        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=OrderCreateSerializer, responses=OrderDetailSerializer)
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            response_serializer = OrderDetailSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailAPIView(APIView):
    permission_classes = [IsOrderOwnerOrAdmin]

    def get_object(self, pk):
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(self.request, order)
        return order

    def get(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

    @extend_schema(request=OrderDetailSerializer, responses=OrderDetailSerializer)
    def put(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderDetailSerializer(order, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=OrderDetailSerializer, responses=OrderDetailSerializer)
    def patch(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderDetailSerializer(order, data=request.data,context={'request': request},partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
