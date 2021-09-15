import "core-js"

// import js files
import './handle-match.js';
import './show-more.js';
import './filter-options.js';
import './pagination.js';
import './results.js';

os2web = window.os2web || {};
(function(os2web, $) {
    // Enable iframe-based modal dialogs
    $('.modal.iframe').on('shown.bs.modal', function() {
      var $this = $(this), src = $this.attr("data-href");
      if(src)
        $this.find('iframe').first().attr("src", src);
    });

    // Validation radio buttons in the domain dialog
    $('input.validateradio').on("click", function() {
        var $this = $(this),
            id = '#validation_method_desc_' + $this.attr('value');
        $this.attr('data-target', id);
        $this.tab('show');
    });

    // Resize iframe according to content height
    $('.modal-body iframe').on('load',function(){
      var $this = $(this);
      $this.height($this.contents().find('body').height());
      $this.contents().on('click','.nav-tabs a',function(){
        $this.height($this.contents().find('body').height());
      });
    });

    $.extend(os2web, {
        iframeDialog: function(id_or_elem, url, title) {
            $elem = $(id_or_elem);
            $elem.find('iframe').first().attr('src', 'about:blank');
            $elem.attr('data-href', url);
            if(title) {
                label_id = $elem.attr('aria-labelledby');
                if(label_id) {
                    $('#' + label_id).html(title);
                }
            }
            $elem.modal({show: true});
        }
    });

    $("a[data-modal='modal:open']").click(function(e){
        e.preventDefault()

        // Find the target element (same as our href)
        var target = $(this).attr("href")

        // Find the src to set
        var src = $(this).attr("data-src")

        // Find the iframe in our target and set its src
        $(target).find("iframe").attr("src",src);
    });

    // Toggle visiblity of expandable rows, start
    $(document).on("click", "[data-toggle]", function() {
      var expandTarget = $(this).attr("data-toggle");

      if ($(expandTarget).is('[hidden]')) {
        $(expandTarget).removeAttr('hidden');
      } else {
        $(expandTarget).attr('hidden','');
      }
    });
    // Toggle visiblity of expandable rows, stop
})(os2web, jQuery);

// declared globally so we can access it from separate IIFEs.
function handleSubChoices(choice) {
  var state = choice.prop("checked");
  var siblings = choice.siblings("input[type='checkbox']");
  siblings.prop("disabled", !state);
  if(!state) {
    siblings.prop("checked", false).change();
  }
}

function recalcIframeHeight() { // we need to do this every time we add/remove an item from the rule list
  var thisBodyHeight = $("body").height();
  var parentIframe = $(".modal-body iframe", window.parent.document);
  parentIframe.height(thisBodyHeight);
}

/* debounce function from https://davidwalsh.name/javascript-debounce-function */
// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
function os2debounce(func, wait, immediate) {
	var timeout;
	return function() {
		var context = this, args = arguments;
		var later = function() {
			timeout = null;
			if (!immediate) func.apply(context, args);
		};
		var callNow = immediate && !timeout;
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
		if (callNow) func.apply(context, args);
	};
};
