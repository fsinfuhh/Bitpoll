// language=JQuery-CSS
(function () {
    $(function () {
        $("[data-toggle-class], [data-remove-class], [data-add-class]").click(function (e) {
            var $target, target;
            target = $(this).data("target");
            $target = target ? $(target) : $(this);
            if ($(this).data('toggle-class')) {
                $target.toggleClass($(this).data('toggle-class'));
            }
            if ($(this).data('add-class')) {
                $target.addClass($(this).data('add-class'));
            }
            if ($(this).data('remove-class')) {
                $target.removeClass($(this).data('remove-class'));
            }
            return e.preventDefault();
        });

        return $('[data-shortcut]').each(function () {
            var $element, shortcuts;
            $element = $(this);
            shortcuts = $element.data('shortcut').split("|");
            return Mousetrap.bind(shortcuts, function () {
                return $element[0].click();
            });
        });
    });

}).call();
