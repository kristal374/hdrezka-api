import copy
import json
import os
import re
from datetime import datetime
from typing import Union, List, Dict, Tuple, Any, Optional

HTML_BASE = '<!DOCTYPE html><html lang="ru-RU"><head><meta charset="utf-8"/></head><body ' \
            'class="has-brand active-brand pp fixed-header"><div id="wrapper"><div id="main"><div ' \
            'class="b-container b-content b-wrapper">{type}</div></div></div></body></html>'

POSTERS = '<div class="b-content__inline"><div class="b-content__inline_inner b-content__inline_inner_mainprobar ' \
          'clearfix"><div class="b-content__inline_items">{data}</div></div></div>'

COLLECTIONS = '<div class="b-content__main"><div class="b-content__collections_list clearfix">{data}</div></div>'

SAMPLE_POSTERS = '<div class="b-content__inline_item" data-id="{id}" data-url="{url}"><div class=' \
                 '"b-content__inline_item-cover"><a href="{url}"> <img src="{img_url}" height="250" ' \
                 'width="166" alt="Смотреть {title} онлайн в HD качестве 720p"/><span class="cat animation">' \
                 '<i class="entity">{entity}{rates}</i><i class="icon"></i></span> {info}<i class="i-sprt play"></i> ' \
                 '</a>{trailer}</div><div class="b-content__inline_item-link"><a href="{url}">{title}</a>' \
                 '<div>{metadata}</div></div></div>'

SAMPLE_COLLECTIONS = '<div class="b-content__collections_item" data-url="{url}"><img class="cover" src="{img_url}" ' \
                     'height="120" width="208" alt="Смотреть {title_lower} онлайн в HD качестве "/><div ' \
                     'title="Количество видео в данной подборке" class="num hd-tooltip">{amount_film}</div>' \
                     '<div class="title-layer"><a href="{url}" class="title">{title}</a></div></div>'

SAMPLE_COMMENTS_TREE = "<ol class=\"comments-tree-list\">{}</ol>"

SAMPLE_COMMENT_ITEM = "<li id=\"comments-tree-item-{id}\" class=\"comments-tree-item\" data-id=\"{id}\" " \
                      "data-indent=\"0\"><div id='comment-id-{id}'><div class=\"b-comment clearfix{admin}\">" \
                      "\r\n    <div class=\"ava\">\r\n        <img src=\"{img_url}\" height=\"60\" width=\"60\" " \
                      "alt=\"{alt_name}\" />\r\n    </div>\r\n    <div class=\"message\">\r\n        <div " \
                      "class=\"info\">\r\n            <!-- <span class=\"b-comment__answers_ctrl\" data-show=" \
                      "\"1\">скрыть ответы</span> -->\r\n            {report}<span class=\"name\">{user_name}" \
                      "</span>,\r\n            <span class=\"date\">{timestamp}</span>{edited}\r\n            " \
                      "<a class=\"share-link\" href=\"{url_postfix}\" data-id=\"{id}\">#</a>\r\n            " \
                      "\r\n        </div>\r\n        <div class=\"text\"><div id='comm-id-{id}'>{text}</div>" \
                      "</div>\r\n        <div class=\"actions\">\r\n            <ul class=\"edit\">" \
                      "\r\n                \r\n                <li></li>\r\n                <li></li>" \
                      "\r\n                \r\n            </ul>\r\n            <span class=\"b-comment__quoteuser\" " \
                      "onclick=\"sof.comments.quoteUser('{user_name}', '{id}', '{indentation}');\">Ответить</span>" \
                      "\r\n            <span data-likes_num=\"{likes_num}\" class=\"show-likes-comment " \
                      "b-comment__like_it guest\" data-comment_id=\"{id}\"><i>Поддерживаю!</i></span>" \
                      "\r\n            <span class=\"b-comment__likes_count\"{style}>(<i{class}>{likes_num}</i>)" \
                      "</span>\r\n            \r\n        </div>\r\n    </div>    \r\n</div>\r\n</div>{replies}</li>"

SPOILER = "<!--dle_spoiler--><div class=\"title_spoiler\"><img id=\"image-sp0123456789abcdef0123456789abcdef\" " \
          "style=\"vertical-align: middle;border: none;\" alt=\"\" src=\"https://rezka.ag/templates/hdrezka/" \
          "dleimages/spoiler-plus.gif\" /><a href=\"javascript:ShowOrHide('sp0123456789abcdef0123456789abcdef')\">" \
          "спойлер<img class=\"attention\" height=\"15\" width=\"16\" src=\"https://static.hdrezka.ac/templates/" \
          "hdrezka/images/spoiler-attention.png\" alt=\"\" /></a></div><div id=\"sp0123456789abcdef0123456789abcdef\"" \
          " class=\"text_spoiler\" style=\"display:none;\">{text}</div><!--/dle_spoiler-->"

NO_AVATAR = "https://static.hdrezka.ac/templates/hdrezka/images/noavatar.png"
EDITED = ' <span class="edited hd-tooltip" title="Отредактировано Администрацией"></span>'
REPORT = "<i title=\"Пожаловаться на комментарий\" class=\"b-comment__report hd-tooltip\" " \
         "data-id=\"{id}\"></i>\r\n            "
LINK = '<a href="{text}" target="_blank">{text}</a>'
YOUTUBE_URL = '<!--noindex--><a class="youtu-link" data-youtube-id="{url_id}"  ' \
              'href="{url}" rel="nofollow" target="_blank">смотреть</a><!--/noindex-->'
TAG = ' <a class="tag-link" href="javascript:void(0)" rel="nofollow">{text}</a>'

SAMPLE_NAVIGATION = '<!--noindex--><div class="b-navigation">{data}</div><!--/noindex-->'
SAMPLE_NAVIGATION_ITEM = '<a rel="nofollow" onclick="sof.comments.loadComments({id}, {page}, false, 0);' \
                         ' return false;" href="javascript:void(0)">{view}</a>'
SAMPLE_CURRENT_NAVIGATION_ITEM = '<span>{page}</span>'
SAMPLE_PREVIEW_NAVIGATION_ITEM = '<span class="b-navigation__prev i-sprt">&nbsp;</span>'
SAMPLE_NEXT_NAVIGATION_ITEM = '<span class="b-navigation__next i-sprt">&nbsp;</span>'
SAMPLE_INTERMEDIATE_NAVIGATION_ITEM = '<span class="nav_ext">...</span>'

SAMPLE_TRAILER = '<iframe width="640" height="360" src="{trailer_url}" frameborder="0" ' \
                 'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" ' \
                 'allowfullscreen style="background: transparent; position: relative;"></iframe>'
SAMPLE_TITLE = '&laquo;{title}&raquo; <small>(оригинальное название: "{original_title}", {release_year})</small>'


def read_reference_file(file_name: str) -> dict:
    current_file_path = os.path.abspath(__file__)
    file_path = os.path.join(os.sep, os.path.dirname(current_file_path), file_name)
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.loads(json_file.read())


def generate_poster_html(content: List[Dict[str, Any]]) -> str:
    data = ""
    for item in content:
        info = re.sub(r'(\d+ сезон) (\d+ серия)', r'\1, \2', item["status"] if item["status"] else "")
        trailer = f'<i class="trailer show-trailer" data-id="{item["id"]}" data-full="1"><b>Смотреть трейлер</b></i>'
        rates = f'<i class="b-category-bestrating rating-green-string" style="display: inline;">({item["rates"]})</i>'
        metadata = (item["year"], item["country"], item["genre"])

        item["info"] = f'<span class="info">{info}</span> ' if info else info
        item["trailer"] = trailer if item["trailer"] else ""
        item["metadata"] = ", ".join(filter(lambda x: x is not None, metadata))
        item["rates"] = rates if item["rates"] else ""
        data += SAMPLE_POSTERS.format(**item)
    return HTML_BASE.format(type=POSTERS.format(data=data).replace("    ", "").replace("\n", ""))


def generate_collections_html(content: List[Dict[str, Any]]) -> str:
    data = ""
    for item in content:
        item["title_lower"] = item["title"].lower()
        data += SAMPLE_COLLECTIONS.format(**item)
    return HTML_BASE.format(type=COLLECTIONS.format(data=data).replace("    ", "").replace("\n", ""))


def generate_fake_html(reference_name: str) -> Tuple[List[Dict[str, Any]], str]:
    reference_data = read_reference_file("reference_posters.json")

    if reference_name == "collections":
        return copy.deepcopy(reference_data)[reference_name], generate_collections_html(reference_data[reference_name])
    return copy.deepcopy(reference_data[reference_name]), generate_poster_html(reference_data[reference_name])


def convert_datetime_into_string(datetime_string):
    month_name = ("", "января", "февраля", "марта", "апреля", "мая", "июня", "июля",
                  "августа", "сентября", "октября", "ноября", "декабря")
    timestamp = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    return timestamp.strftime("%d {month} %Y %H:%M").format(month=month_name[timestamp.month])


def prepare_comment_text(comment_text: str) -> str:
    def convert(pattern, new_pattern, text, fun=None):
        while re.search(pattern, text, flags=re.S):
            match = re.search(pattern, text, flags=re.S)
            formatted_text = new_pattern.format(**(fun if fun is not None else lambda x: {'text': x.group(1)})(match))
            text = re.sub(pattern, formatted_text, text, count=1, flags=re.S)
        return text

    comment_text = convert(r'(https?://youtu[^\s<>"\(\)\,]+(?![^<]*</a>))', YOUTUBE_URL, comment_text,
                           fun=lambda x: {'url': x.group(1), 'url_id': x.group(1)[17:]})
    comment_text = convert(r'(https?://rezka\.ag[^\s<>"\(\)\,]+(?![^<]*</a>))', LINK, comment_text)
    comment_text = convert(r'(?:^|\s)(#[A-z0-9]+(?![^<]*</a>))', TAG, comment_text)
    comment_text = convert(r'<spoiler>((?:(?!<\/?spoiler>).)*)<\/spoiler>', SPOILER, comment_text)

    return comment_text


def generate_comment(comments: List[Dict[str, Any]], indentation=0) -> str:
    result_string = ""
    if not comments:
        return result_string
    for comment in comments:
        comment_content = {
            "id": comment["id"],
            "img_url": comment["author"]["img_url"],
            "alt_name": comment["author"]["name"] if comment["author"]["img_url"] != NO_AVATAR else "",
            "user_name": comment["author"]["name"],
            "timestamp": "оставлен " + convert_datetime_into_string(comment["timestamp"]),
            "url_postfix": "#comment" + str(comment["id"]),
            "text": prepare_comment_text(comment["text"]),
            "indentation": indentation,
            "likes_num": comment["likes_num"],
            "edited": EDITED if comment["edit"] else "",
            "replies": generate_comment(comment["replies"], indentation=indentation + 1),
            "style": ' style="display: inline;"' if comment["likes_num"] > 0 else "",
            "class": ' class="positive"' if comment["likes_num"] > 0 else "",
            "admin": " b-comment__admin" if comment["author"]["name"] == "Администрация" else "",
            "report": REPORT.format(id=comment["id"]) if comment["author"]["name"] != "Администрация" else ""
        }
        result_string += SAMPLE_COMMENT_ITEM.format(**comment_content)
    return SAMPLE_COMMENTS_TREE.format(result_string)


def generate_navigation_string(film_id: Union[str, int], current_page: int, first_page: int, last_page: int) -> str:
    result_string = ""

    if first_page == last_page:
        return result_string

    if current_page != first_page:
        result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=current_page - 1,
                                                       view=SAMPLE_PREVIEW_NAVIGATION_ITEM)

    if current_page - 6 < first_page:
        for page in range(first_page, last_page + 1)[:10]:
            if page != current_page:
                result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=page, view=page)
            else:
                result_string += SAMPLE_CURRENT_NAVIGATION_ITEM.format(page=page)
        if last_page > 10:
            result_string += SAMPLE_INTERMEDIATE_NAVIGATION_ITEM
            result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=last_page, view=last_page)
    elif current_page - 5 > first_page and current_page + 4 < last_page:
        result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=first_page, view=first_page)
        result_string += SAMPLE_INTERMEDIATE_NAVIGATION_ITEM
        for page in range(current_page - 4, current_page + 4 + 1):
            if page != current_page:
                result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=page, view=page)
            else:
                result_string += SAMPLE_CURRENT_NAVIGATION_ITEM.format(page=page)
        if last_page > 10:
            result_string += SAMPLE_INTERMEDIATE_NAVIGATION_ITEM
            result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=last_page, view=last_page)
    else:
        result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=first_page, view=first_page)
        if last_page > 10:
            result_string += SAMPLE_INTERMEDIATE_NAVIGATION_ITEM
            for page in range(last_page - 9, last_page + 1):
                if page != current_page:
                    result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=page, view=page)
                else:
                    result_string += SAMPLE_CURRENT_NAVIGATION_ITEM.format(page=page)
        else:
            for page in range(first_page + 1, last_page + 1):
                if page != current_page:
                    result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=page, view=page)
                else:
                    result_string += SAMPLE_CURRENT_NAVIGATION_ITEM.format(page=page)
    if current_page != last_page:
        result_string += SAMPLE_NAVIGATION_ITEM.format(id=film_id, page=current_page + 1,
                                                       view=SAMPLE_NEXT_NAVIGATION_ITEM)

    return SAMPLE_NAVIGATION.format(data=result_string)


def generate_comments_tree() -> List[Tuple[List[Dict[str, Any]], Dict[str, Union[str, int]]]]:
    reference_data = read_reference_file("reference_comments.json")
    result_lst = []
    for film_id in reference_data:
        for page in reference_data[film_id]:
            response_obj = {
                "navigation": generate_navigation_string(film_id, int(page), 1, len(reference_data[film_id])),
                "comments": generate_comment(reference_data[film_id][page]),
                "last_update_id": 0
            }
            result_lst.append((reference_data[film_id][page], response_obj))
    return result_lst


def generate_trailer_info() -> List[Tuple[Dict[str, Optional[Union[str, int]]], Dict[str, Union[bool, str]]]]:
    reference_data = read_reference_file("reference_trailer.json")
    result_lst = []
    for film_id in reference_data:
        item = reference_data[film_id]
        response_obj = {'success': True,
                        'message': 'Возникла неизвестная ошибка',
                        'code': SAMPLE_TRAILER.format(trailer_url=item["trailer_url"]),
                        'title': SAMPLE_TITLE.format(title=item["title"],
                                                     original_title=item["original_title"],
                                                     release_year=item["release_year"]),
                        'description': item["description"],
                        'link': item["url"]}
        result_lst.append((item, response_obj))
    return result_lst
