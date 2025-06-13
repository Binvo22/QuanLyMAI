from django.contrib import admin
from .models import Task, FinishedTask, EmployeeSignUp, Department, Employee, Admin, Contact, TaskAssignment
from .forms import DepartmentForm

class AdminAdmin(admin.ModelAdmin):
    list_display = ['email']

admin.site.register(Admin, AdminAdmin)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'employee_id', 'address', 'contact_number',
                    'destination', 'date_of_birth', 'date_of_joining', 'email', 'designation', 'description')

@admin.register(EmployeeSignUp)
class EmployeeSignUpAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    form = DepartmentForm

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'mobile', 'message', 'created_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'assigned_to_list', 'deadline_date', 'deadline_time', 'email', 'priority', 'category']

    def assigned_to_list(self, obj):
        return ", ".join([employee.name for employee in obj.assigned_to.all()])
    assigned_to_list.short_description = 'Nhân viên'

@admin.register(FinishedTask)
class FinishedTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'assigned_to_list', 'deadline_date', 'deadline_time', 'email', 'finished']

    def assigned_to_list(self, obj):
        return ", ".join([employee.name for employee in obj.assigned_to.all()])
    assigned_to_list.short_description = 'Nhân viên'

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'task', 'progress', 'start_date', 'updated_at')
    list_filter = ('employee', 'task', 'progress')
    search_fields = ('employee__name', 'task__title')