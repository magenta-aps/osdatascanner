# Grants

Grants are used to store information used to access external systems such as usernames and passwords, API keys and similar.

The admin module uses grants primarily for accessing sources targeted for a scan, while the report module uses grants for deleting sources in external systems through the user interface.

Both the admin module and the report module employ four different grant types: SMBGrant, EWSGrant, GraphGrant, and GoogleApiGrant. All descend from the common Grant parent model class. In the admin module, each grant is related to a GrantExtra model object, which contains information only relevant in the admin module.

## Grant

The base `Grant` model class contains a UUID, a reference to an Organization model object, and a "last_updated" timestamp.

## SMBGrant

This grant is used to communicate with Windows servers (or any compatible server) using the [SMB protocol][1].

The object stores a username, a password and a domain. The password field [is encrypted using AES encryption][2].

## EWSGrant

This grant is used to communicate with Microsoft Exchange mail servers using the [EWS API][3].

The object stores a username and a password. The password field [is encrypted using AES encryption][2].

## GraphGrant

This grant is used to communicate with various Microsoft platform services through the unified [MSGraph API][4].

The object stores the application ID, the tenant ID, and a client secret value from a Microsoft Azure Application. The client secret field [is encrypted using AES encryption][2].

In addition, the object can store the expiry date of the client secret.

## GoogleApiGrant

This grant is used to communicate with various Google services through the [Google API][5].

The object stores a google service account as JSON. The service account field [is encrypted using AES encryption][2].

## GrantExtra

This model class exists only in the admin module, is connected to another grant (the base Grant model class) through a one-to-one relation, and contains a boolean value in the `should_broadcast` field. When this value is `True`, changes made to the related Grant (and subclass model object) in the admin module will be propagated to the report module; when it becomes `False`, the related Grant (and subclass model object) will be removed from the report module.

In the user interface in the admin module, the fields from the GrantExtra model object is included in the form for editing the related Grant model object.

When a Grant model object is created in the admin module, a related GrantExtra model object is also created. If no value for the `should_broadcast` field is given during creation (through the UI for example) the default value is `False`.

## Synchronization

Grant model objects (and subclass model objects) are defined identically in the admin and report module. The synchronization between the two module is executed by broadcasting messages through RabbitMQ from the admin module to the report module through the [event_collector][6].

All encrypted field values on the grant model objects remain encrypted during transfer through RabbitMQ and the event_collector, and are not decrypted at any point in the process. This works only if the master decryption hex in both modules are the same.


[1]: https://en.wikipedia.org/wiki/Server_Message_Block

[2]: architecture/security.md#security

[3]: https://learn.microsoft.com/en-us/exchange/client-developer/exchange-web-services/ews-applications-and-the-exchange-architecture

[4]: https://learn.microsoft.com/en-us/graph/overview

[5]: https://developers.google.com/apis-explorer

[6]: architecture/pipeline.md#event-collector
