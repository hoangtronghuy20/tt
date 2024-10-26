from django.urls import path, include
from .views import (
    PartListApiView,
    TestListApiView,
    TestByPartApiView,
    QuestionListByPartApiView,
    QuestionListByTestApiView,
    FeedbackApiView,
    EmailLoginView,
    RegisterView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    GoogleSignupView,
    ResultCreateOrUpdateView,
    ResultListView,
)

urlpatterns = [
    path('api/login-auth/', EmailLoginView.as_view()),
    path('api/register/', RegisterView.as_view()),
    path('api/part', PartListApiView.as_view()),
    path('api/test/', TestListApiView.as_view()),
    path('api/test-by_part/<int:partId>/', TestByPartApiView.as_view()),
    path('api/question-by-part', QuestionListByPartApiView.as_view()),
    path('api/question-by-test', QuestionListByTestApiView.as_view()),
    path('api/feedback', FeedbackApiView.as_view()),
    path('api/password-reset/', PasswordResetRequestView.as_view()),
    path('api/password-reset/confirm/', PasswordResetConfirmView.as_view()),
    path('api/auth/google/', GoogleSignupView.as_view(), name='google-signup'),
    path('api/results/', ResultCreateOrUpdateView.as_view()),
    path('api/all-result/', ResultListView.as_view()),
]
