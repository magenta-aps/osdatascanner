(($) => {
  htmx.onLoad(() => {
    // Initiate Select2 on all selects:
    const $selects = $("select.select2").select2();

    // Translations:
    const PLACEHOLDER_TEXT = gettext("Search...");
    const SEARCH_TITLE = gettext(
      "Type here to start searching in the available options for this setting."
    );
    const REMOVE_TITLE = gettext("Click here to remove this selection.");

    // Helper to bind re-init logic to any input element:
    function bindReinitPlaceholder($input) {
      // Whenever it's cleared, put the placeholder back:
      $input.on("input", function () {
        if (!this.value.trim()) {
          $(this).attr("placeholder", PLACEHOLDER_TEXT);
        }
      });
    }

    // Helper to apply the "remove selection"-button tooltip:
    function addRemoveTooltip(inst) {
      inst.$container
        .find("span.select2-selection__choice__remove")
        .attr("title", REMOVE_TITLE);
    }

    // Initial setup for each instance:
    $selects.each(function () {
      const inst = $(this).data("select2");
      const $inlineSearch = inst.$container.find(".select2-search__field");

      // Inline-search placeholder + title:
      $inlineSearch
        .attr("placeholder", PLACEHOLDER_TEXT)
        .attr("title", SEARCH_TITLE);

      bindReinitPlaceholder($inlineSearch);

      // Any pre-rendered "remove selection"-buttons:
      addRemoveTooltip(inst);
    });

    // Whenever the dropdown opens, set + bind on the dropdown search field:
    $selects.on("select2:open", function () {
      const inst = $(this).data("select2");
      const $dropdownSearch = inst.$dropdown.find(".select2-search__field");

      $dropdownSearch
        .attr("placeholder", PLACEHOLDER_TEXT)
        .attr("title", SEARCH_TITLE);

      bindReinitPlaceholder($dropdownSearch);

      // Also reapply "remove selection"-button tooltips in case dropdown rendering touched them:
      addRemoveTooltip(inst);
    });

    // After each select/unselect, reapply "remove selection"-button tooltips:
    $selects.on("select2:select select2:unselect", function () {
      addRemoveTooltip($(this).data("select2"));
    });

    // After each selection change, re-apply to the inline search again because Select2 clears it when you pick something:
    $selects.on("select2:select select2:unselect", function () {
      const inst = $(this).data("select2");
      const $inlineAgain = inst.$container.find(".select2-search__field");
      $inlineAgain.attr("placeholder", PLACEHOLDER_TEXT);
    });
  });
})(jQuery);
