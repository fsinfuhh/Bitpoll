$ ->
    $('#create-type-field').customSelect $('#create-type-list li')

    $("#advanced-toggle").click ->
        $("#advanced-toggle .more").toggleClass("hidden")
        $("#advanced-toggle .less").toggleClass("hidden")
        $("#advanced-closed").toggleClass("hidden")
        $("#advanced-open").toggleClass("hidden")
        $("#advanced-open").hide().fadeIn() # bit of effect
        false
