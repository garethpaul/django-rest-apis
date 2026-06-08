django-rest-apis
=================

Sample Django App using Twitter OAuth and REST APIs

REQUIREMENTS
============

To run this sample code, you'll need to install the following libraries:

- Python Social Auth (https://github.com/omab/python-social-auth)
- Python Twitter (https://github.com/bear/python-twitter)
- south (http://south.aeracode.org/)
- Fabric (http://www.fabfile.org/)

GETTING STARTED
============

- Create a Twitter App (https://apps.twitter.com/)
- Set a deployment-specific Django secret key before starting the app:

    export DJANGO_SECRET_KEY="$(python -c 'import base64, os; print(base64.b64encode(os.urandom(32)).decode("ascii"))')"

- For local development, enable debug explicitly when needed:

    export DJANGO_DEBUG=true

- For deployment, set the allowed hostnames:

    export DJANGO_ALLOWED_HOSTS=example.com,www.example.com

- Specify your Twitter App tokens in app/settings.py under the following section:

    SOCIAL_AUTH_TWITTER_KEY = 'YOUR_TWITTER_API_KEY'
    SOCIAL_AUTH_TWITTER_SECRET = 'YOUR_TWITTER_API_SECRET'
    
    TWITTER_ACCESS_TOKEN = 'YOUR_TWITTER_ACCESS_TOKEN'
    TWITTER_ACCESS_TOKEN_SECRET = 'YOUR_TWITTER_ACCESS_TOKEN_SECRET'

- To initialize your database, run the from the `sample-djang-app` directory:

  python manage.py syncdb

- To start the server, run the following from the `sample-djang-app` directory:

  fab start
  
- Open a browser and go to http://localhost:9000

NOTES
============
If you receive a 401 at login/twitter it is most likely caused by a datetime discrepancy between the server making the requst and the Twitter server.

Use NTP to sync time on your server to compensate for the dift.

If you are getting this error on OSX, toggle the "set time zone" checkbox off and back on in Date & Time system preferences for a manual and temporary fix. It has been reported that OSX 10.9 Mavericks has an issue with time drift.
