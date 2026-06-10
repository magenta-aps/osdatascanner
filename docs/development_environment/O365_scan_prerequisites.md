## Prerequisites for setting up an Office 365 scannerjob

To be able to scan files and emails from Office 365 using OSdatascanner, 
you'll need to complete the following steps:

1. Register an Azure Application:  

    Begin by registering an Azure Application in your Azure portal. This 
    application will allow OSdatascanner to retrieve data from your Office 365 
    environment.  
    
    For instructions on how to do this, look [here](../azure/azure-setup-guide.md).
    (For dev-env. purposes, there may already be one you can use, but you'll still need to find
    its Client ID and create a secret)  

2. Grant Required Permissions:  

    Once the Azure Application is registered, ensure that it has been granted 
    the necessary permissions to access Office 365 data.

3. Provide OSdatascanner with Application Details:  

    After setting up the Azure Application and assigning the required permissions, 
    you'll need to create a `GraphGrant` in OSdatascanner with the application's details.

    Open the admin module and locate the "Grants" section in the side menu.
    (`localhost:8020/organizations/grants/`) 

    Create a **`GraphGrant`** and insert the following values from your Azure Application:

    * App ID (Client ID)
    * Tenant ID
    * Client Secret
