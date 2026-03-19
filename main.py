from flask import Flask
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename
import urllib.request
import re
from os import listdir
from os.path import isfile, join
import diffing
from pathlib import Path
from tempfile import gettempdir
from urllib.parse import urlsplit, urlunsplit

app = Flask(__name__)

_cached_values = {}

def compare_tag(tag: str) -> dict[str, dict[str, float]]:
    """
    Given a tag as an argument, this will compare all files in
    the given tags directory, and return a directory showing
    the differences between the files.
    """
    directory_path = join("files", tag)
    # List files in directory
    files = [join(directory_path, f) for f in listdir(directory_path) if isfile(join(directory_path, f))]
    # Compare files
    results = diffing.compare_all_files(files, 0)
    # Format filepaths into purely names
    formatted_results = {}
    for key, value in results.items():
        # Format subdict
        f_values = {}
        for k, v in value.items():
            new_key: str = str(k).split('/')[-1]
            f_values[new_key] = v
        # Format higher level dict
        new_key: str = str(key).split('/')[-1]
        formatted_results[new_key] = f_values

    return formatted_results

def download_link(link: str, tag: str) -> None:
    """
    Downloads the file in the given link in the directory
    specified by the tag 
    """
    directory_path = join("files", tag)
    # Parse user name from link
    user_name = re.findall('\\.com\\/(.+?)\\/', link)[0]
    # Download file at link
    file_path = join(directory_path, f'{user_name}')
    if 'raw' not in link:
        # Add ?raw=true which will automatically redirect to raw.github.com
        s = urlsplit(link)._replace(query='raw=true') # This will override existing params but that shouldn't matter
        link = urlunsplit(s)

    urllib.request.urlretrieve(link, file_path)

@app.route("/", methods = ['GET', 'POST'])
def checklink():
    global _cached_values
    tag = request.args.get('tag')
    if tag == None:
        return 'Missing tag from url'
    if request.method == 'POST':
        # Get form data
        data = request.form
        # Check if request has file with links, or a single link directly
        if 'link' in data and data['link'] != "":
            link = data['link']
            try:
                download_link(link, tag)
            except:
                return 'Unable to download file from url'
        elif 'links' in request.files:
            # Save file temporarily
            tmp_path = join(gettempdir(), 'links.txt')
            file = request.files['links']
            file.save(tmp_path)
            # Read
            try:
                with open(tmp_path, "r") as file:
                    links = file.read().splitlines()
                    for link in links:
                        download_link(link, tag)
            except:
                return 'Unable to download file from url'
        # Compare since new files
        _cached_values[tag] = compare_tag(tag)
    # If cache empty, compare
    if tag not in _cached_values:
        _cached_values[tag] = compare_tag(tag)
    # Print results
    return render_template('index.html',
                           tag=tag,
                           results=_cached_values[tag])
