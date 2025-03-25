from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.conf import settings 
# Create your models here.
 
class CustomUser(AbstractUser):
	full_name = models.CharField(max_length=255, blank=True, verbose_name='ФИО')
	phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
	company_name = models.CharField(max_length=255, blank=True, verbose_name='Компания')
	role = models.CharField(
		max_length=20,
		choices=[('freelancer', 'Фрилансер'), ('client', 'Клиент')],
		default='freelancer',
		verbose_name='Роль'
	)

	def __str__(self):
		return self.username

class Client(models.Model):
	fullname = models.CharField(max_length=200, null=False, blank=False)
	email = models.EmailField(max_length=100, unique=True)
	company = models.CharField(max_length=100, null=True, blank=True)
	phone_number = models.CharField(max_length=25, null=True, blank=True)
	address = models.CharField(max_length=50, null=True, blank=True)
	company_name = models.CharField(max_length=150, null=True, blank=True)
	company_type= models.CharField(max_length=50, null=True, blank=True)

class Project(models.Model):
	STATUS_CHOICES = [
		('new', 'Новый проект'),
		('in_progress', 'В процессе'),
		('completed', 'Выполнен'),
		('on_hold', 'Приостановлен'),
		('canceled', 'Отменен'),
		('waiting_for_feedback', 'Ожидает отзывов от клиентов')
	]

	name = models.CharField(max_length=100, null=False, blank=False)
	description = models.CharField(max_length=350, null=True, blank=True)
	deadline = models.DateTimeField(null=False, blank=False)
	status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new', null=False, blank=False)

class Task(models.Model):
    TASK_CHOICES = [
        ('not_started', 'Задача не начата'),
        ('in_progress', 'Задача в процессе'),
        ('completed', 'Задача завершена'),
        ('on_hold', 'Задача приостановлена'),
        ('blocked', 'Задача заблокирована'),
        ('canceled', 'Задача отменена'),
        ('waiting_for_review', 'Задача ожидает проверки')
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий')
    ]

    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=350, null=True, blank=True)
    status = models.CharField(max_length=45, choices=TASK_CHOICES, null=False, blank=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def is_overdue(self):
        """Проверка, просрочен ли дедлайн"""
        return self.deadline and self.deadline < now()

    def __str__(self):
        return f"{self.name} ({self.get_priority_display()})"

class Message(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='messages')
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

class Communication(models.Model):
	TAG_CHOICES = [
			('requirement', 'Требование'),
			('clarification', 'Уточнение'),
			('revision', 'Правки'),
			('deadline', 'Дедлайн'),
			('payment', 'Оплата'),
	]

	task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='communications')
	message = models.TextField(verbose_name="Текст заметки")
	tag = models.CharField(max_length=50, choices=TAG_CHOICES, blank=True, verbose_name="Тег")
	custom_tag = models.CharField(max_length=50, blank=True, verbose_name='Свой тег')
	file = models.FileField(upload_to='communications_files/', blank=True, null=True, verbose_name='Файл')
	created_at = models.DateTimeField(auto_now_add=True)

	def get_tag_display_name(self):
		return dict(self.TAG_CHOICES).get(self.tag, self.custom_tag)
	
	def __str__(self):
		return f"Заметка ({self.get_tag_display_name()}) - {self.message[:20]}"
		
class Invoice(models.Model):
	ORDER_CHOICES = [
		('pending', 'Оплата ожидает'),
		('paid', 'Оплата успешно проведена'),
		('failed', 'Неудачная попытка оплаты'),
		('refunded', ' Оплата была возвращена '),
		('in_progress', 'Оплата в процессе '),
		('cancelled', 'Оплата отменена'),
		('authorized', 'Оплата авторизована, но еще не завершена')
	]
	salary_order = models.DecimalField(max_digits=10, decimal_places=2)
	status_order = models.CharField(max_length=50, choices=ORDER_CHOICES, null=False, blank=False)

class File(models.Model):
	file = models.FileField(upload_to='uploads/%Y/%m/%d/')
	name = models.CharField(max_length=255)
	upload_date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
	file_type = models.CharField(max_length=50)

	def __str__(self):
		return self.name

class Notification(models.Model):
	notification_text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)
	user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
	