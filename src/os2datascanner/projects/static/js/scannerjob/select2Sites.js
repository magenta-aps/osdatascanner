let selectedValues = [];
(function ($) {
	$.fn.select2ToSites = function (options) {
		var opts = $.extend({}, options);

		if (opts.siteData) {
			buildSelect(opts.siteData, this);
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
					$($item.children()[0]).removeClass('site-icon');
					$($item.children()[0]).addClass('site-icon-selected');
					container.setAttribute('aria-selected', true);
					ele.selected="selected";
				}
			}
			return $item;
		};

		opts.closeOnSelect = false;
		opts.shouldFocusInput = false;
		opts.placeholder = opts.placeholder || 'Select one or more sites';
    	opts.allowClear = true;
		opts.width = 'element';
		var s2inst = this.select2(opts);
		
		// when building the select, add all already selected values and mark them
		s2inst.val().forEach( function(value) {
			selectNodes(value);
		} );

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
			selectNodes(selectedId);
			$('.select2-search__field').val("");
			evt.preventDefault();
		});

		function selectNodes(selectedId) {
			selectedValues.push(selectedId);
			changeSelectedValuesInDropdown();
		}

		// changes the selected values, and triggers change on select
		function changeSelectedValuesInDropdown() {
			uniqueValues = [];
			//remove duplicates
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
	function buildSelect(siteData, $el) {
		for (var i = 0; i < siteData.length; i += 1) {
			var site = siteData[i] || {};
			var $opt = $("<option></option>");
			
			// Use name for display text
			$opt.text(site.name || "");
			// Use id for value
			$opt.val(site.id || "");
			
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
	/** disables file upload when sites are selected */
	function siteSelectOptionValueToggle() {
		if (document.getElementById("sel_1")) {
			if (document.getElementById("sel_1").value) {
				document.getElementById("id_userlist").disabled = true;
				document.getElementById("upload-file").style.backgroundColor = "#dddddd";
				document.getElementById("fileUpload").style.backgroundColor = "#dddddd";
			} else {
				document.getElementById("id_userlist").disabled = false;
				document.getElementById("upload-file").style.backgroundColor = "#fff";
			}
		}
	}
	siteSelectOptionValueToggle();
	if (document.getElementById("sel_1")) {
		document.getElementById("sel_1").onchange = function () {
			siteSelectOptionValueToggle();
		};
	}
}