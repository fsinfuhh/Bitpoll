// language=JQuery-CSS
(function() {
  $.fn.slider = function(options) {
    options = options || {};
    return $(this).each(function() {
      var $container, $tbl, maximum, minimum, step;
      $container = $(this);
      $tbl = $("table.vote");
      minimum = options.minimum || $tbl.data("minimum") || 0;
      maximum = options.maximum || $tbl.data("maximum") || 100;
      step = options.step || $tbl.data("step") || 1;
      return $('.slider').each(function() {
        var $slider;
        $slider = $(this);
        return $slider.jRange({
          from: minimum,
          to: maximum,
          step: step,
          theme: "theme-blue",
          width: 300,
          showLabels: true
        });
      });
    });
  };

  $(function() {
    return $(".slider").slider();
  });

}).call();
