/* ==========================================================================
   ArmWork Freelancer Dashboard Script
   Կառավարում է ֆրիլանսերի էջի «Դիմել աշխատանքին» աջից բացվող panel-ը։
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const applyButtons = document.querySelectorAll(".jobs-list .btn-apply");
    const panelOverlay = document.getElementById("panelOverlay");
    const applyPanel = document.getElementById("applyPanel");
    const closePanelBtn = document.getElementById("closePanelBtn");
    const cancelPanelBtn = document.getElementById("cancelPanelBtn");

    if (!panelOverlay || !applyPanel || !closePanelBtn || !cancelPanelBtn) return;

    function openPanel() {
        document.body.classList.add("panel-open");
        panelOverlay.classList.add("active");
        applyPanel.classList.add("active");
    }

    function closePanel() {
        document.body.classList.remove("panel-open");
        panelOverlay.classList.remove("active");
        applyPanel.classList.remove("active");
    }

    applyButtons.forEach(function (button) {
        button.addEventListener("click", openPanel);
    });

    closePanelBtn.addEventListener("click", closePanel);
    cancelPanelBtn.addEventListener("click", closePanel);
    panelOverlay.addEventListener("click", closePanel);
});
