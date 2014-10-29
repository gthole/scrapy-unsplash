Scrapy Unsplash
===============
Download images from unsplash at a fixed width


## Setup

```bash
# Install pip and virtualenv if you haven't already
$ sudo easy_install pip
$ sudo pip install virtualenv

# Clone this repository and cd into it
$ git clone https://github.com/gthole/scrapy-unsplash
$ cd scrapy-unsplash

# Install dependencies
$ virtualenv venv
$ venv/bin/pip install -r requirements.txt
```


## Run

```bash
# Download images to images/ dir
$ venv/bin/python unsplash.py
```

Or you can override settings by feeding a settings module to scrapy

```bash
$ echo "BASE_WIDTH=320" > settings.py
$ export SCRAPY_SETTINGS_MODULE=settings
$ venv/bin/python unsplash.py
```


## Relevant Settings

- `BASE_WIDTH`: The fixed width to resize images to while preserving aspect ratio.
- `ITEM_PIPELINES`: Is set by default to the `UnsplashPipeline`, but can be overriden to the regular `ImagesPipeline` and used as described in the [Scrapy docs](http://doc.scrapy.org/en/latest/topics/images.html)
- `IMAGES_STORE`: Directory, or S3 uri to persist images in.

You can also apply any normal [Scrapy settings](http://doc.scrapy.org/en/latest/topics/settings.html)
