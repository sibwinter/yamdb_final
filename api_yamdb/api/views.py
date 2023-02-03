from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User
from users.serializers import (RegisterSerializer, TokenSerializer,
                               UserSerializer)
from api.filters import TitleFilter
from api.permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrStaff
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleCreateOrUpdateSerializer,
                             TitleRetrieveSerializer)
from api.mixins import ListCreateDeleteMixin


def get_title_or_review_or_404(self, model, str_id: str):
    return get_object_or_404(
        model,
        id=int(self.kwargs.get(str_id))
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    valid_object = serializer.save()
    confirmation_code = default_token_generator.make_token(valid_object)
    send_mail(
        subject='Registration',
        message=f'Confirm code is: {confirmation_code}',
        from_email=None,
        recipient_list=[serializer.validated_data['email']],
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username'])
    if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response('Неверный код подтверждения или username',
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['=username']
    lookup_field = 'username'
    permission_classes = (IsAdmin,)

    @action(
        methods=[
            'patch',
            'get',
        ],
        detail=False,
        url_path='me',
        serializer_class=UserSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def users_profile(self, request):
        serializer = self.get_serializer(request.user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['role'] = request.user.role
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrStaff,)

    def get_queryset(self):
        review = get_title_or_review_or_404(self, Review, 'review_id')
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_title_or_review_or_404(self, Review, 'review_id')
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrStaff,)

    def get_queryset(self):
        title = get_title_or_review_or_404(self, Title, 'title_id')
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_title_or_review_or_404(self, Title, 'title_id')
        serializer.save(author=self.request.user, title=title)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (Title.objects.select_related('category')
                .annotate(rating=Avg('reviews__score')))
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitleCreateOrUpdateSerializer
        return TitleRetrieveSerializer


class GenreViewSet(ListCreateDeleteMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'


class CategoryViewSet(ListCreateDeleteMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'
