$(document).ready(function () {
    $('input[type=radio]').change(
        function () {
            var clickedRadio = this;
            var afterClickedRadio = false;

            var radios = document.querySelectorAll('input[type=radio]');

            for (i = 0; i < radios.length; ++i) {
                var radio = radios[i];

                if (radio === clickedRadio) {
                    afterClickedRadio = true;
                    continue;
                }

                if (!afterClickedRadio && clickedRadio.value === 'Risky' && radio.value === 'Risky') {
                    radio.checked = true;
                }
                if (afterClickedRadio && clickedRadio.value === 'Safe' && radio.value === 'Safe') {
                    radio.checked = true;
                }
            }
        }
    );
});