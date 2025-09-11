const syncButton = document.getElementById('sharepoint-sync-btn');
const selectElement = document.getElementById('sharepoint_sites');
const grantSelect = document.querySelector("#id_graph_grant");
const orgSelect = document.querySelector('#id_organization');
let savedValues = JSON.parse(document.getElementById('savedValues').textContent);

document.addEventListener('DOMContentLoaded', function() {
    
    if (syncButton && selectElement) {
        syncButton.addEventListener('click', getSites);
    }

    if (grantSelect.value === undefined || grantSelect.value === ''){
        syncButton.disabled = true;
    }
    
    grantSelect.addEventListener('change', ()=> {
        syncButton.disabled = grantSelect.value === undefined || grantSelect.value === '';

        getSites();
    });

    orgSelect.addEventListener('change', ()=> {
        syncButton.disabled = grantSelect.value === undefined || grantSelect.value === '';

        getSites();
    });

    getSites();

});

async function getSites(sync){
    try {
        const grantId = grantSelect.value;
        syncButton.disabled = true;

        const selectedValues = Array.from(selectElement.selectedOptions).map(option => option.value);
        let query = "";

        if (grantId && sync){
            query += `grantId=${grantId}&sync=${sync}`;
        } else if (grantId){
            query += `grantId=${grantId}`;
        }

        const response = await fetch(`/sharepoint-listing?${query}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        selectElement.innerHTML = '';

        const filtered = data.filter((site)=> site.organization === orgSelect.value);

        filtered.forEach(site => {
            const option = document.createElement('option');
            option.value = site.id;
            option.textContent = site.name;

            //Preserve selected options
            if (selectedValues.includes(site.id.toString())) {
                option.selected = true;
            } else if (savedValues && savedValues.includes(site.id)) {
                option.selected = true;
            }

            selectElement.appendChild(option);
        });

        savedValues = [];
        
    } catch (error) {
        console.error('Error fetching SharePoint sites:', error);
        
    } finally {
        syncButton.disabled = false;
    }
} 
