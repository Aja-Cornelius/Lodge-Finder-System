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
    path('lodge/<int:lodge_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('lodge/<int:lodge_id>/review/', views.add_review, name='add_review'),
    path('roommates/', views.roommate_list, name='roommate_list'),
    path('roommates/add/', views.add_roommate_post, name='add_roommate_post'),
    path('alerts/subscribe/', views.subscribe_alerts, name='subscribe_alerts'),
    path('community/', views.community_feed, name='community_feed'),
    path('community/post/create/', views.create_post, name='create_post'),
    path('community/post/<int:post_id>/like/', views.toggle_post_like, name='toggle_post_like'),
    path('community/post/<int:post_id>/comment/', views.add_post_comment, name='add_post_comment'),
    path('owner/my-lodges/', views.my_lodges, name='my_lodges'),
    path('owner/profile/', views.owner_profile, name='owner_profile'),
    path('owner/inquiries/', views.inquiries, name='inquiries'),
]