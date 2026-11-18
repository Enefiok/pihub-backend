from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from accounts.permissions import IsManagementOrReadOnly
from .models import Influencer, ReferralCode, CourseRegistration
from .serializers import (
    InfluencerSerializer, ReferralCodeSerializer, 
    ReferralValidationSerializer, RegistrationAnalyticsSerializer
)
from courses.models import Course


class CodeGuessingThrottle(AnonRateThrottle):
    rate = '30/hour'  # Raised from 5/hour for shared networks/retyping


class ReferralValidateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [CodeGuessingThrottle]

    def post(self, request):
        serializer = ReferralValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated = serializer.validated_data
        return Response({
            "valid": True,
            "message": "Code is valid",
            "discount_percent": float(validated['referral_code'].discount_percent),
            "original_price": str(validated['original_price']),
            "discount_amount": str(validated['discount_amount']),
            "final_price": str(validated['final_price'])
        }, status=status.HTTP_200_OK)


class InfluencerViewSet(viewsets.ModelViewSet):
    queryset = Influencer.objects.all()
    serializer_class = InfluencerSerializer
    permission_classes = [IsManagementOrReadOnly]


class ReferralCodeViewSet(viewsets.ModelViewSet):
    queryset = ReferralCode.objects.select_related('influencer').prefetch_related('applicable_courses')
    serializer_class = ReferralCodeSerializer
    permission_classes = [IsManagementOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CourseRegistrationAdminViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationAnalyticsSerializer
    permission_classes = [IsManagementOrReadOnly]

    def get_queryset(self):
        queryset = CourseRegistration.objects.select_related(
            'course', 'referral_code', 'referral_code__influencer'
        ).order_by('-created_at')
        
        course_id = self.request.query_params.get('course')
        status_filter = self.request.query_params.get('status')
        influencer_id = self.request.query_params.get('influencer')
        search = self.request.query_params.get('search')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if influencer_id:
            queryset = queryset.filter(referral_code__influencer_id=influencer_id)
        if search:
            queryset = queryset.filter(Q(full_name__icontains=search) | Q(email__icontains=search))
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset


class RegistrationActionView(APIView):
    """Bulk actions for registrations (Admin only)"""
    permission_classes = [IsManagementOrReadOnly]

    def post(self, request):
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "ids list is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = CourseRegistration.objects.filter(id__in=ids)
        count = 0
        if action == 'mark_paid':
            for reg in queryset.filter(status='pending'):
                reg.mark_as_paid()
                count += 1
        elif action == 'mark_cancelled':
            count = queryset.update(status='cancelled')
        else:
            return Response({"error": "Invalid action. Use 'mark_paid' or 'mark_cancelled'."}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message": f"Successfully updated {count} registrations", "count": count})


class RegistrationStatusUpdateView(APIView):
    """Single registration status update (Admin only)"""
    permission_classes = [IsManagementOrReadOnly]

    def patch(self, request, pk):
        try:
            reg = CourseRegistration.objects.get(pk=pk)
        except CourseRegistration.DoesNotExist:
            return Response({"error": "Registration not found"}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if new_status not in ['pending', 'paid', 'cancelled']:
            return Response({"error": "Invalid status. Must be 'pending', 'paid', or 'cancelled'."}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status == 'paid' and reg.status == 'pending':
            reg.mark_as_paid()
        else:
            reg.status = new_status
            reg.save()
            
        return Response({"status": reg.status, "message": "Status updated successfully"})


class ReferralAnalyticsView(APIView):
    permission_classes = [IsManagementOrReadOnly]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'day') # day, week, month
        
        queryset = CourseRegistration.objects.all()
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        total_regs = queryset.count()
        paid_regs = queryset.filter(status='paid').count()
        pending_regs = queryset.filter(status='pending').count()
        cancelled_regs = queryset.filter(status='cancelled').count()
        
        revenue = queryset.filter(status='paid').aggregate(Sum('final_price'))['final_price__sum'] or 0
        total_discount = queryset.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0
        total_commission = queryset.filter(status='paid').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
        
        conversion_rate = (paid_regs / total_regs * 100) if total_regs > 0 else 0

        # Time Series
        trunc_map = {'day': TruncDay, 'week': TruncWeek, 'month': TruncMonth}
        trunc_func = trunc_map.get(group_by, TruncDay)
        time_series = queryset.annotate(date=trunc_func('created_at')).values('date').annotate(
            registrations=Count('id'),
            paid_conversions=Count('id', filter=Q(status='paid')),
            revenue=Sum('final_price', filter=Q(status='paid'))
        ).order_by('date')

        # By Influencer
        by_influencer = queryset.values('referral_code__influencer__name').annotate(
            registrations=Count('id'),
            paid_count=Count('id', filter=Q(status='paid')),
            revenue=Sum('final_price', filter=Q(status='paid')),
            discount_given=Sum('discount_amount'),
            commission_owed=Sum('commission_amount', filter=Q(status='paid'))
        ).exclude(referral_code__isnull=True).order_by('-paid_count')
        
        for item in by_influencer:
            item['conversion_rate_percent'] = round((item['paid_count'] / item['registrations'] * 100), 2) if item['registrations'] > 0 else 0

        # By Code
        by_code = queryset.values('referral_code__code').annotate(
            registrations=Count('id'),
            paid_count=Count('id', filter=Q(status='paid')),
            revenue=Sum('final_price', filter=Q(status='paid')),
            commission_owed=Sum('commission_amount', filter=Q(status='paid'))
        ).exclude(referral_code__isnull=True).order_by('-paid_count')

        # Top Courses
        top_courses = queryset.values('course__title').annotate(
            registrations=Count('id'),
            paid_count=Count('id', filter=Q(status='paid'))
        ).order_by('-paid_count')[:5]

        return Response({
            "summary": {
                "total_registrations": total_regs,
                "paid_registrations": paid_regs,
                "pending_registrations": pending_regs,
                "cancelled_registrations": cancelled_regs,
                "total_revenue": str(revenue),
                "total_discount_given": str(total_discount),
                "total_commission_owed": str(total_commission),
                "conversion_rate_percent": round(conversion_rate, 2)
            },
            "status_counts": {"paid": paid_regs, "pending": pending_regs, "cancelled": cancelled_regs},
            "time_series": list(time_series),
            "by_influencer": list(by_influencer),
            "by_code": list(by_code),
            "top_courses": list(top_courses)
        })