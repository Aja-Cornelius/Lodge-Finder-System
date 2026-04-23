from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('student/signup/', views.student_signup, name='student_signup'),
    path('owner/signup/', views.owner_signup, name='owner_signup'),
    path('student/login/', views.student_login, name='student_login'),
    path('owner/login/', views.owner_login, name='owner_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('owner/add-lodge/', views.add_lodge, name='add_lodge'),
    path('search/', views.search_results, name='search_results'),
    path('lodge/<int:lodge_id>/', views.lodge_detail, name='lodge_detail'),
    path('owner/my-lodges/', views.my_lodges, name='my_lodges'),
    path('owner/profile/', views.owner_profile, name='owner_profile'),
    path('owner/inquiries/', views.inquiries, name='inquiries'),
]