from django.urls import path, reverse_lazy
from django.conf.urls.static import static
from django.conf import settings


from . import views

app_name='criticalpath'
urlpatterns = [
    path('journeys/', views.journey_list, name='journey_list'),
    path('my-criticalpath/', views.UserCriticalPathDetailView.as_view(), name='my-criticalpath'),
    # path('my-saved-journeys', views.UserSavedJourneysListView.as_view(), name='my-saved-journeys'),
    # path('journey/<int:pk>/', views.JourneyDetailView.as_view(), name='journey_detail'),
    # path('journey/create/',
    #     views.JourneyCreateView.as_view(success_url=reverse_lazy('criticalpath:phase_create')), name='journey_create'),
    # path('journey/<int:pk>/update/',
    #     views.JourneyUpdateView.as_view(success_url=reverse_lazy('criticalpath:journey_list')), name='journey_update'),
    # path('journey/<int:pk>/delete/',
    #     views.JourneyDeleteView.as_view(success_url=reverse_lazy('criticalpath:journey_list')), name='journey_delete'),
    # path('journey/<int:pk>/comment/', views.CommentCreateView.as_view(), name='comment_create'),
    # path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(success_url=reverse_lazy('journey_list')), name='comment_delete'),
    # path('journey/<int:pk>/favorite',
    #     views.AddFavoriteView.as_view(), name='journey_favorite'),
    # path('journey/<int:pk>/unfavorite',
    #     views.DeleteFavoriteView.as_view(), name='journey_unfavorite'),
    # path('journey/<int:journey_pk>/resource/', views.ResourceAddView.as_view(success_url=reverse_lazy('criticalpath:journey_detail')), name='resource_add'),

    path('resource/create/', views.ResourceCreateView.as_view(success_url=reverse_lazy('home')), name='resource_create'),
    path('resource/<int:resource_pk>/', views.ResourceDetailView.as_view(), name='resource_detail'),
    path('resource/<int:resource_pk>/update/', views.ResourceUpdateView.as_view(), name='resource_update'),
    path('resource/<int:resource_pk>/delete/', views.ResourceDeleteView.as_view(), name='resource_delete'),

    path('ebook/create/', views.EbookCreateView.as_view(success_url=reverse_lazy('home')), name='ebook_create'),
    path('ebook/<int:ebook_pk>/splits/', views.EbookPaymentSplitsView.as_view(), name='ebook_add_splits'),
    path('ebook/<int:ebook_pk>/', views.EbookDetailView.as_view(), name='ebook_detail'),
    path('ebook/<int:ebook_pk>/update/', views.EbookUpdateView.as_view(), name='ebook_update'),
    path('ebook/<int:ebook_pk>/delete/', views.EbookDeleteView.as_view(), name='ebook_delete'),

    path('workshop/create/', views.WorkshopCreateView.as_view(success_url=reverse_lazy('home')), name='workshop_create'),
    path('workshop/<int:workshop_pk>/splits/', views.WorkshopPaymentSplitsView.as_view(), name='workshop_add_splits'),
    path('workshop/<int:workshop_pk>/', views.WorkshopDetailView.as_view(), name='workshop_detail'),
    path('workshop/<int:workshop_pk>/update/', views.WorkshopUpdateView.as_view(), name='workshop_update'),
    path('workshop/<int:workshop_pk>/delete/', views.WorkshopDeleteView.as_view(), name='workshop_delete'),

    path('course/create/', views.CourseCreateView.as_view(success_url=reverse_lazy('criticalpath:creator')), name='course_create'),
    path('course/<int:course_pk>/add/', views.CourseAddResourcesView.as_view(), name='course_add_resources'),
    path('course/<int:course_pk>/splits/', views.CoursePaymentSplitsView.as_view(), name='course_add_splits'),
    path('course/<int:course_pk>/resource/<int:resource_pk>/', views.CourseResourceDetailView.as_view(), name='course_resource_detail'),
    path('course/<int:course_pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:course_pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('course/<int:course_pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),



    path('creator/', views.creation_list, name="my-creations"),
    path('creator/signup/', views.creator_signup, name="creator_signup"),

    # uncomment if you want to enable rewards
    # path('course/<int:course_pk>/resource/<int:resource_pk>/reward/', views.reward_user, name="resource_reward_user"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)