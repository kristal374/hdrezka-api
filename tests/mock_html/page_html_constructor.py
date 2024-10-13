import base64
import re
from typing import Iterable, Callable, Any, List, Dict, Tuple
from urllib.parse import quote, urlsplit

from HDrezka.filters import convert_genres
from tests.mock_html.html_construcror import read_reference_file

BASE_TABLE = '<table class="b-post__info">{data}</table>'
ITEM_TABLE = ' <tr> <td class="l"><h2>{title}</h2>:</td> <td>{data} </td> </tr>'
RELEASE_WRAPPER = ' <tr> <td class="l">{title}:</td> <td>{data} </td> </tr>'
DURATION_WRAPPER = '<tr><td class="l"><h2>Время</h2>:</td> <td itemprop="duration">{duration}.</td></tr>'
ON_THE_LIST_WRAPPER = ' <tr> <td class="l"><h2>Входит в списки</h2>:</td> <td class="rd">{data}</td> </tr>'
ITEM_WRAPPER = '<tr><td colspan="2">{data}</td></tr>'
COLLECTIONS_ITEM = ' <a href="{url}">{title}</a>, '
ON_THE_LIST_LINK_ITEM = '<a href="{url}">{title}</a> ({place})<br/>'
COUNTRY_ITEM = '<a href="https://rezka.ag/country/{percent_encoding}/">{country}</a>,'
YEAR_ITEM = '{date} <a href="https://rezka.ag/year/{year}/">{year_full}</a>{postfix}'
GENRE_ITEM = '<a href="https://rezka.ag/{entity}/{en_genre}/"><span itemprop="genre">{genre}</span></a>, '
PERSON_LIST = ' <div class="persons-list-holder"> {data}</div>'
ACTORS_LIST = ' <span class="l inline"><h2>В ролях актеры</h2>: </span>{data}<span class="item">и другие</span>'
AGE_RESTRICTIONS_ITEM = '<span class="bold" style="color: #666;">{age}</span>{description}'
RATES_ITEM = ' <span class="b-post__info_rates {class}"><a href="{help_url}" rel="nofollow" target="_blank">' \
             '{name}</a>: <span class="bold">{rates:.2f}</span> <i>({votes})</i></span>'
SIMPLE_RATES_ITEM = '<span class="b-post__info_rates {class}">{name}: <span ' \
                    'class="bold">{rates}</span> <i>({votes})</i></span>'
PERSON_ITEM = '<span class="item"><span class="person-name-item" data-id="{person_id}" data-job="{job}" data-photo=' \
              '"{img_url}" data-pid="{film_id}" itemprop="{function}" itemscope="" itemtype="http://schema.org/' \
              'Person"><a href="{url}" itemprop="url"><span itemprop="name">{name}</span></a></span>,</span> '
SIMPLE_PERSON_ITEM = ' <span class="item">{name},</span> '


def build_text_from_template(iteration_obj: Iterable[Any], template: str,
                             transform_func: Callable[[Any], dict] = lambda x: x):
    """Build a text string by applying a template format to each item in the iterable object."""
    return ''.join(template.format(**transform_func(item)) for item in iteration_obj)


def __gen_rates(item):
    hdrezka_item = list(filter(lambda x: x["name"] == "HDrezka", item))
    hdrezka_index = item.index(hdrezka_item[0]) if hdrezka_item else 3
    item = item[0:hdrezka_index] + item[hdrezka_index + 1:0]

    if item:
        result_string = ""
        for rates in item:
            data = {
                "class": "imdb" if rates["name"] == "IMDb" else "kp" if rates["name"] == "Кинопоиск" else "wa",
                "name": rates['name'],
                "rates": rates['rates'],
                "votes": f'{rates["votes"]:,}'.replace(',', ' ')
            }
            if rates['source'] is None:
                result_string += SIMPLE_RATES_ITEM.format(**data)
            else:
                help_url = f"/help/{base64.b64encode(quote(rates['source'], safe='').encode('utf-8')).decode('utf-8')}/"
                data["help_url"] = help_url
                result_string += RATES_ITEM.format(**data)
        return ITEM_TABLE.format(title="Рейтинги", data=result_string)
    return ""


def __gen_release(item):
    matches = re.search(r"(\d+)?\s?([А-я]+)?\s?(\d{4})\s?(года?|-\s\.{3})?", item)
    day, month, year, ending = matches.groups()
    data = {
        "date": f"{day} {month}" if day else "",
        "year": year,
        "year_full": f"{year} {ending}" if ending is not None and ending != '- ...' else year,
        "postfix": f" {ending}" if ending == '- ...' else ""
    }

    if ending == '- ...' or ending is None:
        return RELEASE_WRAPPER.format(title="Год", data=YEAR_ITEM.format(**data))
    return ITEM_TABLE.format(title="Дата выхода", data=YEAR_ITEM.format(**data))


def __gen_country(item):
    data = build_text_from_template(item, COUNTRY_ITEM, lambda x: {
        "country": x,
        "percent_encoding": quote(x.replace(" ", "+"), safe="+")
    })[:-1]
    return ITEM_TABLE.format(title="Страна", data=data)


def __gen_genre(item, entity):
    data = build_text_from_template(item, GENRE_ITEM, lambda x: {
        "entity": entity,
        "en_genre": convert_genres(x),
        "genre": x})
    return ITEM_TABLE.format(title="Жанр", data=data[:-2])


def __gen_age_restrictions(item):
    description = {"0+": "можно смотреть всей семьей и наслаждаться просмотром",
                   "6+": "можно смотреть всей семьей, дети могут задавать вопросы и отвлекать",
                   "12+": "взрослые темы и понятия, но темы не раскрыты",
                   "14+": "взрослые темы и понятия, неподходящие для детей",
                   "16+": "для более зрелых и понимающих",
                   "18+": "только для взрослых"
                   }
    data = AGE_RESTRICTIONS_ITEM.format(age=item, description=description[item])
    return ITEM_TABLE.format(title="Возраст", data=data)


def __gen_persons(item, film_id, role):
    result_string = ""
    for person in item:
        if person["id"] is None:
            result_string += SIMPLE_PERSON_ITEM.format(name=person["name"])
        else:
            result_string += PERSON_ITEM.format(**{
                "person_id": person["id"],
                "job": person["job"],
                "film_id": film_id,
                "function": role,
                "url": person["url"],
                "img_url": person["img_url"] if person["img_url"] is not None else "null",
                "name": person["name"],
            })
    return result_string[:-9] + "</span>"


def create_info_table_html(info_table: dict, url: str) -> str:
    film_id = re.search(r"/(\d*)-", url).group(1)
    entity = urlsplit(url).path.split("/")[1]

    result_string = ""
    for key in info_table:
        value = info_table.get(key)

        if not value:
            continue

        if key == "rates":
            result_string += __gen_rates(value)
        elif key == "on_the_lists":
            data = build_text_from_template(value, ON_THE_LIST_LINK_ITEM)[:-5]
            result_string += ON_THE_LIST_WRAPPER.format(data=data)
        elif key == "tagline":
            result_string += ITEM_TABLE.format(title="Слоган", data=value)
        elif key == "release":
            result_string += __gen_release(value)
        elif key == "country":
            result_string += __gen_country(value)
        elif key == "producer":
            data = __gen_persons(value, film_id, role="director")
            result_string += ITEM_TABLE.format(title="Режиссер", data=PERSON_LIST.format(data=data))
        elif key == "genre":
            result_string += __gen_genre(value, entity)
        elif key == "age_restrictions":
            result_string += __gen_age_restrictions(value)
        elif key == "duration":
            result_string += DURATION_WRAPPER.format(duration=value)
        elif key == "collections":
            data = build_text_from_template(value, COLLECTIONS_ITEM)[:-2]
            result_string += ITEM_TABLE.format(title="Из серии", data=data)
        elif key == "quality":
            result_string += ITEM_TABLE.format(title="В качестве", data=value)
        elif key == "translate":
            data = ', '.join(value) if len(value) == 1 else f"{', '.join(value[:-1])} и {value[-1]}"
            result_string += ITEM_TABLE.format(title="В переводе", data=data)
        elif key == "cast":
            data = __gen_persons(value, film_id, role="actor")
            result_string += ITEM_WRAPPER.format(data=PERSON_LIST.format(data=ACTORS_LIST.format(data=data)))
        else:
            raise TypeError(key)

    return BASE_TABLE.format(data=result_string)


def generate_info_table() -> List[Tuple[Dict[str, Any], str]]:
    reference_data = read_reference_file("reference_movie_data.json")
    result_lst = []
    for film_id in reference_data:
        info_table = create_info_table_html(reference_data[film_id]["info_table"], reference_data[film_id]["url"])
        result_lst.append((reference_data[film_id]["info_table"], info_table))
    return result_lst
