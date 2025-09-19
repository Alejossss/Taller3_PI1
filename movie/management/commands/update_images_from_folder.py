import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Asigna imágenes a las películas desde MEDIA_ROOT/movie/images/ con nombre m_<Título>.png"

    def handle(self, *args, **kwargs):
        media_dir = Path(settings.MEDIA_ROOT) / "movie" / "images"
        if not media_dir.exists():
            self.stderr.write(f"No existe la carpeta: {media_dir}")
            return

        total = 0
        updated = 0
        not_found = 0
        skipped_custom = 0

        qs = Movie.objects.all().order_by("id")
        self.stdout.write(f"Found {qs.count()} movies")

        for movie in qs:
            total += 1

            # Estado actual del campo image
            current_name = (movie.image.name or "").strip()
            is_empty = not current_name
            is_default = current_name.endswith("/default.jpg") or os.path.basename(current_name) == "default.jpg"

            # Solo reemplazar si está vacío o apunta a default.jpg
            if not (is_empty or is_default):
                skipped_custom += 1
                continue

            # Nombre esperado EXACTO: m_<Título>.png
            expected_filename = f"m_{movie.title}.png"
            expected_path = media_dir / expected_filename

            if not expected_path.exists():
                self.stderr.write(f"[NOT FOUND] {movie.title} -> {expected_path}")
                not_found += 1
                continue

            # Asignar ruta relativa a MEDIA_ROOT (upload_to='movie/images/')
            rel_path = f"movie/images/{expected_filename}"
            movie.image.name = rel_path
            movie.save(update_fields=["image"])
            updated += 1
            self.stdout.write(self.style.SUCCESS(f"[UPDATED] {movie.title} -> {rel_path}"))

        # Resumen
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== SUMMARY ==="))
        self.stdout.write(f"Total películas: {total}")
        self.stdout.write(f"Actualizadas:    {updated}")
        self.stdout.write(f"No encontradas:  {not_found}")
        self.stdout.write(f"Con imagen propia (saltadas): {skipped_custom}")
