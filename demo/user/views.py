from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import PhoneVerification, Order, OrderItem
from django.utils import timezone
import json
from .utils import send_otp_to_user

@require_POST
def send_otp(request):
    """Send OTP to user's phone via SMS or WhatsApp"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        delivery_method = data.get('delivery_method', 'sms')
        
        # Validate phone
        if not phone or len(phone) < 10:
            return JsonResponse({
                'success': False,
                'error': 'Please enter a valid phone number'
            })
        
        # Clean phone number
        if not phone.startswith('+'):
            phone = f"+91{phone}"  # Default to India country code
        
        # Generate and save OTP
        verification = PhoneVerification(
            phone_number=phone,
            delivery_method=delivery_method
        )
        otp = verification.generate_otp()
        verification.save()
        
        # Send OTP to user
        success, message = send_otp_to_user(phone, otp, delivery_method)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'OTP sent via {delivery_method}',
                'verification_id': verification.id
            })
        else:
            # Delete the verification record if sending failed
            verification.delete()
            return JsonResponse({
                'success': False,
                'error': f'Failed to send OTP: {message}'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_POST
def verify_otp(request):
    """Verify OTP and unlock address section"""
    try:
        data = json.loads(request.body)
        verification_id = data.get('verification_id')
        otp = data.get('otp', '').strip()
        
        try:
            verification = PhoneVerification.objects.get(id=verification_id)
        except PhoneVerification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid verification session'
            })
        
        # Check expiry
        if verification.is_expired():
            verification.delete()
            return JsonResponse({
                'success': False,
                'error': 'OTP has expired. Please request a new one.'
            })
        
        # Verify OTP
        if verification.otp == otp:
            verification.is_verified = True
            verification.save()
            
            # Store in session that phone is verified
            request.session['verified_phone'] = verification.phone_number
            request.session['verification_id'] = verification.id
            
            return JsonResponse({
                'success': True,
                'message': 'Phone verified successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid OTP. Please try again.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_POST
def resend_otp(request):
    """Resend OTP for existing verification"""
    try:
        data = json.loads(request.body)
        verification_id = data.get('verification_id')
        
        try:
            verification = PhoneVerification.objects.get(id=verification_id)
        except PhoneVerification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid verification session'
            })
        
        # Generate new OTP
        otp = verification.generate_otp()
        verification.save()
        
        # Send OTP to user
        success, message = send_otp_to_user(
            verification.phone_number, 
            otp, 
            verification.delivery_method
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'OTP resent via {verification.delivery_method}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to resend OTP: {message}'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_POST
def save_order(request):
    """Save order after payment"""
    try:
        # Check if phone is verified
        if not request.session.get('verified_phone'):
            return JsonResponse({
                'success': False,
                'error': 'Phone not verified'
            })
        
        data = json.loads(request.body)
        cart = request.session.get('cart', {})
        
        if not cart:
            return JsonResponse({
                'success': False,
                'error': 'Cart is empty'
            })
        
        # Create order
        order = Order.objects.create(
            phone_number=request.session['verified_phone'],
            full_name=data.get('fullname'),
            email=data.get('email'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            pin_code=data.get('pin'),
            delivery_type=data.get('delivery'),
            payment_method=data.get('payment_method'),
            subtotal=float(data.get('subtotal', 0)),
            shipping=float(data.get('shipping', 0)),
            total=float(data.get('total', 0))
        )
        
        # Create order items
        for key, item in cart.items():
            OrderItem.objects.create(
                order=order,
                item_type=item['type'],
                item_id=item['id'],
                title=item['title'],
                price=float(item['price']),
                quantity=item['quantity'],
                image_url=item.get('image', '')
            )
        
        # Clear cart
        del request.session['cart']
        del request.session['verified_phone']
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': 'Order placed successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })