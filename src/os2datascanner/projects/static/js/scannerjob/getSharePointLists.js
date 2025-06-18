var parameters = {};

$(function () {
    parameters.grantId = document.querySelector('#id_graph_grant').value;
    getSharePointSites();

    // Eventlistener on change
    document.querySelector('#id_graph_grant').addEventListener('change', function (e) {
        var grantId = e.target.value;
        if (parameters.grantId !== grantId) {
            parameters.grantId = grantId;
            
            selectedValues = [];

            getSharePointSites();
        }
    });

    // sync button event listener
    document.querySelector('#sharepoint-sync-btn').addEventListener('click', function (e) {
        e.preventDefault();
        
        var $select = $('#sel_2');
        
        // Destroy existing Select2 to prevent resizing issue
        if ($select.hasClass('select2-hidden-accessible')) {
            $select.select2('destroy');
        }
        
        selectedValues = [];
        parameters.sync = true;
        getSharePointSites();
    });


});

function getSharePointSites() {
    var url = $('#sel_2').attr("url");
    $.ajax({
        method: 'GET',
        url: url,
        data: parameters,
        success: function (result) {
            insertData(result);
        },
        error: function () {
            console.error("Error while fetching site list!");
        }
    });
}

function isSiteSelected(sites) {
    // Empty the function when it's called, to make sure it's only called once
    // since we don't want to "refill" the select box, every time a user changes site selection
    /* jshint -W021 */
    isSiteSelected = function () { };
    /* jshint +W021 */
    
    // Determine whether the site is selected
    // Do not use this on create view
    if (document.location.pathname.indexOf('add') === -1) {
        var scannerJobId = document.location.pathname.split('/')[2];

        for (var i = 0; i < sites.length; i++) {
            if (sites[i].scanners && sites[i].scanners.length > 0) {
                for (var j = 0; j < sites[i].scanners.length; j++) {
                    if (sites[i].scanners[j] === parseInt(scannerJobId)) {
                        sites[i].selected = "true";
                    }
                }
            }
        }
    }
}

function insertData(result) {
    isSiteSelected(result);
    $("#sel_2").empty();
    
    $("#sel_2").select2Sites({ siteData: result, placeholder: gettext('Select one or more sites') });
}
