import airbnb
from typing import Mapping
from libreproperty import models


class Listing:
    def __init__(self, title: str, description: str, photos: list[Mapping[str, str]],
                 amenities: list[Mapping[str, str]]):
        self.description = description
        self.photos = photos
        self.title = title
        self.amenities = amenities

    def __str__(self):
        return f"Listing <{self.__dict__}>"

    def create_lp_listing(self) -> models.Listing:
        lp_listing = models.Listing()
        lp_listing.description = self.description
        lp_listing.title = self.title
        return lp_listing

    @classmethod
    def load(cls, listing_id: int) -> 'Listing':
        api = airbnb.Api(randomize=True)
        api.get_listing_details(listing_id)
        result = api.get_listing_details(listing_id)
        description = result["pdp_listing_detail"].get("sectioned_description", "")
        photos = result["pdp_listing_detail"].get("photos", [])
        title = result["pdp_listing_detail"].get("p3_summary_title", "")
        amenities = result["pdp_listing_detail"].get("listing_amenities", [])
        return cls(title=title, description=description, photos=photos, amenities=amenities)
