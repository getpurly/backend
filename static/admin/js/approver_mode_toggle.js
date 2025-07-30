(function () {
    document.addEventListener("DOMContentLoaded", function () {
        const modeSelect = document.querySelector("#id_approver_mode");
        const approverField = document.querySelector(".form-row.field-approver");
        const approverGroupField = document.querySelector(".form-row.field-approver_group");

        function toggleFields() {
            const mode = modeSelect.value;

            if (mode === "individual") {
                approverField.style.display = "";
                approverGroupField.style.display = "none";

                approverField.querySelector("label").classList.add("required");
                approverGroupField.querySelector("label").classList.remove("required");
            } else {
                approverField.style.display = "none";
                approverGroupField.style.display = "";

                approverGroupField.querySelector("label").classList.add("required");
                approverField.querySelector("label").classList.remove("required");
            }
        }

        if (modeSelect && approverField && approverGroupField) {
            toggleFields();

            modeSelect.addEventListener("change", toggleFields);
        }

    });
})();
