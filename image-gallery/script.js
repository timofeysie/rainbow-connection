document.addEventListener("DOMContentLoaded", function () {
    const imageContainer = document.getElementById("displayed-image");
    const imageSelect = document.getElementById("image-select");
    const playButton = document.getElementById("play-button");
    let imageList = [];

    // Function to fetch the list of images from the /images directory
    function fetchImagesList() {
        fetch("/images/") // Use the correct path to your images directory
            .then((response) => response.text())
            .then((data) => {
                console.log('data', data)
                const parser = new DOMParser();
                const doc = parser.parseFromString(data, "text/html");
                const links = doc.querySelectorAll("a");

                imageList = Array.from(links)
                    .map((link) => link.getAttribute("href"))
                    .filter((href) => href.endsWith(".jpg") || href.endsWith(".jpeg"));

                // Populate the select element with image options
                populateImageSelect();

                // Set the default image to the last image in the list
                if (imageList.length > 0) {
                    updateDisplayedImage(imageList[imageList.length - 1]);
                }
            })
            .catch((error) => console.error("Error fetching images:", error));
    }

    // Function to populate the select element with image options
    function populateImageSelect() {
        imageList.forEach((image) => {
            const option = document.createElement("option");
            option.value = image;
            option.text = image;
            imageSelect.appendChild(option);
        });
        console.log('imageList', imageList)
    }

    // Function to update the displayed image
    function updateDisplayedImage(imagePath) {
        imageContainer.src = `/images/${imagePath}`;
        console.log('imageContainer.src', imageContainer.src)
    }

    // Event listener for the select element
    imageSelect.addEventListener("change", function () {
        const selectedImage = imageSelect.value;
        console.log('selectedImage', selectedImage)
        updateDisplayedImage(selectedImage);
    });

    // Event listener for the "Play" button
    playButton.addEventListener("click", function () {
        let currentIndex = 0;
        const playInterval = setInterval(function () {
            if (currentIndex >= imageList.length) {
                clearInterval(playInterval); // Stop playing when all images are displayed
            } else {
                const currentImage = imageList[currentIndex];
                updateDisplayedImage(currentImage);
                currentIndex++;
            }
            console.log('currentIndex', currentIndex)
        }, 1000); // Change images every 1 second
    });

    // Fetch the list of images when the page loads
    fetchImagesList();
});
