

$(document).ready(function() {
    $('.card').on('click', function(event) {
      $(this).find('.article-description').slideToggle();
    })
    $('.slidable p').on('click', function(event) {
      $('.slidable').find('.slidable-content').slideToggle();
    })
    
  
    $('#search_button, #mobile_search_button').click(function() {
      $('.search_holder').toggleClass("hidden");      
      if (!$('.search_holder').hasClass('hidden')) {        
        $('input[name="kereses"]')[0].focus()
      }});
    
    })