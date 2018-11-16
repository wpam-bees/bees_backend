from rest_framework import serializers

from bees.models import JobFilter


class JobFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobFilter
        fields = '__all__'
