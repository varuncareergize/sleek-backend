import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Car, Booking
from .serializers import CarSerializer, BookingSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

# ponytail: AED is a 2-decimal currency on Stripe -> amount in fils (AED 1.00 = 100).
AED_MIN_FILS = 200  # Stripe's minimum charge for AED is 2.00
logger = logging.getLogger(__name__)


# =========================
# CAR LIST + CREATE
# =========================

class CarListCreateAPIView(APIView):

    def get(self, request):

        cars = Car.objects.all()

        serializer = CarSerializer(cars, many=True)

        return Response(serializer.data)

    def post(self, request):

        serializer = CarSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================
# CAR DETAIL
# =========================

class CarDetailAPIView(APIView):

    def get_object(self, pk):

        try:
            return Car.objects.get(pk=pk)

        except Car.DoesNotExist:
            return None

    def get(self, request, pk):

        car = self.get_object(pk)

        if not car:

            return Response(
                {"error": "Car not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CarSerializer(car)

        return Response(serializer.data)

    def put(self, request, pk):

        car = self.get_object(pk)

        if not car:

            return Response(
                {"error": "Car not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CarSerializer(
            car,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):

        car = self.get_object(pk)

        if not car:

            return Response(
                {"error": "Car not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CarSerializer(
            car,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):

        car = self.get_object(pk)

        if not car:

            return Response(
                {"error": "Car not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        car.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# =========================
# BOOKING LIST + CREATE
# =========================

class BookingListCreateAPIView(APIView):

    def get(self, request):

        bookings = Booking.objects.all().order_by('-created_at')

        serializer = BookingSerializer(
            bookings,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = BookingSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        booking = serializer.save()  # status defaults to 'pending'

        # Pay Later: no charge, booking is just a reservation request.
        if not serializer.validated_data.get('pay_now'):
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Pay Now: spin up a Stripe Checkout Session for the pre-book amount.
        if not settings.STRIPE_SECRET_KEY:
            booking.delete()
            return Response(
                {'detail': 'Online payments are not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        amount_fils = int(booking.total_price * 100)
        if amount_fils < AED_MIN_FILS:
            booking.delete()
            return Response(
                {'detail': f'Minimum online payment is AED {AED_MIN_FILS / 100:.2f}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = stripe.checkout.Session.create(
                mode='payment',
                line_items=[{
                    'quantity': 1,
                    'price_data': {
                        'currency': 'aed',
                        'unit_amount': amount_fils,
                        'product_data': {
                            'name': f'{booking.car.brand} {booking.car.name} — Pre-book',
                        },
                    },
                }],
                customer_email=booking.email,
                metadata={'booking_id': str(booking.id)},
                success_url=f'{settings.FRONTEND_URL}/booking/result?status=success',
                cancel_url=f'{settings.FRONTEND_URL}/booking/result?status=cancel',
            )
        except stripe.error.StripeError as exc:
            booking.delete()  # no charge happened; don't leave an orphaned pending row
            logger.warning('Stripe Checkout creation failed: %s', exc)
            return Response(
                {'detail': 'Could not start payment. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {'checkout_url': session.url},
            status=status.HTTP_201_CREATED,
        )


# =========================
# BOOKING DETAIL
# =========================

class BookingDetailAPIView(APIView):

    def get_object(self, pk):

        try:
            return Booking.objects.get(pk=pk)

        except Booking.DoesNotExist:
            return None

    def get(self, request, pk):

        booking = self.get_object(pk)

        if not booking:

            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookingSerializer(booking)

        return Response(serializer.data)

    def put(self, request, pk):

        booking = self.get_object(pk)

        if not booking:

            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookingSerializer(
            booking,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):

        booking = self.get_object(pk)

        if not booking:

            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookingSerializer(
            booking,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):

        booking = self.get_object(pk)

        if not booking:

            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        booking.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# =========================
# STRIPE WEBHOOK
# Plain Django view (not DRF): needs the raw body for signature verification,
# and no auth/CSRF. Stripe POSTs signed events here after a Checkout completes.
# =========================
@csrf_exempt
def stripe_webhook(request):

    secret = settings.STRIPE_WEBHOOK_SECRET
    if not secret:
        # ponytail: no-op until configured; return 200 so Stripe stops retrying.
        return HttpResponse('webhook secret not configured', status=200)

    try:
        event = stripe.Webhook.construct_event(
            payload=request.body,
            sig_header=request.headers.get('stripe-signature', ''),
            secret=secret,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse('invalid payload', status=400)

    # checkout.session.completed fires once the customer has paid.
    if event['type'] == 'checkout.session.completed':
        booking_id = event['data']['object'].get('metadata', {}).get('booking_id')
        if booking_id:
            Booking.objects.filter(pk=booking_id).update(status='paid')

    return HttpResponse(status=200)