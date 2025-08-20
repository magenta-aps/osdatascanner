document.addEventListener('DOMContentLoaded', function() {
    const syncButton = document.getElementById('sharepoint-sync-btn');
    const selectElement = document.getElementById('sharepoint_sites');
    
    if (syncButton && selectElement) {
        syncButton.addEventListener('click', async function() {
            try {
                grantId = document.querySelector("#id_graph_grant").value;
                syncButton.disabled = true;
                
                const selectedValues = Array.from(selectElement.selectedOptions).map(option => option.value);
                
                const response = await fetch(`/sharepoint-listing?grantId=${grantId}`, {
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
                
                data.forEach(site => {
                    const option = document.createElement('option');
                    option.value = site.uuid;
                    option.textContent = site.name;
                    
                    if (selectedValues.includes(site.uuid.toString())) {
                        option.selected = true;
                    }
                    
                    selectElement.appendChild(option);
                });
                
            } catch (error) {
                console.error('Error fetching SharePoint sites:', error);
                
            } finally {
                syncButton.disabled = false;
            }
        });
    }
});
