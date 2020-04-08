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


imgTemplate = Template(
  '<div class="gallery"><img class="lazy" data-src="$imgUrl"></div>'
)

descriptionTemplate = Template(
  """<p>$firstText<span id="dots-$asin">...</span><span id="more-$asin" style="display:none">$moreText</p><button onclick="toggleDescription('$asin')" id="toggleBtn-$asin">Show more</button>
"""
)

ratingStarTemplate = Template('<span class="fa fa-star $checked"></span>')

reviewTextTemplate = Template("$beforeMark<mark>$markedText</mark>$afterMark")
reviewTemplate = Template(
  """
  <div class="review">
    <div class="reviewInfo">
      <span class="reviewerName">$reviewerName</span>
      <span class="reviewerID">$reviewerID</span>
      <div class="rating">
      $reviewerRatingStars
      <span class="overall">$reviewerRating</span>
      <span class="summary">$summary</span>
      </div>
      <div class="reviewTime">$reviewTime</div>
    </div>
    <div class="reviewText">$reviewText</div>
    <div class="question">$question</div>
    <div class="answer">$answer</div>
  </div>"""
)
elementTemplate = Template(
  """
<div class="group">
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
  $reviews
</div>
"""
)

df = pd.read_csv("data/matched.csv")
df["id"] = (
  df["asin"].apply(str)
  + df["overall"].apply(str)
  + df["sentence"].apply(str)
  + df["question"].apply(str)
  + df["answer"].apply(str)
)
gdf = df.groupby("id").first().reset_index(drop=True).groupby("asin")
df = gdf['overall'].apply(list).reset_index()
df['reviewText'] = df['asin'].map(gdf['reviewText'].apply(list))
df['reviewTime'] = df['asin'].map(gdf['reviewTime'].apply(list))
df['reviewerID'] = df['asin'].map(gdf['reviewerID'].apply(list))
df['reviewerName'] = df['asin'].map(gdf['reviewerName'].apply(list))
df['summary'] = df['asin'].map(gdf['summary'].apply(list))
df['unixReviewTime'] = df['asin'].map(gdf['unixReviewTime'].apply(list))
df['sentence'] = df['asin'].map(gdf['sentence'].apply(list))
df['question'] = df['asin'].map(gdf['question'].apply(list))
df['answer'] = df['asin'].map(gdf['answer'].apply(list))
meta = pd.read_json("data/products.metadata", lines=True)
meta = meta.set_index("asin")
from tqdm import tqdm

body = []
for _, row in tqdm(df.iterrows(), desc="Rendering"):
  product = {}
  try:
    product = meta.loc[row["asin"]]
  except:
    pass
  description = (
    descriptionTemplate.substitute(
      asin=row['asin'],
      firstText=str(product.get("description", ""))[:100],
      moreText=str(product.get("description", ""))[100:],
    )
    if len(str(product.get("description", ""))) > 0
    else "No description found for displaying"
  )
  images = "".join([imgTemplate.substitute(imgUrl=product.get("imUrl", ""))])

  reviews = []
  for idx in range(len(row['overall'])):
    reviewerRatingStars = "".join(
      [
        ratingStarTemplate.substitute(checked="checked")
        for _ in range(int(row["overall"][idx]))
      ]
      + [
        ratingStarTemplate.substitute(checked="")
        for _ in range(5 - int(row["overall"][idx]))
      ]
    )

    reviewText = row["reviewText"][idx]
    sentence = row["sentence"][idx]
    searchIdx = reviewText.find(sentence)

    reviewText = reviewTextTemplate.substitute(
      beforeMark=reviewText[:searchIdx],
      markedText=reviewText[searchIdx : searchIdx + len(sentence)],
      afterMark=reviewText[searchIdx + len(sentence) :],
    )
    review = reviewTemplate.substitute(
      reviewerID=row['reviewerID'][idx],
      reviewerName=row["reviewerName"][idx],
      reviewerRatingStars=reviewerRatingStars,
      reviewerRating=row["overall"][idx],
      summary=row["summary"][idx],
      reviewTime=row["reviewTime"][idx],
      reviewText=reviewText,
      question=row["question"][idx],
      answer=row["answer"][idx],
    )
    reviews.append(review)
  reviews = '\n'.join(reviews)
  element = elementTemplate.substitute(
    title=product.get("title"),
    asin=row["asin"],
    images=images,
    description=description,
    reviews=reviews
  )

  body.append(element)


generated = htmlTemplate.substitute(body="".join(body))

with open("docs/review-question-answer.html", "w") as f:
  f.write(generated)
