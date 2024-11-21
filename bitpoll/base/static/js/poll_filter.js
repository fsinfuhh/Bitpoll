var scores;

$(function() {
    // Collect scores for all vote choices
    scores = []
    $("#scores .choice-sum").each(function () {
        // "n/a" should be treated like 0%
        scores.push(parseFloat($(this).data("score")) || 0.0);
    });

    // Event handler
    $("#filter-threshold-percent").on("input", filterUpdatePercent);
    $("#filter-threshold-count").on("input", filterUpdateCount);
    $("#filter-apply").on("click", filterUpdatePercent);
    $("#filter-reset").on("click", filterReset);

    // Fill form inputs with total count
    filterReset();
});

function filterColumns(keepCount) {
    var threshold = $("#filter-threshold-percent").val() || 0.0;

    // Identify filtered columns
    var count = 0;
    var filteredColumns = [true]; // Always show first column (vote author)
    scores.forEach(function (score) {
        if (score >= threshold) {
            filteredColumns.push(true);
            count++;
        } else {
            filteredColumns.push(false);
        }
    });
    filteredColumns.push(true); // Always show last column (edit, impersonate)

    if (!keepCount) {
        $("#filter-threshold-count").val(count);
    }

    filterSetVisibleColumns(filteredColumns);

    return count != scores.length;
}

function filterCountToPercent(count) {
    if (count <= 0) return 100;
    if (scores.length <= count) return 0;
    var sorted = scores.slice();
    sorted.sort((a, b) => a - b);
    return sorted[sorted.length - count];
}

function filterReset() {
    // count will be automatically set by filterUpdate
    $("#filter-threshold-percent").val(0);
    filterUpdate();
}

function filterSetVisibleColumns(columns) {
    // Remove old filtering
    $("[data-original-colspan]").each(function () {
        $(this).attr("colspan", $(this).attr("data-original-colspan"));
    });
    $(".filtered").removeClass("filtered");

    // Set new filtering
    $("#poll tr").each(function () {
        var columnIdx = 0;
        $(this).find("td, th").each(function () {
            var colspan = parseInt($(this).attr("data-original-colspan") ?? $(this).attr("colspan") ?? "1");

            var visible = columns.slice(columnIdx, columnIdx + colspan).filter(x => x).length;
            if (visible > 0) {
                $(this).attr("data-original-colspan", $(this).attr("colspan"));
                $(this).attr("colspan", visible);
            } else {
                $(this).addClass("filtered");
            }

            columnIdx += colspan;
        });
    });
}

function filterUpdate(keepCount) {
    var isFiltered = filterColumns(keepCount)

    if (isFiltered) {
        $("#filterLink").addClass("hidden");
        $("#filterLinkWarning").removeClass("hidden");
    } else {
        $("#filterLink").removeClass("hidden");
        $("#filterLinkWarning").addClass("hidden");
    }
}

function filterUpdateCount() {
    var count = parseInt($("#filter-threshold-count").val());
    var threshold = filterCountToPercent(count);
    $("#filter-threshold-percent").val(threshold);
    filterUpdate(true);
}

function filterUpdatePercent() {
    filterUpdate(false);
}
