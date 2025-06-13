from rest_framework import serializers
from .models import Admin, Employee, Department, Contact, Task, FinishedTask, EmployeeSignUp, TaskAssignment, Checkin

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['email', 'password']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'code', 'head', 'location', 'description']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'mobile', 'message', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeSerializer()
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'deadline_date', 'deadline_time', 'email', 
                  'created_at', 'priority', 'category']

class FinishedTaskSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeSerializer()
    class Meta:
        model = FinishedTask
        fields = ['title', 'description', 'assigned_to', 'deadline_date', 'deadline_time', 'email', 'finished']

class EmployeeSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSignUp
        fields = ['name', 'email', 'password']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignment
        fields = '__all__'
        
class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkin
        fields = '__all__'