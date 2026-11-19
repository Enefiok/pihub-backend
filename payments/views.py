import json
import hashlib
import hmac
import logging
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Payment
from workspaces.models import Booking
from referrals.models import CourseRegistration
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def initialize_payment(request):
    try:
        data = json.loads(request.body)
        booking_reference = data.get('reference')
        email = data.get('email')

        if not all([booking_reference, email]):
            return JsonResponse({"error": "Missing reference or email."}, status=400)

        try:
            booking = Booking.objects.get(reference=booking_reference)
            amount = float(booking.workspace_plan.price)
        except Booking.DoesNotExist:
            return JsonResponse({"error": "Booking not found for this reference."}, status=404)

        amount_in_kobo = int(amount * 100)
        url = "https://api.paystack.co/transaction/initialize"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}
        payload = {"email": email, "amount": amount_in_kobo, "reference": booking_reference}

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
        logger.error(f"❌ Payment initialization error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    signature = request.headers.get('x-paystack-signature')
    if not signature:
        return JsonResponse({"error": "Missing signature"}, status=400)
    
    body = request.body
    hash_digest = hmac.new(settings.PAYSTACK_SECRET_KEY.encode('utf-8'), body, hashlib.sha512).hexdigest()
    
    if not hmac.compare_digest(hash_digest, signature):
        return JsonResponse({"error": "Invalid signature"}, status=401)

    try:
        payload = json.loads(body)
        event = payload.get('event')
        
        if event == 'charge.success':
            data = payload.get('data', {})
            reference = data.get('reference')
            amount = data.get('amount', 0) / 100
            
            try:
                booking = Booking.objects.get(reference=reference)
                payment, created = Payment.objects.get_or_create(
                    transaction_id=reference,
                    defaults={'amount': amount, 'status': 'SUCCESS', 'gateway': 'PAYSTACK', 'booking': booking, 'gateway_response': data}
                )
                if not created:
                    payment.status = 'SUCCESS'
                    payment.save()
                if booking.status == 'PENDING':
                    booking.activate()
                return JsonResponse({"message": "Booking activated successfully."}, status=200)
                    
            except Booking.DoesNotExist:
                try:
                    payment = Payment.objects.get(transaction_id=reference, course_registration_record__isnull=False)
                    registration = payment.course_registration_record
                    
                    payment.status = 'SUCCESS'
                    payment.gateway_response = data
                    payment.save()
                    
                    # This now handles Student creation, status update, and sending the email
                    registration.mark_as_paid(payment)
                    
                    return JsonResponse({"message": "Course registration paid successfully."}, status=200)
                
                except Payment.DoesNotExist:
                    logger.error(f"❌ Payment/Registration record not found for reference: {reference}")
                    return JsonResponse({"error": "Payment record not found for this reference."}, status=404)

        return JsonResponse({"message": "Event ignored."}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all().select_related('booking', 'customer').order_by('-created_at')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]