"""
Copyright (c) 2024 Cloud Defense, Inc. All rights reserved.
"""
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from entity_classifier.utils.config import ConfidenceScore, Entities, SecretEntities
from entity_classifier.utils.utils import get_restricted_entities, add_custom_regex_analyzer_registry

# logger = get_logger("rag.analyzer.entity_classifier")


class EntityClassifier:
    def __init__(self, input_text):
        self.input_text = input_text
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def analyze_response(self):
        analyzer_results = self.analyzer.analyze(text=self.input_text, language='en')
        analyzer_results = [result for result in analyzer_results if result.score >= float(ConfidenceScore.Entity.value)]
        return analyzer_results

    def anomyze_response(self, analyzer_results):
        anonymized_text = self.anonymizer.anonymize(text=self.input_text, analyzer_results=analyzer_results)
        response = anonymized_text.items
        return response

    def presidio_entity_classifier(self):
        """
        Perform classification on the input data and return a dictionary with the count of each entity group.
        Parameters:
            - input_data (dict): A dictionary containing input data for classification.
        Returns:
            dict: containing the entity group Name as key and its count as value.
            total_count: Total count of entity groups.
        Example:{
                "Person":2, # EntityGroup: Count of occurrence of entity group
                "Credit Card Number": 1
            },
            total_count: 3 # Total Count of All Entity group Occurrences
        """
        restricted_entities = {}
        total_count = 0
        try:
            # logger.info("Presidio Entity Classifier Started.")
            # logger.info(f"Data Input: {self.input_text}")
            analyzer_results = self.analyze_response()
            response = self.anomyze_response(analyzer_results)
            # logger.info(f"Presidio Entity Classifier Response: {response}")
            restricted_entities, total_count = get_restricted_entities(Entities, response)
            # logger.info(f"Presidio Entity Classifier Finished {restricted_entities}")
            # logger.info(f"Entity Total count. {total_count}")
            return restricted_entities, total_count
        except Exception as e:
            # logger.error(f"Presidio Entity Classifier Failed, Exception: {e}")
            return restricted_entities, total_count

    def presidio_secret_classifier(self):
        """
        Find regex patterns in the given input data.

        Parameters:
        - input_data (str): The input string to search for regex patterns.

        Returns:
        dict: A dictionary containing key associated with regex patterns and their counts in the input data.
        Example:
        {
            'AWS API ID': 3, # SecretKey: Count of Occurrences of secret key
            'AWS API Secret': 1
        },
        total_count: 4 # total count of all SecretKeys Occurrences
        """
        # logger.info("Presidio Secret Entity Classifier Started.")
        # logger.info(f"Data Input: {self.input_text}")

        # Adding custom analyzer
        custom_recognizer = add_custom_regex_analyzer_registry()
        if custom_recognizer:
            for recognizer in custom_recognizer:
                self.analyzer.registry.add_recognizer(recognizer)

        analyzer_results = self.analyze_response()
        response = self.anomyze_response(analyzer_results)
        # logger.info(f"Presidio Secret Entity Classifier Response: {response}")
        secret_entities, total_count = get_restricted_entities(SecretEntities, response)
        # logger.info(f"Presidio Secret Entity Classifier Finished {secret_entities}")
        # logger.info(f"Secret Entity Total count. {total_count}")
        return secret_entities, total_count
