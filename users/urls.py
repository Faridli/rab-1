from django.urls import path 
from users.views import ( 
    sign_up,sign_in,sign_out,activate_user, 
    admin_dashboard,assign_role,Create_Group,Group_list, 

    
)

urlpatterns = [
    path('sign-up/',sign_up,name='sign-up'),
    path('sign-in/',sign_in,name='sign-in'),
    path('logout/',sign_out, name='logout'),
    path('activate/<int:user_id>/<str:token>/',activate_user, name='activate'), 
    path('admin/dashboard/',admin_dashboard,name='admin-dashboard'), 
    path('admin/<int:user_id>/assign_role/',assign_role, name = 'assign-role'),
    path('admin/create-group/',Create_Group, name='create-group'),
    path('admin/group-list/',Group_list, name='group-list'), 


    
]
