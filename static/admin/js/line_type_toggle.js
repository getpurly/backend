(function () {
    document.addEventListener("DOMContentLoaded", function () {
        function setupToggle(container) {
            const lineTypeSelect = container.querySelector(".line_type-select");
            const quantityValue = container.querySelector(".form-row.field-quantity");
            const unitOfMeasureValue = container.querySelector(".form-row.field-unit_of_measure");
            const unitPriceValue = container.querySelector(".form-row.field-unit_price");
            const lineTotalValue = container.querySelector(".form-row.field-line_total");

            if (!lineTypeSelect || !quantityValue || !unitOfMeasureValue || !unitPriceValue || !lineTotalValue) return;

            function toggleFields() {
                const lineType = lineTypeSelect.value;

                if (lineType === "service") {
                    quantityValue.style.display = "none";
                    quantityValue.querySelector("label").classList.remove("required");

                    unitOfMeasureValue.style.display = "none";
                    unitOfMeasureValue.querySelector("label").classList.remove("required");

                    unitPriceValue.style.display = "none";
                    unitPriceValue.querySelector("label").classList.remove("required");

                    lineTotalValue.style.display = "";
                    lineTotalValue.querySelector("label").classList.add("required");

                } else {
                    quantityValue.style.display = "";
                    quantityValue.querySelector("label").classList.add("required");

                    unitOfMeasureValue.style.display = "";
                    unitOfMeasureValue.querySelector("label").classList.add("required");

                    unitPriceValue.style.display = "";
                    unitPriceValue.querySelector("label").classList.add("required");

                    lineTotalValue.style.display = "none";
                    lineTotalValue.querySelector("label").classList.remove("required");
                }
            }

            toggleFields();

            lineTypeSelect.addEventListener("change", toggleFields);
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