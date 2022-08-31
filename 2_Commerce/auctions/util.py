from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest

from .models import Auction_Listing


def get_current_bid(auction):
    try:
       current_bid = auction.bids.get(highest=True)
    except ObjectDoesNotExist:
        current_bid = -1
    return current_bid 

def get_auction(auction_id):
    try:
        auction = Auction_Listing.objects.get(pk=auction_id)
    except KeyError:
        return HttpResponseBadRequest("Bad Request: auction is not available")
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Bad Request: auction does not exist")
    return auction