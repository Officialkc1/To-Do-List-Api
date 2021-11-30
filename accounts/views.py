from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password, check_password
from . serializers import CustomUserSerializer, ChangePasswordSerializer, LoginSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.signals import user_logged_in
from drf_yasg import openapi



# from django.shortcuts import get_list_or_404, render, get_object_or_404
# from django.core.mail import send_mail


# Create your views here.


User = get_user_model()

@swagger_auto_schema(methods=['POST'], request_body=CustomUserSerializer())
@api_view(['POST'])
def add_user(request):
    
    """ Allows the user to be able to sign up on the platform """

    if request.method == 'POST':
        
        serializer = CustomUserSerializer(data = request.data)
        
        if serializer.is_valid():

            
            #hash password
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            user = User.objects.create(**serializer.validated_data)
            

            serializer = CustomUserSerializer(user)
            data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

            return Response(data, status = status.HTTP_201_CREATED)

        else:
            data = {
                'status'  : False,
                'message' : "Unsuccessful",
                'error' : serializer.errors,
            }

            return Response(data, status = status.HTTP_400_BAD_REQUEST)

@authentication_classes([BasicAuthentication])
@permission_classes([IsAdminUser])
@api_view(['GET'])
def get_user(request):
    
    """Allows the admin to see all users (both admin and normal users) """
    if request.method == 'GET':
        user = User.objects.filter(is_active=True)
    
        
        serializer = CustomUserSerializer(user, many =True)
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)


#Get the detail of a single user by their ID
        
       
@swagger_auto_schema(methods=['PUT','DELETE'], request_body=CustomUserSerializer()) 
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])   
@api_view(['GET', 'PUT', 'DELETE'])

def profile(request):
    """Allows the logged in user to view their profile, edit or deactivate account. Do not use this view for changing password or resetting password"""
    
    try:
        user = User.objects.get(id = request.user.id, is_active=True)
    
    except User.DoesNotExist:
        data = {
                'status'  : False,
                'message' : "Does not exist"
            }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)

    #Update the profile of the user
    elif request.method == 'PUT':
        serializer = CustomUserSerializer(user, data = request.data, partial=True) 

        if serializer.is_valid():
            if 'password' in serializer.validated_data.keys():
                raise ValidationError(detail="Cannot change password with this view")
            
            serializer.save()

            data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

            return Response(data, status = status.HTTP_201_CREATED)

        else:
            data = {
                'status'  : False,
                'message' : "Unsuccessful",
                'error' : serializer.errors,
            }

            return Response(data, status = status.HTTP_400_BAD_REQUEST)

    #delete the account
    elif request.method == 'DELETE':
        user.is_active = False
        user.save()

        data = {
                'status'  : True,
                'message' : "Deleted Successfully"
            }

        return Response(data, status = status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT, 
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    }
))
@api_view(['POST'])
def user_login(request):
    
    """Allows users to log in to the platform. Sends the jwt refresh and access tokens. Check settings for token life time."""
    
    if request.method == "POST":
        user = authenticate(request, username = request.data['username'], password = request.data['password'])
        if user is not None:
            if user.is_active==True:
                
                try:

                    user_detail = {}
                    user_detail['id']   = user.id
                    user_detail['first_name'] = user.first_name
                    user_detail['last_name'] = user.last_name
                    user_detail['email'] = user.email
                    user_detail['username'] = user.username
                    
                    user_logged_in.send(sender=user.__class__,
                                        request=request, user=user)

                    data = {
                    'status'  : True,
                    'message' : "Successful",
                    'data' : user_detail,
                    }
                    return Response(data, status=status.HTTP_200_OK)
                
                

                except Exception as e:
                    raise e
            else:
                data = {
                'status'  : False,
                'error': 'This account has not been activated'
                }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        else:
            data = {
                'status'  : False,
                'error': 'Please provide a valid username and a password'
                }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        
        
@swagger_auto_schema(methods=['POST'], request_body=ChangePasswordSerializer())
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated]) 
@api_view(['POST'])
  
def reset_password(request):
    """Allows users to edit password when logged in."""
    user = request.user
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data = request.data)
        if serializer.is_valid():
            if check_password(serializer.validated_data['old_password'], user.password):
                if serializer.check_pass():
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    
                    data = {
                        'status'  : True,
                        'message': "Successfully saved password"
                        }
                    return Response(data, status=status.HTTP_202_ACCEPTED) 
                else:
                    
                    data = {
                        'status'  : False,
                        'error': "Please enter matching passwords"
                        }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)   
        
            else:
                
                data = {
                    'status'  : False,
                    'error': "Incorrect password"
                    }
                return Response(data, status=status.HTTP_401_UNAUTHORIZED)   
        
            
        else:
            
            data = {
                'status'  : False,
                'error': serializer.errors
                }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)   
        


@swagger_auto_schema(methods=['DELETE'], request_body=CustomUserSerializer())
@api_view(['GET', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAdminUser])
def user_detail(request, user_id):
    """"""
    
    try:
        user = User.objects.get(id =user_id, is_active=True)
    
    except User.DoesNotExist:
        data = {
                'status'  : False,
                'message' : "Does not exist"
            }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)

    #delete the account
    elif request.method == 'DELETE':
        user.is_active = False
        user.save()

        data = {
                'status'  : True,
                'message' : "Deleted Successfully"
            }

        return Response(data, status = status.HTTP_204_NO_CONTENT)
