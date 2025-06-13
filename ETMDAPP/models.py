from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def clean(self):
        super().clean()
        if not self.email:
            raise ValidationError(_('Email cannot be empty'))
        if not self.password:
            raise ValidationError(_('Password cannot be empty'))

    def __str__(self):
        return self.email


class Employee(models.Model):
    account = models.OneToOneField('EmployeeSignUp', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    destination = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    email = models.EmailField(unique=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(
        upload_to='employee_pictures/', blank=True, null=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100,unique=True)
    code = models.CharField(max_length=20, unique=True)
    head = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
    ]
    CATEGORY_CHOICES = [
        ('light', 'Nhẹ'),
        ('medium', 'Vừa'),
        ('heavy', 'Nặng'),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    assigned_to = models.ManyToManyField(Employee)
    deadline_date = models.DateField()
    deadline_time = models.TimeField()
    email = models.EmailField()
    created_at = models.DateTimeField(default=timezone.now)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='medium')
    def get_assigned_emails(self):
        return [employee.email for employee in self.assigned_to.all()]
    def __str__(self):
        return self.title

class FinishedTask(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    assigned_to = models.ManyToManyField(Employee)
    deadline_date = models.DateField()
    deadline_time = models.TimeField()
    email = models.EmailField()
    finished = models.BooleanField(default=False)
    def __str__(self):
        return self.title

class EmployeeSignUp(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    def clean(self):
        super().clean()
        if not self.email:
            raise ValidationError(_('Email cannot be empty'))
        if not self.password:
            raise ValidationError(_('Password cannot be empty'))
    def __str__(self):
        return self.name

class TaskAssignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    progress= models.PositiveIntegerField(
        default=0,
        help_text="Nhập phần trăm hoàn thành từ 0 đến 100"
    )
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('employee', 'task')
    def clean(self):
        if self.progress < 0 or self.progress > 100:
            raise ValidationError(_('Phần trăm hoàn thành phải nằm trong khoảng 0 đến 100'))
    def __str__(self):
        return f"{self.employee.name} - {self.task.title}: {self.progress}%"

class Checkin(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_note = models.CharField(max_length=255, blank=True, null=True)  # Mô tả địa điểm (nếu có)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"