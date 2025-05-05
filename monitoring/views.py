from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.db.models import Sum, Avg
from datetime import datetime
import json
from datetime import timedelta, datetime
from django.utils import timezone
from collections import defaultdict
from .models import (
    CaffeineIntake, UserProfile, CaffeineProduct, CreatedDrink, HealthTip
)
from .serializers import (
    CaffeineIntakeSerializer, RegisterSerializer,
    HealthTipSerializer, CaffeineProductSerializer, UserSerializer
)

class HealthTipViewSet(viewsets.ModelViewSet):
    queryset = HealthTip.objects.all()
    serializer_class = HealthTipSerializer

def get_caffeine_products(request):
    if request.method == 'GET':
        products = CaffeineProduct.objects.filter(status=1)  # only active products
        data = list(products.values())
        return JsonResponse(data, safe=False)

def get_created_drinks(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Missing user_id'}, status=400)

    created_drinks = CreatedDrink.objects.filter(user_id=user_id)
    data = list(created_drinks.values())
    return JsonResponse(data, safe=False)
        
@api_view(['POST'])
def create_custom_drink(request):
    try:
        user_id = request.data.get('user')
        drink_name = request.data.get('drinkName')
        caffeine = request.data.get('caffeine')
        volumeML = request.data.get('volumeML')
        mgPer100ml = request.data.get('mgPer100ml')
        category = request.data.get('category')
        measurementMethod = request.data.get('measurementMethod')  # <-- Add this

        user = User.objects.get(id=user_id)

        new_drink = CreatedDrink.objects.create(
            user=user,
            drinkName=drink_name,
            caffeine=caffeine,
            volumeML=volumeML,
            mgPer100ml=mgPer100ml,
            category=category,
            measurementMethod=measurementMethod,  # <-- Save it here
            status=True
        )
        return Response({'message': 'Drink created!', 'drink_id': new_drink.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def get_user_profile(request, user_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        profile = get_object_or_404(UserProfile, user=user)

        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "weight": profile.weight,
            "bDate": str(profile.bDate),
            "health_condition": profile.health_condition,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ✅ Fetch all caffeine data
@api_view(['GET'])
def get_caffeine_data(request):
    user_id = request.GET.get("user_id")  # ✅ Get user_id from request

    if not user_id:
        return Response({"error": "User ID is required"}, status=400)

    try:
        data = CaffeineIntake.objects.filter(user_id=user_id)  # ✅ Fetch only user's data
        serializer = CaffeineIntakeSerializer(data, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# ✅ Add a new caffeine intake entry
@api_view(['POST'])
def add_caffeine_entry(request):
    print("Request Data:", request.data)
    try:
        user = User.objects.get(id=request.data['user_id'])

        drink_id = request.data.get('drink_id')
        is_created = request.data.get('is_created')  # Optional

        # Convert drink_id to int if needed
        if isinstance(drink_id, str):
            drink_id = int(drink_id)

        entry = CaffeineIntake.objects.create(
            user=user,
            drink_name=request.data['drink_name'],
            caffeine_amount=request.data['caffeine_amount'],
            serving_size=request.data['serving_size'],
            timestamp=request.data['timestamp'],
            drink_id=drink_id,
            is_created=is_created,
            categoryType=request.data.get('category_type')
        )

        serializer = CaffeineIntakeSerializer(entry)
        return Response(serializer.data, status=201)

    except Exception as e:
        print("Error:", str(e))
        return Response({'error': str(e)}, status=400)







# ✅ Register a new user
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'User created successfully'}, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

# ✅ Login user and return admin status
@csrf_exempt  # 🔥 Add this decorator to disable CSRF
@api_view(['POST'])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    print(f"🔍 Attempting login for: {username}")

    user = authenticate(username=username, password=password)
    if user is not None:
        print("✅ Authentication successful!")
        return Response(
            {
                "message": "Login successful!",
                "id": user.id,  # ✅ Use 'id' instead of 'user_id'
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_admin": user.is_staff,  # Return is_admin status
            },
            status=status.HTTP_200_OK,
        )
    else:
        print("❌ Authentication failed!")
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )



# ✅ Add a new user (Admin only)
@api_view(['POST'])
@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        try:
            data = request.data
            username = data.get("username")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            password = data.get("password")
            is_staff = data.get("is_staff", False)

            if not username or not first_name or not last_name or not password:
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            # Create user using Django's create_user method for password hashing
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, is_staff=is_staff)
            return Response({"message": "User added successfully", "id": user.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def get_users(request):
    try:
        users = User.objects.all()  # Fetch all users from the User model
        data = [{"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name} for user in users]
        return JsonResponse(data, safe=False)  # Return a JsonResponse with the user data
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)     
    
# ✅ Fetch all users
@api_view(['GET'])
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ✅ Edit an existing user
@api_view(['PUT'])
@csrf_exempt  # Exempt CSRF validation for testing, remove it for production
def edit_user(request, user_id):
    if request.method == 'POST':
        try:
            # Fetch the user by ID
            user = User.objects.get(id=user_id)

            # Load the updated data from the request body
            data = json.loads(request.body)
            username = data.get('username')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            is_active = data.get('is_active', True)  # Default to True if not provided

            # Update the fields
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.is_active = is_active

            # Save the updated user
            user.save()

            # Return the updated user data in response
            updated_user_data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
            }
            return JsonResponse(updated_user_data, status=200)

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)


# ✅ Delete an existing user
@api_view(['DELETE'])
@csrf_exempt
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)  # Get the user by ID
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@csrf_exempt
def edit_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)  # Get the user by ID

        data = request.data
        updated_data = {}  # We'll store updated data to log

        if "username" in data:
            user.username = data["username"]
            updated_data["username"] = data["username"]

        if "first_name" in data:
            user.first_name = data["first_name"]
            updated_data["first_name"] = data["first_name"]

        if "last_name" in data:
            user.last_name = data["last_name"]
            updated_data["last_name"] = data["last_name"]

        if "password" in data:
            user.set_password(data["password"])
            updated_data["password"] = "*****"  # Avoid logging the password itself

        if "is_staff" in data:
            user.is_staff = data["is_staff"]
            updated_data["is_staff"] = data["is_staff"]

        if "is_active" in data:
            user.is_active = data["is_active"]
            updated_data["is_active"] = data["is_active"]

        user.save()

        return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    
@csrf_exempt  # Optional: Exempt CSRF protection for testing; remove for production
def update_user_profile(request, user_id):
    if request.method in ['POST', 'PUT', 'PATCH']:  # Handle POST, PUT, and PATCH methods
        try:
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)

            username = data.get('username')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            is_active = data.get('is_active', True)  # Default to True if not provided

            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.is_active = is_active

            user.save()

            updated_user_data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
            }
            return JsonResponse(updated_user_data, status=200)

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Method Not Allowed"}, status=405)
    
@csrf_exempt
def update_user(request, user_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=user_id)
            profile, created = UserProfile.objects.get_or_create(user=user)

            if "weight" in data:
                profile.weight = data["weight"]
            if "bDate" in data:
                profile.bDate = data["bDate"]
            if "health_condition" in data:
                profile.health_condition = data["health_condition"]  # ✅ Add this line

            profile.save()

            return JsonResponse({
                "message": "User details updated successfully!",
                "weight": profile.weight,
                "bDate": profile.bDate,
                "health_condition": profile.health_condition
            }, status=200)

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found!"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)



#dashboard typeshit


@api_view(['GET'])
def analytics_dashboard(request):
    total_entries = CaffeineIntake.objects.count()
    total_caffeine_consumed = CaffeineIntake.objects.aggregate(Sum('caffeine_amount'))['caffeine_amount__sum'] or 0
    average_caffeine_per_entry = total_caffeine_consumed / total_entries if total_entries else 0

    user_caffeine_data = CaffeineIntake.objects.values('user__username').annotate(
        total_caffeine=Sum('caffeine_amount'),
        avg_caffeine=Avg('caffeine_amount')
    )

    default_products = CaffeineProduct.objects.count()

    analytics_data = {
        'total_entries': total_entries,
        'total_caffeine_consumed': total_caffeine_consumed,
        'average_caffeine_per_entry': average_caffeine_per_entry,
        'userCaffeineData': list(user_caffeine_data),
        'default_products': default_products,  # ✅ only this
    }

    return JsonResponse(analytics_data)

def analytics_data(request):
    # Use all entries now (no filtering by is_created)
    all_entries = CaffeineIntake.objects.all()

    total_entries = all_entries.count()
    total_caffeine_consumed = float(all_entries.aggregate(Sum('caffeine_amount'))['caffeine_amount__sum'] or 0.0)
    average_caffeine_per_entry = float(all_entries.aggregate(Avg('caffeine_amount'))['caffeine_amount__avg'] or 0.0)

    user_data = []
    users = User.objects.all()

    for user in users:
        user_entries = CaffeineIntake.objects.filter(user=user).values(
            'id', 'caffeine_amount', 'drink_name', 'timestamp'
        )
        total = float(user_entries.aggregate(Sum('caffeine_amount'))['caffeine_amount__sum'] or 0.0)
        avg = float(user_entries.aggregate(Avg('caffeine_amount'))['caffeine_amount__avg'] or 0.0)

        user_data.append({
            'user_id': user.id,
            'username': user.username,
            'total_caffeine': total,
            'avg_caffeine': avg,
            'entries': list(user_entries),
        })

    return JsonResponse({
        'total_entries': total_entries,
        'total_caffeine_consumed': total_caffeine_consumed,
        'average_caffeine_per_entry': average_caffeine_per_entry,
        'user_caffeine_data': user_data,
    })



def analytics_view(request):
    # Your current logic for total_entries, total_caffeine, etc.

    # 👇 Add this block inside your view
    entries = CaffeineIntake.objects.all()

    if entries.exists():
        date_totals = {}
        for entry in entries:
            date = entry.timestamp.date()
            if date not in date_totals:
                date_totals[date] = 0
            date_totals[date] += entry.caffeine_amount

        total_days = len(date_totals)
        total_caffeine = sum(date_totals.values())

        overall_avg_per_day = total_caffeine / total_days if total_days > 0 else 0
    else:
        overall_avg_per_day = 0

    response_data = {
        # existing analytics data
        'total_entries': entries.count(),
        'total_caffeine_consumed': total_caffeine,
        'average_caffeine_per_entry': total_caffeine / entries.count() if entries.exists() else 0,
        # 👇 Add this new key to your response
        'overall_average_caffeine_per_day': overall_avg_per_day,
    }

    return JsonResponse(response_data)
    
class CaffeineEntryDetail(APIView):
    def delete(self, request, entry_id):
        try:
            entry = CaffeineIntake.objects.get(id=entry_id)
            entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CaffeineIntake.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
    
class AnalyticsView(APIView):
    def get(self, request):
        entries = CaffeineIntake.objects.all()

        if entries.exists():
            date_totals = {}
            for entry in entries:
                date = entry.timestamp.date()
                if date not in date_totals:
                    date_totals[date] = 0
                date_totals[date] += entry.caffeine_amount

            total_days = len(date_totals)
            total_caffeine = sum(date_totals.values())

            overall_avg_per_day = total_caffeine / total_days if total_days > 0 else 0
        else:
            overall_avg_per_day = 0

        response_data = {
            'total_entries': entries.count(),
            'total_caffeine_consumed': total_caffeine,
            'average_caffeine_per_entry': total_caffeine / entries.count() if entries.exists() else 0,
            'overall_average_caffeine_per_day': overall_avg_per_day,
        }

        return Response(response_data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Only admin can access this
    
    
@api_view(['POST'])
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    new_password = request.data.get('new_password')
    if new_password:
        user.set_password(new_password)
        user.save()
        return Response({'status': 'password reset successful'})
    return Response({'error': 'No password provided'}, status=400)

class UserListView(APIView):
    def get(self, request):
        # Use select_related to fetch the related UserProfile data efficiently
        users = User.objects.select_related('userprofile').all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    
@api_view(['GET'])
def get_caffeine_products(request):
    products = CaffeineProduct.objects.all()  # Fetch all products
    serializer = CaffeineProductSerializer(products, many=True)
    return Response(serializer.data)


class CaffeineProductViewSet(viewsets.ModelViewSet):
    queryset = CaffeineProduct.objects.all()
    serializer_class = CaffeineProductSerializer
    pagination_class = PageNumberPagination  # Use your pagination class

    # The list method is already provided for handling GET requests
    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            # Serialize the data
            serializer = self.get_serializer(page, many=True)
            # Return paginated response with total count
            return self.get_paginated_response({
                'count': self.queryset.count(),  # Total number of products
                'results': serializer.data,
            })
        # If not paginated, return the full set of results
        return Response(serializer.data)

    # This method handles POST requests to create new products
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new product to the database
            return Response(serializer.data, status=201)  # Respond with the created product and 201 status
        return Response(serializer.errors, status=400)  # If validation fails, respond with errors
    
@csrf_exempt
def update_product_status(request, pk):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            status = data.get('status')
            if status is None:
                return JsonResponse({'error': 'Status not provided'}, status=400)

            product = CaffeineProduct.objects.get(pk=pk)
            product.status = status
            product.save()

            return JsonResponse({'message': 'Product status updated successfully'})
        except CaffeineProduct.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@api_view(['PUT'])
def update_caffeine_product(request, pk):
    try:
        product = CaffeineProduct.objects.get(pk=pk)
    except CaffeineProduct.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CaffeineProductSerializer(product, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def product_count(request):
    total_products = CaffeineProduct.objects.count()
    return JsonResponse({'total_products': total_products})
    
    
@api_view(['GET'])
def get_caffeine_products(request):
    products = CaffeineProduct.objects.all()  
    serializer = CaffeineProductSerializer(products, many=True)
    return Response(serializer.data)

class CaffeineProductViewSet(viewsets.ModelViewSet):
    queryset = CaffeineProduct.objects.all()
    serializer_class = CaffeineProductSerializer

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'count': self.queryset.count(),  # Total number of products
                'results': serializer.data,
            })
        return Response(serializer.data)
    
#generate report

def total_caffeine_last_period(start_date=None, end_date=None):
    if not start_date:
        # Default to the last 7 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
    
    total_caffeine = CaffeineIntake.objects.filter(timestamp__range=[start_date, end_date]).aggregate(Sum('caffeine_amount'))['caffeine_amount__sum'] or 0
    return total_caffeine

def daily_avg_caffeine(start_date=None, end_date=None):
    if not start_date:
        # Default to the last 7 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
    
    entries = CaffeineIntake.objects.filter(timestamp__range=[start_date, end_date])
    total_caffeine = entries.aggregate(Sum('caffeine_amount'))['caffeine_amount__sum'] or 0
    total_days = (end_date - start_date).days or 1  # Ensure there's at least 1 day
    return total_caffeine / total_days


def total_drinks_consumed(start_date=None, end_date=None):
    if not start_date:
        # Default to the last 7 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
    
    total_drinks = CaffeineIntake.objects.filter(timestamp__range=[start_date, end_date]).count()
    return total_drinks

def health_tips():
    tips = HealthTip.objects.all()
    return [{"title": tip.title, "detail": tip.detail, "link": tip.link} for tip in tips]


def caffeine_density_per_category(category):
    drinks = CaffeineIntake.objects.filter(categoryType=category)
    caffeine_density = drinks.aggregate(Avg('caffeine_amount'))['caffeine_amount__avg'] or 0
    return caffeine_density


# def caffeine_per_weight(start_date=None, end_date=None):
#     if not start_date:
#         # Default to the last 7 days
#         end_date = timezone.now()
#         start_date = end_date - timedelta(days=7)
    
#     # Filter the caffeine intake entries by the given date range
#     entries = CaffeineIntake.objects.filter(timestamp__range=[start_date, end_date])
    
#     # Calculate total caffeine intake for the given period
#     total_caffeine = entries.aggregate(Sum('caffeine_amount'))['caffeine_amount__sum'] or 0
    
#     # Calculate total weight for all users (only users with weight are considered)
#     total_weight = UserProfile.objects.aggregate(Sum('weight'))['weight__sum'] or 0
    
#     if total_weight > 0:
#         return total_caffeine / total_weight
#     return 0

def caffeine_intake_trend(start_date=None, end_date=None):
    if not start_date:
        # Default to the last 7 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
    
    entries = CaffeineIntake.objects.filter(timestamp__range=[start_date, end_date])
    trend_data = {}
    
    for entry in entries:
        date = entry.timestamp.date()
        if date not in trend_data:
            trend_data[date] = 0
        trend_data[date] += entry.caffeine_amount
    
    return trend_data

def total_calories_consumed(start_date=None, end_date=None):
    if not start_date:
        # Default to the last 7 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
    
    entries = CaffeineIntake.objects.filter(timestamp__range=[start_date, end_date])
    total_calories = 0
    
    for entry in entries:
        product = CaffeineProduct.objects.filter(drinkName=entry.drink_name).first()
        if product:
            total_calories += product.calorie  # Assuming one product corresponds to one entry
    
    return total_calories


# Convert any datetime.date keys to strings
def convert_date_keys(data):
    if isinstance(data, dict):
        return {str(k): v for k, v in data.items()}
    return data


@api_view(['POST'])
def add_caffeine_product(request):
    serializer = CaffeineProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)  # Created
    return Response(serializer.errors, status=400)  # Bad Request












