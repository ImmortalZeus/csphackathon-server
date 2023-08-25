from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import Contestant, Problem, LeaderBoard

# t phải edit cái này thì nó mới fix đc cái bug hash password t bảo

class ContestantAdmin(UserAdmin):
    model = Contestant
    ordering = ('-tscore', 'tpenalty', 'username')
    list_display = ('username', 'id', 'submitted', 'tscore', 'tpenalty', 'score', 'penalty')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    
class ProblemAdmin(admin.ModelAdmin):
    model = Problem
    list_display = ('name', 'id', 'submissions', 'unsolved')

class LeaderBoardAdmin(admin.ModelAdmin):
    model = LeaderBoard
    list_display = ('name', 'value')

admin.site.register(Contestant, ContestantAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(LeaderBoard, LeaderBoardAdmin)
