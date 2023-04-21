'''
Library of useful functions for working with images.
'''

import requests
import ctypes

def main():
    # TODO: Add code to test the functions in this module
    return

def download_image(image_url):
    """Downloads an image from a specified URL.
    DOES NOT SAVE THE IMAGE FILE TO DISK.
    Args:
        image_url (str): URL of image
    Returns:
        bytes: Binary image data, if succcessful. None, if unsuccessful.
    """
    
    req = requests.get(image_url)
    
    if req.ok:
        return req.content
    else:
        return None
    

def save_image_file(image_data, image_path):
    """Saves image data as a file on disk.
    
    DOES NOT DOWNLOAD THE IMAGE.
    Args:
        image_data (bytes): Binary image data
        image_path (str): Path to save image file
    Returns:
        bytes: True, if succcessful. False, if unsuccessful
    """