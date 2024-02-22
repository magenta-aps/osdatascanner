# Shared components [WIP]

This is a WIP documenting how to use shared components in OSdatascanner. This will be updated whenever new components are ready. 

## Current categories [WIP]

Loosely based on what we already have in OSdatascanner and what terms are commonly used as industry standard:

| Category                                                              | Sub-components                                                                                                                            |
| --------------------------------------------------------------------- |  ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Navigation** <br> _Navigating within the application._              | <ul><li>menus</li><li>breadcrumbs</li><li>tabs</li><li>pagination</li><li>sidebars</li></ul>                                              |
| **Input** <br> _Allows users to enter data._                  | <ul><li>text fields</li><li>checkboxes</li><li>radio buttons</li><li>dropdowns</li><li>toggles</li><li>date pickers</li><li>file upload</li></ul> |
| **Display** <br> _Displays content and information to the user._      | <ul><li>cards</li><li>lists</li><li>tables</li><li>accordions</li></ul>                                                                   |
| **Feedback** <br> _Provides feedback in response to actions._         | <ul><li>alerts</li><li>toasts</li><li>progress bars</li><li>modals</li></ul>                                                              |
| **Containers** <br> _Manages the layout/state of child components._   | <ul><li>modal containers</li><li>tab containers</li><li>accordions</li><li>panels</li></ul>                                                |
| **Utility** <br> _Provides additional info/options to users._         | <ul><li>toolbars</li><li>tooltips</li><li>popovers</li><li>helper text</li></ul>                                                          |
| **Decorative** <br> _Primarily used for esthetic enhancement._        | <ul><li>icons</li><li>dividers</li><li>decorative banners</li></ul>                                                                       |

## Experimental categories [WIP]

Some components that _could_ be interessting for us:

| Category                                                          | Sub-components                                                                                                    |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Layout** <br> _Defines the structure and layout of a page._     | <ul><li>grids</li><li>containers</li><li>rows</li><li>columns</li><li>panels</li></ul>                            |
| **Composite** <br> _Complex UI elements that encapsulate multiple <br> functionalities. Represent a higher level of abstraction._     | Built by combining several other components.  | 

***
***


## Utility components

Here the individual utility components will be described as they get created.

### Popovers

#### Overview
The popover component is a reusable UI element designed to display additional information (like error messages or tips) in a floating, styled box when a user interacts with a trigger element (like an icon or text). It is primarily used to convey status messages or additional context about elements on the page. 


#### Implementation Guide
1. Context Preparation:
    * The popover component requires a context variable named `popover_data` to be passed to the template.
    * This variable should be a dictionary containing keys such as `status`, `title`, and `subtitle`.
    * Example of setting `popover_data` in a Django view:

``` python
popover_data = {
    'status': _("No action required:"),
    'title': _("A temporary error occurred during the latest check of this result. OSdatascanner will automatically check this result again as part of the next scan."),
    'subtitle': _("Additional details if any."),
}
context["popover_data"] = popover_data
```

2. HTML Structure:
    * Include the popover component in the HTML where it needs to be displayed.
    * Use a trigger element with a class `popover__trigger-element` and a unique `data-popover-id`.
    * The actual popover content should be wrapped in a `<div>` with an `id` matching the `data-popover-id` of the trigger.
    * Example of HTML structure:

    
``` html
<i class="material-icons popover__trigger-element" data-popover-id="popover-example">info</i>
<div id="popover-example" class="popover popover--[modifier]">
    {% include "components/modals/popover_component.html" with popover_data=popover_data %}
</div>
```

3. SCSS and JavaScript:
    * Ensure that the relevant SCSS and JavaScript files are included in the template to handle the styling and interactivity of the popover.
    * The popover is hidden by default and displayed when the trigger element is interacted with (on hover).
    * Additional themes can be added to the `popover` container with the BEM modifier prefix `--[custom modifier]`. At the moment, the only available modifier is `--yellow`.

4. Customization:
    * The `popover` component can be customized by passing different values in the `popover_data` dictionary.
    * Developers can add additional keys to `popover_data` for more dynamic content.

5. Localization:
    * Text within the popover supports localization. Use Django’s `gettext` function (`_("Your text here")`) to ensure the content is localizable.

* _Best Practices_
    * Keep the popover content concise and informative.
    * Use the component for supplementary information that does not require immediate action, keeping the primary content of the page clear and uncluttered.
    * Test the popover for accessibility, ensuring it is readable and reachable via keyboard navigation.


***
***


## Future development  [WIP]

We are currently working on creating a `/shared/templates/components` sibling-directive to Admin and Report. To begin with it'll house shared components, but it's not unlikely that it could end up containing all shared template files. Stay tuned for updates.



### Frontend's Notes on "Modals" [WIP]

We currently use "modals" for anything and everything "pop up-ish" - which  c a n  work, but I'd suggest we start being more conscise in how we name/categorize our "pop-ups". Conventionally regular modals and our "modals" fall under the component category: Feedback. 

#### Feedback [WIP]

    Feedback: used to provide feedback to the user in response to their actions.
    * Alerts
        * Success messages
        * Error messages
        * Warnings
    * Toasts
    * Progress bars
    * Modals 