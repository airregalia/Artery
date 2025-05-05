document.getElementById("get-location").addEventListener("click", () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          document.getElementById("latitude").value = position.coords.latitude;
          document.getElementById("longitude").value = position.coords.longitude;
          document.getElementById("depth").value = position.coords.depth;
        },
        (error) => {
          alert("Unable to retrieve location. Please try again.");
        }
      );
    } else {
      alert("Geolocation is not supported by your browser.");
    }
  });
  
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("predictionForm");
    const resultDiv = document.getElementById("results");
    const loadingDiv = document.getElementById("loading");
    const submitButton = form.querySelector('input[type="submit"]');

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        // Disable submit and show loading
        submitButton.disabled = true;
        loadingDiv.style.display = 'block';
        resultDiv.style.display = 'none';
        resultDiv.innerHTML = "";
        const generalLocation = parseInt(document.getElementById("generalLocation").value, 10);
        const latitude = parseFloat(document.getElementById("latitude").value);
        const longitude = parseFloat(document.getElementById("longitude").value);
        const depth = parseFloat(document.getElementById("depth").value);

        const payload = {
            general_location: generalLocation,
            latitude: latitude,
            longitude: longitude,
            depth: depth
        };

        try {
            const response = await fetch("/predict-depths", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });
            
            if (response.ok) {
                const data = await response.json();
                resultDiv.innerHTML = "<h3>Predictions:</h3>";

                // Apply color coding based on prediction
                
                resultDiv.style.display = 'block';
                data.predictions.forEach((prediction) => {
                    let predictionClass = ''; // Assign color class based on prediction type 
                    if (prediction.prediction === 'I') { 
                        predictionClass = 'result-I'; 
                        prediction.prediction="High"
                    } 
                    else if (prediction.prediction === 'II') {
                         predictionClass = 'result-II';
                        prediction.prediction="Moderate"
                    }
                    else if (prediction.prediction === 'III') { 
                        predictionClass = 'result-III';
                        prediction.prediction="Low" 
                    } 
                    resultDiv.innerHTML += ` <div class="result-item"> <div class="depth">${prediction.depth} ft</div> <div class="prediction ${predictionClass}"> ${prediction.prediction} Risk</div> </div>`;
                });
            } else {
                resultDiv.innerHTML = `<p>Error: Unable to fetch predictions.</p>`;
            }
        } catch (error) {
            resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
        } finally {
            // Always hide loading and re-enable submit
            loadingDiv.style.display = 'none';
            submitButton.disabled = false;
        }
    });
});
