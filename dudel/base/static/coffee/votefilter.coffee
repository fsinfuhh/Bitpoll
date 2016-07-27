$.fn.setColumns = (columns, cls) ->
    result = false
    $(this).find("tr").each ->
        colnum = 0
        $(this).find("td, th").each ->
            $cell = $ this
            colspan = ($cell.attr("data-original-colspan") or $cell.attr("colspan") or "1").toNumber()

            visible = columns[colnum ... colnum+colspan].filter((x) -> x).length
            if visible > 0
                $cell.attr "data-original-colspan", $cell.attr "colspan"
                $cell.attr "colspan", visible
            else
                result = true
                $cell.addClass cls

            colnum += colspan
    return result

i18n.ready (gettext) ->
    $filterButton     = $ "#filter-button"
    $thresholdPercent = $ "#filter-threshold-percent"
    $thresholdCount   = $ "#filter-threshold-count"
    $btnApply         = $ "#filter-apply"
    $btnReset         = $ "#filter-reset"
    $table            = $ "#poll"
    $hideVotes        = $ "#filter-hide-votes input[type='radio']"
    $hideVotesFilter  = $ "#filter-hide-votes-filter"
    $choiceValues     = $ ".filter-choice-values"

    return if $filterButton.length == 0

    # Extract scores from table
    scores = []
    $(".choice-sum").each ->
        scores.push($(this).data("score")?.toNumber())

    return if not scores

    countToPercent = (count) ->
        sorted = scores.slice()
        sorted.sort()
        sorted.reverse()
        return 0 if sorted.length < count
        return sorted[count-1]

    filterColumns = (keepCount) ->
        threshold = $thresholdPercent.val().toNumber() / 100.0

        columnsThreshold = []

        # Apply score threshold
        thresholdCount = 0
        scores.forEach (score) ->
            visible = true
            if threshold and score < threshold
                visible = false
            else
                thresholdCount += 1
            columnsThreshold.push(visible)

        if keepCount != true
            $thresholdCount.val(thresholdCount)

        # Build table columns
        columns = [true]
        for i in [0...scores.length]
            columns.push(columnsThreshold[i])
        columns.push(true)

        $votes = $table.find("tr.vote")
        $choiceValues.each ->
            $in           = $ this
            $in.closest(".form-group").removeClass("has-error")
            choiceValueId = $in.attr "data-choice-value"

            value = $in.val()
            return if not value

            regex = null
            try
                regex = new RegExp($in.val(), "i")
            catch e
                $in.closest(".form-group").addClass("has-error")
                return

            $votes.each ->
                $vote = $ this
                author = $vote.data "author"
                return if not regex.test(author)
                for i in [0...scores.length]
                    value = $vote.find("td.vote-choice").eq(i).attr "data-choice-value"
                    if value != choiceValueId
                        columns[i+1] = false

        # Remove old filter, apply new filter
        $table.find("[data-original-colspan]").each ->
            $(this).attr "colspan", $(this).attr("data-original-colspan")
        $table.find(".filtered").removeClass("filtered")

        return $table.setColumns(columns, "filtered")

    filterVotes = ->
        # unfilter all
        $votes = $table.find("tr.vote")
        $votes.removeClass("filtered")
        $hideVotesFilter.closest(".form-group").removeClass("has-error")

        mode = $hideVotes.filter(":checked").val()
        filter = $hideVotesFilter.val()

        # These are simple
        if mode == "show-all" or (not filter and mode == "hide-filter")
            return false
        if mode == "hide-all" or (not filter and mode == "show-filter")
            $votes.addClass("filtered")
            return true

        filtered = false

        regex = null
        try
            regex = new RegExp(filter, "i")
        catch e
            $hideVotesFilter.closest(".form-group").addClass("has-error")
            return

        $votes.each ->
            $vote = $(this)
            author = $vote.data "author"
            matches = regex.test(author)
            visible = if mode == "show-filter" then matches else not matches
            if not visible
                filtered = true
                $vote.addClass("filtered")

        return filtered

    update = (keepCount) ->
        filtered = false

        filtered = true if filterColumns(keepCount)
        filtered = true if filterVotes()

        # Hide votes
        if filtered
            $filterButton.removeClass("btn-default").addClass("btn-warning")
        else
            $filterButton.removeClass("btn-warning").addClass("btn-default")


    updateCount = ->
        count = $thresholdCount.val().toNumber()
        threshold = countToPercent(count)
        $thresholdPercent.val Math.floor(threshold*100)
        update(true)

    reset = ->
        $thresholdPercent.val ""
        $thresholdCount.val ""
        $hideVotes.filter("[value='show-all']").prop "checked", true
        update()

    $thresholdPercent.on "keyup", update
    $thresholdCount.on   "keyup", updateCount
    $hideVotes.on        "click", update
    $hideVotesFilter.on  "keyup", update
    $choiceValues.on     "keyup", update
    $btnApply.on         "click", update
    $btnReset.on         "click", reset

    update()
