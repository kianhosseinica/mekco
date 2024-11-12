const burger = document.querySelector('.burger');
const mobileMenu = document.querySelector('.mobile-menu');
const clearSearch = document.getElementById('clearSearch');
const mobileSearch = document.getElementById('mobileSearch');

burger.addEventListener('click', () => {
    mobileMenu.classList.toggle('nav-active');
    burger.classList.toggle('toggle');
});

clearSearch.addEventListener('click', () => {
    mobileSearch.value = '';
    clearSearch.style.display = 'none';
});

mobileSearch.addEventListener('input', () => {
    clearSearch.style.display = mobileSearch.value ? 'inline' : 'none';
});

// Cart Balance Tab
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Function to update the tab value
function updateTab(value) {
    const fixedTab = document.getElementById('fixed-tab');
    fixedTab.textContent = formatCurrency(value);
    if (value > 0) {
        fixedTab.classList.add('show');
    } else {
        fixedTab.classList.remove('show');
    }
}

(function($) {
  $.fn.currencyInput = function() {
    this.each(function() {
      var wrapper = $("<div class='currency-input' />");
      $(this).wrap(wrapper);
      $(this).before("<span class='currency-symbol'>$</span>");
      $(this).change(function() {
        var min = parseFloat($(this).attr("min"));
        var max = parseFloat($(this).attr("max"));
        var value = this.valueAsNumber;
        if(value < min)
          value = min;
        else if(value > max)
          value = max;
        $(this).val(value.toFixed(2)); 
      });
    });
  };
})(jQuery);

$(document).ready(function() {
  $('input.currency').currencyInput();
});

/*add the JavaScript to handle the sliding functionality on touch:*/
(function ($) {
    $.fn.tabSlideOut = function (callerSettings) {
        var settings = $.extend({
            tabHandle: '.handle',
            speed: 300,
            action: 'click',
            tabLocation: 'left',
            topPos: '200px',
            leftPos: '20px',
            fixedPosition: false,
            positioning: 'absolute',
            pathToTabImage: null,
            imageHeight: null,
            imageWidth: null,
            onLoadSlideOut: false
        }, callerSettings || {});

        settings.tabHandle = $(settings.tabHandle);
        var obj = this;
        if (settings.fixedPosition === true) {
            settings.positioning = 'fixed';
        } else {
            settings.positioning = 'absolute';
        }

        //ie6 doesn't do well with the fixed option
        if (document.all && !window.opera && !window.XMLHttpRequest) {
            settings.positioning = 'absolute';
        }



        //set initial tabHandle css

        if (settings.pathToTabImage != null) {
            settings.tabHandle.css({
                'background': 'url(' + settings.pathToTabImage + ') no-repeat',
                    'width': settings.imageWidth,
                    'height': settings.imageHeight
            });
        }

        settings.tabHandle.css({
            'display': 'block',
                'textIndent': '-99999px',
                'outline': 'none',
                'position': 'absolute'
        });

        obj.css({
            'line-height': '1',
                'position': settings.positioning
        });


        var properties = {
            containerWidth: parseInt(obj.outerWidth(), 10) + 'px',
            containerHeight: parseInt(obj.outerHeight(), 10) + 'px',
            tabWidth: parseInt(settings.tabHandle.outerWidth(), 10) + 'px',
            tabHeight: parseInt(settings.tabHandle.outerHeight(), 10) + 'px'
        };

        //set calculated css
        if (settings.tabLocation === 'top' || settings.tabLocation === 'bottom') {
            obj.css({
                'left': settings.leftPos
            });
            settings.tabHandle.css({
                'right': 0
            });
        }

        if (settings.tabLocation === 'top') {
            obj.css({
                'top': '-' + properties.containerHeight
            });
            settings.tabHandle.css({
                'bottom': '-' + properties.tabHeight
            });
        }

        if (settings.tabLocation === 'bottom') {
            obj.css({
                'bottom': '-' + properties.containerHeight,
                'position': 'fixed'
            });
            settings.tabHandle.css({
                'top': '-' + properties.tabHeight
            });

        }

        if (settings.tabLocation === 'left' || settings.tabLocation === 'right') {
            obj.css({
                'height': properties.containerHeight,
                    'top': settings.topPos
            });

            settings.tabHandle.css({
                'top': 0
            });
        }

        if (settings.tabLocation === 'left') {
            obj.css({
                'left': '-' + properties.containerWidth
            });
            settings.tabHandle.css({
                'right': '-' + properties.tabWidth
            });
        }

        if (settings.tabLocation === 'right') {
            obj.css({
                'right': '-' + properties.containerWidth
            });
            settings.tabHandle.css({
                'left': '-' + properties.tabWidth
            });

            $('html').css('overflow-x', 'hidden');
        }

        //functions for animation events

        settings.tabHandle.click(function (event) {
            event.preventDefault();
        });

        var slideIn = function () {

            if (settings.tabLocation === 'top') {
                obj.animate({
                    top: '-' + properties.containerHeight
                }, settings.speed, settings.onSlideIn).removeClass('open');
            } else if (settings.tabLocation === 'left') {
                obj.animate({
                    left: '-' + properties.containerWidth
                }, settings.speed, settings.onSlideIn).removeClass('open');
            } else if (settings.tabLocation === 'right') {
                obj.animate({
                    right: '-' + properties.containerWidth
                }, settings.speed, settings.onSlideIn).removeClass('open');
            } else if (settings.tabLocation === 'bottom') {
                obj.animate({
                    bottom: '-' + properties.containerHeight
                }, settings.speed, settings.onSlideIn).removeClass('open');
            }

        };

        var slideOut = function () {

            if (settings.tabLocation == 'top') {
                obj.animate({
                    top: '-3px'
                }, settings.speed, settings.onSlideOut).addClass('open');
            } else if (settings.tabLocation == 'left') {
                obj.animate({
                    left: '-3px'
                }, settings.speed, settings.onSlideOut).addClass('open');
            } else if (settings.tabLocation == 'right') {
                obj.animate({
                    right: '-3px'
                }, settings.speed, settings.onSlideOut).addClass('open');
            } else if (settings.tabLocation == 'bottom') {
                obj.animate({
                    bottom: '-3px'
                }, settings.speed, settings.onSlideOut).addClass('open');
            }

            settings.onSlideOut
        };

        var clickScreenToClose = function () {
            obj.click(function (event) {
                event.stopPropagation();
            });

            $(document).click(function () {
                slideIn();
            });
        };

        var clickAction = function () {
            settings.tabHandle.click(function (event) {
                if (obj.hasClass('open')) {
                    slideIn();
                } else {
                    slideOut();
                }
            });

            clickScreenToClose();
        };

        var hoverAction = function () {
            obj.hover(

            function () {
                slideOut();
            },

            function () {
                slideIn();
            });

            settings.tabHandle.click(function (event) {
                if (obj.hasClass('open')) {
                    slideIn();
                }
            });
            clickScreenToClose();

        };

        var slideOutOnLoad = function () {
            slideIn();
            setTimeout(slideOut, 500);
        };

        //choose which type of action to bind
        if (settings.action === 'click') {
            clickAction();
        }

        if (settings.action === 'hover') {
            hoverAction();
        }

        if (settings.onLoadSlideOut) {
            slideOutOnLoad();
        };

    };
})(jQuery);

$(function () { 
    
    $('.slide-out-div').tabSlideOut({
        tabHandle: '.handle', //class of the element that will become your tab
        pathToTabImage: 'http://wpaoli.building58.com/wp-content/uploads/2009/09/contact_tab.gif', //path to the image for the tab //Optionally can be set using css
        imageHeight: '122px', //height of tab image           //Optionally can be set using css
        imageWidth: '40px', //width of tab image            //Optionally can be set using css
        tabLocation: 'left', //side of screen where tab lives, top, right, bottom, or left
        speed: 300, //speed of animation
        action: 'click', //options: 'click' or 'hover', action to trigger animation
        topPos: '200px', //position from the top/ use if tabLocation is left or right
        leftPos: '20px', //position from left/ use if tabLocation is bottom or top
        fixedPosition: false //options: true makes it stick(fixed position) on scroll
    });
    
    $('.slide-out-div > .handle').click();

});

//Slide Tab
function openTab() {
    document.getElementById("slideTab").style.width = "100%";
    document.getElementById("slideTab").style.padding = "60px 10px";
}

function closeTab() {
    document.getElementById("slideTab").style.width = "0";
    document.getElementById("slideTab").style.padding = "0px";
}

//Single Product Page
$(document).ready(function(){
    $('.thumbnail').click(function(){
        var newSrc = $(this).attr('src');
        $('#main-product-image').attr('src', newSrc);
    });
});