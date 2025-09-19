import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Verifica que los embeddings guardados en la BD se puedan recuperar correctamente"

    def handle(self, *args, **kwargs):
        for movie in Movie.objects.all():
            if movie.emb:
                embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)
                # mostramos solo los primeros 5 valores para validar
                self.stdout.write(f"{movie.title}: {embedding_vector[:5]}")
            else:
                self.stdout.write(f"{movie.title}: ⚠️ sin embedding guardado")
