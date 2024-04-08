# Icon Guide

Types of icons used in OSdatascanner:

- [Google's Material Symbols] [1] - *primary library*
- [Google's Material Icons] [2] - *secondary library*
- Custom SVG icons

***

## Material Symbols & Material Icons

### Overview

Material Symbols is a comprehensive and open-source icon library created by Google. These icons are integrated into OSdatascanner to provide a visually consistent and scalable way to use icons across the platform.

Material Icons is the older version of Googles icon library. We're currently in a process where we will either be replacing all material-icons with material-symbols or map out when to use what across the platform. For now the default library will be *Material Symbols*.

### Location:

The `Material <Symbols|Icons>` library is self-hosted within the OSdatascanner project. You can find the necessary font files and styles at the following locations: 

* `/src/os2datascanner/projects/static/fonts/materialsymbols/`
* `/src/os2datascanner/projects/static/fonts/materialicons/`

### Usage

#### Identifying and Formatting Icon IDs

To utilize a specific Google icon in OSdatascanner, first identify its name from the official [library] [1] . Then, format the name for use within OSdatascanner by converting spaces to underscores `_`. For instance:

- Original Name from Google: example icon
- Formatted ID for OSdatascanner: example_icon

#### Implementing Icons in HTML

Once you have the formatted ID, incorporate the icon into your HTML using an `<i>` tag. Here's how you can do it with either library:

``` html
<!-- Material Symbols -->
<i id="formatted_icon_id" class="material-symbols">formatted_icon_id</i>

<!-- Material Icons -->
<i id="formatted_icon_id" class="material-icons">formatted_icon_id</i>
```

In this snippet, replace `formatted_icon_id` with the actual ID of the icon you wish to use. This ID corresponds to the formatted name of the icon.

**Example:**

If you want to use the "search" icon from Material Symbols, you would first check its name in the Material Symbols library, (note that it's a single word so no formatting is needed), and then implement it as follows:

``` html
<i id="search" class="material-symbols">search</i>
```

This approach ensures that you can easily find, format, and implement any Google Icon in your OSdatascanner project, maintaining a consistent and professional UI.

### Note

Given the extensive range of both the Material Symbols and the Material Icons library, developers are encouraged to explore and utilize the range of icons available for enhancing UI/UX in OSdatascanner. However, for any custom icon requirements not met by this library, refer to the Custom SVG Icons section.

***


## Custom SVG Icons

### Overview

A mix of uniquely designed icons created specifically for OSdatascanner and remnants of previous icon implementations.

### Location:

The icons are located across different directories, reflecting their specific use within the OSdatascanner architecture:

- `/static/svg/symbol-defs.svg`
- `/static/svg`
- `/admin/adminapp/templates/components/svg-icons`
- `/report/reportapp/templates/components/svg-icons`

### Implementation 

#### Using SVG Symbols from /symbol-defs.svg

To implement an icon from the global SVG symbols file:

```html
<svg class="icon [additional-class]">
    <use xlink:href="/static/svg/symbol-defs.svg#icon-name"></use>
</svg>
```

Replace [additional-class] with any specific classes needed for styling, and icon-name with the actual icon name. This method is less commonly used, so styling classes may vary.


#### Implementing Locally Hosted SVG Files in Django

For Django applications, SVG files can be integrated directly:

``` html
{% include "components/svg-icons/icon-file.svg" %}
```

Ensure to replace icon-file.svg with the actual SVG file name and use the correct relative path.


<!-- LINKS -->
[1]: https://fonts.google.com/icons "Link to the library for Material Symbols"
[2]: https://fonts.google.com/icons?icon.set=Material+Icons "Link to the library for Material Icons"