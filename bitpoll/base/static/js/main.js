window.addEventListener('DOMContentLoaded', function () {
    // Show elements that were hidden by CSS `.script-only` class
    hide_elems_selector(".script-hidden")
    get_elems(".script-only").forEach(function (el) {
        el.style.display = "block"
    });
    get_elems("a.script-only").forEach(function (el) {
        el.style.display = "inline-block"
    });
    get_elems("button.script-only").forEach(function (el) {
        el.style.display = "inline-block"
    });
    get_elems("td.script-only").forEach(function (el) {
        el.style.display = "table-cell"
    });
    get_elems("tr.script-only").forEach(function (el) {
        el.style.display = "table-row"
    });
    get_elems("table.script-only").forEach(function (el) {
        el.style.display = "table"
    });

    get_elems(".icon-preview button").forEach(function (el) {
        el.addEventListener('click', function () {
            get_elem("#id_icon").value = this.dataset.icon;
        });
    });
});

