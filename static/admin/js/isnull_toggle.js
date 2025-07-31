(function () {
    document.addEventListener("DOMContentLoaded", function () {
        function setupToggle(container) {
            const operatorSelect = container.querySelector(".operator-select");
            const valueField = container.querySelector(".form-row.field-value");

            if (!operatorSelect || !valueField) return;

            function toggleField() {
                const operator = operatorSelect.value;

                if (operator === "is_null") {
                    valueField.style.display = "none";
                    valueField.querySelector("label").classList.remove("required");
                } else {
                    valueField.style.display = "";
                    valueField.querySelector("label").classList.add("required");
                }
            }

            toggleField();

            operatorSelect.addEventListener("change", toggleField);
        }

        const mainForm = document.querySelector("fieldset.module");

        if (mainForm) {
            setupToggle(mainForm);
        }

        const inlineForms = document.querySelectorAll(".inline-group .inline-related");

        inlineForms.forEach(setupToggle);

        document.addEventListener("formset:added", function (event) {
            setupToggle(event.target);
        });
    });
})();
