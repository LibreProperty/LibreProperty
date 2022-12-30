from libreproperty.models import Photo
from libreproperty.auth.models import User


def test_photo_bucket_key():
    photo = Photo()
    photo.location = "s3://mybucket-1/my-key-1"
    assert photo.bucket == "mybucket-1"
    assert photo.object_key == "my-key-1"
