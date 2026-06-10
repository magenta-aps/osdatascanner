## Missing permissions in development environment

During development, we mount our local editable files into the docker
containers which means they are owned by the local user, and **not** the user
running inside the container. Thus, any processes running inside the container,
like management commands, will not be allowed to create or update files in the
mounted locations.

In order to fix this, we need to allow "others" to write to the relevant
locations. This can be done with `chmod -R o+w <path>` (`o` is for "other
users", `+w` is to add write-permissions and `-R` is used to add the
permissions recursively down through the file structure from the location
`<path>` points to).

The above is necessary whenever a process needs write permissions, but should
always be done for the following locations:

- `src/os2datascanner/projects/*/*/migrations/`
- `src/os2datascanner/projects/*/locale/`
- `src/os2datascanner/core_organizational_structure/locale/`
- `src/os2datascanner/engine2/locale`

Depending on what you do, you may also need:

- `src/os2datascanner/projects/admin/*/templates/`
- `src/os2datascanner/projects/report/*/templates/`
- `src/os2datascanner/projects/shared/templates/`
- `src/os2datascanner/projects/report/media/*/`
- `dev-environment/uploads/`

If you want the `django-admin shell_plus` commands to record command-line
history (which you probably do in the development environment), you should also
run `chmod -R o+w` for the following locations:

- `dev-environment/admin/ipython/`
- `dev-environment/report/ipython/`

As a developer, it can be a good idea to create and store a shell script or create an alias
that performs this task for you, as it can become tedious when working with migrations and/or
translations.

**NB!** Git will only save executable permissions, which means that granting
other users write permissions on your local setup, will not compromise
production security.

For convenience, you could create a shell script to run when needed, it may look like this:

```sh
#!/bin/bash
echo "Giving write permissions to migration folders..."
sudo chmod -R o+w src/os2datascanner/projects/*/*/migrations/
echo "Giving write permissions to grants folder"
sudo chmod -R o+w src/os2datascanner/projects/grants/
echo "Giving write permissions to locale folders..."
sudo chmod -R o+w src/os2datascanner/projects/*/locale/
sudo chmod -R o+w src/os2datascanner/core_organizational_structure/locale/
sudo chmod -R o+w src/os2datascanner/engine2/locale
echo "Giving write permissions to admin project apps templates folder"
sudo chmod -R o+w src/os2datascanner/projects/admin/*/templates/
echo "Giving write permissions to report project apps templates folder"
sudo chmod -R o+w src/os2datascanner/projects/report/*/templates/
echo "Giving write permissions to shared templates folder"
sudo chmod -R o+w src/os2datascanner/projects/shared/templates/
echo "Giving write permissions to report media folder"
sudo chmod -R o+w src/os2datascanner/projects/report/media/*/
echo "Giving write permissions to uploads folder"
sudo chmod -R o+w dev-environment/uploads/
echo "Giving write permissions to ipython dirs (shell_plus history)"
sudo chmod -R o+w dev-environment/admin/ipython/
sudo chmod -R o+w dev-environment/report/ipython/
echo "Done"
```