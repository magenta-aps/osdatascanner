#!/bin/bash
echo "Giving write permissions to migration folders..."
sudo chmod -R o+w src/os2datascanner/projects/*/*/migrations/
echo "Done"
echo "Giving write permissions to locale folders..."
sudo chmod -R o+w src/os2datascanner/projects/*/locale/
echo "Done"
echo "Giving write permissions to template folders..."
sudo chmod -R o+w src/os2datascanner/projects/*/*/templates/
echo "Done"
echo "Giving write permissions to media folders..."
sudo chmod -R o+w src/os2datascanner/projects/*/media/
echo "Done"
