function toggleDescription(id) {
  var dots = document.getElementById("dots-" + id);
  var moreText = document.getElementById("more-" + id);
  var btnText = document.getElementById("toggleBtn-" + id);

  if (dots.style.display === "none") {
    dots.style.display = "inline";
    btnText.innerHTML = "Show more";
    moreText.style.display = "none";
  } else {
    dots.style.display = "none";
    btnText.innerHTML = "Show less";
    moreText.style.display = "inline";
  }
}
