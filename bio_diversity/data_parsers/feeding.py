
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from bio_diversity import models, utils
from bio_diversity.utils import DataParser


class FeedingParser(DataParser):
    tank_key = "Tank"
    feedm_key = "Feeding Method"
    feedf_key = "Feeding Frequency"
    type_base = "Feed Type "
    size_base = "Feed Size "
    comment_key = "Comments"

    feed_type_count = 5
    header = 2
    row_count = header + 2
    converters = {tank_key: str, feedm_key: str, feedf_key: str}
    sheet_name = "Feedings"

    def load_data(self):
        self.mandatory_keys = [self.tank_key, self.feedm_key]
        self.mandatory_filled_keys = [self.tank_key, self.feedm_key]
        super(FeedingParser, self).load_data()

    def row_parser(self, row):
        cleaned_data = self.cleaned_data
        tank_id = models.Tank.objects.filter(name=row[self.tank_key], facic_id=cleaned_data["evnt_id"].facic_id).get()
        comments = row.get(self.comment_key)
        feed_method_id = None
        if utils.nan_to_none(row.get(self.feedm_key)):
            feed_method_id = models.FeedMethod.objects.filter(name__iexact=row[self.feedm_key]).get()

        contx_id, entered = utils.enter_contx(tank_id, cleaned_data, return_contx=True)
        self.row_entered += entered

        for feed_type in range(1, self.feed_type_count + 1):
            type_key = self.type_base + str(feed_type)
            size_key = self.size_base + str(feed_type)
            if utils.nan_to_none(row.get(type_key)):
                feedtype_id = models.FeedCode.objects.filter(name__iexact=row[type_key]).get()
                self.row_entered += utils.enter_feed(cleaned_data, contx_id, feedtype_id, feed_method_id,
                                                     row[size_key], freq=row[self.feedf_key], comments=comments)
