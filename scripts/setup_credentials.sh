#!/bin/bash
#
# setup.env.sh
# The purpose of this script is to setup sample environment variables for this project. It is up to the responsibility of the developer to change these values once they are generated for production use.
#

# Step 1: Clear the file.
clear;
cat > nwapp/nwapp/.env << EOL
#--------#
# Django #
#--------#
SECRET_KEY=<YOU_NEED_TO_SET>
DEBUG=True
ALLOWED_HOSTS='*'
ADMIN_NAME='Bartlomiej Mika'
ADMIN_EMAIL=bart@mikasoftware.com

#----------#
# Database #
#----------#
DATABASE_URL=postgis://django:123password@localhost:5432/nwapp_db
DB_NAME=nwapp_db
DB_USER=django
DB_PASSWORD=123password
DB_HOST=localhost
DB_PORT="5432"

#-------#
# Email #
#-------#
DEFAULT_TO_EMAIL=bart@mikasoftware.com
DEFAULT_FROM_EMAIL=do-not-reply@mg.nwapp.com

# PRODUCTION
#EMAIL_BACKEND=anymail.backends.mailgun.EmailBackend
MAILGUN_ACCESS_KEY=<YOU_NEED_TO_SET>
MAILGUN_SERVER_NAME=mg.nwapp.com

# DEVELOPER
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

#--------#
# STRIPE #
#--------#
DJSTRIPE_WEBHOOK_SECRET=<YOU_NEED_TO_SET>
STRIPE_LIVE_PUBLIC_KEY=<YOU_NEED_TO_SET>
STRIPE_LIVE_SECRET_KEY=<YOU_NEED_TO_SET>
STRIPE_TEST_PUBLIC_KEY=<YOU_NEED_TO_SET>
STRIPE_TEST_SECRET_KEY=<YOU_NEED_TO_SET>
STRIPE_LIVE_MODE=0
STRIPE_PRODUCT=<YOU_NEED_TO_SET>
STRIPE_MONTHLY_PLAN_ID=<YOU_NEED_TO_SET>
STRIPE_MONTHLY_PLAN_AMOUNT=5.0
STRIPE_MONTHLY_PLAN_CURRENCY=CAD

#--------#
# AWS S3 #
#--------#
AWS_S3_HOST=s3.ca-central-1.amazonaws.com
AWS_ACCESS_KEY_ID=<YOU_NEED_TO_SET>
AWS_SECRET_ACCESS_KEY=<YOU_NEED_TO_SET>
AWS_STORAGE_BUCKET_NAME=nwapp
AWS_S3_REGION_NAME=nyc3
AWS_S3_ENDPOINT_URL=https://nwapp.nyc3.digitaloceanspaces.com

#-------------#
# SOCIAL-AUTH #
#-------------#
SOCIAL_AUTH_GITHUB_KEY=<YOU_NEED_TO_SET>
SOCIAL_AUTH_GITHUB_SECRET=<YOU_NEED_TO_SET>
SOCIAL_AUTH_FACEBOOK_KEY=<YOU_NEED_TO_SET>
SOCIAL_AUTH_FACEBOOK_SECRET=<YOU_NEED_TO_SET>
SOCIAL_AUTH_TWITTER_KEY=<YOU_NEED_TO_SET>
SOCIAL_AUTH_TWITTER_SECRET=<YOU_NEED_TO_SET>


#--------------------------------#
# Application Specific Variables #
#--------------------------------#
nwapp_LOGLEVEL=INFO
nwapp_DJANGO_STATIC_HOST="localhost:8000"
nwapp_BACKEND_HTTP_PROTOCOL=http://
nwapp_BACKEND_HTTP_DOMAIN=localhost:8000
nwapp_BACKEND_DEFAULT_MONEY_CURRENCY=CAD
nwapp_RESOURCE_SERVER_NAME='Resource Server Authorization'
nwapp_RESOURCE_SERVER_INTROSPECTION_URL=http://localhost:8000/api/introspect
nwapp_RESOURCE_SERVER_INTROSPECTION_TOKEN=<YOU_NEED_TO_SET>
nwapp_FRONTEND_HTTP_PROTOCOL=http://
nwapp_FRONTEND_HTTP_DOMAIN=localhost:3000
EOL

# Developers Note:
# (1) Useful article about setting up environment variables with travis:
#     https://stackoverflow.com/a/44850245
