// Listen for click on toggle checkbox
$("#select-all").change(function () {
    $("input[name='error-checkbox']").prop("checked", $(this).prop("checked"));
    handleChecked();
});

// Handle checkboxes
function handleChecked() {
    var numChecked = $("input[name='error-checkbox']:checked").length;
    $(".selected-cb .num-selected").text(numChecked);
    $(".handle-error__action").prop("disabled", !Boolean(numChecked));

    $("input[name='error-checkbox']:not(:checked)").closest("tr").removeClass("highlighted");
    $("input[name='error-checkbox']:checked").closest("tr").addClass("highlighted");
}
// Iterate each checkbox
$("input[name='error-checkbox']").change(handleChecked);

// Handle matches
function handleMatches(pks, buttonEl) {
    if (pks.length > 0) {
        $(".datatable").addClass("disabled");
        // let user know that we're processing the action by mutating the button
        // of the selected row(s)
        updateButtons(pks, buttonEl, 'sync', 'data-label-processing');

        $.ajax({
            url: "/api",
            method: "POST",
            data: JSON.stringify({
                "action": "set-status-2",
                "report_id": pks,
                "new_status": 0
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }).done(function (body) {
            if (body.status === "ok") {
                // let user know that we succeeded the action by mutating the button(s) again
                updateButtons(pks, buttonEl, 'done', 'data-label-done', 'text-ok-dark', 'text-secondary');
                location.reload(true);
            } else if (body.status === "fail") {
                $(".datatable").removeClass("disabled");

                // revert the button(s)
                updateButtons(pks, buttonEl, 'archive', 'data-label-default');
                console.log(
                    "Attempt to call set-status-2 failed: "
                    + body.message);
            }
        });
    }
}

$(".handle-error__action").click(function () {
    // get pks from checked checkboxes
    var pks = $.map($("input[name='error-checkbox']:checked"), function (e) {
        return $(e).attr("error-log-pk");
    });
    handleMatches(pks, $(this));
});

function updateButtons(pks, buttonEl, icon, attr, addClasses, removeClasses) {
    var buttonSelectors = pks.map(function (pk) {
        return "button[error-log-pk='" + pk + "']";
    }).join(",");

    var buttons = $(buttonSelectors);

    // use buttonEl to target extra button(s) that are not targeted by
    // using the data-report-pk property.
    if (buttonEl) {
        if (buttonEl instanceof jQuery) {
            buttons = buttons.add(buttonEl);
        } else if (buttonEl instanceof String) {
            buttons = buttons.add($(buttonEl));
        }
    }

    buttons.each(function () {
        var button = $(this);
        button.find('.material-icons').text(icon).addClass(addClasses).removeClass(removeClasses);
        var label = button.attr(attr);
        if (label) {
            button.find('span').text(label);
        }
    });
}