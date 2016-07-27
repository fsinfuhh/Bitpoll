$.fn.slider = (options) ->
    options = options or {}

    $(this).each ->
        $container = $ this
        $tbl = $("table.vote")

        minimum  = options.minimum  or $tbl.data("minimum")  or 0
        maximum  = options.maximum  or $tbl.data("maximum")  or 100
        step     = options.step     or $tbl.data("step")     or 1
        # tickstep = options.tickstep or $tbl.data("tickstep") or 1
        # format   = options.format   or $tbl.data("format")   or "normal"

        $('.slider').each ->
            $slider = $ this
            $slider.jRange
                from: minimum
                to: maximum
                step: step
                # scale: [0,25,50,75,100]
                # format: '%s'
                theme: "theme-blue"
                width: 300
                showLabels: true

$ ->
    $(".slider").slider()
