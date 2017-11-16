// language=JQuery-CSS
(function () {
    $(function () {
        $('#create-type-field').customSelect($('#create-type-list').find('li'));
        return $("#advanced-toggle").click(function () {
            var advanced_toggle = $('#advanced-toggle');
            var advanced_open = $('#advanced-open');
            advanced_toggle.find(".more").toggleClass("hidden");
            advanced_toggle.find(".less").toggleClass("hidden");
            $("#advanced-closed").toggleClass("hidden");
            advanced_open.toggleClass("hidden");
            advanced_open.hide().fadeIn(); // bit of effect
            return false;
        });
    });

}).call();
