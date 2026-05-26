from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Car, Booking
from .serializers import CarSerializer, BookingSerializer


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

        serializer = BookingSerializer(
            data=request.data
        )

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