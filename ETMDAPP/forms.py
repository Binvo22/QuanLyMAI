from django import forms
from .models import Task, Contact, Department, Employee, TaskAssignment
from django_select2.forms import Select2MultipleWidget
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['account']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
        labels = {
            'name': 'Tên phòng ban',
            'code': 'Mã phòng ban',
            'head': 'Trưởng phòng',
            'location': 'Vị trí',
            'description': 'Mô tả',
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'mobile', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Nhập tên'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nhập họ'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Nhập email'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Nhập số điện thoại'}),
            'message': forms.Textarea(attrs={'placeholder': 'Nhập nội dung tin nhắn'}),
        }

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': 'Chọn nhân viên...'}),
        label='Giao cho'
    )
    emails = forms.CharField(
        required=False,
        label='Emails',
        widget=forms.TextInput(attrs={'placeholder': 'Nhập các email, phân tách bởi dấu phẩy'}),
        help_text='Nhập nhiều email, cách nhau bằng dấu phẩy.'
    )
    title = forms.CharField(
        label='Tiêu đề',
        widget=forms.TextInput(attrs={'placeholder': 'Nhập tiêu đề công việc'})
    )
    description = forms.CharField(
        label='Mô tả',
        widget=forms.Textarea(attrs={'placeholder': 'Nhập mô tả công việc'})
    )
    deadline_date = forms.DateField(
        label='Ngày hết hạn',
        widget=forms.DateInput(attrs={'placeholder': 'Chọn ngày hết hạn', 'class': 'datepicker'})
    )
    deadline_time = forms.TimeField(
        label='Giờ hết hạn',
        widget=forms.TimeInput(attrs={'placeholder': 'Chọn giờ hết hạn', 'class': 'form-control timepicker'})
    )
    priority = forms.ChoiceField(
        label='Độ ưu tiên',
        choices=Task.PRIORITY_CHOICES
    )
    category = forms.ChoiceField(
        label='Loại công việc',
        choices=Task.CATEGORY_CHOICES
    )
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'deadline_date',
                  'deadline_time', 'emails', 'priority', 'category']
        labels = {
            'title': 'Tiêu đề',
            'description': 'Mô tả',
            'assigned_to': 'Giao cho',
            'deadline_date': 'Ngày hết hạn',
            'deadline_time': 'Giờ hết hạn',
            'emails': 'Emails',
            'priority': 'Độ ưu tiên',
            'category': 'Loại công việc',
        }
    def clean_emails(self):
        emails = self.cleaned_data.get('emails', '')
        email_list = [email.strip() for email in emails.split(',') if email.strip()]
        validator = EmailValidator()
        for email in email_list:
            try:
                validator(email)
            except ValidationError:
                raise forms.ValidationError(f"Email '{email}' không hợp lệ.")
        return ', '.join(email_list)

class EmployeeSignUpForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = TaskAssignment
        fields = ['progress']
        widgets = {
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
