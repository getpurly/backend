(function () {
    document.addEventListener("DOMContentLoaded", function () {
        const approverMode = document.querySelector("#id_approver_mode");
        const approverField = document.querySelector(".form-row.field-approver");
        const approverGroupField = document.querySelector(".form-row.field-approver_group");
        const approverGroupModeField = document.querySelector(".form-row.field-group_mode");

        function toggleFields() {
            const mode = approverMode.value;

            if (mode === "individual") {
                approverField.style.display = "";
                approverGroupField.style.display = "none";
                approverGroupModeField.style.display = "none";

                approverField.querySelector("label").classList.add("required");
                approverGroupField.querySelector("label").classList.remove("required");
                approverGroupModeField.querySelector("label").classList.remove("required");
            } else {
                approverField.style.display = "none";
                approverGroupField.style.display = "";
                approverGroupModeField.style.display = "";

                approverField.querySelector("label").classList.remove("required");
                approverGroupField.querySelector("label").classList.add("required");
                approverGroupModeField.querySelector("label").classList.add("required");
            }
        }

        if (approverMode && approverField && approverGroupField && approverGroupModeField) {
            toggleFields();

            approverMode.addEventListener("change", toggleFields);
        }

    });
})();
