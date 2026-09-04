# MovieLens Analytics

Инструмент для анализа данных о фильмах на основе датасета [MovieLens](https://grouplens.org/datasets/movielens/).
Реализует парсинг метаданных с IMDB, аналитику по жанрам, рейтингам и кассовым показателям.

---

## Возможности

### `Movies` — анализ каталога фильмов
- Распределение фильмов по годам выхода
- Распределение по жанрам
- Топ-N фильмов с наибольшим количеством жанров

### `Links` — парсинг метаданных с IMDB
- Автоматический сбор данных о фильмах: режиссёр, бюджет, мировые сборы, хронометраж, рейтинг IMDb, Metascore
- JSON-кэширование для ускорения повторных запросов
- Очистка и нормализация разнородных форматов (строки валют, хронометраж, N/A)
- Аналитика: топ режиссёров по числу фильмов, самые дорогие / прибыльные фильмы, стоимость на минуту, сравнение рейтингов IMDb и Metacritic

### `Ratings` — анализ пользовательских оценок
- Распределение оценок
- Топ фильмов по средней оценке
- Анализ оценок по жанрам и годам

### `Tags` — анализ пользовательских тегов
- Топ-N тегов по количеству слов и длине
- Самые популярные теги
- Поиск тегов по ключевому слову

---

## Структура проекта

```
├── movielens_analysis.py   # Основной модуль: классы Movies, Links, Ratings, Tags
├── movielens_report.ipynb  # Ноутбук с демонстрацией всех функций
├── imdb_cache.json         # Кэш запросов к IMDB
├── movies.csv              # Датасет MovieLens — фильмы
├── links.csv               # Датасет MovieLens — ссылки на IMDB/TMDB
├── ratings.csv             # Датасет MovieLens — оценки
└── tags.csv                # Датасет MovieLens — теги
```

---

## Технологии

| Инструмент | Применение |
|---|---|
| `requests` + `BeautifulSoup` | Парсинг страниц IMDB |
| `json` | Кэширование результатов запросов |
| `re` | Нормализация строковых форматов данных |
| `collections.Counter` | Агрегация и подсчёт частот |

---

## Запуск

```bash
pip install requests beautifulsoup4
jupyter notebook movielens_report.ipynb
```

Или напрямую в Python:

```python
from movielens_analysis import Movies, Links, Ratings, Tags

movies = Movies('movies.csv')
print(movies.dist_by_release())   # распределение по годам
print(movies.dist_by_genres())    # распределение по жанрам

links = Links('links.csv', 'movies.csv')
links.get_imdb([1, 2, 3], ['Director', 'Budget', 'Rating'])
print(links.top_directors(5))     # топ-5 режиссёров
print(links.most_profitable(5))   # топ-5 самых прибыльных
```
