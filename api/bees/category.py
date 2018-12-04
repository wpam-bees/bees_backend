from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from bees.models import Category


class CategorySerializer(serializers.ModelSerializer):
    active = serializers.SerializerMethodField()

    def get_active(self, obj):
        return self.context['request'].user.worker_bee.filters.categories.filter(pk=obj.pk).exists()

    class Meta:
        model = Category
        fields = '__all__'


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=True, methods=['POST'])
    def mark_interest(self, request, *args, **kwargs):
        instance = self.get_object()
        filters = request.user.worker_bee.filters
        add = request.data.get('interested', True)
        if add:
            filters.categories.add(instance)
            return Response(True)
        filters.categories.remove(instance)
        return Response(False)


