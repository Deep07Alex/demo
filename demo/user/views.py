from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.shortcuts import render
from .models import Order, OrderItem
from .payu_utils import generate_payu_hash, generate_transaction_id, verify_payu_hash
from .utils import send_customer_order_confirmation, send_admin_order_notification
from .shiprocket_utils import ShiprocketAPI
import json
import logging
import time

logger = logging.getLogger(__name__)

def checkout(request):
    """Checkout page that redirects directly to PayU payment gateway"""
    try:
        # Get cart from session (populated by JavaScript Buy Now button)
        cart = request.session.get('cart', {})
        addons = request.session.get('cart_addons', {})
        
        if not cart:
            return HttpResponse("Your cart is empty. Please add books before checkout.", status=400)
        
        # Calculate totals (same logic as initiate_payu_payment)
        subtotal = sum(float(item['price']) * item['quantity'] for item in cart.values())
        addon_prices = {'Bag': 30, 'bookmark': 20, 'packing': 20}
        addon_total = sum(addon_prices.get(key, 0) for key, selected in addons.items() if selected)
        total_books = sum(item['quantity'] for item in cart.values())
        shipping = 0 if subtotal >= 499 else 49.00
        discount = 100 if total_books >= 10 else 0
        total = subtotal + shipping + addon_total - discount
        
        # Create pending order
        order = Order.objects.create(
            email='pending@payment.com',
            verified_email='',
            phone_number='',
            full_name='',
            address='',
            city='',
            state='',
            pin_code='',
            delivery_type='Standard (3-6 days)',
            payment_method='card',
            subtotal=subtotal,
            shipping=shipping,
            discount=discount,
            total=total,
            status='pending_payment'
        )
        
        # Create order items (books)
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
        
        # Create order items (addons)
        addon_names = {'Bag': 'Bag', 'bookmark': 'Bookmark', 'packing': 'Packing'}
        for addon_key, selected in addons.items():
            if selected:
                OrderItem.objects.create(
                    order=order,
                    item_type='addon',
                    item_id=0,
                    title=addon_names[addon_key],
                    price=addon_prices[addon_key],
                    quantity=1,
                    image_url=''
                )
        
        # Generate PayU params
        txnid = generate_transaction_id()
        payu_params = {
            'key': settings.PAYU_MERCHANT_KEY,
            'txnid': txnid,
            'amount': f"{total:.2f}",
            'productinfo': f"Book Order {order.id}",
            'firstname': 'Customer',
            'email': 'customer@example.com',
            'phone': '9999999999',
            'surl': request.build_absolute_uri('/payment/success/'),
            'furl': request.build_absolute_uri('/payment/failure/'),
            'udf1': str(order.id),
            'udf2': str(discount),
            'udf3': str(total_books),
            'udf4': '',
            'udf5': '',
        }
        
        payu_params['hash'] = generate_payu_hash(payu_params)
        request.session['payu_txnid'] = txnid
        request.session['order_id'] = order.id
        
        # Render auto-submitting form to PayU
        return render(request, 'pages/redirect_to_payu.html', {
            'payu_url': settings.PAYU_TEST_URL,
            'params': payu_params
        })
        
    except Exception as e:
        logger.error(f"CHECKOUT ERROR: {str(e)}", exc_info=True)
        return HttpResponse(f"Checkout error: {str(e)}", status=500)

@require_POST
def initiate_payu_payment(request):
    """Direct PayU payment from cart - NO manual verification"""
    try:
        cart = request.session.get('cart', {})
        addons = request.session.get('cart_addons', {})
        
        if not cart:
            return JsonResponse({'success': False, 'error': 'Cart is empty'})
        
        # Calculate totals
        subtotal = sum(float(item['price']) * item['quantity'] for item in cart.values())
        addon_prices = {'Bag': 30, 'bookmark': 20, 'packing': 20}
        addon_total = sum(addon_prices.get(key, 0) for key, selected in addons.items() if selected)
        total_books = sum(item['quantity'] for item in cart.values())
        shipping = 0 if subtotal >= 499 else 49.00
        discount = 100 if total_books >= 10 else 0
        total = subtotal + shipping + addon_total - discount
        
        # Create pending order (will be updated after PayU)
        order = Order.objects.create(
            email='pending@payment.com',  # Will be updated from PayU
            verified_email='',
            phone_number='',
            full_name='',
            address='',
            city='',
            state='',
            pin_code='',
            delivery_type='Standard (3-6 days)',
            payment_method='card',
            subtotal=subtotal,
            shipping=shipping,
            discount=discount,
            total=total,
            status='pending_payment'
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
        
        addon_names = {'Bag': 'Bag', 'bookmark': 'Bookmark', 'packing': 'Packing'}
        for addon_key, selected in addons.items():
            if selected:
                OrderItem.objects.create(
                    order=order,
                    item_type='addon',
                    item_id=0,
                    title=addon_names[addon_key],
                    price=addon_prices[addon_key],
                    quantity=1,
                    image_url=''
                )
        
        # Generate PayU params
        txnid = generate_transaction_id()
        payu_params = {
            'key': settings.PAYU_MERCHANT_KEY,
            'txnid': txnid,
            'amount': f"{total:.2f}",
            'productinfo': f"Book Order {order.id}",
            'firstname': 'Customer',
            'email': 'customer@example.com',
            'phone': '9999999999',
            'surl': request.build_absolute_uri('/payment/success/'),
            'furl': request.build_absolute_uri('/payment/failure/'),
            'udf1': str(order.id),
            'udf2': str(discount),
            'udf3': str(total_books),
            'udf4': '',
            'udf5': '',
        }
        
        payu_params['hash'] = generate_payu_hash(payu_params)
        request.session['payu_txnid'] = txnid
        request.session['order_id'] = order.id
        
        return JsonResponse({
            'success': True,
            'payu_url': settings.PAYU_TEST_URL,
            'payu_params': payu_params
        })
        
    except Exception as e:
        logger.error(f"PAYMENT INIT ERROR: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def payment_success(request):
    """Handle successful PayU payment and create Shiprocket order"""
    if request.method == 'POST':
        response_data = request.POST.dict()
        
        received_hash = response_data.get('hash', '')
        calculated_hash = verify_payu_hash(response_data)
        
        if received_hash == calculated_hash:
            order_id = response_data.get('udf1')
            status = response_data.get('status')
            payment_id = response_data.get('mihpayid', '')
            
            try:
                order = Order.objects.get(id=order_id)
                
                if status == 'success':
                    # Update order with PayU data
                    order.status = 'processing'
                    order.payment_id = payment_id
                    order.email = response_data.get('email', '')[:100]
                    order.verified_email = response_data.get('email', '')[:100]
                    order.full_name = response_data.get('firstname', '')
                    order.phone_number = response_data.get('phone', '')
                    order.address = response_data.get('address1', '')
                    order.city = response_data.get('city', '')
                    order.state = response_data.get('state', '')
                    order.pin_code = response_data.get('zipcode', '')
                    order.save()
                    
                    items = order.items.all()
                    shiprocket_success = False
                    shiprocket_order_id = None
                    
                    # CREATE SHIPROCKET ORDER
                    try:
                        shiprocket = ShiprocketAPI()
                        shiprocket_success, shiprocket_result = shiprocket.create_order(order, items)
                        
                        if shiprocket_success:
                            order.shiprocket_order_id = shiprocket_result
                            order.status = 'shipped'
                            order.save()
                            shiprocket_order_id = shiprocket_result
                        else:
                            logger.error(f"Shiprocket failed: {shiprocket_result}")
                            
                    except Exception as shiprocket_error:
                        logger.error(f"Shiprocket error: {str(shiprocket_error)}", exc_info=True)
                    
                    # Send notifications
                    admin_success, _ = send_admin_order_notification(order, items)
                    customer_success, _ = send_customer_order_confirmation(order, items)
                    
                    # Clear session
                    request.session.pop('cart', None)
                    request.session.pop('cart_addons', None)
                    request.session.pop('payu_txnid', None)
                    request.session.pop('order_id', None)
                    
                    return render(request, 'pages/payment_success.html', {
                        'order': order,
                        'shiprocket_order_id': shiprocket_order_id,
                        'shiprocket_status': 'Success' if shiprocket_success else 'Manual processing required',
                        'notification_sent': customer_success
                    })
                else:
                    order.delete()
                    return render(request, 'pages/payment_failure.html', {
                        'error': f'Payment status: {status}'
                    })
                    
            except Order.DoesNotExist:
                return render(request, 'pages/payment_failure.html', {
                    'error': 'Order not found'
                })
        else:
            return render(request, 'pages/payment_failure.html', {
                'error': 'Security verification failed'
            })
    
    return render(request, 'pages/payment_failure.html', {
        'error': 'Invalid request method'
    })

@csrf_exempt
def payment_failure(request):
    """Handle failed/cancelled PayU payment"""
    if request.method == 'POST':
        response_data = request.POST.dict()
        order_id = response_data.get('udf1')
        
        if order_id:
            try:
                Order.objects.get(id=order_id, status='pending_payment').delete()
            except Order.DoesNotExist:
                pass
        
        return render(request, 'pages/payment_failure.html', {
            'error': response_data.get('error_Message', 'Payment failed')
        })

    return render(request, 'pages/payment_failure.html', {
        'error': 'Payment cancelled or failed'
    })

def test_hash(request):
    """Test hash generation against PayU's example"""
    test_params = {
        'key': 'kdbOTy',
        'txnid': 'TXN-378A9FCDF2DB',
        'amount': '248.00',
        'productinfo': 'Book Order 9',
        'firstname': 'Aritra',
        'email': 'aritradatt39@gmail.com',
        'udf1': '9',
        'udf2': '',
        'udf3': '',
        'udf4': '',
        'udf5': '',
    }
    
    original_salt = settings.PAYU_MERCHANT_SALT
    settings.PAYU_MERCHANT_SALT = 'BKipBlA1YKJopYdzyBtErUmRUkkXMPiU'
    generated_hash = generate_payu_hash(test_params)
    settings.PAYU_MERCHANT_SALT = original_salt
    
    expected_hash = "c95324fa66e20bd8a4a080a22419a6a9bdfb92992b0096c09f7511629329f31ed6f85f7ebce004535e36009c26648a2333934135f903436f5f3e870cc4458f06"
    
    return HttpResponse(f"""
        <h1>Hash Test Results</h1>
        <p><strong>Generated:</strong> {generated_hash}</p>
        <p><strong>Expected:</strong> {expected_hash}</p>
        <p><strong>Match:</strong> {generated_hash == expected_hash}</p>
    """)

@require_POST
def calculate_shipping(request):
    """Calculate shipping rates for given pincode"""
    try:
        data = json.loads(request.body)
        pincode = data.get('pincode', '')
        
        if not pincode or len(pincode) != 6:
            return JsonResponse({
                'success': False, 
                'error': 'Please enter a valid 6-digit PIN code'
            })
        
        # Get cart items
        cart = request.session.get('cart', {})
        if not cart:
            return JsonResponse({
                'success': False, 
                'error': 'Cart is empty'
            })
        
        # Calculate package details
        total_items = sum(item['quantity'] for item in cart.values())
        total_weight = 0.5 * total_items  # Approximate weight
        package_length = 20
        package_width = 15
        package_height = 5 if total_items == 1 else total_items * 2
        
        # Your pickup location pincode (configure this)
        pickup_pincode = "743248"  # Update with your actual pickup pincode
        
        shiprocket = ShiprocketAPI()
        success, rates = shiprocket.calculate_shipping_rates(
            pickup_pincode=pickup_pincode,
            delivery_pincode=pincode,
            weight=total_weight,
            length=package_length,
            width=package_width,
            height=package_height
        )
        
        if success and rates:
            # Filter and format rates
            formatted_rates = []
            for rate in rates[:3]:  # Show top 3 options
                formatted_rates.append({
                    'courier_name': rate.get('courier_name', 'Standard'),
                    'estimated_days': rate.get('estimated_delivery_days', '3-5'),
                    'rate': float(rate.get('freight_charge', 0)),
                    'total_charge': float(rate.get('total_charge', 0))
                })
            
            return JsonResponse({
                'success': True,
                'rates': formatted_rates,
                'pickup_pincode': pickup_pincode
            })
        else:
            # Fallback rates if Shiprocket fails
            fallback_rates = [
                {
                    'courier_name': 'Standard Delivery',
                    'estimated_days': '5-7',
                    'rate': 49.0,
                    'total_charge': 49.0
                },
                {
                    'courier_name': 'Express Delivery',
                    'estimated_days': '2-3',
                    'rate': 99.0,
                    'total_charge': 99.0
                }
            ]
            
            return JsonResponse({
                'success': True,
                'rates': fallback_rates,
                'note': 'Using standard rates',
                'pickup_pincode': pickup_pincode
            })
            
    except Exception as e:
        logger.error(f"Shipping calculation error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to calculate shipping rates'
        })

def get_order_tracking(request, order_id):
    """Get tracking information for an order"""
    try:
        order = Order.objects.get(id=order_id)
        
        if not order.shiprocket_order_id:
            return JsonResponse({
                'success': False,
                'error': 'Order not yet shipped'
            })
        
        shiprocket = ShiprocketAPI()
        success, tracking_data = shiprocket.track_order(order.shiprocket_order_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'tracking_data': tracking_data
            })
        else:
            return JsonResponse({
                'success': False,
                'error': tracking_data
            })
            
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order not found'
        })
    except Exception as e:
        logger.error(f"Order tracking error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to fetch tracking information'
        })