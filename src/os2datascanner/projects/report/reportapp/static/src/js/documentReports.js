// variable that keeps all the filter information

var send_data = {}

$(document).ready(function () {
    // reset all parameters on page load

    resetFilters();
    // bring all the data without any filters

    getAPIData();
    // get all countries from database via 

    // AJAX call to get sensitivites select options

    getSensitivities();

    getScannerjobs();

    // on filtering the sensitivity input

    $('#sensitivities').on('change', function () {
        // get the api data of updated variety

        if(this.value == "all")
            send_data['sensitivity'] = "";
        else
            send_data['sensitivity'] = this.value;
        getAPIData();
    });

    $('#scannerjobs').on('change', function () {
        // get the api data of updated variety

        if(this.value == "all")
            send_data['scannerjob'] = "";
        else
            send_data['scannerjob'] = this.value;
        getAPIData();
    });

    $('#30_day_rule').on('change', function () {
        // get the api data of updated variety
        if(this.checked)
            send_data['30-day-rule'] = true;
        else
            send_data['30-day-rule'] = false;
        getAPIData();
    });
    

    // display the results after reseting the filters

    $("#display_all").click(function(){
        resetFilters();
        getAPIData();
    })
})


/**
    Function that resets all the filters   
**/
function resetFilters() {
    $("#sensitivities").val("all");
    $("#scannerjobs").val("all");
    $("#30_day_rule").prop('checked', false);

    send_data['sensitivity'] = '';
    send_data['scannerjob'] = '';
    send_data['30-day-rule'] = false;
}

/**.
    Utility function to showcase the api data 
    we got from backend to the table content
**/
function putTableData(result) {
    // creating table row for each result and

    // pushing to the html cntent of table body of listing table

    let row;
    if(result["results"].length > 0){
        $("#no_results").hide();
        $("#list_data").show();
        $("#listing").html("");  
        $.each(result["results"], function (a, b) {
            row = `
            <tr tabindex="0">
                <td class="datatable__column--handle">
                    <div class="datatable__column--filetype-icon">
                        <input type="checkbox" value="" id="match-checkbox" name="match-checkbox" 
                            class="datatable-checkbox" data-report-pk="${b.id}">
                        <span class="icon-filetype icon-filetype--ews">
                            <svg viewBox="0 0 17 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M0 16L4 14.75V5L11 3V17.5L0.5 16.25L11 20L17 18.75V1.5L10.95 0L0 3.75V16Z" />
                            </svg>
                        </span>
                    </div>
                </td>
                <td class="datatable__column--item">
                    <span class="scan__item-title">
                        <strong>${b.data.matches.handle.path}</strong>
                    </span>
                    <span class="scan__item-count">
                        Matches: <em>${b.data.matches.matches[0].matches.length}</em>
                    </span>
                    <span class="scan__item-meta">
                        <strong>${b.data.matches.handle.path}</strong>
                    </span>
                    <div class="hit-link">
                        <div class="button-group">
                            <a href="https://www.google.dk" class="button" target="_blank" rel="noopener">Open</a>    
                        </div>
                    </div>
                </td>
                <td colspan="3">
                    <table class="datatable datatable--nested">
                        <tbody>
                            <tr>
                                <td class="datatable__column--match">
                                    <span class="more">${b.data.matches.matches[0].matches[0].match}</span>
                                </td>
                                <td class="datatable__column--context">
                                </td>
                                <td class="datatable__column--probability">
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>`
            $("#listing").append(row);   
        });
    }
    else{
        // if no result found for the given filter, then display no result

        $("#no_results h5").html("No results found");
        $("#list_data").hide();
        $("#no_results").show();
    }
    // setting previous and next page url for the given result

    let prev_url = result["previous"];
    let next_url = result["next"];
    // disabling-enabling button depending on existence of next/prev page. 

    if (prev_url === null) {
        $("#previous").addClass("disabled");
        $("#previous").prop('disabled', true);
    } else {
        $("#previous").removeClass("disabled");
        $("#previous").prop('disabled', false);
    }
    if (next_url === null) {
        $("#next").addClass("disabled");
        $("#next").prop('disabled', true);
    } else {
        $("#next").removeClass("disabled");
        $("#next").prop('disabled', false);
    }
    // setting the url

    $("#previous").attr("url", result["previous"]);
    $("#next").attr("url", result["next"]);
    // displaying result count

    $("#result-count span").html(result["count"]);
}

function getAPIData() {
    let url = $('#list_data').attr("url")
    console.log('API CALL');
    $.ajax({
        method: 'GET',
        url: url,
        data: send_data,
        beforeSend: function(){
            $("#no_results h5").html("Loading data...");
        },
        success: function (result) {
            putTableData(result);
        },
        error: function (response) {
            $("#no_results h5").html("Something went wrong");
            $("#list_data").hide();
        }
    });
}

$("#next").click(function () {
    // load the next page data and 

    // put the result to the table body

    // by making ajax call to next available url

    let url = $(this).attr("url");
    if (!url)
        $(this).prop('all', true);

    $(this).prop('all', false);
    $.ajax({
        method: 'GET',
        url: url,
        success: function (result) {
            putTableData(result);
        },
        error: function(response){
            console.log(response)
        }
    });
})

$("#previous").click(function () {
    // load the previous page data and 

    // put the result to the table body 

    // by making ajax call to previous available url

    let url = $(this).attr("url");
    if (!url)
        $(this).prop('all', true);

    $(this).prop('all', false);
    $.ajax({
        method: 'GET',
        url: url,
        success: function (result) {
            putTableData(result);
        },
        error: function(response){
            console.log(response)
        }
    });
})

function getSensitivities() {
    // fill the options of sensitivites by making ajax call

    // obtain the url from the sensitivites select input attribute

    let url = $("#sensitivities").attr("url");

    // makes request to getSensitivites(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {
            sensitivities_option = "<option value='all' selected>All Sensitivities</option>";
            $.each(result["sensitivities"], function (a, b) {
                sensitivities_option += "<option>" + b + "</option>"
            });
            $("#sensitivities").html(sensitivities_option)
        },
        error: function(response){
            console.log(response)
        }
    });
}

function getScannerjobs() {

    let url = $("#scannerjobs").attr("url");

    // makes request to getSensitivites(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {
            scannerjobs_option = "<option value='all' selected>All scannerjobs</option>";
            $.each(result["scannerjobs"], function (a, b) {
                scannerjobs_option += "<option>" + b + "</option>"
            });
            $("#scannerjobs").html(scannerjobs_option)
            
        },
        error: function(response){
            console.log(response)
        }
    });
}
