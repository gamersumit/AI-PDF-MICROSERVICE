import os
import json
import firebase_admin
from firebase_admin import credentials, storage
from google.cloud import storage as gcs

# Load service account certificate
cred_path = os.getenv('CERTIFICATE_PATH')
cred = credentials.Certificate(cred_path)

# Check if the default app is already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.getenv("STORAGE_BUCKET")
    })

# Initialize Google Cloud Storage client with the same credentials
gcs_client = gcs.Client.from_service_account_json(cred_path)

def set_cors(bucket_name):
    """Set CORS policy for the given bucket."""
    bucket = gcs_client.bucket(bucket_name)
    cors_configuration = [
        {
            "origin": ["*"],
            "responseHeader": ["Content-Type"],
            "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
            "maxAgeSeconds": 3600
        }
    ]
    bucket.cors = cors_configuration
    bucket.update()

print("here")
bucket_name = os.getenv("STORAGE_BUCKET", "ai-book-428212.appspot.com")
set_cors(bucket_name)
print("done")
