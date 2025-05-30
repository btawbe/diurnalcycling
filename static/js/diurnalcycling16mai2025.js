// Function to fetch metals based on the selected location
$(document).ready(function () {
    $("#dropdown4").on("change", function () {
        const selectedLocation = $(this).val(); // Get the selected location value

        // Send a POST request to the Flask backend
        $.ajax({
            url: "/getmetals", // Flask route
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ location: selectedLocation }), // Send the location
            success: function (response) {
                // Clear and populate the metals dropdown
                const metalsDropdown = $("#characteristics");
                metalsDropdown.empty(); // Clear existing options

                // Add new options from the response
                response.metals.forEach(function (metal) {
                    metalsDropdown.append(`<option value="${metal}">${metal}</option>`);
                });

                // ✅ Une fois que le dropdown est mis à jour, maintenant on peut mettre à jour la carte
                getAllMetalsAndLocation();
            },
            error: function (xhr, status, error) {
                alert("AJAX request failed! " + error);
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

