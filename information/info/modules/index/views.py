from flask import render_template, current_app, session, request, jsonify

from . import index_blu
from ... import constants
from ...models import User, News, Category
from ...utils.response_code import RET


@index_blu.route('/')
def index():
    """
    主页
    :return:
    """
    # 获取到当前登录用户的id
    user_id = session.get("user_id")
    # 通过id获取登录用户信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    click_news_list = []
    for news in news_list if news_list else []:
        click_news_list.append(news.to_basic_dict())
    # 新闻分类展示
    categories = Category.query.all()
    categories_dicts = []
    for category in categories:
        # 拼接内容
        categories_dicts.append(category.to_dict())

    data = {
        "user_info":user.to_dict() if user else None,
        "click_news_list": click_news_list,
        "categories": categories_dicts,
    }
    return render_template('news/index.html', data=data)

@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')

@index_blu.route('/newslist')
def get_new_list():
    """
    获取制定分类的新闻列表
    :return:
    """
    # 1. 获取参数
    args_dict = request.args
    page = args_dict.get("p", '1')
    per_page = args_dict.get("per_page", constants.HOME_PAGE_MAX_NEWS)
    category_id = args_dict.get("cid", "1")
    # 2. 校验参数
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误！")
    # 3. 查询数据并分页
    filters = []
    # 如果分类id不为1, 那么添加分类id的过滤
    if category_id != '1':
        filters.append(News.category_id == category_id)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        # 获取查询出来的数据
        items = paginate.items
        # 获取到总页数
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败！")
    news_li = []
    for news in items:
        news_li.append(news.to_basic_dict())

    # 返回数据
    return jsonify(errno=RET.OK, errmsg="OK", total_page=total_page, currentPage=current_page, newsList=news_li, cid=category_id)

# @index_blu.route('/newslist')
# def get_news_list():
#     """
#     获取指定分类的新闻列表
#     1. 获取参数
#     2. 校验参数
#     3. 查询数据
#     4. 返回数据
#     :return:
#     """
#
#     # 1. 获取参数
#     args_dict = request.args
#     page = args_dict.get("p", '1')
#     per_page = args_dict.get("per_page", constants.HOME_PAGE_MAX_NEWS)
#     category_id = args_dict.get("cid", '1')
#
#     # 2. 校验参数
#     try:
#         page = int(page)
#         per_page = int(per_page)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
#
#     # 3. 查询数据并分页
#     filters = []
#     # 如果分类id不为1，那么添加分类id的过滤
#     if category_id != "1":
#         filters.append(News.category_id == category_id)
#     try:
#         paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
#         # 获取查询出来的数据
#         items = paginate.items
#         # 获取到总页数
#         total_page = paginate.pages
#         current_page = paginate.page
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
#
#     news_li = []
#     for news in items:
#         news_li.append(news.to_basic_dict())
#
#     # 4. 返回数据
#     return jsonify(errno=RET.OK, errmsg="OK", totalPage=total_page, currentPage=current_page, newsList=news_li, cid=category_id)