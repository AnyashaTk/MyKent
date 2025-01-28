from sklearn.metrics.pairwise import cosine_similarity
import torch
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import pandas as pd
from PIL import Image
import io

class MemeRecommender:
    def __init__(self):
        self.ds = load_dataset("./data/foldl___rumeme-desc")
        
        self.df = pd.DataFrame({
            'meme_id': range(len(self.ds["train"]["text"])),
            'description': self.ds["train"]["text"]
        })
        
        # Инициализируем модель
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Преобразуем описания мемов в векторы
        self.meme_embeddings = self.model.encode(self.df['description'].tolist(), convert_to_tensor=True)

    def get_relevant_meme(self, input_query, top_k=1):
        # Векторизуем ввод пользователя
        user_embedding = self.model.encode([input_query], convert_to_tensor=True)
        
        # Вычисляем косинусное сходство
        cosine_scores = torch.nn.functional.cosine_similarity(user_embedding, self.meme_embeddings)
        
        # Находим индексы топ-K мемов
        top_results = torch.topk(cosine_scores, k=top_k)
        
        # Извлекаем информацию о лучших мемах
        results = []
        for score, idx in zip(top_results.values, top_results.indices):
            idx = idx.item()  # Преобразуем тензор в целое число
            meme = self.df.iloc[idx]
            results.append({
                'meme_id': meme['meme_id'],
                'description': meme['description'],
                'score': score.item()
            })
        return results
    
    def get_meme_image(self, meme_id):
        image_bytes = self.ds["train"]['image'][meme_id]
        if isinstance(image_bytes, Image.Image):
            return image_bytes
        return Image.open(io.BytesIO(image_bytes))
    
    def display_meme(self, meme_id):
        # Получаем изображение
        return self.get_meme_image(meme_id)

# # Пример использования
# recommender = MemeRecommender()
# user_description = "После 2 недель неприрывного программирования."
# relevant_memes = recommender.get_relevant_meme(user_description, top_k=1)