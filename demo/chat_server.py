"""
@auther Hyunwoong
@since 7/1/2020
@see https://github.com/gusdnd852
"""
from kochat.app import KochatApi
from kochat.data import Dataset
from kochat.loss import CenterLoss, CRFLoss
from kochat.model import intent, embed, entity
from kochat.proc import DistanceClassifier, GensimEmbedder, EntityRecognizer
from demo.scenrios import weather, dust, travel, restaurant

dataset = Dataset(ood=True)
emb = GensimEmbedder(model=embed.FastText())

clf = DistanceClassifier(
    model=intent.CNN(dataset.intent_dict),
    loss=CenterLoss(dataset.intent_dict)
)

rcn = EntityRecognizer(
    model=entity.LSTM(dataset.entity_dict),
    loss=CRFLoss(dataset.entity_dict)
)

kochat = KochatApi(
    dataset=dataset,
    embed_processor=emb,
    intent_classifier=clf,
    entity_recognizer=rcn,
    scenarios=[weather, dust, travel, restaurant]
)

kochat.fit_all()
kochat.run(port=8081)
