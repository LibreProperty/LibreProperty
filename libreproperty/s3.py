import boto3
from flask import current_app


def get_s3_client() -> boto3.session.Session.client:
    if current_app.config.get("S3_ENDPOINT").lower() == "aws":
        return boto3.client('s3')
    return boto3.client(
        "s3",
        endpoint_url=current_app.config.get("S3_ENDPOINT"),
        config=boto3.session.Config(signature_version='s3v4'),
        aws_session_token=None,
        verify=current_app.config.get("S3_VERIFY")
    )
