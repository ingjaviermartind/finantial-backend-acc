import re
import pandas as pd


def extraer_coordenadas(texto):
    if pd.isna(texto):
        return [None, None]
    texto = str(texto)

    # Caso (6.28105N, -75.3318W)
    patron = (
        r'\(\s*'
        r'(-?\d+(?:\.\d+)?)\s*[NS]'
        r'\s*,\s*'
        r'(-\d+(?:\.\d+)?)\s*[EW]'
        r'\s*\)'
    )

    match = re.search(patron, texto, flags=re.IGNORECASE)

    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))

        if -5 <= lat <= 14 and -82 <= lon <= -66:
            return [lat, lon]

    # NORMALIZACIÓN
    texto = texto.replace(';', ' ')
    texto = texto.replace('`', ' ')
    texto = texto.replace(',', '.')

    texto = re.sub(
        r'(?<=\d)\s*\.\s*(?=-)',
        ' ',
        texto
    )

    texto = re.sub(r'\s+', ' ', texto).strip()

    try:

        # LAT ... LON ... con segundos separados
        # LAT 2 55 31 15 LON 75 16 55.24
        patron = (
            r'\bLAT\s+'
            r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
            r'\s+LON\s+'
            r'(\d+)\s+(\d+)\s+([\d.]+)'
        )

        match = re.search(
            patron,
            texto,
            flags=re.IGNORECASE
        )

        if match:
            lat_g, lat_m, lat_s1, lat_s2, lon_g, lon_m, lon_s = match.groups()

            lat_s = float(f'{lat_s1}.{lat_s2}')

            lat = (
                float(lat_g)
                + float(lat_m) / 60
                + lat_s / 3600
            )

            lon = (
                float(lon_g)
                + float(lon_m) / 60
                + float(lon_s) / 3600
            )

            lon = -lon

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

        # LAT ... LON ...
        patron = (
            r'\bLAT\s*'
            r'(-?\d+(?:\.\d+)?)'
            r'\s*,?\s*'
            r'LON\s*'
            r'(-?\d+(?:\.\d+)?)'
        )

        match = re.search(
            patron,
            texto,
            flags=re.IGNORECASE
        )

        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

        # (LONGITUD ; LATITUD)
        patron = (
            r'\(\s*'
            r'(-7\d+(?:\.\d+)?)'
            r'\s*;\s*'
            r'(\d+(?:\.\d+)?)'
            r'\s*\)'
        )

        match = re.search(patron, texto)

        if match:
            lon = float(match.group(1))
            lat = float(match.group(2))

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

        # COORD + DMS con segundos separados
        # COORD 1 12 36 36 N 77 59 34 58 W
        patron = (
            r'COORD\s+'
            r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*([NS])\s+'
            r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*([EWO])'
        )

        match = re.search(
            patron,
            texto,
            flags=re.IGNORECASE
        )

        if match:
            (
                lat_g, lat_m, lat_s1, lat_s2, lat_dir,
                lon_g, lon_m, lon_s1, lon_s2, lon_dir
            ) = match.groups()

            lat_s = float(f'{lat_s1}.{lat_s2}')
            lon_s = float(f'{lon_s1}.{lon_s2}')

            lat = (
                float(lat_g)
                + float(lat_m) / 60
                + lat_s / 3600
            )

            lon = (
                float(lon_g)
                + float(lon_m) / 60
                + lon_s / 3600
            )

            if lat_dir.upper() == 'S':
                lat = -lat

            if lon_dir.upper() in ('W', 'O'):
                lon = -lon

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

        # COORD + DMS
        patron = (
            r'COORD\s+'
            r'(\d+)\s+([\d.]+)\s+([\d.]+)\s*([NS])\s+'
            r'(\d+)\s+([\d.]+)\s+([\d.]+)\s*([EWO])'
        )

        match = re.search(
            patron,
            texto,
            flags=re.IGNORECASE
        )

        if match:
            (
                lat_g, lat_m, lat_s, lat_dir,
                lon_g, lon_m, lon_s, lon_dir
            ) = match.groups()

            lat = (
                float(lat_g)
                + float(lat_m) / 60
                + float(lat_s) / 3600
            )

            lon = (
                float(lon_g)
                + float(lon_m) / 60
                + float(lon_s) / 3600
            )

            if lat_dir.upper() == 'S':
                lat = -lat

            if lon_dir.upper() in ('W', 'O'):
                lon = -lon

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

        # DMS con °
        patron = (
            r'(\d+)°\s*'
            r'(\d+)\s+([\d.]+)\s*([NS])'
            r'\s*[-–]\s*'
            r'(\d+)°\s*'
            r'(\d+)\s+([\d.]+)\s*([EWO])'
        )

        match = re.search(
            patron,
            texto,
            flags=re.IGNORECASE
        )

        if match:
            (
                lat_g, lat_m, lat_s, lat_dir,
                lon_g, lon_m, lon_s, lon_dir
            ) = match.groups()

            lat = (
                float(lat_g)
                + float(lat_m) / 60
                + float(lat_s) / 3600
            )

            lon = (
                float(lon_g)
                + float(lon_m) / 60
                + float(lon_s) / 3600
            )

            if lat_dir.upper() == 'S':
                lat = -lat

            if lon_dir.upper() in ('W', 'O'):
                lon = -lon

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

        # DMS con LAT / LONG
        patron = (
            r'\bLAT\s+'
            r'(\d+)\s+(\d+)\s+([\d.]+)\s*([NS])'
            r'.*?'
            r'\bLONG?\s+'
            r'(\d+)\s+(\d+)\s+([\d.]+)\s*([EWO])'
        )

        match = re.search(
            patron,
            texto,
            flags=re.IGNORECASE
        )

        if match:
            (
                lat_g, lat_m, lat_s, lat_dir,
                lon_g, lon_m, lon_s, lon_dir
            ) = match.groups()

            lat = (
                float(lat_g)
                + float(lat_m) / 60
                + float(lat_s) / 3600
            )

            lon = (
                float(lon_g)
                + float(lon_m) / 60
                + float(lon_s) / 3600
            )

            if lat_dir.upper() == 'S':
                lat = -lat

            if lon_dir.upper() in ('W', 'O'):
                lon = -lon

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

        # Decimales implícitos
        patron = (
            r'(?<!\d)'
            r'(\d{1,2})\s+(\d{4,8})'
            r'\s+'
            r'(-?7\d)\s+(\d{4,8})'
            r'(?!\d)'
        )

        match = re.search(patron, texto)

        if match:
            lat_g, lat_dec, lon_g, lon_dec = match.groups()

            lat = float(f'{lat_g}.{lat_dec}')
            lon = float(f'{lon_g}.{lon_dec}')

            if lon > 0:
                lon = -lon

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

        # Decimales normales
        patron = (
            r'(?<![\d.])'
            r'(-?\d+\.\d+)°?'
            r'\s*'
            r'(-(?:6\d|7\d|8[01])(?:\.\d+)?)°?'
            r'(?!\d)'
        )

        match = re.search(patron, texto)

        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))

            if -5 <= lat <= 14 and -82 <= lon <= -66:
                return [lat, lon]

    except Exception:
        return [None, None]

    return [None, None]