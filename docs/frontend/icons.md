# Icons in DataScanner (Work in Progress)

Types of icons used:

- [Google's Material Icons] [1]
- Custom SVG icons 
    - (that weird document where a billion svg's are written)
    - /src/os2datascanner/projects/static/svg
    - /src/os2datascanner/projects/admin/adminapp/templates/components/svg-icons
    - /src/os2datascanner/projects/report/reportapp/templates/components/svg-icons

***

## Material Icons

**What:**
An opensource icon library created by Google. It is self-hosted and relevant files can be found here:
`/src/os2datascanner/projects/static/fonts/materialicons/`

**How:**
Using an `<i>` tag with the coresponding ID/content for your desired icon like so:

``` html
<i id="icon_name" class="material-icons">icon_name</i>
```

**Where:**
Find the ID/content byt finding the name of the icon [here] [1]. If a name consists of several words, then replace the spaces with `_`

***

## Custom SVG's

**What:**

**How:**

**Where:**



<!-- LINKS -->
[1]: https://fonts.google.com/icons?icon.set=Material+Icons "Google's own library for Material Icons"