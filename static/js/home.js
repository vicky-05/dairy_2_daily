            // Array of image URLs
            const images = [
                "{% static 'images/DAIRY_TO_DAILY_UPDATED-1.png' %}",
                "{% static 'images/ghee-product.png' %}",
                "{% static 'images/curd-23 (2).png' %}",
                "{% static 'images/panner-our-product-slider.png' %}",
                "{% static 'images/milky-cow-cartoon.png' %}",
            ];

            let currentImageIndex = 0; // Track the current image index
            const imageElement = document.getElementById("slideshow-image");

            // Function to change the image
            function changeImage() {
                imageElement.classList.add("fade-out"); // Add fade-out animation

                setTimeout(() => {
                    // Change the image source
                    currentImageIndex = (currentImageIndex + 1) % images.length;
                    imageElement.src = images[currentImageIndex];

                    // Add the fade-in class and remove fade-out
                    imageElement.classList.remove("fade-out");
                    imageElement.classList.add("fade-in");

                    // Remove the fade-in class after animation
                    setTimeout(() => imageElement.classList.remove("fade-in"),500);
                }, 500); // Wait for fade-out animation to complete
            }

            // Change image every 5 seconds
            setInterval(changeImage, 5000);