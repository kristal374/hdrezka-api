import copy
import json
import os
import re

HTML_BASE = '<!DOCTYPE html><html lang="ru-RU"><head><meta charset="utf-8"/></head><body ' \
            'class="has-brand active-brand pp fixed-header"><div id="wrapper"><div id="main"><div ' \
            'class="b-container b-content b-wrapper">{type}</div></div></div></body></html>'

POSTERS = '<div class="b-content__inline"><div class="b-content__inline_inner b-content__inline_inner_mainprobar ' \
          'clearfix"><div class="b-content__inline_items">{data}</div></div></div>'

COLLECTIONS = '<div class="b-content__main"><div class="b-content__collections_list clearfix">{data}</div></div>'

SAMPLE_POSTERS = '<div class="b-content__inline_item" data-id="{id}" data-url="{url}"><div class=' \
                 '"b-content__inline_item-cover"><a href="{url}"> <img src="{img_url}" height="250" ' \
                 'width="166" alt="Смотреть {title} онлайн в HD качестве 720p"/><span class="cat animation">' \
                 '<i class="entity">{entity}</i><i class="icon"></i></span> {info}<i class="i-sprt play"></i> ' \
                 '</a>{trailer}</div><div class="b-content__inline_item-link"><a href="{url}">{title}</a>' \
                 '<div>{metadata}</div></div></div>'

SAMPLE_COLLECTIONS = '<div class="b-content__collections_item" data-url="{url}"><img class="cover" src="{img_url}" ' \
                     'height="120" width="208" alt="Смотреть {title_lower} онлайн в HD качестве "/><div ' \
                     'title="Количество видео в данной подборке" class="num hd-tooltip">{amount_film}</div>' \
                     '<div class="title-layer"><a href="{url}" class="title">{title}</a></div></div>'


def generate_poster_html(content):
    data = ""
    for item in content:
        info = re.sub(r'(\d+ сезон) (\d+ серия)', r'\1, \2', item["info"] if item["info"] else "")
        trailer = f'<i class="trailer show-trailer" data-id="{item["id"]}" data-full="1"><b>Смотреть трейлер</b></i>'
        metadata = (item["year"], item["country"], item["genre"])

        item["info"] = f'<span class="info">{info}</span> ' if info else info
        item["trailer"] = trailer if item["trailer"] else ""
        item["metadata"] = ", ".join(filter(lambda x: x is not None, metadata))
        data += SAMPLE_POSTERS.format(**item)
    return HTML_BASE.format(type=POSTERS.format(data=data).replace("    ", "").replace("\n", ""))


def generate_collections_html(content):
    data = ""
    for item in content:
        item["title_lower"] = item["title"].lower()
        data += SAMPLE_COLLECTIONS.format(**item)
    return HTML_BASE.format(type=COLLECTIONS.format(data=data).replace("    ", "").replace("\n", ""))


def generate_fake_html(reference_name):
    current_file_path = os.path.abspath(__file__)
    file_path = os.path.join(os.sep, os.path.dirname(current_file_path), 'reference_data.json')
    with open(file_path, "r", encoding="utf-8") as json_file:
        reference_data = json.loads(json_file.read())

    if reference_name == "collections":
        return copy.deepcopy(reference_data), generate_collections_html(reference_data[reference_name])
    return copy.deepcopy(reference_data), generate_poster_html(reference_data[reference_name])
