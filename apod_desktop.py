""" 
COMP 593 - Final Project
Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.
Usage:
  python apod_desktop.py [apod_date]
Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import date
import hashlib
import os
import re
from apod_api import get_apod_image_url
from apod_api import get_apod_info as get_apod_info_api
import image_lib
import inspect
import sys
import sqlite3


# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path']) 

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.
    Returns:
        date: APOD date
    """
    apod_date = date.today()
    
    if len(sys.argv) == 2:
        try:
            apod_date = date.fromisoformat(sys.argv[1])
        except ValueError:
            print("Error: invalid isoformat string --> " + str(sys.argv[1]))
            sys.exit()
    
    if apod_date > date.today():
        print("Error: the date must be in the past --> " + apod_date.isoformat())
        sys.exit()
    
    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides
    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.
    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir
    global image_cache_db
    # Determine the path of the image cache directory
    image_cache_dir = os.path.join(parent_dir, "image_cache\\")
    # Create the image cache directory if it does not already exist
    if os.path.isdir(image_cache_dir) == False:
        os.mkdir(image_cache_dir)
        print("Image cache directory created: " + image_cache_dir)
    else:
        print("Image cache directory already exists: " + image_cache_dir)
        
    # Determine the path of image cache DB
    image_cache_db = os.path.join(image_cache_dir, "image_cache.db")
    
    
    # Create the DB if it does not already exist
    if os.path.exists(image_cache_db) == False:
        con = sqlite3.connect(image_cache_db)
        cur = con.cursor()
        create_apod_table_sql = """
        CREATE TABLE IF NOT EXISTS apod_image
        (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            explanation TEXT NOT NULL,
            path TEXT NOT NULL,
            sha256 TEXT NOT NULL
        );
        """
        
        cur.execute(create_apod_table_sql)
        
        con.commit()
        con.close()
        print("Image cache DB created: " + image_cache_db)
    else:
        print("Image cache DB already exists: " + image_cache_db)
    return
        

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.
    Args:
        apod_date (date): Date of the APOD image
    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    
    
    print("APOD date:", apod_date.isoformat())
    # Download the APOD information from the NASA API
    apod_info = get_apod_info_api(apod_date)
    
    # Download the APOD image
    apod_image_url = get_apod_image_url(apod_info)
    image_data = image_lib.download_image(apod_image_url)
    print("Downloaded image from " + apod_image_url)
    
    
    # Check whether the APOD already exists in the image cache
    image_hash = hashlib.sha256(image_data).hexdigest()
    print("APOD SHA-256: " + str(image_hash))
    
    apod_id = get_apod_id_from_db(image_hash)
    if  apod_id == 0:
        
        apod_image_path = determine_apod_file_path(
                apod_info['title'],
                apod_image_url
                )
        # Save the APOD file to the image cache directory
        print("APOD does not exist in cache")
        image_lib.save_image_file(image_data, apod_image_path)
        
        # Add the APOD information to the DB
        apod_id = add_apod_to_db(
            apod_info['title'],
            apod_info['explanation'],
            apod_image_path,
            image_hash
        )
        
        return apod_id
        
        
    else:
        print("APOD already exists in cache")
        return apod_id

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image
    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    
    # Check if the apod already exits in the DB as a double check
    apod_id = get_apod_id_from_db(sha256)
    if apod_id != 0:
        return apod_id
    
    # Connect tot eh sqlite DB
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    
    
    # Create the apod sql query
    add_apod_query = """
    INSERT INTO apod_image (title, explanation, path, sha256)
    VALUES (?, ?, ?, ?);
    """
    
    apod = (title, explanation, file_path, sha256)
    
    cur.execute(add_apod_query, apod)
    
    con.commit()
    con.close()
    
    
    return cur.lastrowid
    
def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.
    Args:
        image_sha256 (str): SHA-256 hash value of APOD image
    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    
    find_apod_query = """
    SELECT id FROM apod_image WHERE sha256 = ?;
    """
    cur.execute(find_apod_query, (image_sha256,))
    result = cur.fetchone()
    con.close()
    
    
    if result is not None:
        return result[0]
    
    return 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed
    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '
    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'
    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    
    image_title = image_title.strip().replace(' ', '_')
    image_title = re.sub('[^A-Za-z0-9_]+', '', image_title)
    image_title = image_title + '.' + image_url.split('.')[-1]    
    image_title =  os.path.join(image_cache_dir, image_title)
    
    return image_title

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.
    Args:
        image_id (int): ID of APOD in the DB
    Returns:
        dict: Dictionary of APOD information
    """
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    
    # TODO: Query DB for image info
    select_apod_query = """ SELECT title, explanation, path FROM apod_image WHERE id = ? """
    # Put information into a dictionary
    
    cur.execute(select_apod_query, (image_id,))
    result = cur.fetchone()
    con.close()
    
    apod_info = {
        'title': result[0], 
        'explanation': result[1],
        'file_path': result[2],
    }
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache
    Returns:
        list: Titles of all images in the cache
    """
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    
    # TODO: Query DB for image info
    select_apod_query = """ SELECT title FROM apod_image"""
    # Put information into a dictionary
    
    cur.execute(select_apod_query)
    result = cur.fetchall()
    con.close()
    
    if result is not None:
        return result
    
    return None

if __name__ == '__main__':
    main()