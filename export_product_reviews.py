import os
import sys
import pandas as pd
from tqdm import tqdm
import gzip
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder


download_dir = sys.argv[1]


def parse(path):
    g = gzip.open(path, "r")
    for l in g:
        yield eval(l)


def getDF(path, asins):
    i = 0
    df = {}
    for d in tqdm(parse(path), desc="Loading {}".format(path)):
        if d["asin"] in asins:
            df[i] = d
            i += 1
    return pd.DataFrame.from_dict(df, orient="index")


def get_reviews_from_dataframe(df, asin):
    return df[df["asin"] == asin]


qr = pd.read_csv(
    "data/QR.csv",
    header=None,
    names=["asin", "question", "review", "answer", "label"],
    usecols=[0, 1, 2, 3, 4],
)
pos_qr = qr[qr["label"] == 1]
asins = pos_qr["asin"].unique().tolist()
print("Load McAuley data")
from time import time

start_time = time()
dfs = [
    getDF(os.path.join(download_dir, "reviews_Cell_Phones_and_Accessories.json.gz"), asins),
    getDF(os.path.join(download_dir, "reviews_Electronics.json.gz"), asins),
]
print("Finish load McAuley data in {}s".format(time() - start_time))
start_time = time()

summary = open("data/summary.csv", "w")
summary.write("asin,# reviews (McAuley),is_matched,source\n")
match_count = 0
result_dfs = []
for idx, row in tqdm(pos_qr.iterrows()):
    is_matched = False
    asin = row["asin"]
    source = ""
    df = pd.concat(
        [get_reviews_from_dataframe(dfs[0], asin), get_reviews_from_dataframe(dfs[1], asin)]
    )

    df["is_matched"] = df["reviewText"].apply(lambda x: row["review"].lower() in x.lower())
    df.to_csv("data/product_reviews/{}.csv".format(asin), index=False)

    matched = df[df["is_matched"] == True]
    if len(matched) > 0:
        source = "McAuley"
        is_matched = True
        match_count += 1
        matched["sentence"] = row["review"]
        matched["question"] = row["question"]
        matched["answer"] = row["answer"]
        result_dfs.append(matched)

    summary.write("{},{},{},{}\n".format(asin, len(df), is_matched, source))

pd.concat(result_dfs).to_csv("data/matched.csv", index=False)

summary.close()

print("Done", match_count)
