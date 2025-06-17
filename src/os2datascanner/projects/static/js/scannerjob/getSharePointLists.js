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
        
        var $select = $('#sel_1');
        
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
    var url = $('#sel_1').attr("url");
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
    // Do not use this on add new pages
    if (document.location.pathname.indexOf('add') === -1) {
        var scannerJobId = document.location.pathname.split('/')[2];
        
        // Since sites now only have id and name, we need a different approach
        // Option 1: If sites have a direct relationship to scanner jobs
        for (var i = 0; i < sites.length; i += 1) {
            // Check if this site's ID matches the scanner job ID
            if (sites[i].id === scannerJobId) {
                sites[i].selected = "true";
            }
            
            // OR if you have scanner job data available elsewhere:
            // Check if this site has scanners that include the current job
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
    $("#sel_1").empty();
    
    $("#sel_1").select2ToSites({ siteData: result });
    // Count the number of chosen units. If any, keep the correct radio button checked.
    var sites = 0;
    for (var res of result) {
        if (res.selected === "true") {
            sites++;
        }
    }
    if (sites > 0) {
        $("#select-org-units").prop("checked", true);
        $("#sel_1").prop("disabled", false);
    }
}
