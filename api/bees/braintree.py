from django.conf import settings
from rest_framework import permissions, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response


class BraintreeViewSet(viewsets.GenericViewSet):
    gateway = settings.GATEWAY
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user.employer_bee

    @action(detail=False, methods=['GET'])
    def token(self, request, *args, **kwargs):
        instance = self.get_object()
        token = self.gateway.client_token.generate({
            'customer_id': instance.braintree_id,
            'merchant_account_id': 'bees',
        })
        return Response(token)
