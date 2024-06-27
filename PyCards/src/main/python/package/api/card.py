import json
import os
import random

COLLECTION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'collections')

class Card:
    def __init__(self, question: str, answer: str, understood : int = 5) -> None:
        self.question = question
        self.answer = answer
        self.understood = understood
        
    def understood_count_up(self) -> None:
        if self.understood < 10:
            self.understood += 1
        
    def understood_count_down(self) -> None:
        if self.understood > 0:
            self.understood -= 1   

class Collection:
    def __init__(self, cards: list = None) -> None:
        if cards is None:
            cards = []
        self.cards = cards
        
    def add_card(self, question, answer) -> None:
        self.cards.append(Card(question, answer))
        
    def remove_card(self, card) -> None:
        self.cards.remove(card)
    
    def load_collection(self, path) -> None:
        with open(path, 'r') as f:
            data = json.load(f)
            self.cards = [Card(card['question'], card['answer'], card['understood']) for card in data]
            
    def export_collection(self, path: str, file_name: str) -> None:
        file_path = os.path.join(path, file_name)
        if not os.path.exists(path):
            os.makedirs(path)

        data = [{'question': card.question, 'answer': card.answer, "understood" : card.understood} for card in self.cards]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent = 4)
            
    def get_card_question(self, card : Card) -> str:
        return card.question
    
    def get_card_answer(self, card : Card) -> str:
        return card.answer
    
    def get_card(self) -> Card:
        max_understood = max(card.understood for card in self.cards)
        weights = [(max_understood - card.understood + 1) for card in self.cards]
        return random.choices(self.cards, weights=weights, k=1)[0]
        
if __name__ == '__main__':
    collection = Collection([Card('What is 2 + 2?', '4'), Card('What is 3 + 3?', '6')])
    collection.export_collection(COLLECTION_PATH, 'test.json')
    collection.load_collection(os.path.join(COLLECTION_PATH, 'test.json'))
    for card in collection.cards:
        print(card.question, card.answer)