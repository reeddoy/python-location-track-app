from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication

def index(request):
    return HttpResponse('Working Fine')



@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        device_id = data.get('device_id')  # You can use the IMEI for additional checks if needed

        print(device_id)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User is authenticated, generate token
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key, 'message': 'Login successful!'}, status=200)
        else:
            # Authentication failed
            return JsonResponse({'message': 'Invalid username or password!'}, status=400)

    return JsonResponse({'message': 'Method not allowed!'}, status=405)




def test(request):
    data = {
        'message': 'Working Fine',
        'status': 'success'
    }
    return JsonResponse(data)






@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure that the user is authenticated
def location_view(request):
    lat = request.data.get('latitude')
    lon = request.data.get('longitude')
    
    # Get the username of the authenticated user
    username = request.user.first_name
    print(username)
    # Here you can add your logic to handle the location data
    # For example, checking if the location is valid or not
    if lat is not None and lon is not None:
        # You can check the coordinates against registered ones
        if is_within_registered_area(lat, lon):
            return JsonResponse({'message': 'Location is valid.', 'username': username}, status=200)
        else:
            return JsonResponse({'message': 'You are out of the registered location.', 'username': username}, status=400)

    return JsonResponse({'message': 'Invalid location data.', 'username': username}, status=400)

def is_within_registered_area(lat, lon):
    # Implement your logic to verify if the lat/lon is within the registered area
    # For example, checking against a predefined boundary or database entries
    return False  # Replace with actual validation