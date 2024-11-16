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
import math
from home.models import *

def index(request):
    return HttpResponse('Server Running')



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
    username = request.user.first_name
    user = request.user

    
    if lat is None and lon is None:
        return JsonResponse({'message': 'Invalid location data.', 'username': username}, status=400)
    
    lat, lon = float(lat), float(lon)
    if is_within_registered_area(lat, lon, user):
        return JsonResponse({'message': 'Location is valid.', 'username': username}, status=200)
    else:
        return JsonResponse({'message': 'You are out of the registered location.', 'username': username}, status=400)



def is_within_registered_area(user_lat, user_lon, user):
    temp = Add_Project_User.objects.get(user=user)
    project = Project.objects.get(name = temp.project_name)

    project_lat, project_lon, project_radius = float(project.lat), float(project.lon), float(project.radious)

    if project_lat is not None and project_lon is not None and project_radius is not None:
        distance = haversine(user_lat, user_lon, project_lat, project_lon)
        print(distance)
        if distance <= project_radius:
            return True
    return False  


def haversine(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate the distance between two lat/lon points in kilometers
    R = 6371  # Earth radius in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c