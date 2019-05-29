#!/usr/bin/env bash

prod_dir=/var/www/os2datascanner
repo_dir=`cat .pwd`
install_dir=$repo_dir


function prepare_ressources()
{

\. install.sh

# Migrate
source $install_dir/python-env/bin/activate

managepy=$install_dir/webscanner_site/manage.py

python $managepy collectstatic
python $managepy makemigrations --merge
python $managepy migrate

python $managepy makemessages --ignore=scrapy-webscanner/* --ignore=python-env/*
python $managepy compilemessages

}

#
# PRODUCTION SETUP
#

function copy_to_prod_dir()
{

sudo rm --recursive $prod_dir/webscanner_site/static/ $prod_dir/python-env $prod_dir/django-os2webscanner/

sudo cp --recursive -u cron django-os2webscanner python-env scrapy-webscanner webscanner_client webscanner_site xmlrpc_clients $prod_dir
sudo cp NEWS LICENSE README VERSION $prod_dir

sudo chown --recursive www-data:www-data $prod_dir

}

function restart_ressources()
{

sudo kill `pidof python`
sudo pkill soffice.bin

sudo service datascanner-manager reload
sudo service supervisor reload
sudo service apache2 reload

}

prepare_ressources
copy_to_prod_dir
restart_ressources