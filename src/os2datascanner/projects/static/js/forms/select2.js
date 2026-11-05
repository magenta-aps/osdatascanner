(($) => {
  // Options marked data-action (like "Create new …") will be seen as actions instead of choices:
  const isAction = (data) =>
    data.element instanceof HTMLOptionElement && "action" in data.element.dataset;
  const defaultMatcher = $.fn.select2.defaults.defaults.matcher;

  htmx.onLoad((elt) => {
    // Initiate Select2 on the selects in what htmx just loaded (the whole page on the first
    // load), skipping those already set up (select2 marks them select2-hidden-accessible):
    const $selects = $(elt)
      .find("select.select2")
      .addBack("select.select2")
      .not(".select2-hidden-accessible")
      .each(function () {
        const $dialog = $(this).closest("dialog");
        $(this).select2({
          // Inside a modal, the dropdown has to be part of the <dialog>, or the modal covers it:
          ...($dialog.length ? { dropdownParent: $dialog } : {}),
          matcher: (params, data) => (isAction(data) ? data : defaultMatcher(params, data)),
          templateResult: (data, container) => {
            if (isAction(data)) {
              container.classList.add("select2-results__option--action");
            }
            return data.text;
          },
        });

        // Messages for when there's nothing to choose:
        const inst = $(this).data("select2");
        const { emptyMessage, emptyNote } = this.dataset;
        const row = (className, text) => {
          const li = document.createElement("li");
          li.className = `select2-results__option ${className}`;
          li.textContent = text;
          return li;
        };

        // Highlight nothing, and tell screen readers so:
        const clearHighlight = () => {
          inst.$dropdown[0]
            .querySelectorAll(".select2-results__option--highlighted")
            .forEach((option) => option.classList.remove("select2-results__option--highlighted"));
          inst.$dropdown[0]
            .querySelector(".select2-search__field")
            .removeAttribute("aria-activedescendant");
          inst.$container[0]
            .querySelector(".select2-selection")
            .removeAttribute("aria-activedescendant");
        };

        // An action is only highlighted while the mouse is on it (or the keyboard has moved to it):
        inst.$dropdown[0].addEventListener("mouseout", (e) => {
          const action = e.target.closest(".select2-results__option--action");
          if (action && !action.contains(e.relatedTarget)) {
            clearHighlight();
          }
        });

        inst.on("results:all", ({ data, query }) => {
          const list = inst.$dropdown[0].querySelector(".select2-results__options");
          const searching = Boolean((query.term || "").trim());

          // Like a native select, highlight nothing on open when nothing is chosen, and never
          // highlight an action unless the user goes to it:
          const highlighted = list.querySelector(".select2-results__option--highlighted");
          if (!this.multiple && highlighted && (
            highlighted.classList.contains("select2-results__option--action") ||
            (!searching && !list.querySelector('[aria-selected="true"]'))
          )) {
            clearHighlight();
          }

          // The placeholder's empty option is in the results too, though select2 doesn't show it:
          if (data.results.some((result) => !isAction(result) && result.id !== "")) {
            return;
          }

          if (searching) {
            // Actions match every search, so select2 doesn't say "No results found" itself:
            if (data.results.some(isAction)) {
              const message = row(
                "select2-results__message",
                inst.options.get("translations").get("noResults")()
              );
              message.setAttribute("role", "alert");
              message.setAttribute("aria-live", "assertive");
              list.prepend(message);
            }
          } else if (emptyMessage) {
            // No options at all: show the select's own message (and note) instead of the search:
            list.querySelectorAll(".select2-results__message").forEach((own) => own.remove());
            const message = row("select2-results__message", emptyMessage);
            list.prepend(message);
            if (emptyNote) {
              message.after(row("select2-results__note", emptyNote));
            }
            // select2's own class for a search field it doesn't show:
            inst.$dropdown[0]
              .querySelector(".select2-search--dropdown")
              .classList.add("select2-search--hide");
          }
        });

        // The list is attached to <body>, so mark the single selects' lists for styling:
        if (!this.multiple) {
          inst.$dropdown[0]
            .querySelector(".select2-dropdown")
            .classList.add("select2-dropdown--single");
        }

        // Remove old classes so each dropdown opening picks a direction with a fresh assessment:
        inst.on("close", () => {
          inst.$dropdown[0]
            .querySelector(".select2-dropdown")
            .classList.remove("select2-dropdown--above", "select2-dropdown--below");
          inst.$container[0].classList.remove("select2-container--above", "select2-container--below");
        });
      });

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

    // Choosing an action fires a native "select2-action" event instead, so other listeners don't
    // need jQuery:
    $selects.on("select2:selecting", function (e) {
      const data = e.params.args.data;
      if (!isAction(data)) {
        return;
      }
      e.preventDefault();
      $(this).select2("close");
      this.dispatchEvent(new CustomEvent("select2-action", {
        bubbles: true,
        detail: { option: data.element },
      }));
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
