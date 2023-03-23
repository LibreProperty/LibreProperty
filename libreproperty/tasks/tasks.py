import logging
import os
import urllib
from random import choice
from string import ascii_lowercase
from typing import Mapping

from huey import RedisHuey
from libreproperty.db import db
from libreproperty.models import Photo
from libreproperty.s3 import get_s3_client

huey = RedisHuey(
    host=os.getenv('REDIS_HOST', "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379))
)

logger = logging.getLogger("huey")

@huey.task()
def store_airbnb_photos(listing_id: int, photos: list[Mapping[str, str]]):
    logger.info(f"Storing airbnb photos for listing {listing_id}")
    from libreproperty.app import create_huey_app
    app = create_huey_app()
    with app.app_context():
        s3 = get_s3_client()
        for airbnb_photo in photos:
            photo_url = airbnb_photo.get("large_cover")
            data = urllib.request.urlopen(photo_url)
            bucket = app.config.get("BUCKET")
            random_str = ''.join(choice(ascii_lowercase) for i in range(4))
            key = f'{str(listing_id)}-{random_str}-{airbnb_photo.get("id", "no-id")}'
            s3.upload_fileobj(data, bucket, key)
            location = f"s3://{bucket}/{key}"
            photo = Photo(location=location, caption=airbnb_photo.get("caption", ""), listing_id=listing_id)
            db.session.add(photo)
            logger.info(f"Added photo {location} to listing {listing_id}")
        db.session.commit()
    logger.info(f"Finished storing airbnb photos for listing {listing_id}")
