// Function to fetch metals based on the selected location
$(document).ready(function () {
    $("#dropdown4").on("change", function () {
        const selectedLocation = $(this).val(); // Get the selected location value

        // Références aux éléments
        const metalsDropdown = $("#characteristics");
        const loadingMessage = $("#loading-message");

        // Masquer le menu déroulant et afficher un message de chargement
        metalsDropdown.hide(); // cacher le dropdown
        loadingMessage.show().text("Please wait, metal recovery in progress...");

        // Envoyer la requête AJAX
        $.ajax({
            url: "/getmetals",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ location: selectedLocation }),
            success: function (response) {
                metalsDropdown.empty(); // Effacer les anciennes options

                // Ajouter les nouvelles options
                response.metals.forEach(function (metal) {
                    metalsDropdown.append(`<option value="${metal}">${metal}</option>`);
                });

                // Réafficher le dropdown et cacher le message
                loadingMessage.hide();
                metalsDropdown.show();

                // Mise à jour de la carte
                getAllMetalsAndLocation();
            },
            error: function (xhr, status, error) {
                loadingMessage.text("Error while recovering metals.");
                console.error("Error fetching metals:", error);
            }
        });
    });
});


        // Function to select/deselect the parameters
        function toggleAllCheckboxes(source) {
            const checkboxes = document.querySelectorAll('input[name="parameters"]');
            checkboxes.forEach(checkbox => {
                if (checkbox !== source) {
                    checkbox.checked = source.checked;
                }
            });
        }

