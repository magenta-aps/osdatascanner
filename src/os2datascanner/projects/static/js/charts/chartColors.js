/* exported cssVar, colorFunction, getChartPalette, paletteForN */
/* exported DATASOURCE_COLORS, RESOLUTION_STATUS_COLORS, BAR_CHART_COLORS */
/* exported DOUGHNUT_HANDLED_COLOR, DOUGHNUT_EMPTY_COLOR */
/* exported ANALYSIS_COLORS, ANALYSIS_BAR_COLOR */

/* ————— REFACTOR NOTES —————
This is where chart specific colours should live.

TODO: 
  • Revisit this file later when we're ready to implement a reusable colour scheme that all chart.js charts will use.
*/

// ————— ScanStatus charts —————

// Reads a CSS custom property from :root.
function cssVar(name) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
}

// Legacy alias for cssVar.
var colorFunction = function (color) { // jshint ignore:line
  "use strict";
  return cssVar(color);
};

function getChartPalette(startBaseIndex = 0) {
  // Base order matters: `startBaseIndex` rotates this list for the second chart.
  const bases = [
    "green",
    "turquoise",
    "osds-blue",
    "blue",
    "purple",
    "mauve",
    "red",
    "orange",
    "yellow",
  ];

  // "-darker" and "-lighter" are intentionally disabled to reduce shades per hue.
  // Palette size = bases.length × suffixes.length.
  // Current: 9 × 3 = 27 colours.
  const suffixes = [
    // "-darker",
    "-dark",
    "",
    "-light",
    // "-lighter",
  ];

  const rotatedBases = bases
    .slice(startBaseIndex)
    .concat(bases.slice(0, startBaseIndex));

  const colors = [];

  for (const base of rotatedBases) {
    for (const suffix of suffixes) {
      const token = `--chart-color-${base}${suffix}`;
      const value = cssVar(token);
      if (value) {
        colors.push(value);
      }
    }
  }

  return colors;
}

function paletteForN(n, startBaseIndex = 0) {
  // Return an array of N colours.
  // If N exceeds palette length, colours repeat (intentional fallback).
  const palette = getChartPalette(startBaseIndex);
  const out = [];

  for (let i = 0; i < n; i++) {
    out.push(palette[i % palette.length]);
  }

  return out;
}

// ————— Statistics charts —————

const DATASOURCE_COLORS = [
  "#fed149",
  "#5ca4cd",
  "#21759c",
  "#00496e",
  "#bfe474",
  "#e47483",
];

const RESOLUTION_STATUS_COLORS = [
  "#80ab82",
  "#a2e774",
  "#35bd57",
  "#1b512d",
  "#7e4672",
];

const BAR_CHART_COLORS = [
  "#21759c",
  "#d4efff",
  "#00496e",
  "#5ca4cd",
];

const DOUGHNUT_HANDLED_COLOR = "#21759c";
const DOUGHNUT_EMPTY_COLOR   = "#f5f5f5";

// ————— Analysis charts —————

const ANALYSIS_COLORS = [
  "rgba(84, 71, 140)",
  "rgba(44, 105, 154)",
  "rgba(4, 139, 168)",
  "rgba(13, 179, 158)",
  "rgba(22, 219, 147)",
  "rgba(131, 227, 119)",
  "rgba(185, 231, 105)",
  "rgba(239, 234, 90)",
  "rgba(241, 196, 83)",
];

const ANALYSIS_BAR_COLOR = "rgba(100, 44, 145, 0.8)";
