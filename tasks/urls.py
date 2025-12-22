from django.urls import path
from tasks.views import ( 
    Dashboard,
    Bn_Hq_Br,  
    Address,
    Force_bio,
    Force_detail,
    Company_members_of_bnhq,
    duty_create_group,
    duty_edit,
    duty_list_by_company,
    duty_delete,
    miroom_visit_create, 
    miroom_daily_report,
    get_member, 
    ro_create,
    ro_list,
    member_get,  


    # -----------------------------
    # CPC-1........................
    # ----------------------------- 
    CPC_One_Br,

)

# app_name = "tasks"  
urlpatterns = [
    # -----------------------------
    # Manager & User Dashboards
    # -----------------------------
    path('manager-dashboard/', Dashboard, name='manager-dashboard'),
    path('br/', Bn_Hq_Br, name='br'),
    path('address/<int:member_id>', Address, name='address'),
    # path('user-dashboard/', user_dashboard, name='user-dashboard'),

    # -----------------------------
    # Force Bio  and Bn-HQ
    # -----------------------------
    path('bio/', Force_bio, name='force-bio'),
    path('force/',Force_detail, name='force-detail'),
    path("company-member/",Company_members_of_bnhq, name="company-member"),


    path('duties/add/<str:company>/', duty_create_group, name='duty_create'),
    path('duties/<int:pk>/edit/', duty_edit, name='duty_edit'),
    path('duties/<str:company>/', duty_list_by_company, name='duty_list'),
    path('duties/<int:pk>/delete/', duty_delete, name='duty_delete'),

    path('mi/',miroom_daily_report, name='miroom_visit_list'), 
    path('mi/create/', miroom_visit_create, name='miroom_visit_create'), 
    path("get-member/<int:per_no>/", get_member, name="get-member"),

    # -----------------------------
    # ro
    # -----------------------------
    path('ro/create/',ro_create, name='ro-create'),
    path('ro/list/',ro_list, name='ro-list'),
    path('member-get/<str:query>/',member_get, name='member-get'),

    
    # -----------------------------
    # Member Posting View
    # -----------------------------
    # path('member-posting/', member_posting_view, name='member-posting'), 

    # -----------------------------
    # CPC-1........................
    # ----------------------------- 
   
    path('cpcbr/<str:company>/', CPC_One_Br, name='cpc'),

]




















# python manage.py shell 
# from django.template.loader import get_template
# get_template('bnhq/list.html')