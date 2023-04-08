$('#load_more_button').click(function() {

    loadArticles("Running");
})

function loadArticles() {

var page = $('#load_more_button').data("page-id");
var slug = $('#load_more_button').data("slug");
var perPage = 2;
$.ajax({    
  url: "/" + slug + "/?page=" + page + "&per_page=" + perPage,
  success: function(data) {            
    var html = '';
    for (var i = 0; i < data.length; i++) {             
      var article = data[i]      
      html += '<div class="article_card" style="--background_url: url(' + article.image + ');">';
    html += '<div class="article_card_content">';
    html += '<h4 class="article_title"><a href="' + article.link + '">' + article.title + '</a></h4>';
    html += '<div class="article_agent_and_datum"><a href="/feed/' + article.source_slug + '">' + article.source + '</a>  <span class="published"><span>| </span>' + article.date_published + '</span></div>';
    html += '<div class="description_container">';    
    if (article.description.length >= 220) {
    html += '<p class="article_description">' + article.description.slice(0,220) + '... </p>';
    } else {
    html += '<p class="article_description">' + article.description.slice(0,220) + '</p>';
    }
    html += '<a class="btn_read_more" href="' + article.link + '" target="_blank">Elolvasom</a>';
    html += '</div></div></div>';
    }
    $('#articles_holder').append(html);
    page++;
    $('#load_more_button').data("page-id", page)
  }
});
}

