from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import User, Part, Test, Question, Translate, Language, Result
from .serializers import PartSerializer, TestSerializer, FeedbackSerializer, ResultSerializer
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from .serializers import PasswordResetSerializer, PasswordResetConfirmSerializer, RegisterSerializer
from django.conf import settings
import requests
from django.shortcuts import render


class EmailLoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        response = super(EmailLoginView, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        data = {
            'userId': user.pk,
            'token': token.key,
            'username': user.username,
            'email': user.email
        }

        return Response(data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class PartListApiView(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        parts = Part.objects.all()
        serializer = PartSerializer(parts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TestListApiView(APIView):

    def get(self, request, *args, **kwargs):
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TestByPartApiView(APIView):

    def get(self, request, *args, **kwargs):
        part = get_object_or_404(Part, id=kwargs.get('partId'))
        tests = Test.objects.filter(part_id=part)
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuestionListByPartApiView(APIView):

    def get(self, request, *args, **kwargs):
        part_id = request.GET.get('part')
        test_id = request.GET.get('test')
        lang_id = request.GET.get('lang')

        if not part_id or not test_id or not lang_id:
            return JsonResponse({'error': 'part_id, test_id and lang_id are required'}, status=400)

        part = get_object_or_404(Part, id=part_id)
        test = get_object_or_404(Test, id=test_id)
        language = get_object_or_404(Language, id=lang_id)
        questions = Question.objects.filter(part_id=part, test_id=test, isRelease=True)
        data = []
        for question in questions:
            translate = Translate.objects.filter(question_id=question, language_id=language).first()
            data.append({
                'partId': part_id,
                'questionId': question.pk,
                'question': question.question,
                'photo': question.photo.url if question.photo else None,
                'audio': question.audio.url if question.audio else None,
                'optionA': question.option_a,
                'optionB': question.option_b,
                'optionC': question.option_c,
                'optionD': question.option_d,
                'correct': question.correct,
                'translateA': translate.option_a if translate else None,
                'translateB': translate.option_b if translate else None,
                'translateC': translate.option_c if translate else None,
                'translateD': translate.option_d if translate else None,
                'hint': translate.hint if translate else None,
            })

        return JsonResponse(data, safe=False)

class QuestionListByTestApiView(APIView):

    def get(self, request, *args, **kwargs):
        test_id = request.GET.get('test')
        lang_id = request.GET.get('lang')

        if not test_id or not lang_id:
            return JsonResponse({'error': 'test_id and lang_id are required'}, status=400)

        test = get_object_or_404(Test, id=test_id)
        language = get_object_or_404(Language, id=lang_id)
        questions = Question.objects.filter(test_id=test, isRelease=True)
        data = []
        for question in questions:
            translate = Translate.objects.filter(question_id=question, language_id=language).first()
            data.append({
                'partId': question.part_id.id,
                'questionId': question.pk,
                'question': question.question,
                'photo': question.photo.url if question.photo else None,
                'audio': question.audio.url if question.audio else None,
                'optionA': question.option_a,
                'optionB': question.option_b,
                'optionC': question.option_c,
                'optionD': question.option_d,
                'correct': question.correct,
                'translateA': translate.option_a if translate else None,
                'translateB': translate.option_b if translate else None,
                'translateC': translate.option_c if translate else None,
                'translateD': translate.option_d if translate else None,
                'hint': translate.hint if translate else None,
            })

        return JsonResponse(data, safe=False)

def question_photo(request, pk):
    question = Question.objects.get(pk=pk)
    return render(request, 'question_photo.html', {'question': question})

def question_audio(request, pk):
    question = Question.objects.get(pk=pk)
    return render(request, 'question_audio.html', {'question': question})

class FeedbackApiView(APIView):

    def post(self, request, *args, **kwargs):
        data = {
            'user_id': request.data.get('user_id'),
            'version': request.data.get('version'),
            'android': request.data.get('android'),
            'fullname': request.data.get('fullname'),
            'content': request.data.get('content')
        }
        serializer = FeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                # Prepare email content
                subject = 'Password Reset Request'
                message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'domain': get_current_site(request).domain,
                    'uid': uid,
                    'token': token,
                })
                send_mail(subject, message, None, [email])
                response = {
                    "message": "Password reset email sent.",
                    "token": token,
                    "uid": uid
                }

                return Response(response, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"message": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            uid = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                uid = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "Password has been reset."}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"message": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleSignupView(APIView):
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Authorization code not provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange the authorization code for an access token
        token_data = self.get_access_token(code)
        if 'error' in token_data:
            return Response({'error': 'Failed to obtain access token'}, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_data.get('access_token')
        user_info = self.get_user_info(access_token)

        if not user_info or 'email' not in user_info:
            return Response({'error': 'Failed to retrieve user information'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update the user
        user, created = User.objects.get_or_create(
            email=user_info['email'],
            defaults={'username': user_info['email'].split('@')[0]}
        )

        # Generate or retrieve a token for the user
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'userId': user.pk,
            'token': token.key,
            'username': user.username,
            'email': user.email
        })

    def get_access_token(self, code):
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=data)
        return response.json()

    def get_user_info(self, access_token):
        url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        return response.json()

class ResultCreateOrUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('user_id')
        test_id = request.data.get('test_id')

        if not user_id or not test_id:
            return Response(
                {"error": "user_id and test_id are required."},
                status=status.HTTP_400_BAD_REQUEST)

        result = Result.objects.filter(user_id=user_id, test_id=test_id).first()

        # If the result exists, update it, otherwise create a new one
        if result:
            serializer = ResultSerializer(result, data=request.data, partial=True)
        else:
            serializer = ResultSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            status_code = status.HTTP_200_OK if result else status.HTTP_201_CREATED
            return Response(serializer.data, status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResultListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        results = Result.objects.all()
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
