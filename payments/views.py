import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Payment
from workspaces.models import Booking

@csrf_exempt
@require_POST
def paystack_webhook(request):
    """
    Endpoint to receive payment status updates from Paystack.
    """
    try:
        # Parse the raw JSON body from the payment gateway
        payload = json.loads(request.body)
        
        # Paystack sends an 'event' type. We only care about successful charges.
        event = payload.get('event')
        
        if event == 'charge.success':
            data = payload.get('data', {})
            reference = data.get('reference')
            amount = data.get('amount') / 100  # Paystack sends amount in kobo/cents
            
            try:
                # 1. Find the associated Booking first (using the 'reference' field we added to Booking)
                booking = Booking.objects.get(reference=reference)
                
                # 2. Find or Create the Payment record using your model's actual field names
                payment, created = Payment.objects.get_or_create(
                    transaction_id=reference,  # <-- Changed from 'reference' to 'transaction_id'
                    defaults={
                        'amount': amount,
                        'status': 'SUCCESS',
                        'gateway': 'PAYSTACK',       # <-- Changed from 'provider' to 'gateway'
                        'booking': booking,          # <-- Link the payment to the booking
                        'gateway_response': json.dumps(data) # <-- Changed from 'metadata'
                    }
                )
                
                if not created:
                    payment.status = 'SUCCESS'
                    payment.save()

                # 3. Activate the booking if it's still pending
                if booking.status == 'PENDING':
                    booking.activate()  # This assigns the tag and updates dates!
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