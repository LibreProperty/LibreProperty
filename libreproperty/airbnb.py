import airbnb
from typing import Mapping
from dataclasses import dataclass

from libreproperty import models


@dataclass
class Listing:
    title: str
    description: str
    photos: list[Mapping[str, str]]
    amenities: list[Mapping[str, str]]
    accommodates: int
    city: str
    min_nights: int

    def __str__(self):
        return f"Listing <{self.__dict__}>"

    def create_lp_listing(self) -> models.Listing:
        lp_listing = models.Listing()
        for attribute in dir(self):
            if not attribute.startswith("_") and attribute != "photos":
                setattr(lp_listing, attribute, getattr(self, attribute))

        return lp_listing

    @classmethod
    def load(cls, listing_id: int) -> 'Listing':
        api = airbnb.Api(randomize=True)
        api.get_listing_details(listing_id)
        result = api.get_listing_details(listing_id)
        description = result["pdp_listing_detail"].get("sectioned_description", {}).get("description", "")
        photos = result["pdp_listing_detail"].get("photos", [])
        title = result["pdp_listing_detail"].get("p3_summary_title", "")
        amenities = result["pdp_listing_detail"].get("listing_amenities", [])
        city = result["pdp_listing_detail"].get("localized_city", "")
        min_nights = result["pdp_listing_detail"].get("min_nights", 0)
        # property_type = result["pdp_listing_detail"].get("room_and_property_type", "")
        # room_type_category = result["pdp_listing_detail"].get("room_type_category", "")
        # host_about = result["pdp_listing_detail"].get("primary_host", {}).get("about", "")
        person_capacity = result["pdp_listing_detail"].get("person_capacity", 0)
        # bed_label = result["pdp_listing_detail"].get("bed_label", "2 beds")
        # bath_label = result["pdp_listing_detail"].get("bath_label", "1 bath")
        return cls(title=title, description=description, amenities=amenities, photos=photos,
                   min_nights=min_nights, accommodates=person_capacity, city=city)
