class Opinion:
    def __init__(self, opinion_id, author, recommendation, score, content, pros, cons, helpful, unhelpful, publish_date, purchase_date):
        self.opinion_id = opinion_id
        self.author = author
        self.recommendation = recommendation
        self.score = score
        self.content = content
        self.pros = pros
        self.cons = cons
        self.helpful = helpful
        self.unhelpful = unhelpful
        self.publish_date = publish_date
        self.purchase_date = purchase_date

    def to_dict(self):
        return self.__dict__
