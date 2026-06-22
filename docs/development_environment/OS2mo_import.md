## Setting up OS2mo-importjob

OSdatascanner's development environment incorporates OS2mo organisational import
functionality. To test functionality, it is required to clone the Git-repository.

1. Clone the repo and start the OS2mo-project
    ```
    git clone https://github.com/OS2mo/os2mo.git
    cd os2mo
    ```

2. Add a docker-compose.override.yml file in the root of the OS2mo project, and add the code: 
    
    ```
       services:
           mo:
             environment:
               OS2MO_AUTH: "false"
    ```
   
   This allows you to access localhost:5001, using the user admin/admin. 
    
3. Run the container with:
    ```
    docker compose up --build
    ```

4. Go to http://localhost:5000/auth/admin/master/console/#/mo/clients
5. Enter username and password "admin"
6. Select the client "dipex"
7. Go to tab "Credentials"
8. Copy the "Secret". You can regenerate a new secret here as well
9. Open the dev-settings.toml file in the OSdatascanner-project and scroll down to "[os2mo]"  
10. Change OS2MO_CLIENT_ID to "dipex" and OS2MO _CLIENT_SECRET to the secret
11. Start the OSdatascanner-project. Use the "--build" flag to let the updated 
dev-settings.toml-file take effect.
    ```
    docker compose up --build
    ```

12. Go to http://localhost:8020/admin/core/client/
13. Change your "client"-object in the Django-admin page to both allow "support of 
structured organizations" and "importservice (OS2mo)"

You can now perform an OS2mo-import from the organizations-page, http://localhost:8020/organizations/.

!!! note
    If you would like to run a larger fixture than the default "Kolding kommune"-fixture, 
    start by emptying the databases in both containers with the command:

    `docker compose down -v --remove-orphans`

Repeat previous command on both containers until you no longer receive errors on either of the projects, like:

    error while removing network: network os2mo_default id <id> has active endpoints

When you get this warning, the database is empty:

    WARNING: Network os2mo_default not found.

Then build both containers again, but build the OS2mo-container with the command:

    FIXTURE=aalborg docker compose up --build