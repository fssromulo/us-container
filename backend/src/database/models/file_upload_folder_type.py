# Python imports
from enum import Enum


class FileUploadFolderType(str, Enum):
    DL_FRONT = "dl_front"
    DL_BACK = "dl_back"
    CC_FRONT = "cc_front"
    CC_BACK = "cc_back"
    W9 = "w9"
    PRODUCT_IMAGE = "product_image"
