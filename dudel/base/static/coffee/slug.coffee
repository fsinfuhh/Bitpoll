makeRandomString = (length) ->
    text = ""
    possible = "ABCDEFGHJKLMNPQRTUVWXYZabcdefghjkmnpqrstuvwxyz0123456789"

    for i in [0...length]
        text += possible.charAt(Math.floor(Math.random() * possible.length))

    return text

$ ->
    $randomizeButton = $ '#slug-randomize'
    $title           = $ '#title-input'
    $slugInput       = $ '#slug-input'

    # Check if we are on a page with a slug input
    return if $title.length == 0

    update = (random) ->
        title     = $title.val()

        if RANDOM_SLUGS or random or not title
            slug = makeRandomString 8
        else
            slug = get_slug title

        $slugInput.val slug

    updateTitle = ->
        update(false)
        return false

    updateRandom = ->
        update(true)
        return false


    # Bind events
    $randomizeButton.on "click", updateRandom
    $title.on "input", updateTitle
    update(false)
