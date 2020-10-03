# Guya.moe
Generalized manga reading framework. Adapted for Kaguya-sama manga, but can be used generically for any and all manga.

Testing Supported By<br/>
<img width="160" src="http://foundation.zurb.com/sites/docs/assets/img/logos/browser-stack.svg" alt="BrowserStack"/>

⚠ **Note:** The install instructions below will not result in a general purpose CMS due to the amount of hardcoded assets in Guyamoe.

## Prerequisites 
- git
- python 3.6.5+
- pip
- virtualenv

## Install
1. Create a venv for Guyamoe in your home directory.
```
virtualenv ~/guyamoe
```

2. Clone Guyamoe's source code into the venv.
```
git clone https://github.com/appu1232/guyamoe ~/guyamoe/app
```

3. Activate the venv.
```
cd ~/guyamoe/app && source ../bin/activate
```

4. Install Guyamoe's dependencies.
```
pip3 install -r requirements.txt
```

5. Change the value of the `SECRET_KEY` variable to a randomly generated string.
```
sed -i "s|\"o kawaii koto\"|\"$(openssl rand -base64 32)\"|" guyamoe/settings/base.py
```

6. Generate the default assets for Guyamoe.
```
python3 init.py
```

7. Create an admin user for Guyamoe.
```
python3 manage.py createsuperuser
```

Before starting the server, create a `media` folder in the base directory. Add manga with the corresponding chapters and page images. Structure it like so:
```
media
└───manga
    └───<series-slug-name>
        └───001
            ├───001.jpg
            ├───002.jpg
            └───...
```
E.g. `Kaguya-Wants-To-Be-Confessed-To` for `<series-slug-name>`. 

**Note:** Zero pad chapter folder numbers like so: `001` for the Kaguya series (this is how the fixtures data for the series has it). It doesn't matter for pages though nor does it have to be .jpg. Only thing required for pages is that the ordering can be known from a simple numerical/alphabetical sort on the directory.

## Start the server
-  `python3 manage.py runserver` - keep this console active

Now the site should be accessible on localhost:8000

## Other info
Relevant URLs (as of now): 

- `/` - home page
- `/about` - about page
- `/admin` - admin view (login with created user above)
- `/admin_home` - admin endpoint for clearing the site's cache
- `/reader/series/<series_slug_name>` - series info and all chapter links
- `/reader/series/<series_slug_name>/<chapter_number>/<page_number>` - url scheme for reader opened on specfied page of chapter of series.
- `/api/series/<series_slug_name>` - all series data requested by reader frontend
- `/media/manga/<series_slug_name>/<chapter_number>/<page_file_name>` - url scheme to used by reader to actual page as an image.
