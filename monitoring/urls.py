from .views import get_caffeine_data, add_caffeine_entry, register_user, login_user
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import get_users, add_user, edit_user, delete_user, get_user, update_user, analytics_data, analytics_dashboard,update_user_profile,get_user_profile, CaffeineEntryDetail, HealthTipViewSet, UserListView, get_caffeine_products
from django.conf import settings
from django.conf.urls.static import static
from . import views

router = DefaultRouter()
router.register(r'health-tips', HealthTipViewSet)

urlpatterns = [
    # Caffeine Data
    path('caffeine/', get_caffeine_data, name='get_caffeine_data'),
    path('caffeine/add/', add_caffeine_entry, name='add_caffeine_entry'),

    # User Registration and Login
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),

    # User CRUD
    path("update-user/<int:user_id>/", update_user, name="update_user"),
    path('get_users/', get_users, name='get_users'),
    path('add_user/', add_user, name='add_user'),
    path('edit_user/<int:user_id>/', edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
    path('get_user/<int:user_id>/', get_user, name='get_user'),
    path("updateprofile/<int:user_id>/", update_user_profile, name="update_user_profile"),
    path('userprofile/<int:user_id>/', get_user_profile, name='get_user_profile'),
    path('users/', UserListView.as_view(), name='user-list'), 
    
    
    
    #caffeine_products:
    #user
    path('caffeine-products/', views.get_caffeine_products, name='get_caffeine_products'),
    #admin
    path('caffeine_products/', get_caffeine_products, name='get_caffeine_products'),
    path('caffeine_products/update_status/<int:pk>/', views.update_product_status, name='update_product_status'),
    path('caffeine_products/<int:pk>/', views.update_caffeine_product, name='update_caffeine_product'),
    path('created-drinks/', views.get_created_drinks),
    path('create-drink/', views.create_custom_drink, name='create_custom_drink'),
    path('product-count/', views.product_count, name='product_count'),
    path('caffeine_products/', views.add_caffeine_product, name='add_caffeine_product'),




    # Analytics
    path('admin/analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('analytics/', analytics_data, name='analytics_data'),

    # Caffeine Entry Detail
    path('caffeine_entries/<int:entry_id>/', CaffeineEntryDetail.as_view(), name='caffeine_entry_detail'),

    # Health Tips API (Router)
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
