import json
import hashlib
import hmac
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Payment
from workspaces.models import Booking

# --- 1. INITIALIZE PAYMENT (Called by Frontend) ---
@require_POST
def initialize_payment(request):
    """
    Called by the frontend to initialize a Paystack transaction.
    Returns the authorization_url and reference.
    """
    try:
        data = json.loads(request.body)
        booking_reference = data.get('reference')
        amount = data.get('amount') # Amount in Naira (e.g., 5000)
        email = data.get('email')

        if not all([booking_reference, amount, email]):
            return JsonResponse({"error": "Missing reference, amount, or email."}, status=400)

        # Paystack expects amount in kobo (multiply Naira by 100)
        amount_in_kobo = int(float(amount) * 100)

        # Call Paystack API
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": amount_in_kobo,
            "reference": booking_reference,
            # "callback_url": "https://your-frontend-url.com/payment-success" 
        }

        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        if response_data.get('status'):
            return JsonResponse({
                "status": "success",
                "authorization_url": response_data['data']['authorization_url'],
                "reference": response_data['data']['reference'],
                "access_code": response_data['data']['access_code']
            }, status=200)
        else:
            return JsonResponse({"error": response_data.get('message', 'Failed to initialize payment')}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --- 2. SECURE WEBHOOK (Called by Paystack) ---
@csrf_exempt
@require_POST
def paystack_webhook(request):
    """
    Secure endpoint to receive payment status updates from Paystack.
    Verifies the signature to ensure the request is genuinely from Paystack.
    """
    # 1. Verify the signature
    signature = request.headers.get('x-paystack-signature')
    if not signature:
        return JsonResponse({"error": "Missing signature"}, status=400)
    
    body = request.body
    hash_digest = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        body,
        hashlib.sha512
    ).hexdigest()
    
    if hash_digest != signature:
        return JsonResponse({"error": "Invalid signature"}, status=401)

    # 2. Process the payload
    try:
        payload = json.loads(body)
        event = payload.get('event')
        
        if event == 'charge.success':
            data = payload.get('data', {})
            reference = data.get('reference')
            amount = data.get('amount') / 100  # Convert kobo to Naira
            
            try:
                # Find the associated Booking
                booking = Booking.objects.get(reference=reference)
                
                # Find or Create the Payment record
                payment, created = Payment.objects.get_or_create(
                    transaction_id=reference,
                    defaults={
                        'amount': amount,
                        'status': 'SUCCESS',
                        'gateway': 'PAYSTACK',
                        'booking': booking,
                        'gateway_response': data # Store as JSON/dict
                    }
                )
                
                if not created:
                    payment.status = 'SUCCESS'
                    payment.save()

                # Activate the booking if it's still pending
                if booking.status == 'PENDING':
                    booking.activate()
                    return JsonResponse({"message": "Booking activated successfully."}, status=200)
                else:
                    return JsonResponse({"message": "Booking already processed."}, status=200)
                    
            except Booking.DoesNotExist:
                return JsonResponse({"error": "Booking not found for this reference."}, status=404)

        return JsonResponse({"message": "Event ignored."}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)