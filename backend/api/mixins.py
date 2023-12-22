from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny


class SimpleViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):

    permission_classes = (AllowAny,)
    pagination_class = None
