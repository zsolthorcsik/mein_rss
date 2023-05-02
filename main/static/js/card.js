
$(function () {
    run_card_js();
  });


  


  function run_card_js() {
    const card = $(".article_card");
    const description = $(".description_container");

    card.on("click", function (e) {
      const target = $(e.target);
      target.find(description).toggle("fast");
    });
  }