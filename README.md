# awesomsfontsfoundry
 Sample implementation of the Type.World Sign-In service and font installation service through the Type.World App as a Google App Engine project

Run locally: `gunicorn -t 0 -b :8080 awesomefontsfoundry:app`
Deploy unsafely: `gcloud config configurations activate awesomefonts && gcloud app deploy --quiet`
Logs: `gcloud config configurations activate awesomefonts && gcloud app logs tail`
