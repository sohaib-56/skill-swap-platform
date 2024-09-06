from django.urls import path
from .views import *

urlpatterns = [
    path("",login_view, name="login"),
    path('register', register, name="register"),
    path('Userdashboard', Userdashboard, name="Userdashboard"),
    path('Skills_offer', Skills_offer, name="Skills_offer"),
    path('validate', validate, name="validate"),
    path('Skills_need', Skills_need, name="Skills_need"),
    path('Set_password', Set_password, name="Set_password"),
    path('change_password', change_password, name="change_password"),
    path('skills_update', skills_update, name="skills_update"),
    path('profile',profile, name = 'profile'),
    path('verify_email',verify_email,name='verify_email'),
    path('home',home,name='home'),
    path('match_view',match_view,name='match_view'),
    path('settings',settings, name = 'settings'),
    path('logout',logout,name='logout'),
    path('like/<int:post_id>/',like_post, name='like_post'),
    path('comment/<int:post_id>/',comment,name='comment'),
    path('like_comment/<int:comment_id>/', like_comment, name='like_comment'),
    path('profile/<int:user_id>/', profile_view, name='profile'),
    path('match_suggestions',match_suggestions,name='match_suggestions'),
    

]
