import requests
from bs4 import BeautifulSoup
import time
from collections import Counter
import json
import os
import re
import datetime
import pytest

class Movies:
    def __init__(self, path_to_the_file):
        self.list_id = []
        self.list_titles = []
        self.list_genres = []
        try:
            with open (path_to_the_file, 'r', encoding='UTF=8') as f:
                f.readline()
                for _ in range(1000):
                    line = f.readline()
                    if not '"' in line:

                        parts = line.split(",") 
                        self.list_id.append(int(parts[0]))
                        self.list_titles.append(parts[1])
                        self.list_genres.append(parts[2].strip())
                    else:
                        parts = []
                        k = line.split('"')
                        for j in range(len(k)):
                            p = k[j].strip(",")
                            parts.append(p)
                        self.list_id.append(int(parts[0]))
                        self.list_titles.append(parts[1])
                        self.list_genres.append(parts[2].strip())
        except FileNotFoundError:
            raise Exception(f"File {path_to_the_file} is not found")
        except Exception as e:
            print(f"Error : {e}")


    def dist_by_release(self):    
        release_years1 = {}
        for i in self.list_titles:
            year = i[-5:-1] 
            if year not in release_years1:
                release_years1[year] = 1
            else:
                release_years1[year] += 1

        release_years = sorted(release_years1.items(),key=lambda x: x[1] , reverse=True)



        return dict(release_years)
    
    def dist_by_genres(self):
        genres_list = [ "Action", "Adventure", "Animation", "Children", "Comedy", "Crime", "Documentary",
                        "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi",
                          "IMAX","Thriller", "War", "Western", "(no genres listed)"]

        dict_gen = dict.fromkeys(genres_list, 0)
        for i in self.list_genres:
            stroka = i.split("|")
            for genr in stroka:    
                dict_gen[genr] += 1

        genres = sorted(dict_gen.items(),key=lambda x: x[1] , reverse=True)
                
        return dict(genres)


#ключ - название фильма, значение - кол-во жанров, топ n лучших фильмов, 
    def most_genres(self, n):
        movie_counts = {}
        for i in range(len(self.list_titles)):
            title = self.list_titles[i]
            genres = self.list_genres[i]
        
        # Считаем количество жанров
            count = len(genres.split('|'))
            movie_counts[title] = count

    # Сортировка остается такой же
        sorted_res = sorted(movie_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_res[:n])
        
class Links:
    """
    Analyzing data from links.csv
    """
    def __init__(self, path_to_links, path_to_movies):
        """
        Put here any fields that you think you will need.
        """

        self.all_data_dict = {}
        filepath = [path_to_movies, path_to_links]

        try:
            with open (path_to_movies, 'r', encoding='UTF=8') as fm:
                fm.readline()
                for _ in range(1000):
                    line = fm.readline()
                    if not '"' in line:
                        parts = line.split(",") 
                    else:
                        parts = []
                        k = line.split('"')
                        for j in range(len(k)):
                            p = k[j].strip(",")
                            parts.append(p)
                    film_id  = int(parts[0])
                    titel = parts[1]
                    self.all_data_dict[film_id] = {
                        'title' : titel,
                        'imdb_id' : None,
                        'tmdb_id' : None,
                        'Director' : None,
                        'Budget' : None,
                        'Cumulative Worldwide Gross' : None,
                        'Runtime' : None,
                        'Rating' : None,
                        "Metascore" : None
                    }
                        
            with open (path_to_links, 'r', encoding='UTF=8') as fl:
                line = fl.readline()
                for _ in range(1000):
                    line = fl.readline()
                    parts = line.split(",")
                    film_id = int(parts[0]) 
                    imdb_id = parts[1]
                    tmdb_id = parts[2].strip()
                    if film_id in self.all_data_dict:
                        self.all_data_dict[film_id]['imdb_id'] = imdb_id
                        self.all_data_dict[film_id]['tmdb_id'] = tmdb_id
    
        except FileNotFoundError:
            raise Exception(f"File {filepath} is not found")
        except Exception as e:
            print(f" : {e}")

        self.load_all_data()

    def save_all_data(self, filename="imdb_cache.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.all_data_dict, f, ensure_ascii=False, indent=4)
                print(f"Данные успешно сохранены в {filename}")
        except Exception as e:
            print(f"Ошибка : {e}")   

    def load_all_data(self, filename="imdb_cache.json"):
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                    # Превращаем ключи в int и обновляем основной словарь
                    cache = {int(k): v for k, v in raw.items()}
                    self.all_data_dict.update(cache)
                
                # Используем метод для получения актуального состояния после загрузки
                valuable_count = self.get_valuable_index()
                
                print(f"Загрузка завершена.")
                print(f"Всего записей в кэше: {len(cache)}")
                print(f"Реально спаршено данных (валидный индекс): {valuable_count}")
                
                # Пример логики: если данных мало, можно выкинуть предупреждение
                if valuable_count == 0:
                    print("Предупреждение: валидных данных не обнаружено.")
        except Exception as e:
            print(f"Ошибка : {e}")   
     
    def get_imdb(self,list_of_movies, list_of_fields):
        imdb_info = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }
        session = requests.Session()
        session.headers.update(headers)
        
        for film_id in list_of_movies:
            movie_data = self.all_data_dict.get(film_id)

            if not movie_data:
                print(f"Фильм с ID {film_id} не найден в базе")
                continue

            needs_parsing = any(movie_data.get(f) is None for f in list_of_fields)
            
            if needs_parsing:
                imdb_id = movie_data.get('imdb_id')
                film_info = []
                url =  f"https://www.imdb.com/title/tt{imdb_id}"
                try:
                    response = session.get(url,timeout=10)
                    if response.status_code != 200:
                        raise Exception("Некорретный URL(или тикер)")
                
                    soup = BeautifulSoup(response.text, 'html.parser')

                    #Поиск рейтинга
                    rait_elem = soup.find(attrs= {"data-testid": "hero-rating-bar__aggregate-rating__score"})
                    if rait_elem:
                        imdb_rait = rait_elem.find("span").text
                    else: imdb_rait = "N/A" 

                    #Поиск имени директора - чертовщина
                    dir_block = soup.find("li", {"data-testid": "title-pc-principal-credit"})
                    if dir_block:
                        dir_name = dir_block.find("a").text
                    else: dir_name = "N/A" 

                    #Поиск рейтинга Metacritics
                    metascore_tag = soup.find("span", class_="metacritic-score-box")
                    if metascore_tag:
                        metascore = metascore_tag.get_text(strip=True)
                    else: metascore = "N/A"

                    #Поиск бюджета
                    budget_elem = soup.find(attrs= {"data-testid":"title-boxoffice-budget"})
                    if budget_elem:
                        value_tag = budget_elem.find("span", class_="ipc-metadata-list-item__list-content-item")
                        if value_tag:
                            budget = value_tag.get_text(strip=True)
                        else: budget = "N/A"

                    #Поиск мировых сборов
                    gros_elem = soup.find(attrs= {"data-testid":"title-boxoffice-cumulativeworldwidegross"})
                    if gros_elem:
                        content = gros_elem.find(class_="ipc-metadata-list-item__list-content-item")
                        gros = content.get_text(strip=True) if content else "N/A"
                    else: gros = "N/A"
                    
                    #Продолжительность фильма
                    run_elem = soup.find(attrs={"data-testid":"title-techspec_runtime"})
                    if run_elem:  
                        runtime = run_elem.find("div").get_text(strip=True)  
                    else: runtime = "N/A"

                    self.all_data_dict[film_id].update({
                    'Director': dir_name,
                    'Budget': budget,
                    'Cumulative Worldwide Gross': gros,
                    'Runtime': runtime,
                    'Rating': imdb_rait,
                    'Metascore': metascore
                })
                    time.sleep(2)

                except Exception as e:
                    print(f"Ошибка на ID {film_id}: {e}")

        self.data_cleaner()
        self.save_all_data()

        for film_id in list_of_movies:
            row = [film_id]
            for field in list_of_fields:
                row.append(self.all_data_dict[film_id].get(field))
            imdb_info.append(row)

        imdb_info.sort(key=lambda x: x[0], reverse=True)
        return imdb_info

    def data_cleaner(self):
        ids = list(self.all_data_dict.keys())
        for film_id in ids:
            movie = self.all_data_dict[film_id]
            for field in list(movie.keys()):
                value = movie[field]
                if value is None or value == "":
                    continue
                if value == "N/A" and field != 'Director':
                    value = 0

                try:
                    str_val = str(value)
                    
                    if field in ["Cumulative Worldwide Gross", "Metascore", "Budget"]:
                        # Оставляем только цифры
                        digits = "".join(filter(str.isdigit, str_val))
                        movie[field] = int(digits) if digits else None
                            
                    elif field == "Rating":
                        # Ищем число с точкой или просто число (например 8.5 или 8)
                        match = re.search(r"(\d+\.\d+|\d+)", str_val)
                        if match:
                            movie[field] = float(match.group(1))
                        else:
                            movie[field] = None

                    elif field == "Runtime":
                        if "(" in str_val and "min" in str_val:
                            inside_brackets = str_val.split("(")[1].split(")")[0]
                            minutes = "".join(filter(str.isdigit, inside_brackets))
                            movie[field] = int(minutes) if minutes else 0
                        else:
                            h = 0
                            m = 0
                            if 'h' in str_val:
                                h_part = str_val.split('h')[0]
                                h = int("".join(filter(str.isdigit, h_part)))
                                # Отрезаем часы, работаем с остатком
                                str_val = str_val.split('h')[1]
                            
                            # Ищем минуты в оставшейся части строки
                            m_digits = "".join(filter(str.isdigit, str_val))
                            m = int(m_digits) if m_digits else 0
                            
                            movie[field] = h * 60 + m
                            
                except Exception as e:
                    print(f"Ошибка в cleaner (ID {film_id}, {field}): {e}")
    
    def get_valuable_index(self):
        ids = list(self.all_data_dict.keys())
            
        index = 0
        for film_id in ids:
            movie = self.all_data_dict[film_id]

            if any(value is None for value in movie.values()):
                return index 
                
            index += 1
                
        return index
        
    def top_directors(self, n):
        try:
            only_dirs_list = []
            for movie in self.all_data_dict.values():
                dir_name = movie.get('Director') 
                if dir_name not in (None, "N/A"):
                    only_dirs_list.append(dir_name)

            directors_count_dict = Counter(only_dirs_list)
            directors = directors_count_dict.most_common(n)

            return dict(directors)
        except Exception as e:
            print(f"Ошибка : {e}")   
            
    def most_expensive(self, n):
        try:
            budgets = []
            for movie in self.all_data_dict.values():
                title = movie.get('title')
                budget = movie.get('Budget')
                if title not in (None,"N/A") and budget not in (None,"N/A"):
                    budgets.append([title, budget])

            sorted_budgets = sorted(budgets, key= lambda x: x[1], reverse=True)
            res = dict(sorted_budgets[:n])
            return res
        except Exception as e:
            print(f"Ошибка : {e}")   
            
    def most_profitable(self, n):
        try:
            budgets = []
            for movie in self.all_data_dict.values():
                title = movie.get('title')
                budget = movie.get('Budget')
                gros = movie.get('Cumulative Worldwide Gross')
                if all (item not in (None,"N/A") for item in [title, gros, budget]):
                    budgets.append([title, gros-budget])

            sorted_budgets = sorted(budgets, key= lambda x: x[1], reverse=True)
            res = dict(sorted_budgets[:n])
            return res
        except Exception as e:
            print(f"Ошибка : {e}")   
            
    def longest(self, n):
        try:
            runtimes = []
            for movie in self.all_data_dict.values():
                title = movie.get('title')
                runtime = movie.get('Runtime')
                if title not in (None,"N/A") and runtime not in (None,"N/A"):
                    runtimes.append([title, runtime])


            sorted_runtimes = sorted(runtimes, key= lambda x: x[1], reverse=True)
            res = dict(sorted_runtimes[:n])
            return res
        except Exception as e:
            print(f"Ошибка : {e}")   
            
    def top_cost_per_minute(self, n):
        try:
            costs = []
            for movie in self.all_data_dict.values():
                title = movie.get('title')
                budget = movie.get('Budget')
                runtime = movie.get('Runtime')
                if all (item not in (None,"N/A",0) for item in [title, runtime, budget]):
                    costs.append([title, round(budget/runtime,2)])

            sorted_costs = sorted(costs, key= lambda x: x[1], reverse=True)
            res = dict(sorted_costs[:n])
            return res
        except Exception as e:
            print(f"Ошибка : {e}")   

    def dual_raiting(self,n):
        try:
            ratings = []
            for movie in self.all_data_dict.values():
                title = movie.get('title')
                imdb_rait = movie.get('Rating')
                meta = movie.get('Metascore')
                if all (item not in (None,"N/A",0) for item in [title, meta, imdb_rait]):
                    ratings.append([title, [imdb_rait, meta]])

            sorted_ratings = sorted(ratings, key=lambda x: x[1][0], reverse=True)
            res = dict(sorted_ratings[:n])
            return res
        except Exception as e:
            print(f"Ошибка : {e}")   

class Ratings:
    merged_data = []
    def __init__(self, path_to_the_file, path_to_the_movies):
        """
        Put here any fields that you think you will need.
        """            
        Ratings.merged_data = []
        movie_map = {}
        try:
            with open (path_to_the_movies, 'r', encoding='UTF=8') as f:
                f.readline()
                for _ in range(1000):
                    line = f.readline()
                    if not '"' in line:
                        parts = line.strip().split(",")
                        m_id = parts[0]
                        title = parts[1]
                        movie_map[m_id] = title
                    else:
                        parts = line.strip().split('"')
                        m_id = parts[0]
                        title = parts[1]
                        movie_map[m_id] = title

            with open (path_to_the_file, 'r', encoding='UTF=8') as f:
                f.readline()
                for _ in range(1000):
                    line = f.readline()
                    parts = line.strip().split(",") 
                    m_id = parts[1]                     #???
                    if m_id in movie_map:
                        Ratings.merged_data.append({'userID': parts[0], 'title': movie_map[m_id], 'rating': float(parts[2]), 'timestamp': int(parts[3])})

        except FileNotFoundError:
            raise Exception(f"File {path_to_the_file} is not found")
        except Exception as e:
            print(f"Error : {e}")

    class Movies:
        def dist_by_year(self):
            try:
                ratings_by_year = {}
                for i in range(len(Ratings.merged_data)):
                    timestamp = Ratings.merged_data[i]['timestamp']
                    year = datetime.datetime.fromtimestamp(timestamp).year
                    if year not in ratings_by_year:
                        ratings_by_year[year] = 1
                    else:
                        ratings_by_year[year] += 1
                
                sorted_ratings_by_year = sorted(ratings_by_year.items(), key=lambda x: x[0])
                return dict(sorted_ratings_by_year)
            except Exception as e:
                print(f"Error: {e}")


        def dist_by_rating(self):
            try:
                ratings_distribution = {}
                for i in range(len(Ratings.merged_data)):
                    score = Ratings.merged_data[i]['rating']
                    if score not in ratings_distribution:
                        ratings_distribution[score] = 1
                    else:
                        ratings_distribution[score] += 1
                
                sorted_ratings_distribution = sorted(ratings_distribution.items(), key=lambda x: x[0], reverse=False)
                return dict(sorted_ratings_distribution)
            except Exception as e:
                print(f"Error: {e}")
            

        def top_by_num_of_ratings(self, n):
            try:
                top = {}
                for i in range(len(Ratings.merged_data)):
                    score = Ratings.merged_data[i]['title']
                    if score not in top:
                        top[score] = 1
                    else:
                        top[score] += 1   

                top_movies = sorted(top.items(), key=lambda x: x[1], reverse=True)

                return dict(top_movies[:n])
            except Exception as e:
                print(f"Error: {e}")
            

        def top_by_ratings(self, n, metric='average'):
            try:
                movie_rating = {}
                for i in Ratings.merged_data:
                    title = i['title']
                    rating = i['rating']
                    if title not in movie_rating:
                        movie_rating[title] = []
                    movie_rating[title].append(rating)

                res_movie_rating = {}
                for k, v in movie_rating.items():
                    if metric == 'average':
                        score = sum(v)
                        count = len(v) 
                        val = score/count
                    elif metric == 'median':
                        sorted_val = sorted(v)
                        size = len(sorted_val)
                        if size % 2 == 1:
                            val = sorted_val[size // 2]
                        else:
                            val = (sorted_val[size // 2 - 1] + sorted_val[size // 2]) /2
                    else:
                        raise ValueError("Invalid metric. Expected 'average' or 'median'.")
                    res_movie_rating[k] = round(val,2)

                top_movies = sorted(res_movie_rating.items(), key=lambda x: x[1], reverse=True)
                return dict(top_movies[:n])
            except Exception as e:
                print(f"Error: {e}")
        
        def top_controversial(self, n):
            try:
                movie_rating = {}
                for i in Ratings.merged_data:
                    title = i['title']
                    rating = i['rating']
                    if title not in movie_rating:
                        movie_rating[title] = []
                    movie_rating[title].append(rating)

                mov_dispersia = {}
                for k,v in movie_rating.items():
                    avg = sum(v) / len(v)
                    chislitel = sum((x-avg)**2 for x in v)
                    mov_dispersia[k] = round(chislitel/len(v), 2)
                top_movies = sorted(mov_dispersia.items(), key=lambda x: x[1], reverse=True)

                return dict(top_movies[:n])
            except Exception as e:
                print(f"Error: {e}")
    
    class Users(Movies):
        def users_by_numrat(self):
            try:
                every_user = {}
                #здесь посчитаем сколько юзер поставил оценок
                for i in range (len(Ratings.merged_data)):
                    user = Ratings.merged_data[i]['userID']
                    if user not in every_user:
                        every_user[user] = 1
                    else:
                        every_user[user] += 1

                dist = {}
                for i in every_user.values():
                    if i not in dist:
                        dist[i] = 1
                    else:
                        dist[i] += 1
                
                every_user = sorted(dist.items(), key=lambda x: x[0])
                
                return dict(every_user)
            except Exception as e:
                print(f"Error: {e}")
            


        def users_by_average(self, metric='average'):
            try:
                rate = {}
                for i in Ratings.merged_data:
                    user = i['userID']
                    rating = i['rating']
                    if user not in rate:
                        rate[user] = []
                    rate[user].append(rating)
                temp = {}
                for v in rate.values():
                    if metric == 'average':
                        val = round(sum(v)/len(v), 2)
                    elif metric == 'median':
                        sorted_v = sorted(v)
                        size = len(sorted_v)
                        if size % 2 == 1:
                            val = sorted_v[size//2]
                        else:
                            val = (sorted_v[size // 2-1] + sorted_v[size//2]) / 2
                    else:
                        raise ValueError("inval metric. Expected 'average' or 'median' ")
                    
                    val = round(val, 2)
                    if val not in temp:
                        temp[val] = 1
                    else:
                        temp[val] += 1

                res_rating = sorted(temp.items(), key=lambda x: x[0])
                return dict(res_rating)
            except Exception as e:
                print(f"Error: {e}")
         

        def top_dipersia(self, n):
            try:
                rate = {}

                for i in Ratings.merged_data:
                    user = i['userID']
                    rating = i['rating']
                    if user not in rate:
                        rate[user] = []
                    rate[user].append(rating)

                mov_dispersia = {}
                for k,v in rate.items():
                    avg = sum(v) / len(v)
                    chislitel = sum((x-avg)**2 for x in v)
                    mov_dispersia[k] = round(chislitel/len(v), 2)
                top_movies = sorted(mov_dispersia.items(), key=lambda x: x[1], reverse=True)

                return dict(top_movies[:n])
            except Exception as e:
                print(f"Error: {e}")
                        
class Tags:
    def __init__(self, path_to_the_file):
        self._path_to_the_file = path_to_the_file

        with open(self._path_to_the_file, 'r', encoding='utf-8') as file:
            self.content = file.read()

        self.lines = self.content.split("\n")
        self.headers = [w for w in self.lines[0].split(",")]
        self.dict = {}

        for header in self.headers:
            self.dict.update({header:[]})

        for line in self.lines:
            if line in self.lines[0]:
                continue
            line = line.split(',')
            
            for i in range(len(line)):

                self.dict[self.headers[i]].append(line[i])



    def most_words(self, n):
        unique_tags = set(self.dict["tag"])
        tag_word_count = {}

        for tag in unique_tags:
            if tag != '':
                tag_word_count[tag] = len(tag.split())
        sorted_items = sorted(tag_word_count.items(), key=lambda x: x[1], reverse=True)
        big_tags = dict(sorted_items[:n])

        return big_tags

    def longest(self, n):
        unique_tags = set(self.dict["tag"])
        non_empty = [t for t in unique_tags if t != '']
        sorted_tags = sorted(non_empty, key=lambda x: len(x), reverse=True)
        big_tags = sorted_tags[:n]
        return big_tags

    def most_words_and_longest(self, n):
        set1 = set(self.most_words(n).keys())
        set2 = set(self.longest(n))
        big_tags = sorted(list(set1 & set2))
        return big_tags
        
    def most_popular(self, n):
        from collections import Counter
        non_empty = [t for t in self.dict["tag"] if t != '']
        counter = Counter(non_empty)
        popular_tags = dict(counter.most_common(n))
        return popular_tags
        
    def tags_with(self, word):
        unique_tags = set(t for t in self.dict["tag"] if t != '')
        filtered = [t for t in unique_tags if word.lower() in t.lower()]
        tags_with_word = sorted(filtered)

        return tags_with_word
    


class TestAll:
    @pytest.fixture(scope="class")
    def data(self):
        return Ratings('ratings.csv', 'movies.csv')

    def test_by_year_types_and_sort(self, data):
        mv = data.Movies()
        res = mv.dist_by_year()
        assert isinstance(res, dict)
        assert all(isinstance(k, int) for k in res.keys())
        assert all(isinstance(v, int) for v in res.values())
        keys = list(res.keys())
        assert keys == sorted(keys)

    def test_by_rating_types_and_sort(self, data):
        mv = data.Movies()
        res = mv.dist_by_rating()
        assert isinstance(res, dict)
        assert all(isinstance(k, float) for k in res.keys())
        assert all(isinstance(v, int) for v in res.values())
        keys = list(res.keys())
        assert keys == sorted(keys)

    def test_top_by_num(self, data):
        mv = data.Movies()
        n = 10
        res = mv.top_by_num_of_ratings(n)
        assert isinstance(res, dict)
        assert len(res) <= n, f"Метод должен вернуть не более {n} элементов"
        assert all(isinstance(k, str) for k in res.keys())
        assert all(isinstance(v, int) for v in res.values())
        values = list(res.values())
        assert values == sorted(values, reverse=True)

    def test_top_by_ratings(self, data):
        mv = data.Movies()
        n = 5
        res = mv.top_by_ratings(n, metric='average')
        assert isinstance(res, dict)
        assert len(res) <= n
        assert all(isinstance(k, str) for k in res.keys())
        assert all(isinstance(v, float) for v in res.values())
        values = list(res.values())
        assert values == sorted(values, reverse=True)

    def test_top_controversial(self, data):
        mv = data.Movies()
        n = 5
        res = mv.top_controversial(n)
        assert isinstance(res, dict)
        assert all(isinstance(k, str) for k in res.keys())
        assert all(isinstance(v, float) for v in res.values())
        values = list(res.values())
        assert values == sorted(values, reverse=True)

    def test_users_by_numrat_types_and_sort(self, data):
        usr = data.Users()
        res = usr.users_by_numrat()
        assert isinstance(res, dict)
        assert all(isinstance(k, int) for k in res.keys())
        assert all(isinstance(v, int) for v in res.values())
        keys = list(res.keys())
        assert keys == sorted(keys)

    def test_users_by_average_types_and_sort(self, data):
        usr = data.Users()
        res = usr.users_by_average()
        assert isinstance(res, dict)
        assert all(isinstance(k, float) for k in res.keys())
        assert all(isinstance(v, int) for v in res.values())
        keys = list(res.keys())
        assert keys == sorted(keys)

    def test_top_dispersion_users_types_and_sort(self, data):
        usr = data.Users()
        n = 5
        res = usr.top_dipersia(n)
        assert isinstance(res, dict)
        assert all(isinstance(k, str) for k in res.keys())
        assert all(isinstance(v, float) for v in res.values())
        values = list(res.values())
        assert values == sorted(values, reverse=True)

    @pytest.fixture(scope="class")
    def tags_sample(self):
        return Tags('tags.csv')

    def test_most_words(self, tags_sample):
        n = 5
        result = tags_sample.most_words(n)
        assert isinstance(result, dict)
        assert len(result) <= n
        for tag, word_count in result.items():
            assert isinstance(tag, str)
            assert isinstance(word_count, int)
            assert word_count >= 1
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True)

    def test_longest(self, tags_sample):
        n = 5
        result = tags_sample.longest(n)
        assert isinstance(result, list)
        assert len(result) <= n
        for tag in result:
            assert isinstance(tag, str)
            assert len(tag) >= 1
        lengths = [len(tag) for tag in result]
        assert lengths == sorted(lengths, reverse=True)

    def test_most_words_and_longest(self, tags_sample):
        n = 5
        result = tags_sample.most_words_and_longest(n)
        assert isinstance(result, list)
        for tag in result:
            assert isinstance(tag, str)
        assert len(result) == len(set(result))
        set_most_words = set(tags_sample.most_words(n).keys())
        set_longest = set(tags_sample.longest(n))
        assert set(result).issubset(set_most_words & set_longest)

    def test_most_popular(self, tags_sample):
        n = 5
        result = tags_sample.most_popular(n)
        assert isinstance(result, dict)
        assert len(result) <= n
        for tag, count in result.items():
            assert isinstance(tag, str)
            assert isinstance(count, int)
            assert count >= 1
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True)

    def test_tags_with(self, tags_sample):
        word = "funny"
        result = tags_sample.tags_with(word)
        assert isinstance(result, list)
        for tag in result:
            assert isinstance(tag, str)
            assert word.lower() in tag.lower()
        assert len(result) == len(set(result))
        assert result == sorted(result)

    @pytest.fixture(scope="class")
    def links_sample(self):
        links = Links('links.csv', 'movies.csv')
        list_of_ids = [1,2,3,4,5,6,7,8,9,10]
        links.get_imdb(list_of_ids, ['title', 'imdb_id', 'tmdb_id', 'Director', 'Budget', 'Cumulative Worldwide Gross', 'Runtime', 'Rating', "Metascore"])
        return links

    def test_valid_parse(self, links_sample):
        list_of_ids = [1,2,3,4,5,6,7,8,9,10]
        for movie_id in list_of_ids:
            movie = links_sample.all_data_dict.get(movie_id)
            assert movie is not None, f"Фильм с ID {movie_id} не найден в данных!"
            assert movie['title'] is not None
            assert movie['imdb_id'] is not None
            assert movie['Director'] is not None
            assert movie['Budget'] is not None
            assert movie['Cumulative Worldwide Gross'] is not None
            assert movie['Runtime'] is not None
            assert movie['Rating'] is not None
            assert movie['Metascore'] is not None

    def test_valid_fields(self, links_sample):
        links_sample.data_cleaner()
        for movie in links_sample.all_data_dict.values():
            assert isinstance(movie['Budget'], int) or movie['Budget'] is None
            gross = movie['Cumulative Worldwide Gross']
            assert isinstance(gross, int) or gross is None
            assert isinstance(movie['Runtime'], int) or movie['Runtime'] is None
            assert isinstance(movie['Rating'], float) or movie['Rating'] is None
            assert isinstance(movie['Metascore'], int) or movie['Metascore'] is None

    def test_top_dirs(self, links_sample):
        n = 3
        res = links_sample.top_directors(n)
        assert isinstance(res, dict)
        assert len(res) == n
        for dirs, count in res.items():
            assert isinstance(dirs, str)
            assert isinstance(count, int)
            assert count > 0
        counts = list(res.values())
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i+1], f"Ошибка: {counts[i]} не больше {counts[i+1]}"

    def test_longest(self, links_sample):
        n = 3
        res = links_sample.longest(n)
        assert isinstance(res, dict)
        assert len(res) == n
        for title, runtime in res.items():
            assert isinstance(title, str)
            assert isinstance(runtime, int)
            assert runtime > 0
        counts = list(res.values())
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i+1], f"Ошибка: {counts[i]} не больше {counts[i+1]}"

    def test_most_expensive(self, links_sample):
        n = 3
        res = links_sample.most_expensive(n)
        assert isinstance(res, dict)
        assert len(res) == n
        for title, budget in res.items():
            assert isinstance(title, str)
            assert isinstance(budget, int)
            assert budget > 0
        counts = list(res.values())
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i+1], f"Ошибка: {counts[i]} не больше {counts[i+1]}"

    def test_most_profitable(self, links_sample):
        n = 3
        res = links_sample.most_profitable(n)
        assert isinstance(res, dict)
        assert len(res) == n
        for title, profit in res.items():
            assert isinstance(title, str)
            assert isinstance(profit, int)
            assert profit > 0
        counts = list(res.values())
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i+1], f"Ошибка: {counts[i]} не больше {counts[i+1]}"

    def test_top_cost_per_minute(self, links_sample):
        n = 3
        res = links_sample.top_cost_per_minute(n)
        assert isinstance(res, dict)
        assert len(res) == n
        for title, cost in res.items():
            assert isinstance(title, str)
            assert isinstance(cost, float)
            assert cost == round(cost,2), f"Число {cost} имеет больше 2 знаков после запятой!"
            assert cost > 0
        counts = list(res.values())
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i+1], f"Ошибка: {counts[i]} не больше {counts[i+1]}"

    def test_dual_rating_logic(self, links_sample):
        n = 3
        res = links_sample.dual_raiting(n)
        assert isinstance(res, dict)
        assert len(res) <= n
        for title, scores in res.items():
            assert isinstance(title, str)
            assert isinstance(scores, list)
            assert len(scores) == 2
            imdb_val = scores[0]
            meta_val = scores[1]
            assert isinstance(imdb_val, (float, int))
            assert 0 <= imdb_val <= 10
            assert isinstance(meta_val, int)
            assert 0 <= meta_val <= 100
        imdb_ratings = [val[0] for val in res.values()]
        assert imdb_ratings == sorted(imdb_ratings, reverse=True), "Сортировка по IMDb неверна!"

    @pytest.fixture(scope="class")
    def movies_sample(self):
        return Movies('movies.csv')

    def test_valid_movie_list(self, movies_sample):
        list_ids = movies_sample.list_id
        list_titles = movies_sample.list_titles
        list_genres = movies_sample.list_genres
        assert len(list_ids) == len(list_genres) == len(list_titles)
        assert isinstance(list_ids, list)
        assert isinstance(list_genres, list)
        assert isinstance(list_titles, list)
        for item in list_ids:
            assert isinstance(item, int)
        for item in list_titles:
            assert isinstance(item, str)
        for item in list_genres:
            assert isinstance(item, str)

    def test_dist_by_release(self, movies_sample):
        res = movies_sample.dist_by_release()
        assert isinstance(res, dict)
        assert len(res) > 0
        for year, count in res.items():
            assert len(year) == 4
            assert year.isdigit()
            assert isinstance(count, int)
            assert count >= 1
        counts = list(res.values())
        assert counts == sorted(counts, reverse=True)

    def test_dist_by_genres(self, movies_sample):
        res = movies_sample.dist_by_genres()
        assert isinstance(res, dict)
        assert len(res) > 0
        for genre, count in res.items():
            assert isinstance(genre, str)
            assert isinstance(count, int)
        counts = list(res.values())
        assert counts == sorted(counts, reverse=True)

    def test_most_genres(self, movies_sample):
        n = 5
        res = movies_sample.most_genres(n)
        assert isinstance(res, dict)
        assert len(res) == n
        for genre, count in res.items():
            assert isinstance(genre, str)
            assert isinstance(count, int)
        counts = list(res.values())
        assert counts == sorted(counts, reverse=True)
