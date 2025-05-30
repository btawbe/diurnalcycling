 function zoomImage(imageId, scaleMultiplier) {
          const image = document.getElementById(imageId);
          // Get the current scale from the transform property
          const currentScale = parseFloat(image.style.transform.replace(/scale\((.*)\)/, '$1')) || 1;
          const newScale = currentScale * scaleMultiplier;
          image.style.transform = `scale(${newScale})`;
      }

  // Function to delete an image
  function removeImage(containerId) {
      const container = document.getElementById(containerId);
      if (container) {
          container.remove(); // Removes the HTML element from the interface
      }
  }

  // Function to reset all images to their original size 
  function resetImage(imageId) {
       const image = document.getElementById(imageId);
       image.style.transform = "scale(1)";
   }


   // Function to rotate an image
   function rotateImage(imageId, angle) {
       const image = document.getElementById(imageId);
       const currentRotation = parseFloat(image.getAttribute('data-rotation') || '0');
       const newRotation = currentRotation + angle;
       image.style.transform = `rotate(${newRotation}deg)`;
       image.setAttribute('data-rotation', newRotation);
   }

   // Function to display an image in full screen
   function viewFullScreen(imageId) {
       const image = document.getElementById(imageId);
       if (image.requestFullscreen) {
           image.requestFullscreen();
       } else if (image.webkitRequestFullscreen) {
           image.webkitRequestFullscreen();
       } else if (image.msRequestFullscreen) {
           image.msRequestFullscreen();
       }
   }

// Recuperate all metals name and displaying them on the interactive map
// Fonction pour récupérer tous les métaux et la localisation sélectionnée
function getAllMetalsAndLocation() {
    const metalsDropdown = document.getElementById('characteristics');
    const locationDropdown = document.getElementById('dropdown4');
    //alert("aaaaa");
    //alert(locationDropdown);
    // Vérification si les menus déroulants existent
    if (!metalsDropdown || !locationDropdown) {
        console.error("Dropdowns not found!");
        return;
    }

    // Récupérer la liste des métaux sélectionnés
    const metals = Array.from(metalsDropdown.options)
                        .map(option => option.text.trim())  // Extraire le texte de chaque option
                        .filter(text => text !== "");  // Filtrer les métaux vides

    // Récupérer la localisation sélectionnée
    //const selectedLocation = locationDropdown.value.trim();
    const selectedOption = locationDropdown.options[locationDropdown.selectedIndex];
    const selectedLocation = selectedOption.textContent.trim();
    //alert("bbb");
    //alert(metals);
    //alert(selectedLocation);
    // Si une localisation et des métaux sont sélectionnés, afficher les métaux autour de la localisation
    if (selectedLocation && metals.length > 0) {
        displayMetalsAroundLocation(selectedLocation, metals);
    } else {
        console.warn("No location selected or no metals found.");
    }
//alert("dddddddd");
}

// Fonction pour afficher les métaux autour de la localisation sur la carte
function displayMetalsAroundLocation(locationName, metals) {
    // Trouver la localisation dans les données des emplacements (locations)
    const location = locations.find(loc => loc[2] === locationName);  // Utiliser le nom de la location
    //alert(locations);
    //alert(locationName);
    //alert(location);
    //alert("ffffff");
    if (!location) {
        console.error("Location not found:", locationName);
        return;
    }

    const lat = parseFloat(location[3]);
    const lon = parseFloat(location[4]);
    const doii=location[1];
    //alert("AAAAA");
    //alert(doii);
    //alert(lat);
    //alert(lon);
    //alert("eeeeeeee");
    // Pour chaque métal, afficher un marqueur à proximité de la localisation
    metals.forEach((metal, index) => {
        const maxOffset = 5; // Distance maximum (plus grande pour séparer un peu plus les bulles)

        const latOffset = (Math.random() - 0.8) * maxOffset; // Valeur aléatoire entre -0.025 et +0.025
        const lonOffset = (Math.random() - 0.8) * maxOffset;

        const newLat = lat + latOffset;
        const newLon = lon + lonOffset;
        // Créer un cercle jaune pour chaque métal autour de la localisation
        const randomColor = '#' + Math.floor(Math.random() * 16777215).toString(16);
    L.circleMarker([newLat, newLon], {
        radius: 4,
        fillColor: randomColor,
        color: "white",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    }).addTo(specialLayer)
    .bindPopup(`
      <b>${metal}</b><br>
      <a href="#" class="open-analysis" data-metal="${metal}" data-doi="${doii}">
      see analysis  ${metal}
  </a>
    `)
     .bindTooltip(metal, {
    permanent: false,  // Tooltip s'affiche seulement au survol
    direction: 'top'   // S'affiche au-dessus de la bulle
});
});
}

// Quand la page est chargée, initialiser la fonction
window.addEventListener('load', function() {
    getAllMetalsAndLocation();
});


//document.getElementById('dropdown4').addEventListener('change', function() {
    // Ici tu sais que la sélection est faite, donc PAS besoin de setTimeout
  //  getAllMetalsAndLocation();
//});

//document.getElementById('characteristics').addEventListener('change', function() {
    // Ici aussi, la sélection du caractéristique est faite, donc PAS besoin de setTimeout
  //  getAllMetalsAndLocation();
//});

// Fonction pour filtrer les locations selon la catégorie sélectionnée
function filterLocationsByCategory(locations) {
    const categorySelect = document.getElementById("category_location");
    const locationSelect = document.getElementById("dropdown4");
    const defaultOption = document.createElement("option");
    // Quand la catégorie change
    categorySelect.addEventListener("change", function () {
        const selectedCategory = this.value;

        // Nettoyer les options existantes
        locationSelect.innerHTML = "";

        defaultOption.textContent = "Choose a location"; // Texte affiché
        defaultOption.value = "";                        // Valeur vide
        defaultOption.disabled = true;                   // Empêche l'utilisateur de la re-sélectionner après
        defaultOption.selected = true;                   // Affiche cette option par défaut
        locationSelect.appendChild(defaultOption);       // L’ajoute dans le <select>

        // Filtrer et ajouter les nouvelles options
        locations.forEach(location => {
            const doi = location[1];
            const name = location[2];
            const category = location[5];

            // Vérifie si la catégorie correspond ou si "All" est sélectionné (valeur '4')
            if (selectedCategory === '4' || category.toString() === selectedCategory) {
                const option = document.createElement("option");
                option.value = doi;
                option.textContent = name;
                locationSelect.appendChild(option);

            }
        });
    });
}
