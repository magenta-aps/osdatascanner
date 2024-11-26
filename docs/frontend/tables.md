Note: This is an ongoing project, so be mindfull that changes might occur.

# Table Guide [WIP]

All tables in OSdatascanner consist of two sets of style classes:

- General classes, that apply styling to all tables:
  - `.datatable__card-container`, `.datatable__wrapper`, `.datatable`, and `.datatable__row`
- Individual classes, that define local only styling for each table:
  - `.[table ID]-table`, `.column`, and `.column--[column ID]`

### General classes

| HTML Tag           | Class                               | Reason                                            |
| ------------------ | ----------------------------------- | ------------------------------------------------- |
| `<div>`            | `datatable__card-container`         | Sets the background and "contains" the table      |
| `<div>`            | `datatable__wrapper`                | Handles scroll behaviour                          |
| `<table>`          | `datatable` <br> `[table ID]-table` | General styling + specific styling for this table |
| `<tr>`             | `datatable__row`                    | Handles general styling for `<th>` and `<td>`     |
| `<th>` <br> `<td>` | `column` <br> `column--[column ID]` | Handles unique styling for individual columns     |

See the code snippet below to get familiar with the required structure of a new datatable.

## Semantic structure

```html
<div class="datatable__card-container">
  <div class="datatable__wrapper">
    <table class="datatable [table ID]-table">
      <thead>
        <tr class="datatable__row">
          <th class="column column--[column ID]">
            {% trans "[column label]"|capfirst %}
          </th>

          <!-- Other table headers here -->
        </tr>
      </thead>

      {% if [dataset] %}

      <tbody>
        {% for [data] in [dataset] %}

        <tr class="datatable__row">
          <td class="column column--[column ID]">{{ [data].[ID tag] }}</td>

          <!-- Other data cells here -->
        </tr>

        {% endfor %}
      </tbody>

      {% endif %}
    </table>
  </div>
</div>
```

## Creating a new table

### 1. Constructing the HTML

- Use the HTML template from the [Table templates](#table-templates).
- Name the table identifier something that both _make sense_ and is _unique_ for this table, and combine it with a "-table" suffix, e.g. `.org-table`.
- Name each column identifier something relevant to the content type, e.g. `.column--import`.

### 2. Constructing the SCSS

Whenever we create a new table, we first need to consider the wanted layout of the table:

- **If this table requires a column with a fixed width:** <br>
  (e.g. if theres a column with check boxes or action buttons). <br>
  There should only ever be a maximum of two "fixed width" columns per table and they should be placed at one of either ends of the table.

After figuring this out, you can use the appropriate SCSS [template](#table-templates). You can find the templates for tables with a fixed column [here](#scss-template-1-or-more-fixed-columns), and the templates for tables with flexible columns [here](#scss-template-flexible-columns-only).

- **The prefered min-width for this specific table:** <br>
  The layout **has** to work at this width.
  The min-width will be the base for the math required to define the width of each column.
- **The width for each table column in percentages:** <br>
  The percentage of the total table width we want _each_ individual column to fill. This will depend on the content for each cell and can require some tweaking during development. <br> (_Note: if there's a "fixed" width column in the table, then it is_ **not** _counted as a part of the 100% for the total table width. More on this later._)

#### The architecture of an SCSS section

In `_datatable.scss` you should find different sections for each table inside each module like so:

```scss
// ***********************************
// ***** EXAMPLE TABLE FOR ADMIN *****
// ***********************************

// SCSS vars for über precise and responsive column widths:
$sidemenu_and_content: calc(var(--width-sidemenu) + var(--padding-content));
$relative_table_width--admin: calc(100vw - #{$sidemenu_and_content});

// The example block below is what we need to create for each table on Admin:

.example-table {
  // This table has 4 columns with flexible widths and no fixed columns. There
  // will be a separate example showcasing how to style tables with fixed columns.

  // Table SCSS vars:
  $table_width: $relative_table_width--admin;
  $table_min-width: 70rem; // The size for this specific table

  // In this table we want columns that take up 15%, 20%, 25%, and 40% of the total
  // table width:

  // Column SCSS vars:
  $width_15: calc(#{$table_width} * 0.15); // Responsive column size
  $min-width_15: calc(#{$table_min-width} * 0.15); // 70rem * 0.15

  $width_20: calc(#{$table_width} * 0.2); // Responsive column size
  $min-width_20: calc(#{$table_min-width} * 0.2); // 70rem * 0.2

  $width_25: calc(#{$table_width} * 0.25); // Responsive column size
  $min-width_25: calc(#{$table_min-width} * 0.25); // 70rem * 0.25

  $width_40: calc(#{$table_width} * 0.4); // Responsive column size
  $min-width_40: calc(#{$table_min-width} * 0.4); // 70rem * 0.4

  // Styles:
  min-width: $table_min-width;

  .column {
    &--name {
      // We want this column to take up 25% of the table, so we need $width_25
      // and $min-width_25

      // Because HTML tables aren't reliably complying with the "min-width" attribute,
      // we're using "clamp(min, val, max)" to set a range for the column widths:

      width: clamp(
        calc(#{$min-width_25}),
        calc(#{$width_25}),
        calc(#{$width_25})
      );

      // "clamp()" requires 3 parameters:
      // "min" --> the lower bound of the allowed range
      // "val" --> the preferred value
      // "max" --> the upper bound of the allowed range

      // As we're only interessted in defining a min-width, we're letting "val" and
      // "max" be the same value.
    }

    &--date {
      width: clamp(
        calc(#{$min-width_15}),
        calc(#{$width_15}),
        calc(#{$width_15})
      );
    }

    &--description {
      width: clamp(
        calc(#{$min-width_40}),
        calc(#{$width_40}),
        calc(#{$width_40})
      );
    }

    &--email {
      width: clamp(
        calc(#{$min-width_20}),
        calc(#{$width_20}),
        calc(#{$width_20})
      );
    }
  }
}

// ************************************
// ***** EXAMPLE TABLE FOR REPORT *****
// ************************************

// The example block below is what we need to create for each table on Report:

.example-table {
  // This table has 4 columns with flexible widths and no fixed columns. There
  // will be a separate example showcasing how to style tables with fixed columns.

  // Table SCSS vars:
  $table_min-width: 70rem; // The size for this specific table

  // In this table we want columns that take up 15%, 20%, 25%, and 40% of the total
  // table width:

  // Column SCSS vars:
  $width_15: 15%; // Responsive column size
  $min-width_15: calc(#{$table_min-width} * 0.15); // 70rem * 0.15

  $width_20: 20%; // Responsive column size
  $min-width_20: calc(#{$table_min-width} * 0.2); // 70rem * 0.2

  $width_25: 25%; // Responsive column size
  $min-width_25: calc(#{$table_min-width} * 0.25); // 70rem * 0.25

  $width_40: 40%; // Responsive column size
  $min-width_40: calc(#{$table_min-width} * 0.4); // 70rem * 0.4

  // Styles:
  min-width: $table_min-width;

  .column {
    &--name {
      // We want this column to take up 25% of the table, so we need $width_25
      // and $min-width_25

      // Because HTML tables aren't reliably complying with the "min-width" attribute,
      // we're using "clamp(min, val, max)" to set a range for the column widths:

      width: clamp(
        calc(#{$min-width_25}),
        calc(#{$width_25}),
        calc(#{$width_25})
      );

      // "clamp()" requires 3 parameters:
      // "min" --> the lower bound of the allowed range
      // "val" --> the preferred value
      // "max" --> the upper bound of the allowed range

      // As we're only interessted in defining a min-width, we're letting "val" and
      // "max" be the same value.
    }

    &--date {
      width: clamp(
        calc(#{$min-width_15}),
        calc(#{$width_15}),
        calc(#{$width_15})
      );
    }

    &--description {
      width: clamp(
        calc(#{$min-width_40}),
        calc(#{$width_40}),
        calc(#{$width_40})
      );
    }

    &--email {
      width: clamp(
        calc(#{$min-width_20}),
        calc(#{$width_20}),
        calc(#{$width_20})
      );
    }
  }
}
```

There are module dependant sizes, which will be defined locally as `SCSS` vars, and we use these to calculate relative widths inside each style section. E.g. in Admin we have a fixed width for the sidemenu and content padding, so we use these to calculate the relative width of the table - to then later use _these_ to calculate the percentages for each table.

We're hardcoding the percentages this way, because html table elements won't accept attributes like `min-width: 40%;` without having a fixed and well defined width for their parent element. Tables are silly that way.

For datatables in Report we won't have the same issues with calculating relative widths - because there's no side-nav.

##### Example table with fixed-width columns

Starting with an example; let's say we have a table with four columns like the one below

```scss
// *******************************************************
// ***** EXAMPLE TABLE WITH A FIXED COLUMN FOR ADMIN *****
// *******************************************************

.fixed-table {
  // This table has 5 columns with flexible widths and 1 column with fixed width.

  // Table SCSS vars:
  $fixed-column_width: 10rem; // The "fixed" column of this specific table
  $table_width: calc(#{$relative_table_width--admin} - #{$fixed-column_width});
  $table_min-width: 70rem; // The size for this specific table

  // In this example we want columns that take up 15%, 20%, and 30% of the remaining
  // width of the table:

  $width_15: calc(#{$table_width} * 0.15); // Responsive column size
  $min-width_15: calc(#{$table_min-width} * 0.15); // 75rem * 0.15

  $width_20: calc(#{$table_width} * 0.2); // Responsive column size
  $min-width_20: calc(#{$table_min-width} * 0.2); // 75rem * 0.2

  $width_30: calc(#{$table_width} * 0.3); // Responsive column size
  $min-width_30: calc(#{$table_min-width} * 0.3); // 75rem * 0.3

  // This is not "perfect" math but life's too short for unnecessarily complicated
  // SCSS calculations just to have good looking table columns.

  // Styles:
  min-width: $table_min-width;

  .column {
    &--name,
    &--org {
      width: clamp(
        calc(#{$min-width_20}),
        calc(#{$width_20}),
        calc(#{$width_20})
      );
    }

    &--phone,
    &--email {
      width: clamp(
        calc(#{$min-width_15}),
        calc(#{$width_15}),
        calc(#{$width_15})
      );
    }

    &--import {
      width: clamp(
        calc(#{$min-width_30}),
        calc(#{$width_30}),
        calc(#{$width_30})
      );
    }

    &--actions {
      // The "fixed" column of this specific table
      width: $fixed-column_width;
    }
  }
}
```

---

## Table templates

### The HTML template

```html
<div class="datatable__card-container">
  <div class="datatable__wrapper">
    <table class="datatable [tableID]-table">
      <thead>
        <tr class="datatable__row">
          <th class="column column--[columnID]">
            {% trans "[label]"|capfirst %}
          </th>

          <!-- Other table headers here -->
        </tr>
      </thead>

      <tbody>
        <tr class="datatable__row">
          <td class="column column--[columnID]"></td>

          <!-- Other data cells here -->
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

---

### SCSS template (flexible columns only)

```scss
// *********************************************************
// *********************************************************
// ********** EXAMPLE TABLE WITH FLEXIBLE COLUMNS **********
// *********************************************************
// *********************************************************

// **********************
// ***** ADMIN ONLY *****
// **********************
.example-table {
  // Table SCSS vars:
  $table_width: $relative_table_width--admin;
  $table_min-width: [table size]rem; // The size for this specific table

  // Column SCSS vars:
  $width_10: calc(#{$table_width} * 0.1);
  $min-width_10: calc(#{$table_min-width} * 0.1);

  $width_15: calc(#{$table_width} * 0.15);
  $min-width_15: calc(#{$table_min-width} * 0.15);

  $width_20: calc(#{$table_width} * 0.2);
  $min-width_20: calc(#{$table_min-width} * 0.2);

  $width_25: calc(#{$table_width} * 0.25);
  $min-width_25: calc(#{$table_min-width} * 0.25);

  $width_30: calc(#{$table_width} * 0.3);
  $min-width_30: calc(#{$table_min-width} * 0.3);

  $width_35: calc(#{$table_width} * 0.35);
  $min-width_35: calc(#{$table_min-width} * 0.35);

  $width_40: calc(#{$table_width} * 0.4);
  $min-width_40: calc(#{$table_min-width} * 0.4);

  $width_45: calc(#{$table_width} * 0.45);
  $min-width_45: calc(#{$table_min-width} * 0.45);

  $width_50: calc(#{$table_width} * 0.5);
  $min-width_50: calc(#{$table_min-width} * 0.5);

  $width_55: calc(#{$table_width} * 0.55);
  $min-width_55: calc(#{$table_min-width} * 0.55);
  /* NOTE: delete all unused vars after setup */

  // Styles:
  min-width: $table_min-width;

  .column {
    &--[columnID] {
      width: clamp(
        calc(#{$min-width_10}),
        calc(#{$width_10}),
        calc(#{$width_10})
      );
    }

    /* Other column styles here */
  }
}

// ***********************
// ***** REPORT ONLY *****
// ***********************

.example-table {
  // Table SCSS vars:
  $table_min-width: [table size]rem; // The size for this specific table

  // Column SCSS vars:
  $width_10: 10%;
  $min-width_10: calc(#{$table_min-width} * 0.1);

  $width_15: 15%;
  $min-width_15: calc(#{$table_min-width} * 0.15);

  $width_20: 20%;
  $min-width_20: calc(#{$table_min-width} * 0.2);

  $width_25: 25%;
  $min-width_25: calc(#{$table_min-width} * 0.25);

  $width_30: 30%;
  $min-width_30: calc(#{$table_min-width} * 0.3);

  $width_35: 35%;
  $min-width_35: calc(#{$table_min-width} * 0.35);

  $width_40: 40%;
  $min-width_40: calc(#{$table_min-width} * 0.4);

  $width_45: 45%;
  $min-width_45: calc(#{$table_min-width} * 0.45);

  $width_50: 50%;
  $min-width_50: calc(#{$table_min-width} * 0.5);

  $width_55: 55%;
  $min-width_55: calc(#{$table_min-width} * 0.55);
  /* NOTE: delete all unused vars after setup */

  // Styles:
  min-width: $table_min-width;

  .column {
    &--[columnID] {
      width: clamp(
        calc(#{$min-width_10}),
        calc(#{$width_10}),
        calc(#{$width_10})
      );
    }

    /* Other column styles here */
  }
}
```

---

### SCSS template (1 or more fixed columns)

```scss
// *******************************************************
// *******************************************************
// ********** EXAMPLE TABLE WITH A FIXED COLUMN **********
// *******************************************************
// *******************************************************

// **********************
// ***** ADMIN ONLY *****
// **********************

.fixed-table {
  // Table SCSS vars:
  $fixed-column_width: [fixed column size]rem; // The "fixed" column of this specific table
  $table_width: calc(#{$relative_table_width--admin} - #{$fixed-column_width});
  $table_min-width: [table size]rem; // The size for this specific table

  // Column SCSS vars:
  $width_10: calc(#{$table_width} * 0.1);
  $min-width_10: calc(#{$table_min-width} * 0.1);

  $width_15: calc(#{$table_width} * 0.15);
  $min-width_15: calc(#{$table_min-width} * 0.15);

  $width_20: calc(#{$table_width} * 0.2);
  $min-width_20: calc(#{$table_min-width} * 0.2);

  $width_25: calc(#{$table_width} * 0.25);
  $min-width_25: calc(#{$table_min-width} * 0.25);

  $width_30: calc(#{$table_width} * 0.3);
  $min-width_30: calc(#{$table_min-width} * 0.3);

  $width_35: calc(#{$table_width} * 0.35);
  $min-width_35: calc(#{$table_min-width} * 0.35);

  $width_40: calc(#{$table_width} * 0.4);
  $min-width_40: calc(#{$table_min-width} * 0.4);

  $width_45: calc(#{$table_width} * 0.45);
  $min-width_45: calc(#{$table_min-width} * 0.45);

  $width_50: calc(#{$table_width} * 0.5);
  $min-width_50: calc(#{$table_min-width} * 0.5);

  $width_55: calc(#{$table_width} * 0.55);
  $min-width_55: calc(#{$table_min-width} * 0.55);
  /* NOTE: delete all unused vars after setup */

  // Styles:
  min-width: $table_min-width;

  .column {
    &--[columnID] {
      width: clamp(
        calc(#{$min-width_10}),
        calc(#{$width_10}),
        calc(#{$width_10})
      );
    }

    /* Other column styles here */

    &--[columnID] {
      // The "fixed" column of this specific table
      width: $fixed-column_width;
    }
  }
}

// ***********************
// ***** REPORT ONLY *****
// ***********************

.example-table {
  // Table SCSS vars:
  $fixed-column_width: [fixed column size]rem; // The "fixed" column of this specific table
  $table_min-width: [table size]rem; // The size for this specific table

  // Column SCSS vars:
  $width_10: 10%;
  $min-width_10: calc(#{$table_min-width} * 0.1);

  $width_15: 15%;
  $min-width_15: calc(#{$table_min-width} * 0.15);

  $width_20: 20%;
  $min-width_20: calc(#{$table_min-width} * 0.2);

  $width_25: 25%;
  $min-width_25: calc(#{$table_min-width} * 0.25);

  $width_30: 30%;
  $min-width_30: calc(#{$table_min-width} * 0.3);

  $width_35: 35%;
  $min-width_35: calc(#{$table_min-width} * 0.35);

  $width_40: 40%;
  $min-width_40: calc(#{$table_min-width} * 0.4);

  $width_45: 45%;
  $min-width_45: calc(#{$table_min-width} * 0.45);

  $width_50: 50%;
  $min-width_50: calc(#{$table_min-width} * 0.5);

  $width_55: 55%;
  $min-width_55: calc(#{$table_min-width} * 0.55);
  /* NOTE: delete all unused vars after setup */

  // Styles:
  min-width: $table_min-width;

  .column {
    &--[columnID] {
      width: clamp(
        calc(#{$min-width_10}),
        calc(#{$width_10}),
        calc(#{$width_10})
      );
    }

    /* Other column styles here */

    &--[columnID] {
      // The "fixed" column of this specific table
      width: $fixed-column_width;
    }
  }
}
```

---

## Notes on content in expandable rows

Some of our tables have expandable rows with additional data about a given report/user/scanner job and so on. Currently there's not a "one true way" to do this, but have the following in mind when adding new content:

1. Content should always take up the full width of it's parental/associated `<tr>` element with `padding: var(--datatable-cell-padding);`.

2. Consider if it makes sense for your new content to be displayed inside of a card element or as a separate "section". Try to match current content layout, if possible.

3. All data in your content has to be legible and usable for screens down to _1024px_ and up to whatever the content max-width is for the page you're working on. (And remember to take _edgecases_ for datasizes into consideration). If the layout is too figgety to wrangle, then consider if you either need a simpler layout, or use media queries for specific layout break points.

4. Be mindful of repetetive "titles" on related elements. Solutions can be giving a group of elements a common headline/title, or rewording the individual titles. Unfortunately this needs to be considered from usecase to usecase.

Most of these are generally "good practices" for layout and if time allows it, they'll be added to a new chapter with "Overall layout guidelines".

---
