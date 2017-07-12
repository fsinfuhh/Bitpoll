$ ->
    $("[data-toggle-class], [data-remove-class], [data-add-class]").click (e) ->
        target = $(this).data("target")
        $target = if target then $(target) else $(this)

        if $(this).data('toggle-class')
            $target.toggleClass($(this).data('toggle-class'))

        if $(this).data('add-class')
            $target.addClass($(this).data('add-class'))

        if $(this).data('remove-class')
            $target.removeClass($(this).data('remove-class'))

        e.preventDefault()

    # Mousetrap.bind 'f', ->
    #     console.log 'triggereds'
    #     $("#poll-container").toggleClass("fullscreen")

    $('[data-shortcut]').each ->
        $element = $(this)
        shortcuts = $element.data('shortcut').split("|")

        Mousetrap.bind shortcuts, ->
            $element[0].click()

