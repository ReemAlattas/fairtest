from django.db import models

from geopy.distance import vincenty
from decimal import Decimal
from random import randint

from correlation.dummy_correlation  import Correlation

class Product(models.Model):
    """A product to be sold online

    Attributes:
        name(str):           The name of the product
        base_price(decimal): The initial price of the product, which is subject
                             to modification based on competitor locations
    """
    name = models.CharField(max_length=200)
    baseprice = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    @Correlation.input
    @Correlation.output
    #Depends on: Competitor...
    def adjust_price(self, zip_code):
        #print("my zipcode:", zip_code)
        if HasProduct.objects.filter(product__name=self.name,
                                     competitor__zip_code=zip_code):
                return self.baseprice + Decimal(1000.0)
        return self.baseprice

    def adjusted_price(self, request):
        # Get the zipcode of a random competitor
        #
        # TODO: We will fix this based on the IP of the user or the login
        #       information. For now just pick it randomly
        pos = randint(0,len(Competitor.objects.all()) - 1 )
        zip_code = Competitor.objects.all()[pos].zip_code
        return self.adjust_price(zip_code)
#        # Based on Zip
#        rate = 1.0
#        if request.GET.get('zip',''):
#            co = Zipcode.objects.filter(zip=request.GET['zip'])[0].coordinate()
#            for c in Competitor.objects.all():
#                cz = Zipcode.objects.filter(zip=str(c.zip))[0].coordinate()
#                if vincenty(co, cz).miles < 5:
#                    rate = 0.8
#                break
#        return self.baseprice * Decimal(rate)


class Competitor(models.Model):
    """A Competitor that sells similar products.

    Attributes:
        name(str):    The name of the competitor
        address(str): The address of the competitor.
        zip_code(int):The zip code of the competitor.

    """
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    zip_code = models.IntegerField(default=0)

    def __str__(self):
        return self.name + self.address


class Zipcode(models.Model):
    """A Zipcode geocoding database.

    Attributes:
        zip(str): Zipcode
        city(str): City represented by the zipcode
        state(str): State represented by the zipcode
        la(float): Latitude of the zipcode
        lo(float): Longtitude of the zipcode
    """
    zip = models.CharField(max_length=6)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=3)

    la = models.FloatField()
    lo = models.FloatField()

    def coordinate(self):
        return (self.la, self.lo)

    def __str__(self):
        return self.city + ", " + self.state + self.zip


class HasProduct(models.Model):
    """A relation that connect a Competitor with a product"""
    competitor = models.ForeignKey(Competitor)
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.competitor.name + " has " + self.product.name