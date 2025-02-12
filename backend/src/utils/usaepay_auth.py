# Python imports
import base64
import hashlib
import secrets

# Pip imports
from loguru import logger


# Function to generate a random value
def random_value():
    return secrets.token_hex(16)  # 16 bytes (32 characters) random value


# Function to calculate sha256 hash
def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


# Function to calculate base64 encode
def base64_encode(data):
    return base64.b64encode(data.encode()).decode()


# Example usage:
apikey = ""
apipin = "1993"

seed = random_value()
prehash = apikey + seed + apipin
apihash = f's2/{seed}/{sha256(prehash)}'
auth_key = base64_encode(apikey + ':' + apihash)

logger.info("Seed:", seed)
logger.info("Prehash:", prehash)
logger.info("API Hash:", apihash)
logger.info("Auth Key:", auth_key)
