from libreproperty.airbnb import Listing


def test_load_listing_and_create_lp_listing():
    listing = Listing.load(28583591)
    assert len(listing.title) > 0
    assert len(listing.description) > 0
    assert len(listing.photos) > 0
    assert len(listing.amenities) > 0

    lp_listing = listing.create_lp_listing()
    assert len(lp_listing.title) > 0
