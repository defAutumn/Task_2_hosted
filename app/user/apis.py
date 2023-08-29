from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import views, response, exceptions, permissions, status
from . import serializer as user_serializer
from . import services, authentication
from . import emails


@extend_schema(tags=["Register"])
class RegisterApi(views.APIView):
    @extend_schema(
        summary='Register new user',
        request=user_serializer.CustomUserSerializer,
        responses={status.HTTP_200_OK: user_serializer.CustomUserSerializer,
                   status.HTTP_400_BAD_REQUEST: user_serializer.CustomUserSerializer,
                   status.HTTP_401_UNAUTHORIZED: user_serializer.CustomUserSerializer,
                   status.HTTP_403_FORBIDDEN: user_serializer.CustomUserSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                       response=None,
                       description='Описание 500 ответа'),
                   },
    )
    def post(self, request):
        serializer = user_serializer.CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        serializer.instance = services.create_user(user_dc=data)

        return response.Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Login and Logout"])
class LoginApi(views.APIView):
    @extend_schema(
        summary='Login user',
        request=user_serializer.CustomUserLoginSerializer,
        responses={status.HTTP_200_OK: user_serializer.CustomUserSerializer,
                   status.HTTP_400_BAD_REQUEST: user_serializer.CustomUserSerializer,
                   status.HTTP_401_UNAUTHORIZED: user_serializer.CustomUserSerializer,
                   status.HTTP_403_FORBIDDEN: user_serializer.CustomUserSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                       response=None,
                       description='Описание 500 ответа'
                   ),
        },

    )
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = services.user_mail_selector(email=email)

        if user is None:
            raise exceptions.AuthenticationFailed('Invalid Credentials')

        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed('Invalid Credentials')

        emails.send_otp_email(user.email)

        return response.Response({"result": "check OTP on mail"})


class VerifyOTP(views.APIView):
    @extend_schema(
        summary='Login user',
        request=user_serializer.VerifyAccountSerializer,
        responses={status.HTTP_200_OK: user_serializer.CustomUserSerializer},
    )
    def post(self, request):
        try:
            data = request.data
            serializer = user_serializer.VerifyAccountSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            email = serializer.data['email']
            otp = serializer.data['otp']

            user = services.user_mail_selector(email)

            if user is None:
                raise exceptions.AuthenticationFailed('Invalid Credentials')

            if not user.otp == otp:
                raise exceptions.AuthenticationFailed('Invalid Credentials')

            user.is_verified = True
            user.save()

            token = services.create_token(user_id=user.id)

            resp = response.Response({'result':'All is ok'})

            resp.set_cookie(key='jwt', value=token, httponly=True)

            return resp
        except Exception as e:
            print(e)


@extend_schema(tags=["User"])
class UserApi(views.APIView):
    """
    This endpoint can only be used
    if the user is authenticated
    """
    authentication_classes = (authentication.CustomUserAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(summary='User Info',
                   request=user_serializer.CustomUserSerializer,
                   responses={status.HTTP_200_OK: user_serializer.CustomUserSerializer,
                              status.HTTP_400_BAD_REQUEST: user_serializer.CustomUserSerializer,
                              status.HTTP_401_UNAUTHORIZED: user_serializer.CustomUserSerializer,
                              status.HTTP_403_FORBIDDEN: user_serializer.CustomUserSerializer,
                              status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                                  response=None,
                                  description='Описание 500 ответа'
                              ),
                   },
    )
    def get(self, request):
        user = request.user

        serializer = user_serializer.CustomUserSerializer(user)

        return response.Response(serializer.data)

    @extend_schema(summary='Update User Info',
                   request=user_serializer.CustomUserPutSerializer,
                   responses={status.HTTP_200_OK: user_serializer.CustomUserSerializer,
                              status.HTTP_400_BAD_REQUEST: user_serializer.CustomUserSerializer,
                              status.HTTP_401_UNAUTHORIZED: user_serializer.CustomUserSerializer,
                              status.HTTP_403_FORBIDDEN: user_serializer.CustomUserSerializer,
                              status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                                  response=None,
                                  description='Описание 500 ответа'
                              ),
                   },
    )
    def put(self, request):
        user = request.user
        serializer = user_serializer.CustomUserPutSerializer(user, data=request.data)  # use new serializer here
        if serializer.is_valid():
            serializer.save()
            return response.Response()
        return response.Response(serializer.errors)

    @extend_schema(summary='Delete User',
                   request=None,
                   responses={status.HTTP_200_OK: user_serializer.CustomUserSerializer,
                              status.HTTP_400_BAD_REQUEST: user_serializer.CustomUserSerializer,
                              status.HTTP_401_UNAUTHORIZED: user_serializer.CustomUserSerializer,
                              status.HTTP_403_FORBIDDEN: user_serializer.CustomUserSerializer,
                              status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                                  response=None,
                                  description='Описание 500 ответа'
                              ),
                   },
    )
    def delete(self, request):
        user = request.user
        user.delete()

        return response.Response({"result": "user delete"})


@extend_schema(tags=["Login and Logout"])
class LogoutApi(views.APIView):
    authentication_classes = (authentication.CustomUserAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary='Logout',
        request=None,
        responses={status.HTTP_200_OK: user_serializer.CustomUserSerializer,
                   status.HTTP_400_BAD_REQUEST: user_serializer.CustomUserSerializer,
                   status.HTTP_401_UNAUTHORIZED: user_serializer.CustomUserSerializer,
                   status.HTTP_403_FORBIDDEN: user_serializer.CustomUserSerializer,
                   status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                       response=None,
                       description='Описание 500 ответа'
                   ),
        },
    )
    def post(self, request):
        resp = response.Response()
        resp.delete_cookie('jwt')
        resp.data = {'message': 'bye'}

        return resp