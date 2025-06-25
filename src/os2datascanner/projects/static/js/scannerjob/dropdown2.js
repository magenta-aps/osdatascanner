let selectedValues = [];
(function ($) {
	$.fn.dropdown2 = function (options) {
		var opts = $.extend({}, options);

		if (opts.data) {
			buildSelect(opts.data, this);
		}

		opts._templateResult = opts.templateResult;
		//defines a template on how to build/rebuild the select options
		opts.templateResult = function (data, container) {
			var label = data.text;
			if (typeof opts._templateResult === "function") {
				label = opts._templateResult(data, container);
			}
			var $item = $("<span class='item-label'><span class='site-icon'></span></span>").append(label);
			if (data.element) {
				var ele = data.element;
				container.setAttribute("data-val", ele.value);
				if (ele.className) {
                    container.className += " " + ele.className;
                }
				if(selectedValues.indexOf(ele.value)!==-1) {
					$($item.children()[0]).removeClass(opts.icon);
					$($item.children()[0]).addClass(opts.icon + '-selected');
					container.setAttribute('aria-selected', true);
					ele.selected="selected";
				}
			}
			return $item;
		};

		opts.closeOnSelect = false;
		opts.shouldFocusInput = false;
		opts.placeholder = opts.placeholder;
    	opts.allowClear = true;
		opts.width = 'element';
		var s2inst = this.select2(opts);
		
		// when building the select, sync selectedValues with what's actually selected
		// This ensures selectedValues reflects the current state after pre-selection
		var currentlySelected = [];
		this.find('option:selected').each(function() {
			var val = $(this).val();
			if (val && val !== '') {
				currentlySelected.push(val);
			}
		});
		selectedValues = currentlySelected.slice(); 

		s2inst.on("select2:open", function () {
			var s2data = s2inst.data("select2");
			//reusing the styling from tree version
			s2data.$dropdown.addClass("s2-to-tree");
			s2data.$dropdown.removeClass("searching-result");
			var $allsch = s2data.$dropdown.find(".select2-search__field").add(s2data.$container.find(".select2-search__field"));
			$allsch.off("input", inputHandler);
			$allsch.on("input", inputHandler);
		});

		// Show search result options
		function inputHandler() {
			var s2data = s2inst.data("select2");

			if ($(this).val().trim().length > 0) {
				s2data.$dropdown.addClass("searching-result");
			} else {
				s2data.$dropdown.removeClass("searching-result");
			}
		}

		// when unselecting a site
		s2inst.on('select2:unselect', function (evt) {
			let selectedId = evt.params.data.id;
			let options = Array.prototype.slice.call(document.querySelectorAll("li.select2-results__option"));
			let selectedNode = options.filter(function (element) { return element.dataset.val === selectedId; })[0];
			//if the dropdown menu is opened, remove the checkmark
			if( selectedNode ) {
				$(selectedNode.querySelector(".item-label").children[0]).removeClass('site-icon-selected');
				$(selectedNode.querySelector(".item-label").children[0]).addClass('site-icon');
			}
			
			// remove from selectedValues
			selectedValues = selectedValues.filter(function (value) { return value !== selectedId; });
			changeSelectedValuesInDropdown();
		});

		// add selected site
		s2inst.on('select2:selecting', function (evt) {
			let selectedId = evt.params.args.data.id;
			
			// Add to selectedValues if not already there
			if (selectedValues.indexOf(selectedId) === -1) {
				selectedValues.push(selectedId);
			}
			
			// Update the select2 value and trigger change
			var newValues = selectedValues.slice(); // Create copy
			$(s2inst).val(newValues);
			$(s2inst).trigger('change');
			
			$('.select2-search__field').val("");
			evt.preventDefault();
		});

		// changes the selected values, and triggers change on select
		function changeSelectedValuesInDropdown() {
			// Remove duplicates
			var uniqueValues = [];
			selectedValues.forEach(function (value) {
				if (uniqueValues.indexOf(value) === -1) {
                    uniqueValues.push(value);
                }
			});
			selectedValues = uniqueValues;
			$(s2inst).val(selectedValues);
			$(s2inst).trigger('change');
		}

		s2inst.on('change', function () {
			if(selectedValues.length > 0) {
				let options = Array.prototype.slice.call(document.querySelectorAll("li.select2-results__option"));
				let selectedNodes = options.filter(function (option) {
					return selectedValues.indexOf(option.dataset.val)!==-1;
				});
				selectedNodes.forEach( function(node){
					//If the dropdown elements exist
					if(node.querySelector(".item-label").children[0]) {
						$(node.querySelector(".item-label").children[0]).removeClass('site-icon');
						$(node.querySelector(".item-label").children[0]).addClass('site-icon-selected');
						node.setAttribute('aria-selected', true);
					}
				});
			}
		});

		return s2inst;
	};

	/* Build the Select Option elements from simple JSON objects */
	function buildSelect(data, $el) {
		// Clear selectedValues when rebuilding to avoid conflicts
		selectedValues = [];
		
		for (var i = 0; i < data.length; i += 1) {
			var site = data[i] || {};
			var $opt = $("<option></option>");
			
			// Use name for display text
			$opt.text(site.name || "");
			// Use id for value
			$opt.val(site.id || "");
			
			// Check if site has selected property and mark option as selected
			if (site.selected === "true" || site.selected === true) {
				$opt.prop("selected", true);
				// Add to selectedValues array for proper tracking
				if (site.id && selectedValues.indexOf(site.id) === -1) {
					selectedValues.push(site.id);
				}
			}
			
			// Handle empty values
			if ($opt.val() === "") {
				$opt.prop("disabled", true);
				$opt.val(getUniqueValue());
			}
			
			$el.append($opt);
		}
	}

	var uniqueIdx = 1;
	function getUniqueValue() {
		return "autoUniqueVal_" + (uniqueIdx += 1);
	}

})(jQuery);

/* jshint -W098 */ //disable check is used ( called from other file )
function createSiteView() {
	siteSelectOptionValueToggle();
	if (document.getElementById("sel_2")) {
		document.getElementById("sel_2").onchange = function () {
			siteSelectOptionValueToggle();
		};
	}
}