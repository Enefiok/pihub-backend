import random
import string
import requests
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import User
from accounts.permissions import IsCourseInstructorOrManagement, IsManagementOrReadOnly
from .models import Course, Student
from .serializers import CourseSerializer, StudentSerializer, CourseRegistrationSerializer
from referrals.models import CourseRegistration, ReferralCode, quantize_money
from payments.models import Payment


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsCourseInstructorOrManagement()]

    def get_queryset(self):
        return Course.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or user.role == User.Role.CUSTOMER:
            raise permissions.PermissionDenied("Only staff can create courses.")

        if user.role == User.Role.INSTRUCTOR and 'instructor' not in serializer.validated_data:
            serializer.save(instructor=user)
        else:
            serializer.save()


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsManagementOrReadOnly]
    queryset = Student.objects.all()


class CourseRegistrationView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CourseRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        course = data['course']
        email = data['email']
        full_name = data['full_name']
        phone = data.get('phone', '')
        payment_option = data['payment_option']
        referral_code_input = (data.get('referral_code') or '').strip().upper()

        if CourseRegistration.objects.filter(
            email=email, course=course, status=CourseRegistration.Status.PENDING
        ).exists():
            return Response(
                {"error": "A pending registration already exists for this email and course."},
                status=status.HTTP_400_BAD_REQUEST
            )

        original_price = quantize_money(course.price)
        discount_percent_applied = Decimal("0.00")
        discount_amount = Decimal("0.00")
        commission_amount = Decimal("0.00")
        referral_code_obj = None

        with transaction.atomic():
            if referral_code_input:
                try:
                    referral_code_obj = ReferralCode.objects.select_for_update().get(code=referral_code_input)
                except ReferralCode.DoesNotExist:
                    return Response({"error": "Invalid referral code."}, status=status.HTTP_400_BAD_REQUEST)

                is_valid, message = referral_code_obj.is_valid_for_course(course)
                if not is_valid:
                    return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

                discount_percent_applied = referral_code_obj.discount_percent
                commission_percent = referral_code_obj.commission_percent
                
                discount_amount = quantize_money(original_price * discount_percent_applied / Decimal("100"))
                
                # Commission base is switchable via settings.COMMISSION_ON ("final" default).
                commission_base = (original_price - discount_amount) if getattr(settings, "COMMISSION_ON", "final") == "final" else original_price
                commission_amount = quantize_money(commission_base * commission_percent / Decimal("100"))

            final_price = quantize_money(original_price - discount_amount)

            registration = CourseRegistration.objects.create(
                course=course,
                full_name=full_name,
                email=email,
                phone=phone,
                payment_option=payment_option,
                status=CourseRegistration.Status.PENDING,
                referral_code=referral_code_obj,
                original_price=original_price,
                discount_percent_applied=discount_percent_applied,
                discount_amount=discount_amount,
                final_price=final_price,
                commission_amount=commission_amount
            )

        send_mail(
            subject=f"Registration Received: {course.title}",
            message=f"Hello {full_name},\n\nYour registration for {course.title} has been received. Final Price: NGN {final_price}.\n\nWe will notify you once payment is confirmed.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        if payment_option == CourseRegistration.PaymentOption.PAY_LATER:
            send_mail(
                subject=f"New Pay-Later Registration: {course.title}",
                message=f"New registration received:\nName: {full_name}\nEmail: {email}\nCourse: {course.title}\nAmount: NGN {final_price}\n\nPlease follow up.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', 'admin@pihubng.com')],
                fail_silently=True,
            )
            return Response({
                "status": "pending",
                "message": "Registration successful. Admin will contact you for payment.",
                "registration_id": registration.id,
                "final_price": str(final_price),
                "original_price": str(original_price),
                "discount_amount": str(discount_amount)
            }, status=status.HTTP_201_CREATED)

        random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        reference = f"CRG{registration.id}{random_str}"

        Payment.objects.create(
            amount=final_price,
            currency='NGN',
            gateway=Payment.Gateway.PAYSTACK,
            status=Payment.Status.PENDING,
            transaction_id=reference,
            course_registration_record=registration
        )

        callback_url = f"{getattr(settings, 'PAYSTACK_CALLBACK_URL', 'https://pihubng.com/payment-success.html')}?reference={reference}"
        amount_in_kobo = int(quantize_money(final_price) * 100)
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": amount_in_kobo,
            "reference": reference,
            "callback_url": callback_url
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response_data.get('status'):
                return Response({
                    "status": "success",
                    "message": "Payment initialized",
                    "registration_id": registration.id,
                    "authorization_url": response_data['data']['authorization_url'],
                    "reference": response_data['data']['reference'],
                    "access_code": response_data['data']['access_code'],
                    "original_price": str(original_price),
                    "discount_amount": str(discount_amount),
                    "final_price": str(final_price)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": response_data.get('message', 'Failed to initialize payment')
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentStatusView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({"error": "Reference query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(transaction_id=reference, course_registration_record__isnull=False)
            registration = payment.course_registration_record
        except Payment.DoesNotExist:
            return Response({"error": "Registration not found for this reference."}, status=status.HTTP_404_NOT_FOUND)

        if payment.status == 'PENDING':
            url = f"https://api.paystack.co/transaction/verify/{reference}"
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            try:
                resp = requests.get(url, headers=headers)
                data = resp.json()
                if data.get('status') and data['data'].get('status') == 'success':
                    payment.status = 'SUCCESS'
                    payment.gateway_response = data['data']
                    payment.save()
                    registration.mark_as_paid(payment)
            except Exception:
                pass

        return Response({
            "reference": reference,
            "status": registration.status,
            "course_title": registration.course.title,
            "final_price": str(registration.final_price)
        })