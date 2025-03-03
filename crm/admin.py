from django.contrib import admin
from .models import CustomUser, Client, Project, Task, Communication, Invoice, File, Notification

admin.site.register(CustomUser)
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Communication)
admin.site.register(Invoice)
admin.site.register(File)
admin.site.register(Notification)






