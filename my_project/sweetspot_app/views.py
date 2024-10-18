import requests
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from .models import Customer, Cake, CakeCustomization, Cart, Order
from .serializers import CustomerSerializer, CakeSerializer, CakeCustomizationSerializer, CartSerializer, OrderSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action 
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from drf_spectacular.utils import extend_schema  
from rest_framework.viewsets import ViewSet


# This ModelViewSet class automatically provides 
# the routes for all CRUD operations
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


    @action(detail=False, methods=['post'], url_path='login')
    @extend_schema(tags=["Customer"])
#Write a sub API in CustomerViewset for login with 
# Input : email and password  Output : “Login Successfull”.
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

    # Check if email and password are provided
        if not email or not password:
            return Response({"message": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(email=email)

        # Check the password
            if check_password(password, customer.password):
                return Response({"message": "Login Successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
        # Log the error for debugging
            print(f"Error during login: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Cake CRUD operations
class CakeViewSet(viewsets.ModelViewSet):
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer
    @extend_schema(tags=["Cake"],exclude=True)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

# CakeCustomization CRUD operations
class CakeCustomizationViewSet(viewsets.ModelViewSet):
    queryset = CakeCustomization.objects.all()
    serializer_class = CakeCustomizationSerializer

    @extend_schema(tags=["CakeCustomization"],exclude=True)

    def create(self, request, *args, **kwargs):
        # Call the default create method
        response = super().create(request, *args, **kwargs)

        # Add custom message after successful creation
        if response.status_code == status.HTTP_201_CREATED:
            return Response({
                "message": "Your customization is done",
                "data": response.data  # Include the created object data
            }, status=status.HTTP_201_CREATED)
        else:
            return response  # Return the default response if something goes wrong
        
# Cart CRUD operations
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=False, methods=['post'], url_path='add-to-cart')
    @extend_schema(tags=["Cart"], description="Add cake to cart with or without customization")
    def add_to_cart(self, request):
        try:
            customer_id = request.data.get('customer_id')
            cake_id = request.data.get('cake_id')
            quantity = request.data.get('quantity', 1)
            customization_id = request.data.get('customization_id', None)

            errors = {}

            # Validate quantity (it should be a positive integer)
            if not str(quantity).isdigit() or int(quantity) <= 0:
                errors['quantity'] = "Quantity should be a positive integer"

            if errors:
                return Response({"message": errors}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the cake exists and is available
            try:
                cake = Cake.objects.get(id=cake_id, available=True)
            except Cake.DoesNotExist:
                return Response({"message": "Cake not available"}, status=status.HTTP_404_NOT_FOUND)

            # Get the customer
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check for customization (if provided)
            customization = None
            if customization_id:
                try:
                    customization = CakeCustomization.objects.get(id=customization_id, cake=cake, customer=customer)
                except CakeCustomization.DoesNotExist:
                    return Response({"message": "Customization not found or doesn't belong to this cake"}, status=status.HTTP_404_NOT_FOUND)

            # Add the cake to the cart
            total_amount = cake.price * int(quantity)
            cart, created = Cart.objects.get_or_create(customer=customer, defaults={'quantity': 0, 'total_amount': 0})

            if customization:
                cart.customization = customization

            cart.cake.add(cake)
            cart.quantity += int(quantity)
            cart.total_amount += total_amount
            cart.save()

            return Response({"message": "Cake added to cart successfully", "cart_id": cart.id}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)

# Order CRUD operations
logger = logging.getLogger(__name__)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    def get_object(self):
        try:
            # Use the `pk` from the URL to retrieve the order
            order = super().get_object()  # This calls the inherited method
            return order
        except Order.DoesNotExist:
            # If the order doesn't exist, raise a NotFound exception
            raise NotFound("Order not found")

    @action(detail=False, methods=['post'], url_path='place-order')
    def place_order(self, request):
        try:
            customer_id = request.data.get('customer_id')
            cake_ids = request.data.get('cake_ids')
            cake_customization_id = request.data.get('cake_customization_id')
            delivery_address = request.data.get('delivery_address')
            payment_method = request.data.get('payment_method')

            # Validate required fields
            errors = {}

        # Check if cake_ids are provided
            if not cake_ids:
                errors['cake_ids'] = "At least one cake ID is required"
            if not customer_id:
                errors['customer_id']="Customer Id is required"
            if not delivery_address:
                errors['delivery_address']="Delivery Address is required"
            if not isinstance(cake_ids, list) or len(cake_ids) == 0:
                return Response({"message": "At least one cake must be included in the order"}, status=status.HTTP_400_BAD_REQUEST)
        # Validate payment method
            valid_payment_methods = ['Credit Card', 'Debit Card', 'Net Banking','Cash on Delivery']
            if payment_method not in valid_payment_methods:
                errors['payment_method'] = f"Invalid payment method. Choose from: {', '.join(valid_payment_methods)}"

        # If there are any validation errors, return them
            if errors:
                return Response({"message": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch customer
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch cake customization
            try:
                cake_customization = CakeCustomization.objects.get(id=cake_customization_id)
            except CakeCustomization.DoesNotExist:
                return Response({"message": "Cake customization not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch available cakes
            cakes = Cake.objects.filter(id__in=cake_ids, available=True)
            if not cakes.exists():
                return Response({"message": "No available cakes found in the cart"}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate total price and quantity
            total_price = sum(cake.price for cake in cakes)
            quantity = len(cakes)

            # Create the order
            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    cake_customization=cake_customization,
                    total_price=total_price,
                    quantity=quantity,
                    delivery_address=delivery_address,
                    order_status="Processing",
                    payment_status="Pending",
                    payment_method=payment_method
                )

                order.items.set(cakes)  # Link cakes to the order

            # Serialize the order and return it in the response
            order_data = OrderSerializer(order).data

            return Response({"message": "Order placed successfully", "order": order_data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"message": f"Error placing order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
    @action(detail=True, methods=['patch'], url_path='update-order')
    def update_order(self, request, pk=None):
        try:
            # Get the order object by ID
            order = self.get_object()
            serializer = self.get_serializer(order, data=request.data, partial=True)

            if serializer.is_valid():
                # Save the updated order details
                serializer.save()

                # Check for payment status and handle payment details
                payment_status = request.data.get('payment_status')
                if payment_status == 'Paid' and order.payment_method != 'Cash on Delivery':
                    # Send email for successful payment
                    self.send_payment_success_email(order.customer.email)
                    # Remove ordered items from the cart
                    Cart.objects.filter(customer=order.customer).delete()
                
                # For Cash on Delivery, handle COD-specific logic
                elif order.payment_method == 'Cash on Delivery':
                    self.send_cod_order_confirmation_email(order.customer.email)
                     # No need to remove cart items until actual payment at delivery

                return Response({
                    "message": "Order updated successfully, email sent and items removed from cart",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
        except Exception as e:
            logger.error(f"Unexpected error during order update: {str(e)}")  # Log the unexpected error
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def send_payment_success_email(self, email):
        try:
            send_mail(
                'Payment Successful! Your order has been placed',
                'Dear customer, your payment has been processed successfully. Your order will be delivered soon.',
                'lily163183@gmail.com',  # Replace with your email
                [email],  # Recipient's email
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")  # Log the email sending error
    def send_cod_order_confirmation_email(self, email):
        try:
            send_mail(
                'Order Confirmed: Cash on Delivery',
                'Dear customer, your order has been placed. You can pay on delivery.',
                'lily163183@gmail.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Error sending COD email: {str(e)}")