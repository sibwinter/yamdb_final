from rest_framework import mixins, viewsets


class ListCreateDeleteMixin(mixins.ListModelMixin, mixins.DestroyModelMixin,
                            mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass
