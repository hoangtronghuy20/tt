from django.contrib import admin
from .models import Part, Test, Question, Language, Translate, Result, Feedback

class PartAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "created")

admin.site.register(Part, PartAdmin)

class TestAdmin(admin.ModelAdmin):
    list_display = ("pk", "part_id", "name", "created")
admin.site.register(Test, TestAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ("pk", "part_id", "test_id", "question", "photo", "audio", "option_a", "option_b", "option_c", "option_d", "correct", "isRelease", "created")
admin.site.register(Question, QuestionAdmin)

class LanguageAdmin(admin.ModelAdmin):
    list_display = ("language", "region", "created")
admin.site.register(Language, LanguageAdmin)

class TranslateAdmin(admin.ModelAdmin):
    list_display = ("question_id", "language_id", "option_a", "option_b", "option_c", "option_d", "hint", "created")
admin.site.register(Translate, TranslateAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user_id", "version", "android", "fullname", "content", "created")
admin.site.register(Feedback, FeedbackAdmin)

class ResultAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "test_id", "isListening", "score", "time", "created")
admin.site.register(Result, ResultAdmin)
