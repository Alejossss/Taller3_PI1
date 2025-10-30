# recommendations/views.py
import os
import numpy as np
from numpy.typing import NDArray
from django.shortcuts import render
from django.contrib import messages
from openai import OpenAI
from dotenv import load_dotenv
from movie.models import Movie
from pathlib import Path
from django.conf import settings


# ✅ Load environment variables from the .env file
load_dotenv(Path(settings.BASE_DIR) / "openAI.env")

# ✅ Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # Asegura 1D float32
    a_vec: NDArray[np.float32] = np.asarray(a, dtype=np.float32).ravel()
    b_vec: NDArray[np.float32] = np.asarray(b, dtype=np.float32).ravel()

    # Convierte los norms explícitamente a float para contentar al type checker
    a_norm = float(np.linalg.norm(a_vec))
    b_norm = float(np.linalg.norm(b_vec))

    if a_norm == 0.0 or b_norm == 0.0:
        return -1.0

    dot = float(np.dot(a_vec, b_vec))
    return dot / (a_norm * b_norm)

def recommendations(request):
    query = ""
    result = None
    similarity = None

    if request.method == "POST":
        query = (request.POST.get("prompt") or "").strip()

        if not query:
            messages.warning(request, "Enter a text to search a recommendation for.")
        else:
            try:
                # 1) Embedding del prompt
                resp = client.embeddings.create(
                    input=[query],
                    model="text-embedding-3-small"
                )
                prompt_vec = np.array(resp.data[0].embedding, dtype=np.float32)

                # 2) Recorrer DB y comparar similitud
                best_movie = None
                best_sim = -1.0

                for mv in Movie.objects.exclude(emb__isnull=True):
                    try:
                        movie_vec = np.frombuffer(mv.emb, dtype=np.float32)
                        sim = _cosine_similarity(prompt_vec, movie_vec)
                        if sim > best_sim:
                            best_sim = sim
                            best_movie = mv
                    except Exception:
                        continue

                if best_movie is None:
                    messages.info(request, "Couldn't find a coincidence.")
                else:
                    result = best_movie
                    similarity = best_sim

            except Exception as e:
                messages.error(request, f"An error occurred while generating the recommendation. {e}")

    return render(request, "recommendations.html", {
        "query": query,
        "result": result,
    })
