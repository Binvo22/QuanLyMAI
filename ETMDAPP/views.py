from django.core.exceptions import ValidationError
from .forms import TaskAssignmentForm
from .models import EmployeeSignUp
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from .utils import (
    generate_task_distribution_plot,
    generate_remaining_tasks_plot,
    generate_task_deadlines_table,
    generate_completed_tasks_over_time_plot,
    generate_employee_performance_plot,
    generate_task_description_wordcloud,
    generate_completion_rate_by_employee_plot,
    generate_task_distribution_by_category_plot,
    generate_task_distribution_by_priority_plot,
    generate_task_duration_distribution_plot, 
)
from .models import FinishedTask
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect, render
from .models import Task
from .models import EmployeeSignUp 
from .models import Task, FinishedTask
from .forms import TaskForm
from .models import Employee, Task
from .forms import ContactForm
from django.shortcuts import render, get_object_or_404, redirect
from .forms import TaskAssignmentForm
from .forms import DepartmentForm
from .models import Department
from .models import TaskAssignment
from .forms import EmployeeForm
from .forms import EmployeeForm 
from .models import Employee
from django.shortcuts import render, redirect
from .models import Admin
from django.shortcuts import render
from django.db.models import Count
from .models import Checkin
from django.views.decorators.csrf import csrf_exempt

def HOME(request):
    return render(request,"home.html")

def REGIEMP(request):
    departments = Department.objects.all()
    if request.method == "POST":
        try:
            emp = Employee(
                name=request.POST.get("firstname"),
                department=request.POST.get("department"),
                employee_id=request.POST.get("id"),
                address=request.POST.get("address"),
                contact_number=request.POST.get("number"),
                destination=request.POST.get("dest"),
                date_of_birth=request.POST.get("dob"),
                date_of_joining=request.POST.get("doj"),
                email=request.POST.get("email"),
                designation=request.POST.get("des"),
                description=request.POST.get("desc"),
            )
            if request.FILES.get("pictureInput"):
                emp.picture = request.FILES["pictureInput"]

            emp.save()
            return render(request, "regiemp.html", {
                "success_message": "Thêm nhân viên thành công!",
                "departments": departments
            })
        except Exception as e:
            print("Lỗi khi thêm nhân viên:", e)
            return render(request, "regiemp.html", {
                "error_message": "Có lỗi xảy ra!",
                "departments": departments
            })
    return render(request, "regiemp.html", {"departments": departments})

def employee_signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")
        department = request.POST.get("department")
        employee_id = request.POST.get("employee_id")
        address = request.POST.get("address")
        contact_number = request.POST.get("contact_number")
        destination = request.POST.get("destination")
        date_of_birth = request.POST.get("date_of_birth")
        date_of_joining = request.POST.get("date_of_joining")
        designation = request.POST.get("designation")
        description = request.POST.get("description")
        required_fields = [email, password, name, department, employee_id, address, contact_number, date_of_birth, date_of_joining]
        if any(not field for field in required_fields):
            return render(request, "signup.html", {'error_message': "Vui lòng nhập đầy đủ các trường bắt buộc."})
        if EmployeeSignUp.objects.filter(email=email).exists():
            return render(request, "signup.html", {'error_message': "Email đã được đăng ký."})
        hashed_password = make_password(password)
        new_user = EmployeeSignUp.objects.create(
            name=name,
            email=email,
            password=hashed_password
        )
        Employee.objects.create(
            account=new_user,
            name=name,
            email=email,
            department=department,
            employee_id=employee_id,
            address=address,
            contact_number=contact_number,
            destination=destination,
            date_of_birth=date_of_birth,
            date_of_joining=date_of_joining,
            designation=designation,
            description=description or ""
        )
        return render(request, "login.html", {'success_message': "Đăng ký thành công! Vui lòng đăng nhập."})
    return render(request, "signup.html")

def employee_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = EmployeeSignUp.objects.get(email=email)
        except EmployeeSignUp.DoesNotExist:
            return render(request, "login.html", {'error_message': "Email hoặc mật khẩu không đúng."})
        if check_password(password, user.password):
            request.session['employee_id'] = user.id
            request.session['employee_email'] = user.email
            request.session['employee_name'] = user.name
            return redirect('empdashboard') 
        else:
            return render(request, "login.html", {'error_message': "Email hoặc mật khẩu không đúng."})
    return render(request, "login.html")

def employee_logout(request):
    try:
        del request.session['employee_id']
        del request.session['employee_email']
        del request.session['employee_name']
    except KeyError:
        pass
    return redirect('home')

def employee_list(request):
    try:
        query = request.GET.get('q')
        if query:
            employees = Employee.objects.filter(email__icontains=query)
        else:
            employees = Employee.objects.all()
        return render(request, 'emplist.html', {'employees': employees, 'query': query})
    except ValidationError as ve:
        error_message = "Validation Error: {}".format(ve)
        return render(request, "error.html", {'error_message': error_message})
    except Exception as e:
        error_message = "An error occurred while processing your request."
        return render(request, "error.html", {'error_message': error_message})

def search_employee(request):
    query_email = request.GET.get('email')
    query_emp_id = request.GET.get('emp_id')
    employees = Employee.objects.all()
    if query_email:
        employees = employees.filter(email__icontains=query_email)
    if query_emp_id:
        employees = employees.filter(employee_id__icontains=query_emp_id)
    return render(request, 'emplist.html', {'employees': employees, 'query_email': query_email, 'query_emp_id': query_emp_id})

def delete_employee(request, pk):
    employee = Employee.objects.get(pk=pk)
    employee.delete()
    return redirect('employee_list')

def edit_employee(request, pk):
    employee = Employee.objects.get(pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('admindashboard')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'editemp.html', {'form': form})

def ABOUT(request):
    return render(request, "about.html")

def EMPDASHBOARD(request):
    try:
        email = request.session.get("employee_email")
        if not email:
            return render(request, "error.html", {
                'error_message': "Session data missing. Please log in again."
            })
        employee = Employee.objects.get(email=email)
        total_tasks = Task.objects.filter(assigned_to=employee).count()
        just_started_tasks = TaskAssignment.objects.filter(
            employee=employee,
            progress__gte=1,
            progress__lte=10
        ).count()
        in_progress_tasks = TaskAssignment.objects.filter(
            employee=employee,
            progress__gt=10,
            progress__lt=100
        ).count()
        completed_tasks = FinishedTask.objects.filter(
            assigned_to=employee,
            finished=True
        ).count()
        return render(request, "empdashboard.html", {
            'total_tasks': total_tasks,
            'just_started_tasks': just_started_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
        })
    except Employee.DoesNotExist:
        return render(request, "error.html", {
            'error_message': "Employee not found."
        })
    except Exception as e:
        return render(request, "error.html", {
            'error_message': f"An unexpected error occurred: {str(e)}"
        })
 
def ADMINLOGIN(request):
    if request.method == "POST":
        admin_email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            admin = Admin.objects.get(email=admin_email)
        except Admin.DoesNotExist:
            return render(request, "adminlogin.html", {"error_message": "Admin not found"})
        if check_password(password, admin.password):
            request.session['admin_email'] = admin.email
            total_employees = Employee.objects.count()
            return redirect("admindashboard")
        else:
            return render(request, "adminlogin.html", {"error_message": "Invalid credentials"})
    admin_email = request.session.get('admin_email', None)
    return render(request, "adminlogin.html", {"admin_email": admin_email})

def AdminDashboard(request):
    try:
        admin_email = request.session.get('admin_email', None)
        if admin_email is None:
            return redirect('adminlogin')
        total_employees = Employee.objects.count()
        total_departments = Department.objects.count()
        finished_tasks_count = FinishedTask.objects.count()
        assigned_tasks_count = Task.objects.count()
        return render(request, "admindashboard.html", {
            'total_employees': total_employees,
            'total_departments': total_departments,
            'finished_tasks_count': finished_tasks_count,
            'assigned_tasks_count': assigned_tasks_count,
            'admin_email': admin_email,
        })
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return render(request, "error.html", {'error_message': error_message})

def REGIDMENT(request):
    try:
        admin_email = request.session.get('admin_email', None)
        if admin_email is None:
            return redirect('adminlogin')
        if request.method == 'POST':
            form = DepartmentForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admindashboard')
        else:
            form = DepartmentForm()
        return render(request, 'regidment.html', {'form': form, 'admin_email': admin_email})
    except Exception as e:
        error_message = "An error occurred while processing department registration."
        return render(request, "error.html", {'error_message': error_message})

def department_list(request):
    departments = Department.objects.all()
    total_departments = departments.count()
    context = {
        'departments': departments,
        'total_departments': total_departments
    }
    return render(request, 'dlist.html', context)

def edit_department(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'edit_department.html', {'form': form})

def delete_department(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(request, 'admindashboard', {'department': department})

def search_department(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        departments = Department.objects.filter(name__icontains=name)
        return render(request, 'dlist.html', {'departments': departments})
    else:
        return render(request, 'department_search_results.html')

def CONTACT(request):
    try:
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('home')
        else:
            form = ContactForm()
        return render(request, 'contact.html', {'form': form})
    except Exception as e:
        error_message = "An error occurred while processing the contact form."
        return render(request, "error.html", {'error_message': error_message})

def assign_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            assigned_employees = form.cleaned_data['assigned_to']
            task.assigned_to.set(assigned_employees)
            task.save()
            for employee in assigned_employees:
                TaskAssignment.objects.create(
                    task=task,
                    employee=employee,
                    progress=0
                )
            return redirect('taskemployeelist')
    else:
        form = TaskForm()
    return render(request, 'assigntask.html', {'form': form})

def task_des(request):
    employees_with_tasks = Employee.objects.filter(
        task__isnull=False).distinct().annotate(task_count=Count('task'))
    return render(request, 'taskdes.html', {'employees': employees_with_tasks})

def assigned_tasks(request):
    employee_data = []
    for emp in Employee.objects.all():
        assignments = TaskAssignment.objects.filter(employee=emp).select_related('task')
        task_list = []
        for assign in assignments:
            task_list.append({
                'task': assign.task,
                'progress': assign.progress,
                'notes': assign.notes,
                'updated_at': assign.updated_at,
                'start_date': assign.start_date
            })
        employee_data.append({
            'employee': emp,
            'tasks': task_list
        })
    return render(request, 'assigntasks.html', {'employee_data': employee_data})

def TaskReport(request):
    generate_task_distribution_plot()
    generate_remaining_tasks_plot()
    generate_task_deadlines_table()
    generate_completed_tasks_over_time_plot()
    generate_employee_performance_plot()
    generate_task_description_wordcloud()
    generate_completion_rate_by_employee_plot()
    generate_task_distribution_by_category_plot()
    generate_task_distribution_by_priority_plot()
    generate_task_duration_distribution_plot()
    deadlines_data = generate_task_deadlines_table()
    context = {
        'deadlines_data': deadlines_data
    }
    return render(request, 'taskreport.html', context)

def mark_task_finished(request, task_id, email):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_id, assigned_to__email=email)
        finished_task = FinishedTask.objects.create(
            title=task.title,
            description=task.description,
            deadline_date=task.deadline_date,
            deadline_time=task.deadline_time,
            email=task.email,
            finished=True
        )
        finished_task.assigned_to.set(task.assigned_to.all())
        finished_task.save()
        task.delete()
        return redirect('admindashboard')
    else:
        pass

def DEV(request):
    return render(request, "developers.html")

def task_end_dates(request):
    tasks = Task.objects.all()
    return render(request, 'taskenddate.html', {'tasks': tasks})


def TaskDashboard(request):
    email = request.session.get("EmployeeEmail")
    assigned_tasks = Task.objects.filter(email=email)
    total_tasks = assigned_tasks.count()
    completed_tasks = FinishedTask.objects.filter(
        email=email, finished=True).count()
    completion_rate = 0
    if total_tasks > 0:
        if total_tasks == completed_tasks:
            completion_rate = 50
        else:
            completion_rate = round((completed_tasks / total_tasks) * 100,2)
    performance_rate = completion_rate
    NoOfTasks=total_tasks + completed_tasks
    context = {
        'completion_rate': completion_rate,
        'total_tasks': NoOfTasks,
        'performance_rate': performance_rate,
    }
    return render(request, "emptaskdashboard.html", context)

def EMPTaskEndDate(request):
    try:
        email = request.session.get("EmployeeEmail", None)
        if email:
            tasks = Task.objects.filter(email=email)
        else:
            tasks = []
        return render(request, 'emptaskenddate.html', {'tasks': tasks})
    except Exception as e:
        error_message = "An error occurred while loading the employee tasks."
        return render(request, "error.html", {'error_message': error_message})

def EmployeeTask(request):
    try:
        email = request.session.get("EmployeeEmail", None)
        username = request.session.get("EmployeeUsername", None)
        if email:
            tasks = Task.objects.filter(emails__contains=email)
        else:
            tasks = []
        return render(request, 'employeetask.html', {'email': email, 'tasks': tasks, 'username': username})
    except Exception as e:
        print("=== LỖI DASHBOARD ===")  
        print(e)
        error_message = f"Lỗi khi load trang dashboard: {str(e)}"
        return render(request, "error.html", {'error_message': error_message})

def finished_tasks_view(request):
    try:
        finished_tasks = FinishedTask.objects.filter(finished=True)
        return render(request, 'finished_tasks.html', {'finished_tasks': finished_tasks})
    except Exception as e:
        print("=== LỖI HIỂN THỊ TASK HOÀN THÀNH ===")
        print(e)
        return render(request, 'error.html', {'error_message': str(e)})

def employee_dashboard(request):
    email = request.session.get("employee_email")
    if email:
        try:
            employee = Employee.objects.get(email=email)
            assigned_tasks = Task.objects.filter(assigned_to=employee)
            total_tasks = assigned_tasks.count()
            completed_tasks_qs = FinishedTask.objects.filter(assigned_to=employee, finished=True)
            completed_tasks = completed_tasks_qs.count()
            in_progress_tasks = total_tasks - completed_tasks
            return render(request, 'employee_dashboard.html', {
                'tasks': assigned_tasks,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks
            })
        except Employee.DoesNotExist:
            return HttpResponse("Không tìm thấy nhân viên.")
    return redirect('employeesignuplogin')

from django.shortcuts import get_object_or_404, redirect, render

def update_Assignment(request, task_id):
    email = request.session.get("employee_email")
    if not email:
        return redirect('employeesignuplogin')
    task = get_object_or_404(Task, id=task_id)
    employee = get_object_or_404(Employee, email=email)
    assignment, created = TaskAssignment.objects.get_or_create(task=task, employee=employee)
    if request.method == 'POST':
        form = TaskAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            if assignment.progress == 100:
                finished_task = FinishedTask.objects.create(
                    title=task.title,
                    description=task.description,
                    deadline_date=task.deadline_date,
                    deadline_time=task.deadline_time,
                    email=task.email,
                    finished=True
                )
                finished_task.assigned_to.set(task.assigned_to.all())
                task.delete()
                return redirect('employee_dashboard')
            return redirect('update_assignment', task_id=task.id)
    else:
        form = TaskAssignmentForm(instance=assignment)
    return render(request, 'update_assignment.html', {
        'task': task,
        'form': form,
        'assignment': assignment,
    })

from django.shortcuts import render

def timesheet_view(request):
    import requests
    import pandas as pd
    from io import BytesIO
    import datetime
    url = 'https://docs.google.com/spreadsheets/d/1hRBixIYOX5_oaXOawR16OFmsI1UBIYNqgs30GoPJja0/export?format=xlsx'
    response = requests.get(url)
    if response.status_code != 200:
        return render(request, 'chamcong.html', {'error': 'Không tải được file Excel từ Google Sheets'})
    file_bytes = BytesIO(response.content)
    try:
        xls = pd.ExcelFile(file_bytes)
        sheet_names = xls.sheet_names
        selected_sheet = request.GET.get('sheet', sheet_names[0])
        selected_sheet = selected_sheet.strip()
        match_sheets = [s for s in sheet_names if s.strip().lower() == selected_sheet.lower()]
        if match_sheets:
            selected_sheet = match_sheets[0]
        else:
            selected_sheet = sheet_names[0]
        df = pd.read_excel(xls, sheet_name=selected_sheet, header=2)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.dropna(axis=1, how='all', inplace=True)
        if df.columns[0] != 'STT':
            df.rename(columns={df.columns[0]: 'STT'}, inplace=True)
        df = df.fillna('')
        table_html = df.to_html(classes='table table-bordered table-striped', index=False)
        report_date = datetime.datetime.now().strftime('%d/%m/%Y')
        context = {
            'sheet_names': sheet_names,
            'selected_sheet': selected_sheet,
            'table': table_html,
            'report_date': report_date,
        }
        return render(request, 'chamcong.html', context)
    except Exception as e:
        return render(request, 'chamcong.html', {'error': f'Lỗi khi đọc file Excel: {str(e)}'})

def employee_profile(request):
    employee_email = request.session.get('employee_email')
    if not employee_email:
        return redirect('employeesignuplogin')
    try:
        employee = Employee.objects.get(email=employee_email)
    except Employee.DoesNotExist:
        employee = None
    return render(request, 'employee_profile.html', {'employee': employee})

def incomplete_tasks_view(request):
    employee_email = request.session.get('employee_email')
    if not employee_email:
        return redirect('employeesignuplogin')
    try:
        employee = Employee.objects.get(email=employee_email)
    except Employee.DoesNotExist:
        return redirect('employeesignuplogin')
    incomplete_tasks = TaskAssignment.objects.filter(employee=employee, progress__lt=100)
    return render(request, 'incomplete_tasks.html', {'incomplete_tasks': incomplete_tasks})

def completed_tasks_view(request):
    employee_email = request.session.get('employee_email')
    if not employee_email:
        return redirect('employeesignuplogin')
    try:
        employee = Employee.objects.get(email=employee_email)
    except Employee.DoesNotExist:
        return redirect('employeesignuplogin')
    finished_tasks = FinishedTask.objects.filter(assigned_to=employee, finished=True)
    return render(request, 'completed_tasks.html', {'finished_tasks': finished_tasks})


import requests
from decimal import Decimal, InvalidOperation
from django.contrib import messages
def get_address_from_latlng(lat, lng):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&addressdetails=1"
    headers = {'User-Agent': 'YourAppName/1.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # In debug để xem chi tiết
        print(data.get('address'))
        return data.get('display_name')
    return None

def check_in_view(request):
    employee_email = request.session.get('employee_email')
    if not employee_email:
        return redirect('employeesignuplogin')
    try:
        employee = Employee.objects.get(email=employee_email)
    except Employee.DoesNotExist:
        messages.error(request, "Tài khoản nhân viên không hợp lệ.")
        return redirect('employeesignuplogin')
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        try:
            latitude_dec = Decimal(latitude) if latitude else None
            longitude_dec = Decimal(longitude) if longitude else None
        except InvalidOperation:
            latitude_dec = None
            longitude_dec = None
        location_note = None
        if latitude_dec and longitude_dec:
            location_note = get_address_from_latlng(latitude_dec, longitude_dec)
        Checkin.objects.create(
            employee=employee,
            latitude=latitude_dec,
            longitude=longitude_dec,
            location_note=location_note
        )
        messages.success(request, "Bạn đã chấm công thành công!")
        return redirect('checkin')
    return render(request, 'checkin.html', {'employee': employee})


def checkin_list(request):
    checkins = Checkin.objects.select_related('employee').order_by('-check_in_time')
    return render(request, 'checkin_list.html', {'checkins': checkins})