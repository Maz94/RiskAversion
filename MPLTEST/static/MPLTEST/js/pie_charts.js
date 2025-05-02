

function showExternality(element, option, externality) {
    const popup = element.closest('td').querySelector('.popup');

    if (popup) {
        // Update content
        const sign = (externality > 0) ? '+' : '';
        popup.innerHTML = `<span>${sign}${externality}€</span>`;

        // Apply color based on externality
        popup.classList.remove('positive', 'negative', 'evaporated');
        popup.classList.add(externality > 0 ? 'positive' : 'negative');

        // Reset and apply animation
        popup.style.animation = 'none';
        popup.offsetHeight;  // Trigger reflow to reset animation
        popup.style.animation = 'pulse 0.5s ease-in-out, slideUpEvaporate 1.5s forwards';

        popup.classList.add('show');

        // Ensure it remains hidden after animation
        setTimeout(() => {
            popup.classList.remove('show');
            popup.classList.add('evaporated');  // Ensures it stays invisible
        }, 2000);
    } else {
        console.error('Popup element not found');
    }
}

document.querySelectorAll('.info-icon').forEach(icon => {
    icon.addEventListener('mouseenter', () => {
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.innerHTML = icon.getAttribute('title');
        document.body.appendChild(tooltip);

        const rect = icon.getBoundingClientRect();
        tooltip.style.left = `${rect.right + 10}px`;
        tooltip.style.top = `${rect.top}px`;
    });

    icon.addEventListener('mouseleave', () => {
        document.querySelector('.custom-tooltip').remove();
    });
});
document.querySelectorAll('input[type="radio"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
        const selectedExternality = this.nextElementSibling.querySelector('.externality-display span').getAttribute('value');
        console.log('Selected Externality:', selectedExternality);  // Logs +5 or -5
    });
});
function initializeTimer() {
    console.log("Initializing timer script...");

    function waitForElements() {
        const timerElement = document.getElementById("circle-timer-text");
        const progressCircle = document.getElementById("progress-circle");
        const nextButton = document.getElementById("next-button");
        const timerMessage = document.getElementById("timer-message");

        if (!timerElement || !progressCircle || !nextButton || !timerMessage) {
            console.log("Elements not found, retrying in 500ms...");
            setTimeout(waitForElements, 500); // Retry every 500ms
            return;
        }

        console.log("Timer elements found, starting countdown...");
        startCountdown(timerElement, progressCircle, nextButton, timerMessage);
    }

    waitForElements(); // Start checking for elements
}

function startCountdown(timerElement, progressCircle, nextButton, timerMessage) {
    let countdown = parseInt(timerElement.textContent);
    const totalTime = countdown;
    const radius = 50; // Match the radius from SVG
    const circumference = 2 * Math.PI * radius; // Properly calculate circumference

    progressCircle.style.strokeDasharray = `${circumference}`;
    progressCircle.style.strokeDashoffset = `${circumference}`;
    progressCircle.style.stroke = "red";
    nextButton.disabled = true;

    function updateCountdown() {
        if (countdown > 0) {
            countdown -= 1;
            timerElement.textContent = countdown;

            const progressPercentage = (totalTime - countdown) / totalTime;
            const strokeOffset = circumference * (1 - progressPercentage);
            progressCircle.style.strokeDashoffset = `${strokeOffset}`;

            if (progressPercentage < 0.25) {
                progressCircle.style.stroke = "red";
            } else if (progressPercentage < 0.50) {
                progressCircle.style.stroke = "orange";
            } else if (progressPercentage < 0.75) {
                progressCircle.style.stroke = "yellow";
            } else {
                progressCircle.style.stroke = "green";
            }
        } else {
            timerElement.textContent = "Terminé!";
            progressCircle.style.strokeDashoffset = "0";
            progressCircle.style.stroke = "green";
            nextButton.disabled = false;

            timerMessage.textContent = "Vous pouvez accéder à la page suivante !";
            timerMessage.style.color = "green";

            clearInterval(timerInterval);
            console.log("Terminé !");
        }
    }

    const timerInterval = setInterval(updateCountdown, 1000);
}

document.addEventListener("DOMContentLoaded", initializeTimer);
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".slider").forEach(slider => {
            let output = document.getElementById(slider.id + "_value");

            // Position the value dynamically
            function updateSliderValue() {
                output.innerText = slider.value;
                let percent = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
                output.style.left = `calc(${percent}% - 10px)`; // Adjust position dynamically
            }

            // Initial update
            updateSliderValue();

            // Update value on input change
            slider.addEventListener("input", updateSliderValue);
        });
    });

document.addEventListener("DOMContentLoaded", function () {
        let sliders = document.querySelectorAll(".form-range");
        let submitButton = document.getElementById("next-button");

        sliders.forEach(slider => {
            slider.addEventListener("input", function () {
                submitButton.disabled = false;
            });
        });
    });
document.addEventListener("DOMContentLoaded", function () {
    const earningsField = document.querySelector('[name="first_session_earnings"]');
    const broughtField = document.querySelector('[name="amount_brought"]');
    const reasonField = document.querySelector('[name="reason_for_difference"]');
    const submitButton = document.querySelector('#next-button');

    function validateReason() {
        let earnings = parseFloat(earningsField.value) || 0;
        let brought = parseFloat(broughtField.value) || 0;
        let reason = reasonField.value.trim();

        if (earnings !== brought) {
            if (reason.length < 10) {
                reasonField.setCustomValidity("Veuillez écrire au moins 10 caractères.");
            } else {
                reasonField.setCustomValidity("");
            }
        } else {
            reasonField.setCustomValidity("");
        }

        submitButton.disabled = !document.querySelector("form").checkValidity();
    }

    earningsField.addEventListener("input", validateReason);
    broughtField.addEventListener("input", validateReason);
    reasonField.addEventListener("input", validateReason);
});