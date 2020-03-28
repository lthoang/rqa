import pandas as pd
from string import Template

htmlTemplate = Template(
    """<!DOCTYPE html>
<html>

<head>
  <meta charset='utf-8'>
  <title>Visualize User Review with Product Question-Answer pair</title>
  <link rel='stylesheet' type='text/css' media='screen' href='assets/main.css'>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
  <script src='assets/main.js'></script>
</head>

<body>
$body
</body>

</html>"""
)


imgTemplate = Template('<!-- <div class="gallery"><img class="lazy" src="placeholder-image.jpg" data-src="$imgUrl" data-srcset="image-to-lazy-load-2x.jpg 2x, image-to-lazy-load-1x.jpg 1x"></div> -->')

descriptionTemplate = Template(
    """<p>$firstText<span id="dots-$asin-$reviewerID">...</span><span id="more-$asin-$reviewerID" style="display:none">$moreText</p><button onclick="toggleDescription('$asin-$reviewerID')" id="toggleBtn-$asin-$reviewerID">Show more</button>
"""
)

ratingStarTemplate = Template('<span class="fa fa-star $checked"></span>')

reviewTextTemplate = Template("$beforeMark<mark>$markedText</mark>$afterMark")

elementTemplate = Template(
    """<div class="group">
    <div class="product">
      <div class="title">$title</div>
      <div class="asin">$asin</div>

      <div class="product-images">
        $images
      </div>
      <div class="description">
        $description
      </div>
    </div>

    <div class="review">
      <div class="reviewInfo">
        <span class="reviewerName">$reviewerName</span>
        <span class="reviewerID">$reviewerID</span>
      </div>
      <div class="rating">
        $reviewerRatingStars
        <span class="overall">$reviewerRating</span>
        <span class="summary">$summary</span>
      </div>
      <div class="reviewTime">$reviewTime</div>
      <div class="reviewText">$reviewText</div>
      <div class="question">$question</div>
      <div class="answer">$answer</div>
    </div>
  </div>
"""
)

df = pd.read_csv("data/matched.csv")
meta = pd.read_json("data/products.metadata", lines=True)
meta = meta.set_index('asin')
from tqdm import tqdm
body = []
for idx, row in tqdm(df.iterrows(), desc='Rendering'):
    product = {}
    try:
        product = meta.loc[row['asin']]
    except:
        pass
    description = descriptionTemplate.substitute(
        asin=row["asin"],
        reviewerID=row["reviewerID"],
        firstText=str(product.get("description", ""))[:100],
        moreText=str(product.get("description", ""))[100:],
    ) if len(str(product.get("description",""))) > 0 else "No description found for displaying"
    images = "".join(
        [imgTemplate.substitute(imgUrl=product.get('imUrl'))]
    )

    reviewerRatingStars = "".join(
        [ratingStarTemplate.substitute(checked="checked") for _ in range(int(row["overall"]))]
        + [ratingStarTemplate.substitute(checked="") for _ in range(5 - int(row["overall"]))]
    )

    review = row["reviewText"]
    sentence = row["sentence"]
    searchIdx = review.find(sentence)

    reviewText = reviewTextTemplate.substitute(
        beforeMark=review[:searchIdx],
        markedText=review[searchIdx : searchIdx + len(sentence)],
        afterMark=review[searchIdx + len(sentence) :],
    )
    element = elementTemplate.substitute(
        title=product.get("title"),
        asin=row["asin"],
        reviewerID=row["reviewerID"],
        images=images,
        description=description,
        reviewerName=row["reviewerName"],
        reviewerRatingStars=reviewerRatingStars,
        reviewerRating=row["overall"],
        summary=row["summary"],
        reviewTime=row["reviewTime"],
        reviewText=reviewText,
        question=row["question"],
        answer=row["answer"],
    )

    body.append(element)


generated = htmlTemplate.substitute(body="".join(body))

with open("docs/review-question-answer.html", "w") as f:
    f.write(generated)

