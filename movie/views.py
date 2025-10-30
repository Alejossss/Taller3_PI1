import re
import base64
import io
from collections import Counter
import matplotlib.pyplot as plt
from django.shortcuts import render

from django.db.models import Count

from .models import Movie

import matplotlib
matplotlib.use("Agg")  # backend para servidor (sin GUI)


def home(request):
    # return HttpResponse('<h1>Welcome to Home Page</h1>')
    # return render(request, 'home.html')
    # return render(request, 'home.html', {'name':'Alejandro Jaramillo'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(
        request,
        'home.html',
        {'searchTerm': searchTerm, 'movies': movies, 'name': 'Alejandro Jaramillo'}
    )


def about(request):
    return render(request, 'about.html')


def signup(request):
    email = (request.POST.get('email')
             or request.GET.get('email') or "").strip()
    return render(request, 'signup.html', {'email': email})


# ---- util: fig -> base64 ----------------------------------------------------
def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img64


def statistics_view(request):
    # ---------- Gráfica 1: Películas por AÑO (consulta eficiente a la DB)
    qs_year = (
        Movie.objects
        .values('year')               # GROUP BY year
        .annotate(total=Count('id'))  # COUNT(*)
        .order_by('year')
    )
    labels_year = [('Sin año' if r['year'] is None else r['year'])
                   for r in qs_year]
    values_year = [r['total'] for r in qs_year]

    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(range(len(values_year)), values_year, width=0.6)
    ax1.set_title('Movies per Year')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of movies')
    ax1.set_xticks(range(len(labels_year)))
    ax1.set_xticklabels(labels_year, rotation=90)
    fig1.tight_layout()
    graphic_year = _fig_to_base64(fig1)

    # ---------- Gráfica 2: Películas por PRIMER GÉNERO -----------------------
    # Si genre tiene múltiples valores (p.ej. "Action, Sci-Fi" o "Drama|Romance"),
    # tomamos solo el primero.
    splitter = re.compile(r'[|/,]')  # separadores: | , /
    counts = Counter()

    for g in Movie.objects.values_list('genre', flat=True):
        if not g:
            first = 'Sin género'
        else:
            first = splitter.split(g)[0].strip() or 'Sin género'
        counts[first] += 1

    if counts:
        genres, totals = zip(
            *sorted(counts.items(), key=lambda x: x[1], reverse=True))
    else:
        genres, totals = [], []

    # Horizontal bar para mejor legibilidad
    fig2, ax2 = plt.subplots(figsize=(8, max(3, 0.4 * len(genres))))
    ax2.barh(range(len(totals)), totals)
    ax2.set_yticks(range(len(genres)))
    ax2.set_yticklabels(genres)
    ax2.invert_yaxis()
    ax2.set_xlabel('Number of movies')
    ax2.set_title('Movies by Genre (first tag)')
    fig2.tight_layout()
    graphic_genre = _fig_to_base64(fig2)

    # Render
    return render(
        request,
        'statistics.html',
        {
            'graphic_year': graphic_year,
            'graphic_genre': graphic_genre,
        }
    )
