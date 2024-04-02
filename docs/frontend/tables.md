# Table Guide [WIP]

[WIP]

This is an ongoing project, so be mindfull that changes might occur.

## Semantic structure

``` html
<div class="datatable__card-container">
  <div class="datatable__wrapper">
    <table class="datatable [table ID]-table">
      <thead>
        <tr class="datatable__row">
          <th class="column column--[table ID]-[column ID]">
            {% trans "[column label]"|capfirst %}
          </th>

          <!-- Other table headers here -->
        </tr>
      </thead>

      {% if [dataset] %}

        <tbody>

          {% for [data] in [dataset] %}

            <tr class="datatable__row">
              <td class="column column--[table ID]-[column ID]">
                {{ [data].[ID tag] }}
              </td>

              <!-- Other data cells here -->
            </tr>

          {% endfor %}

        </tbody>

      {% endif %}

    </table>
  </div>
</div>
``` 

## Required attributes

All tables in OSdatascanner consists of two sets of style classes:

- General classes, that apply styling to all tables:
    - `.datatable__card-container`, `.datatable__wrapper`, `.datatable`, and `.datatable__row`
- Individual classes, that define local only styling for each table:
    - `.[table ID]-table`, `.column`, and `.column--[table ID]-[column ID]`

| HTML Tag            | Class                                           | Reason                                            |
| ------------------- | ----------------------------------------------- | ------------------------------------------------- |
| `<div>`             | `datatable__card-container`                     | Sets the background and "contains" the table      |
| `<div>`             | `datatable__wrapper`                            | Handles scroll behaviour                          |
| `<table>`           | `datatable` <br> `[table ID]-table`             | General styling + specific styling for this table |
| `<tr>`              | `datatable__row`                                | Handles general styling for `<th>` and `<td>`     |
| `<th>` <br> `<td>`  | `column` <br> `column--[table ID]-[column ID]`  | Handles unique styling for individual columns     |


## Creating a new table

This process consists of two phases:

- Constructing the HTML table and naming the elements
- Constructing the SCSS section for this specific table

It doesn't matter with order these are done in as long as their classes match. 

### Constructing the HTML

1. Build the new table according to the standard semantic structure seen above.
2. Name the table identifier something that both *make sense* and is *unique* for this table, and combine it with a "-table" suffix, e.g. `.org-table`.
3. Name each column identifier by combining the table identifier and the column type, e.g. `.org-import`.

### Constructing the SCSS

Whenever we create a new table, we need to consider the following:

- **The prefered min-width for this specific table:** <br> 
The layout **has** to work at this width.
The min-width will be the base for the math required to define the width of each column.
- **If this table requires a column with a fixed width:** <br> 
(e.g. if theres a column with check boxes or action buttons). <br>
There should only ever be a maximum of two "fixed width" columns per table and they should be placed at one or either ends of the table.
- **The width for each table column in percentages:** <br> 
The percentage of the total table width we want *each* individual column to fill. This will depend on the content for each cell and can require some tweaking during development. <br> (*Note: if there's a "fixed" width column in the table, then it is* **not** *counted as a part of the 100% for the total table width. More on this later.*)

#### The architecture of an SCSS section

In `_datatable.scss` you should find different sections for each table inside each module like so:


``` scss
// ************************************************
// ************************************************
// ********** TABLES IN THE ADMIN MODULE **********
// ************************************************
// ************************************************

// SCSS vars for über precise and responsive column widths:
$sidemenu_and_content: calc(var(--width-sidemenu) + var(--padding-content));
$relative_table_width: calc(100vw - #{$sidemenu_and_content});

// The example block below is what we need to create for each table

// *************************
// ***** EXAMPLE TABLE *****
// *************************

.example-table {
  // This table has 4 columns with flexible widths and no fixed columns. There 
  // will be a separate example showcasing how to style tables with fixed columns.
 
  // Table SCSS vars:
  $table_width: $relative_table_width; 
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
    &--example-name {
      // We want this column to take up 25% of the table, so we need $width_25 
      // and $min-width_25

      // Because HTML tables aren't reliably complying with the "min-width" attribute, 
      // we're using "clamp(min, val, max)" to set a range for the column widths:

      width: clamp(calc(#{$min-width_25}), calc(#{$width_25}), calc(#{$width_25}));

      // "clamp()" requires 3 parameters:
        // "min" --> the lower bound of the allowed range 
        // "val" --> the preferred value
        // "max" --> the upper bound of the allowed range

      // As we're only interessted in defining a min-width, we're letting "val" and 
      // "max" be the same value.
    }
    
    &--example-date {
      width: clamp(calc(#{$min-width_15}), calc(#{$width_15}), calc(#{$width_15}));
    }

    &--example-description {
      width: clamp(calc(#{$min-width_40}), calc(#{$width_40}), calc(#{$width_40}));
    }

    &--example-email { 
      width: clamp(calc(#{$min-width_20}), calc(#{$width_20}), calc(#{$width_20}));
    }
  }
}
```

There are module dependant sizes, which will be defined locally as `SCSS` vars, and we use these to calculate relative widths inside each style section. E.g. in Admin we have a fixed width for the sidemenu and content padding, so we use these to calculate the relative width of the table - to then later use *these* to calculate the percentages for each table.

We're hardcoding the percentages this way, because html table elements won't accept attributes like `min-width: 40%;` without having a fixed and well defined width for their parent element. Tables are silly that way. 

##### Example table with fixed-width columns 

Starting with an example; let's say we have a table with four columns like the one below

``` scss
// *********************************************
// ***** EXAMPLE TABLE WITH A FIXED COLUMN *****
// *********************************************

.fixed-table {
  // This table has 5 columns with flexible widths and 1 column with fixed width. 

  // Table SCSS vars:
  $fixed-column_width: 10rem; // The "fixed" column of this specific table
  $table_width: calc(#{$relative_table_width} - #{$fixed-column_width}); 
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
    &--fixed-name,
    &--fixed-org {
      width: clamp(calc(#{$min-width_20}), calc(#{$width_20}), calc(#{$width_20}));
    }

    &--fixed-phone,
    &--fixed-email {
      width: clamp(calc(#{$min-width_15}), calc(#{$width_15}), calc(#{$width_15}));
    }    

    &--fixed-import {
      width: clamp(calc(#{$min-width_30}), calc(#{$width_30}), calc(#{$width_30}));
    }    

    &--fixed-actions { // The "fixed" column of this specific table
      width: $fixed-column_width;
    }
  }
}
```

***

## Table templates

### HTML

``` html
<div class="datatable__card-container">
  <div class="datatable__wrapper">
    <table class="datatable [tableID]-table">
      <thead>
        <tr class="datatable__row">
          <th class="column column--[tableID]-[columnID]">
            {% trans "[label]"|capfirst %}
          </th>

          <!-- Other table headers here -->
        </tr>
      </thead>

      <tbody>
        <tr class="datatable__row">
          <td class="column column--[tableID]-[columnID]"></td>

          <!-- Other data cells here -->
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

***

### SCSS for tables with flexible columns

``` scss
// ****************************************************
// ***** EXAMPLE TABLE WITH FLEXIBLE COLUMNS ONLY *****
// ****************************************************

.example-table {
  // Table SCSS vars:
  $table_width: $relative_table_width; 
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
    &--example-[columnID] {
      width: clamp(calc(#{$min-width_10}), calc(#{$width_10}), calc(#{$width_10}));
    }

    /* Other column styles here */
  }
}

// NOTE: Replace "example" with whatever you choose as [tableID] for the table
```

*** 

### SCSS for tables with a fixed column

``` scss
// *********************************************
// ***** EXAMPLE TABLE WITH A FIXED COLUMN *****
// *********************************************

.fixed-table {
  // Table SCSS vars:
  $fixed-column_width: [fixed column size]rem; // The "fixed" column of this specific table
  $table_width: calc(#{$relative_table_width} - #{$fixed-column_width}); 
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
    &--fixed-[columnID] {
      width: clamp(calc(#{$min-width_10}), calc(#{$width_10}), calc(#{$width_10}));
    }

    /* Other column styles here */

    &--fixed-[columnID] { // The "fixed" column of this specific table
      width: $fixed-column_width;
    }
  }
}

// NOTE: Replace "fixed" with whatever you choose as [tableID] for the table
```

***