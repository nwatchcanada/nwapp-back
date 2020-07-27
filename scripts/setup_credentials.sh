#!/bin/bash
#
# setup.env.sh
# The purpose of this script is to setup sample environment variables for this project. It is up to the responsibility of the developer to change these values once they are generated for production use.
#

# Step 1: Clear the file.
clear;
cat > ../nwapp/nwapp/.env << EOL
#--------#
# Django #
#--------#
SECRET_KEY=<PLEASE-SET-THIS-VALUE>
DEBUG=True
ALLOWED_HOSTS='*'
ADMIN_NAME='Bartlomiej Mika'
ADMIN_EMAIL=bart@mikasoftware.com

#----------#
# Database #
#----------#
DATABASE_URL=postgis://vagrant:123password@localhost:5432/nwapp_db
DB_NAME=nwapp_db
DB_USER=vagrant
DB_PASSWORD=123password
DB_HOST=localhost
DB_PORT="5432"

#-------#
# Email #
#-------#
DEFAULT_TO_EMAIL=bart@mikasoftware.com
DEFAULT_FROM_EMAIL=do-not-reply@mg.nwapp.ca

# PRODUCTION
#EMAIL_BACKEND=anymail.backends.mailgun.EmailBackend
MAILGUN_ACCESS_KEY=<PLEASE-SET-VALUE>
MAILGUN_SERVER_NAME=mg.nwapp.ca

# DEVELOPER
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

#-----------------#
# DIGITALOCEAN S3 #
#-----------------#
AWS_ACCESS_KEY_ID=<PLEASE-SET-THIS-VALUE>
AWS_SECRET_ACCESS_KEY=<PLEASE-SET-THIS-VALUE>
AWS_STORAGE_BUCKET_NAME=<PLEASE-SET-THIS-VALUE>
AWS_S3_REGION_NAME=<PLEASE-SET-THIS-VALUE>
AWS_S3_ENDPOINT_URL=<PLEASE-SET-THIS-VALUE>

#----------------#
# GOOGLE MAP API #
#----------------#
GOOGLE_MAP_API_KEY=<PLEASE-SET-THIS-VALUE>

#--------------------------------#
# Application Specific Variables #
#--------------------------------#
NWAPP_LOGLEVEL=INFO
NWAPP_BACKEND_HTTP_PROTOCOL=http://
NWAPP_BACKEND_HTTP_DOMAIN=localhost
NWAPPY_APP_DEFAULT_MONEY_CURRENCY=CAD
NWAPPY_GITHUB_WEBHOOK_SECRET=<PLEASE-SET-THIS-VALUE>
NWAPPY_INVOICEBUILDER_MICROSERVICE_ADDRESS_AND_PORT=localhost:50051
NWAPP_RESOURCE_SERVER_NAME="API Web-Service"
EOL

# Developers Note:
# (1) Useful article about setting up environment variables with travis:
#     https://stackoverflow.com/a/44850245
