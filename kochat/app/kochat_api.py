from typing import List

from flask import Flask

from kochat.app.scenario import Scenario
from kochat.app.scenario_manager import ScenarioManager
from kochat.data.dataset import Dataset
from kochat.proc.base_processor import BaseProcessor


class KochatApi:

    def __init__(self,
                 dataset: Dataset,
                 embed: BaseProcessor,
                 intent: BaseProcessor,
                 entity: BaseProcessor,
                 fit_embed: bool = False,
                 fit_intent: bool = False,
                 fit_entity: bool = False,
                 fit_all: bool = True,
                 scenarios: List[Scenario] = None):
        """
        Flask를 이용해 구현한 RESTFul API 클래스입니다.

        :param dataset: 데이터셋 객체
        :param embed: 임베딩 프로세서 객체
        :param intent: 인텐트 분류기 객체
        :param entity: 개체명 인식기 객체
        :param scenarios : 시나리오 리스트 (list 타입)
        """

        self.app = Flask(__name__)
        self.app.config['JSON_AS_ASCII'] = False

        self.dataset = dataset
        self.embed_processor = embed
        self.intent_classifier = intent
        self.entity_recognizer = entity
        self.scenario_manager = ScenarioManager()
        self.dialogue_cache = {}

        if fit_all:
            self.__fit_embed()
            self.__fit_intent()
            self.__fit_entity()

        else:
            if fit_embed:
                self.__fit_embed()
            if fit_intent:
                self.__fit_intent()
            if fit_entity:
                self.__fit_entity()

        for scenario in scenarios:
            self.scenario_manager.add_scenario(scenario)

        self.__build()

    def __build(self):
        """
        flask 함수들을 build합니다.
        """

        @self.app.route('/request_chat/<uid>/<text>', methods=['GET'])
        def request_chat(uid: str, text: str) -> dict:
            """
            문자열을 입력하면 intent, entity, state, answer 등을 포함한
            딕셔너리를 json 형태로 반환합니다.

            :param uid: 유저 아이디 (고유값)
            :param text: 유저 입력 문자열
            :return: json 딕셔너리
            """

            prep = self.dataset.load_predict(text, self.embed_processor)
            intent = self.intent_classifier.predict(prep, calibrate=False)
            entity = self.entity_recognizer.predict(prep)
            text = self.dataset.prep.tokenize(text, train=False)
            self.dialogue_cache[uid] = self.scenario_manager.apply_scenario(intent, entity, text)
            return self.dialogue_cache[uid]

        @self.app.route('/fill_slot/<uid>/<text>', methods=['GET'])
        def fill_slot(uid: str, text: str) -> dict:
            """
            이전 대화에서 entity가 충분히 입력되지 않았을 때
            빈 슬롯을 채우기 위해 entity recognition을 요청합니다.

            :param uid: 유저 아이디 (고유값)
            :param text: 유저 입력 문자열
            :return: json 딕셔너리
            """

            prep = self.dataset.load_predict(text, self.embed_processor)
            entity = self.entity_recognizer.predict(prep)
            text = self.dataset.prep.tokenize(text, train=False)
            intent = self.dialogue_cache[uid]['intent']

            text = text + self.dialogue_cache[uid]['input']  # 이전에 저장된 dict에 추가
            entity = entity + self.dialogue_cache[uid]['entity']  # 이전에 저장된 dict에 추가
            self.dialogue_cache[uid] = self.scenario_manager.apply_scenario(intent, entity, text)
            return self.dialogue_cache[uid]

        @self.app.route('/get_intent/<text>', methods=['GET'])
        def get_intent(text: str) -> dict:
            """
            Intent Classification을 수행합니다.

            :param text: 유저 입력 문자열
            :return: json 딕셔너리
            """

            prep = self.dataset.load_predict(text, self.embed_processor)
            intent = self.intent_classifier.predict(prep, calibrate=False)
            return {
                'input': text,
                'intent': intent,
                'entity': None,
                'state': 'REQUEST_INTENT',
                'answer': None
            }

        @self.app.route('/get_entity/<text>', methods=['GET'])
        def get_entity(text: str) -> dict:
            """
            Entity Recognition을 수행합니다.

            :param text: 유저 입력 문자열
            :return: json 딕셔너리
            """

            prep = self.dataset.load_predict(text, self.embed_processor)
            entity = self.entity_recognizer.predict(prep)
            return {
                'input': text,
                'intent': None,
                'entity': entity,
                'state': 'REQUEST_ENTITY',
                'answer': None
            }

    def __fit_intent(self):
        """
        Intent Classifier를 학습합니다.

        :return: 학습된 IntentClassifier
        """

        self.intent_classifier.fit(self.dataset.load_intent(self.embed_processor))
        return self.intent_classifier

    def __fit_entity(self):
        """
        Entity Recognizr를 학습합니다.

        :return: 학습된 Entity Recognizr
        """

        self.entity_recognizer.fit(self.dataset.load_entity(self.embed_processor))
        return self.entity_recognizer

    def __fit_embed(self):
        """
        Embedding을 학습합니다.

        :return: 학습된 Embedding
        """

        self.embed_processor.fit(self.dataset.load_embed())
        return self.embed_processor
