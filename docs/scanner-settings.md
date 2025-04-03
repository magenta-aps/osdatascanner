# Scanner settings

## Scan subjects

This setting is only available for the email scanners.
When this is set to `True`, the scanner will wrap the selected rule in a `EmailHeaderRule`, meaning the engine will also find results in the subject header of emails scanned.

Specifically, if `UserRule` is the user chosen rule for the scanner, the constructed rule will be:

```
OrRule(
    UserRule,
    EmailHeaderRule(prop='subject', rule=UserRule)
)
```
