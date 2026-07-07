# Icon Guide

We currently use two types of icons in OSdatascanner:

- [Google's Material Symbols] [1] - *primary library*
- Custom SVG icons

***

## Material Symbols

### Overview

Material Symbols is a comprehensive and open-source icon library created by Google. It comes in three font families (outlined, rounded, sharp) whereof we only use "outlined". The other two font families are respectively too "hard/sharp" and too "rounded/cute" —> which is why we've landed on "outlined" as our Goldilock icon style. Not too sharp, and not too cute, but just right. 

We primarily use the "filled" version of "outlined". It may sound a bit contradictory, but Google named the font types, not us.

In niche cases an icon is deliberately rendered unfilled instead (e.g. `chat_error`, `visibility_off`) where it improves visual balance against surrounding icons. There is no separate `-outlined` CSS class for this. Unfilled rendering is applied via a per-icon `font-variation-settings` override in the SCSS, not something you opt into when adding an icon.

!!! Warning "Please check in with UX"
    Icon selection should happen in collaboration with UX, unless the icon is for a similar use case or behaviour to something that already exists elsewhere in the project — in that case, follow the existing precedent instead.

### Location:

The Material Symbols library is self-hosted within the OSdatascanner project. You can find the font file and styles here: `/src/os2datascanner/projects/static/fonts/materialsymbols/`

The font file here is **not** the full Material Symbols library. It's a curated subset including only the icons and style ranges the project actually uses. The subset is generated from `icons.json` in the same directory, which is the actual source of truth for what's available. 

!!! Note "Can't find the icon you need?"
    If the icon you want isn't already in use somewhere in the project, it almost certainly isn't in the font yet. See [Adding a new icon](#adding-a-new-icon).

### Usage

#### Implementing icons in HTML templates

Icons are primarily incorporated templates using an `<i>` tag, the `.material-symbols` class, and the name of the icon. Here's how:

```html
<i class="material-symbols">icon_name</i>
```


**Example:** You want to use the "search" icon from Material Symbols, so you're first checking if it's included in the current list of available icons in `icons.json`. If it is, you can implement it in your template right away:

```html
<i class="material-symbols">search</i>
```

**If it isn't**, you'll have to [add it](#adding-a-new-icon) yourself.

#### Adding a new icon

Because the font is a subset, using an icon name that isn't already registered will render the string value itself as raw text (not even a fallback glyph, just a weird text blob).

Before using a new icon:

1. Add its name to the `icons` list in `static/fonts/materialsymbols/icons.json`.
2. If the icon needs a `font-variation-settings` value outside the currently supported ranges (`FILL 0..1`, `wght 300..500`, `GRAD -25..0`, `opsz 20..48`), widen the corresponding entry in that same file's `axes` object.
3. Regenerate the font using this [management command](../management-commands.md):
   `docker compose exec -u 0 admin python manage.py compileicons`
4. Commit the regenerated font file along with your `icons.json` change.

!!! Note "Try it locally"
    Because the icon set is a hand-maintained subset rather than the full library, always check `icons.json` (or just try it locally) before assuming an icon is available. Don't rely on the icon simply existing just because you can see it in Google's online catalog.

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