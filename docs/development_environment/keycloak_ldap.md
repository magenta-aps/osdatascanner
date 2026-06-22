#### Keycloak instance

Interface available at `localhost:8090` on the host machine.

By default, login credentials will be `admin:admin`

The Keycloak instance is automatically configured by a mounted `realm.json` file.
This file contains configurations for a client in the "Master Realm" with appropriate permissions
to perform actions such as creation of new realms, users and user federation connections.

In `dev-settings.toml` appropriate settings for the **KEYCLOAK_BASE_URL**, **KEYCLOAK_ADMIN_CLIENT** and 
**KEYCLOAK_CLIENT_SECRET** are set.

The purpose of the Keycloak instance is to use its User Federation support. When an LDAP configuration is set in
OSdatascanner, we create a "User Federation" in Keycloak which imports data from e.g. Active Directory. 
Finally, we import this data to Django.

!!! note
    We also use Keycloak for Single Sign-On. There's more on that in the
    [Single Sign-On section](../single-sign-on.md)


#### Setting up OpenLDAP

OSdatascanner's development environment incorporates the OpenLDAP server,
which should be used to work with the system's organisational import
functionality. Setting up OpenLDAP is a little complicated, though; even though
the "L" stands for "lightweight", LDAP is an old technology that doesn't *feel*
very lightweight.

We suggest two ways of defining an organisation in OpenLDAP:

* through the _phpLDAPadmin_ frontend, also included in the development
  environment. This is a fairly self-explanatory but clunky UI for much of
  LDAP's functionality; or

* through an external LDAP client program, such as those provided by the
  Ubuntu/Debian package `ldap-utils`.

If you wish to access the phpLDAPadmin it will be accessible on the host machine at `localhost:8100`

Credentials will be `cn=admin,dc=magenta,dc=test:testMAG`


##### External LDAP clients

The development environment's OpenLDAP server is also exposed to the host
system on port 387, the usual port for LDAP servers. That means it's fairly
easy to interact with it from outside the Docker universe.

LDAP has a standard text format, known as the _LDAP Data Interchange Format_,
for representing objects in the organisational hierarchy. We can define an
organisation in this format and then give it to a tool like `ldapadd` in order
to import it into the LDAP world:

```
$ cat <<END > organisation.ldif
dn: ou=Test Department,dc=magenta,dc=test
objectClass: organizationalUnit
ou: Test Department

dn: cn=Mikkel Testsen,ou=Test Department,dc=magenta,dc=test
objectClass: inetOrgPerson
cn: Mikkel Testsen
givenName: Mikkel
sn: Testsen
mail: mt@test.example

dn: cn=Hamish MacTester,ou=Test Department,dc=magenta,dc=test
objectClass: inetOrgPerson
cn: Hamish MacTester
givenName: Hamish
sn: MacTester
mail: hm@test.example
END
$ ldapadd -D cn=admin,dc=magenta,dc=test -w testMAG -f organisation.ldif 
adding new entry "ou=Test Department,dc=magenta,dc=test"

adding new entry "cn=Mikkel Testsen,ou=Test Department,dc=magenta,dc=test"

adding new entry "cn=Hamish MacTester,ou=Test Department,dc=magenta,dc=test"
```