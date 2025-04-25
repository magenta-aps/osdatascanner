# Scanner settings

## Scan images

Available for all scanner types.

Enables OCR-conversion of image format files. The OCR engine is optimized for converting scanned, machine-written documents.

Images taking longer than 45 seconds to convert are skipped by default.

## Check date of last modification

Available for all scanner types.

Will skip scanning objects which have not changed since the previous scan.

This works slightly differently for scanner types with and without account-based scanning.

### Account-based scanning

MSGraph mail scanners, OneDrive scanners, EWS scanners, Gmail scanners and Google Drive scanners scan based on accounts in the admin module.
When an account is scanned, a CoveredAccount-object is created in the admin module, tracking which account was scanned for which scanner, and at what time. When scanning a second time with this setting on, only objects which have changed after the timestamp on the CoveredAccount-object for that scanner and account will be included in the scan.

Because each account has their own timestamp for their most recent scan, adding a new account to an existing scanner will scan everything associated with that account, even if the scanner has been run before.

### Non-account-based scanning

Scanners which do not scan based on accounts in the admin module will not scan objects changed before the scan time of the most recent ScanStatus related to the scanner when scanning a second time with this setting on.

## Keep false positives

Available for all scanner types

Normally, conducting a complete scan will revert handling of reports for which the matched object still exists.

This setting makes sure reports marked as false positives in the report module are never reverted in this case.

## Only notify superadmin

Available for all scanner types.

All reports found while scanning with this setting on will have the boolean field `only_notify_superadmin` set to `True`. Alias relations are still created as normal.

Reports with this flag will not be visible to the users connected to the report through an alias relation, but will instead be visible in the "withheld"-tab in the report module to superusers.

This flag can later be removed through the UI in the report module.

## Check dead links

This setting is only available for web scanners.

Applying this setting to a web scan will add a `LinksFollowRule` wrapped in an `AllRule` along with other rules applied to the scan.
This means the scan will also create reports for all instances of links found during the scan which are not followable.

## Skip super-hidden files

This setting is only available for file scanners.

Applying this setting will instruct the scanner to skip super-hidden files (and
normal files in super-hidden folders).

A _super-hidden_ file or folder is one that

* is marked with the `HIDDEN` attribute; and
* either
  * is marked with the `SYSTEM` attribute; or
  * has a `~` at the start of its name.

(Super-hidden files and folders are often used by backup systems to store old
versions of files; whether or not it makes sense to scan these depends on your
organisational policies.)

## UNC is home root

This setting is only available for file scanners.

This setting is intended for scanning "personal" folders in a file-system. Consider a file system with the following structure:

```
.
├── shared/
└── personal/
    ├── john/
    │   ├── mail_from_jill.txt
    │   └── recipes.docx
    └── jill/
```

In this case, the file "mail_from_jill.txt" is owned by the user "jill", while the file "recipes.docx" is owned by the user "john". Matches found in these files will be assigned to "jill" and "john" based on the owner of the file.

Using the "UNC is home root" however and specifying the "personal/"-folder as the UNC, both results will be assigned to the user "john", as that user is the owner of the folder "john/".

In other words, the owners of the first children folders of the UNC will be responsible for all matches found in those first child folders, regardless of the owners of the individual files.

Note that this setting is not necessarily the right choice for all
environments. (For example, the system administrator is technically the owner
of all user folders in many Windows deployments.) Check before you switch this
flag on.
## Scan subjects

This setting is only available for all types of email scanners.
When this is set to `True`, the scanner will wrap the selected rule in a `EmailHeaderRule`, meaning the engine will also find results in the subject header of emails scanned.

Specifically, if `UserRule` is the user chosen rule for the scanner, the constructed rule will be:

```
OrRule(
    UserRule,
    EmailHeaderRule(prop='subject', rule=UserRule)
)
```

## Scan deleted items folder

This setting is only available for MSGraph mail scanners.

Turning this setting on will scan mails found in the "deleted items" folder.

If the organization has a deletion policy for mails in the "deleted items" folder, it is recommended to turn this setting off to save resources on the scanner server.

## Scan syncissues folder

This setting is only available for MSGraph mail scanners.

Turning this setting on will scan mails found in the "syncissues" folder.

Mails will usually be found in this folder if users regularly use multiple different clients to access the same mailbox.

## Scan attachments

This setting is only available for MSGraph mail scanners and gmail scanners.

Turning on this setting will scan files attached to scanned emails.

