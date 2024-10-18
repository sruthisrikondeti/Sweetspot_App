import re
from rest_framework import serializers
from .models import Customer, Cake, CakeCustomization, Cart, Order
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator

class CustomerSerializer(serializers.ModelSerializer):
    phone_no = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^[6-9]\d{9}$',
                message="Phone number must start with 6, 7, 8, or 9 and be 10 digits long"
            )
        ]
    )
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")

        if not re.search(r'[A-Za-z]', value) or not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain both letters and numbers")

        return value
    def validate_email(self, value):
        if "@" not in value:
            raise serializers.ValidationError("Enter a valid email address")
        return value
    class Meta:
        model = Customer
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True,'required': False},
            'email': {'required': False},  # Set email as optional
            'first_name': {'required': False},  # Set first_name as optional
            'last_name': {'required': False},  # Set last_name as optional
            'phone_no': {'required': False},  # Set phone_no as optional
            'address': {'required': False},  # Set address as optional
            'city': {'required': False},  # Set city as optional
            'state': {'required': False},  # Set state as optional
            'pincode': {'required': False},  # Set pincode as optional
        }
    def create(self, validated_data):
        # Hash the password before saving the customer
        customer = Customer(
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            phone_no=validated_data.get('phone_no', ''),
            address=validated_data.get('address', ''),
            city=validated_data.get('city', ''),
            state=validated_data.get('state', ''),
            pincode=validated_data.get('pincode', ''),
        )
        customer.password = make_password(validated_data['password'])  # Hashing password
        customer.save()
        return customer

class CakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cake
        fields = '__all__'
    
class CakeCustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CakeCustomization
        fields = '__all__'
    
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'payment_status': {'required': False},
            'payment_method': {'required': False},
        }
    