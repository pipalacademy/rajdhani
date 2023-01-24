"""Email notifications on bookings.
"""
from . import config

def send_booking_confirmation_email(booking):
    """Sends a confirmation email on successful booking.

    The argument `booking` is a row in the database as a dict that contains the
    following fields:

        id, passenger_name, passenger_email, train_number, train_name,
        ticket_class, date
    """
    # The smtp configuration is available in the config module
    pass
