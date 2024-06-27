import os
import json
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib

class Product:
  def __init__(self, product_id, product_name, opinions):
    self.product_id = product_id
    self.product_name = product_name
    self.opinions = opinions

  def generate_charts(self):
    opinions_df = pd.DataFrame.from_dict(list(map(lambda opinion: opinion.to_dict(), self.opinions)))

    MAX_SCORE = 5
    opinions_df.score = opinions_df.score.apply(lambda score: round(score*MAX_SCORE, 1))
    opinions_count = opinions_df.index.size
    pros_count = opinions_df.pros.apply(lambda p: None if not p else p).count()
    cons_count = opinions_df.cons.apply(lambda c: None if not c else c).count()
    average_score = round(opinions_df.score.mean(), 2)
    score_distribution = opinions_df.score.value_counts().reindex(np.arange(0,5.5,0.5), fill_value = 0)
    recommendation_distribution = opinions_df.recommendation.value_counts(dropna=False).reindex([True, False, np.nan], fill_value = 0)

    product_info = {
      'product_id': self.product_id,
      'product_name': self.product_name,
      'opinions_count': int(opinions_count),
      'pros_count': int(pros_count),
      'cons_count': int(cons_count),
      'average_score': average_score,
      'score_distribution': score_distribution.to_dict(),
      'recommendation_distribution': recommendation_distribution.to_dict()
    }

    if not os.path.exists("app/products"):
      os.makedirs("app/products")
    with open(f"app/products/{self.product_id}.json", "w", encoding="UTF-8") as jf:
      json.dump(product_info, jf, indent=4, ensure_ascii=False)

    matplotlib.use('Agg')
    if not os.path.exists("app/static"):
      os.makedirs("app/static")
    if not os.path.exists("app/static/charts"):
      os.makedirs("app/static/charts")

    fig, ax = plt.subplots()
    score_distribution.plot.bar(color="hotpink")
    plt.xlabel("Number of stars")
    plt.ylabel("Number of opinions")
    plt.title(f"Score histogram for {self.product_name}")
    plt.xticks(rotation=0)
    ax.bar_label(ax.containers[0], label_type='edge', fmt=lambda l: int(l) if l else "")
    plt.savefig(f"app/static/charts/{self.product_id}_score.png")
    plt.close()

    recommendation_distribution.plot.pie(
      labels=["Recommend", "Not recommend", "Indifferent"],
      label="",
      colors=["forestgreen", "crimson", "silver"],
      autopct=lambda l: "{:1.1f}%".format(l) if l else ""
    )
    plt.title(f"Recommendations shares for {self.product_name}")
    plt.savefig(f"app/static/charts/{self.product_id}_recommendation.png")
    plt.close()
