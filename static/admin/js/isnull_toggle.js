(function () {
    document.addEventListener("DOMContentLoaded", function () {
        const operatorSelect = document.querySelector("#id_operator");
        const valueField = document.querySelector(".form-row.field-value");

        function toggleField() {
            const operator = operatorSelect.value;

            if (operator === "is_null") {
                valueField.style.display = "none"

                valueField.querySelector("label").classList.remove("required");
            } else {
                valueField.style.display = ""

                valueField.querySelector("label").classList.add("required");
            }
        }

        if (operatorSelect && valueField) {
            toggleField()

            operatorSelect.addEventListener("change", toggleField)
        }
    });
})();
