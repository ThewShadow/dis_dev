from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from main.models import Subscription
from config import settings

import logging

logger = logging.getLogger(__name__)


