from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin
from .models import ForceMember, Duty, MiRoomVisit, Ro
from .forms import (
    ForceModelForm,
    CompanySelectForm,
    PresentModelForm,
    PermanentModelForm,
    DutyForm,
    MiRoomVisitForm,
    RoForm,
)

# ---------------------------------------------------
# Generic Group & Company Checks
# ---------------------------------------------------
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

def company_required(param='company'):
    """Decorator to check if user belongs to the company"""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            company = kwargs.get(param)
            if not in_group(request.user, company):
                return HttpResponseForbidden("No permission for this company")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# ---------------------------------------------------
# Dashboard Views
# ---------------------------------------------------
# @user_passes_test(lambda u: in_group(u, 'Co'), login_url='no-permission')
@login_required 
def Dashboard(request): 
    return render(request, 'dashboard/dashboard.html')

@login_required 
def User_Dashboard(request): 
    return render(request, 'dashboard/user_dashboard.html')


@user_passes_test(lambda u: in_group(u, 'Bn HQ'), login_url='no-permission')
def Bn_Hq_Br(request):
    return render(request, 'bnhq/list.html')


# ---------------------------------------------------
# Force Bio Data Entry
# ---------------------------------------------------
@login_required 
@permission_required("tasks.add_forcemember", login_url='no-permission')
def Force_bio(request):
    if request.method == 'POST':
        force_form = ForceModelForm(request.POST)
        present_form = PresentModelForm(request.POST)
        permanent_form = PermanentModelForm(request.POST)

        if force_form.is_valid() and present_form.is_valid() and permanent_form.is_valid():
            try:
                with transaction.atomic():
                    force = force_form.save()

                    present = present_form.save(commit=False)
                    present.member = force
                    present.save()

                    permanent = permanent_form.save(commit=False)
                    permanent.member = force
                    permanent.save()

                    messages.success(request, "Saved successfully!")
                    return redirect('force-bio')
            except Exception as e:
                messages.error(request, f"Error saving data: {str(e)}")
        else:
            messages.error(request, "Please fix the errors!")
            print("ForceForm errors:", force_form.errors)
            print("PresentForm errors:", present_form.errors)
            print("PermanentForm errors:", permanent_form.errors)
    else:
        force_form = ForceModelForm()
        present_form = PresentModelForm()
        permanent_form = PermanentModelForm()

    return render(request, 'dashboard/bio.html', {
        'force_form': force_form,
        'present_form': present_form,
        'permanent_form': permanent_form,
    })


# ---------------------------------------------------
# Force Detail / Company Select
# ---------------------------------------------------
@login_required 
@permission_required("tasks.view_forcemember", login_url='no-permission')
def Force_detail(request):
    members = ForceMember.objects.exclude(company__iexact="RAB-1 Out") \
        .select_related('present_address', 'permanent_address')

    out_members = ForceMember.objects.filter(company__iexact="RAB-1 Out") \
        .select_related('present_address', 'permanent_address') \
        .order_by('-out_date')

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        member_id = request.POST.get("member_id")
        member = get_object_or_404(ForceMember, id=member_id)
        form = CompanySelectForm(request.POST, instance=member)
        if form.is_valid():
            company = form.cleaned_data["company"].strip()
            member.company = company
            member.out_date = timezone.now().date() if company.lower() == "rab-1 out" and not member.out_date else None
            member.save()
            return JsonResponse({
                "success": True,
                "member_id": member.id,
                "company_name": member.get_company_display(),
                "is_out": company.lower() == "rab-1 out",
                "out_date": member.out_date.strftime("%d-%m-%Y") if member.out_date else ""
            })
        return JsonResponse({"success": False})

    forms_dict = {m.id: CompanySelectForm(instance=m) for m in members}
    return render(request, "bnhq/force_detail.html", {
        "members": members,
        "out_members": out_members,
        "forms_dict": forms_dict
    })


# ---------------------------------------------------
# Company Wise Members
# ---------------------------------------------------
@user_passes_test(lambda u: in_group(u, 'Bn HQ'), login_url='no-permission')
def Company_members_of_bnhq(request):
    members = ForceMember.objects.filter(company='Bn HQ').order_by('rank')
    force_state = members.values('force').annotate(total=Count('id'))
    rank_state = members.values('rank').annotate(total=Count('id'))
    return render(request, 'bnhq/company_members.html', {
        'members': members,
        'company': 'Bn HQ',
        'force_state': force_state,
        'rank_state': rank_state
    })


# ---------------------------------------------------
# Address View
# ---------------------------------------------------
@user_passes_test(lambda u: in_group(u, 'Co'), login_url='no-permission')
def Address(request, member_id):
    m = get_object_or_404(ForceMember.objects.select_related('present_address', 'permanent_address'), id=member_id)
    return render(request, "bnhq/address.html", {
        "m": m,
        "present_dict": vars(m.present_address),
        "permanent_dict": vars(m.permanent_address),
        "service_dict": {
            "Svc Join": m.svc_join,
            "RAB Join": m.rab_join,
            "Mother Unit": m.mother_unit,
            "NID": m.nid,
            "Birth Day": m.birth_day,
            "WF Phone": m.wf_phone,
        },
    })


# ---------------------------------------------------
# Duty Views
# ---------------------------------------------------
@login_required 
@permission_required("tasks.add_duty", login_url='no-permission')
@company_required('company')
def duty_create_group(request, company):
    if request.method == "POST":
        form = DutyForm(request.POST, request.FILES)
        if form.is_valid():
            raw_numbers = form.cleaned_data['member_numbers']
            numbers = [n.strip() for n in raw_numbers.replace(",", " ").split() if n.strip()]

            valid_members, invalid_numbers = [], []
            for num in numbers:
                member = ForceMember.objects.filter(no=num, company=company).first()
                if member:
                    valid_members.append(member)
                else:
                    invalid_numbers.append(num)

            if invalid_numbers:
                messages.error(request, f"Invalid Member Numbers: {', '.join(invalid_numbers)}")
                return render(request, 'bnhq/duty_create_group.html', {'form': form, 'company': company})

            with transaction.atomic():
                Duty.objects.bulk_create([
                    Duty(
                        member=member,
                        name=member.name,
                        rank=member.get_rank_display(),
                        phone=member.phone,
                        date=form.cleaned_data['date'],
                        start_time=form.cleaned_data['start_time'],
                        end_time=form.cleaned_data['end_time'],
                        destination=form.cleaned_data['destination'],
                    ) for member in valid_members
                ])
            messages.success(request, f"{company} group duty created successfully!")
            return redirect('duty_list', company=company)
    else:
        form = DutyForm()

    return render(request, 'bnhq/duty_create_group.html', {'form': form, 'company': company})


@login_required 
@permission_required("tasks.change_duty", login_url='no-permission')
def duty_edit(request, pk):
    duty = get_object_or_404(Duty, pk=pk)
    form = DutyForm(request.POST or None, instance=duty)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('duty_list')
    return render(request, 'bnhq/duty_form.html', {'form': form, 'edit': True})


@login_required 
# @permission_required("tasks.change_duty", login_url='no-permission')
# @company_required('company')
def duty_list_by_company(request, company):
    duties = Duty.objects.select_related('member').filter(member__company=company).order_by('destination', 'date')
    return render(request, 'bnhq/duty_list.html', {'duties': duties, 'company': company})


@login_required 
@permission_required("tasks.delete_duty", login_url='no-permission')
@user_passes_test(lambda u: in_group(u, 'Admin'), login_url='no-permission')
def duty_delete(request, pk):
    duty = get_object_or_404(Duty, pk=pk)
    if request.method == "POST":
        duty.delete()
        return redirect('duty_list')
    return render(request, 'bnhq/duty_delete.html', {'duty': duty})


# ---------------------------------------------------
# MI Room Views
# ---------------------------------------------------
# @login_required 
@permission_required("tasks.add_duty", login_url='no-permission')
def miroom_daily_report(request):
    visits = MiRoomVisit.objects.select_related("member").order_by("-date", "member__rank")
    grouped_data = {}
    for v in visits:
        date = v.date
        if date not in grouped_data:
            grouped_data[date] = {"count": 0, "items": []}
        grouped_data[date]["count"] += 1
        grouped_data[date]["items"].append(v)
    return render(request, 'mi/miroom.html', {"grouped_data": grouped_data})


@login_required 
# @permission_required("tasks.add_duty", login_url='no-permission')
# @user_passes_test(lambda u: in_group(u,'mi'), login_url='no-permission')
def miroom_visit_create(request):
    member = None
    if request.method == "POST":
        form = MiRoomVisitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "MI Room Visit saved successfully!")
            return redirect('miroom_visit_list')
        else:
            per_no = request.POST.get('per_number')
            if per_no:
                member = ForceMember.objects.filter(no=per_no).first()
    else:
        form = MiRoomVisitForm()
    return render(request, 'mi/miroom_create.html', {'form': form, 'member': member})


def get_member(request, per_no):
    try:
        member = ForceMember.objects.get(no=per_no)
        return JsonResponse({
            "success": True,
            "id": member.id,
            "name": member.name,
            "rank": member.get_rank_display()
        })
    except ForceMember.DoesNotExist:
        return JsonResponse({"success": False})


# ---------------------------------------------------
# RO Views
# ---------------------------------------------------
 
@permission_required("tasks.add_duty", login_url='no-permission')
@user_passes_test(lambda u: in_group(u, 'ro'), login_url='no-permission')
def ro_create(request):
    form = RoForm()
    if request.method == "POST":
        form = RoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ro-list')
        else:
            print(form.errors)
    return render(request, 'ro/ro_form.html', {'form': form, 'member': None})


@user_passes_test(lambda u: in_group(u, 'ro'), login_url='no-permission')
def ro_list(request):
    ro_entries = Ro.objects.select_related("member").all()
    return render(request, 'ro/ro_list.html', {'ro_entries': ro_entries})


def member_get(request, query):
    try:
        member = ForceMember.objects.filter(no=query).first() or ForceMember.objects.filter(nid=query).first()
        if member:
            return JsonResponse({"success": True, "rank": member.rank, "name": member.name})
        return JsonResponse({"success": False})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ---------------------------------------------------
# CPC Views
# ---------------------------------------------------
@login_required 
@permission_required("tasks.add_duty", login_url='no-permission')
@company_required('company')
def CPC_One_Br(request, company):
    return render(request, 'cpcone/list.html', {'company': company})


def is_manager(user):
    return user.groups.filter(name__iexact='manager').exists()

def is_employee(user):
    return user.groups.filter(name__iexact='employee').exists()



@login_required
def dashboard1(request):
    
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('user-dashboard')

    return redirect('no-permission')
