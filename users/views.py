from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages 
from users.forms import loginForm 
from django.contrib.auth.tokens import default_token_generator  
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Prefetch



def is_admin(user):
    return user.groups.filter(name__iexact='admin').exists() 

def sign_up(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            user.set_password(form.cleaned_data.get('password'))
            user.is_active = False 
            user.save()
           
            messages.success(request, "Registration successful")
            return redirect('sign-in')
    else:
        form = CustomRegistrationForm()

    return render(request, 'registration/register.html', {"form": form})


def sign_in(request): 
    form = loginForm()
    if request.method == 'POST':
        form = loginForm(data=request.POST)
        if form.is_valid():        
        # username = request.POST.get('username')
        # password = request.POST.get('password')
        # user = authenticate(request, username=username, password=password)
            user = form.get_user() 
        # if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # form = loginForm()
            messages.error(request, "Invalid username or password")
    return render(request, 'registration/login.html', {'form':form})

@login_required
def sign_out(request):
    logout(request)
    return redirect('sign-in')

def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True 
            user.save() 
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid ID or token')
    except User.DoesNotExist:
        return HttpResponse('User not found') 
    


@login_required
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch(
            'groups',
            queryset=Group.objects.all(),
            to_attr='all_groups'   # ✔ সঠিক
        )
    )

    for user in users:
        if hasattr(user, 'all_groups') and user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No groups assigned'

    return render(request, 'admin/dashboard.html', {'users': users})


@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request, user_id):
    # ইউজার নেই হলে 404 দেখাবে
    user = get_object_or_404(User, id=user_id)
    
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()  # পুরোনো role remove
            user.groups.add(role)  # নতুন role add
            messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
            return redirect('admin-dashboard')
    
    # template-এ user info পাঠানো হচ্ছে
    context = {
        "form": form,
        "user": user
    }
    return render(request, 'admin/assign_role.html', context)



@user_passes_test(is_admin, login_url='no-permission')
def Create_Group(request): 
    form = CreateGroupForm() 
    if request.method == 'POST':
        form = CreateGroupForm(request.POST) 

        if form.is_valid():
            group = form.save() 
            messages.success(request, f"Group {group.name} has been created successfuly") 
            return redirect('create-group') 
    return render(request, 'admin/create_group.html', {"form":form})




@user_passes_test(is_admin, login_url='no-permission')
def Group_list(request):
    groups = Group.objects.prefetch_related('permissions').all() 
    return render(request, 'admin/group_list.html', {"groups":groups}) 



