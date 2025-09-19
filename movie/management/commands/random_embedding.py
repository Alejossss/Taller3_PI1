import numpy as np
import random
from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Selecciona una película al azar y muestra los primeros valores de su embedding"

    def handle(self, *args, **kwargs):
        movies = Movie.objects.exclude(emb__isnull=True)
        count = movies.count()

        if count == 0:
            self.stdout.write("⚠️ No hay películas con embeddings guardados en la base de datos.")
            return

        # Selecciona una película al azar
        movie = random.choice(list(movies))

        # Reconstruir el embedding como numpy array
        embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)

        self.stdout.write(self.style.SUCCESS(f"🎬 Película seleccionada: {movie.title}"))
        self.stdout.write(f"🔢 Longitud del embedding: {len(embedding_vector)}")
        self.stdout.write(f"🔍 Primeros 10 valores: {embedding_vector[:10]}")
