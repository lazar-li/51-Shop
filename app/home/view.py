from . import home
from app import db
# from app.home.forms import LoginForm, RegisterForm, PasswordForm
from app.models import User, Goods, Orders, Cart, OrdersDetail
from flask import render_template, url_for, redirect, flash, session, request, make_response
from werkzeug.security import generate_password_hash
from functools import wraps
import random
import string
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

def user_login(f):
    """
    登录装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            # return redirect(url_for("home.login"))
            pass
        return f(*args, **kwargs)

    return decorated_function

#-------------------------显示商品的详细信息功能---------------------------------

@home.route("/goods_detail/<int:id>")
#id 为商品ID
def goods_detail(id=None):
    """
    详情页
    """
    #获取用户ID 判断用户是否登录
    user_id = session.get("user_id",0)
    #根据景区ID获取景区数据，如果不存在则返回404
    goods = Goods.query.get_or_404(id)
    #浏览器量加1
    goods.views_count += 1
    db.session.add(goods) #添加数据
    db.session.commit()#提交数据
    #获取左侧热门商品

    hot_goods = Goods.query.filter_by(subcat_id=goods.subcat_id).order_by(Goods.views_count.desc()).limit(5).all()
    #获取底部相关商品
    similar_goods = Goods.query.filter_by(subcat_id=goods.subcat_id).order_by(Goods.addtime.desc()).limit(5).all()
    #渲染模板
    return render_template('home/goods_detail.html',goods=goods,hot_goods=hot_goods,similar_goods=similar_goods,user_id=user_id)



#--------------------------------------添加购物车----------------------------------
@home.route("/cart_add")

@user_login
def cart_add():
    """
    添加购物车
    """
    #获取前端输入的值
    cart = Cart(
        goods_id = request.args.get("goods_id"),
        number = request.args.get("number"),
        #判断用户ID 判断用户是否登陆
        user_id = session.get("user_id",0)
    )
    #增加数据
    db.session.add(cart)
    #提交数据
    db.session.commit()
    return redirect(url_for("home.shopping_cart"))


#-----------------------------------查看购物车功能------------------------------------
@home.route("/shopping_cart")
@user_login
def shopping_cart():
    user_id = session.get('user_id',0)
    cart = Cart.query.filter_by(user_id=int(user_id)).order_by(Cart.addtime.desc()).all()

    if cart:
        return render_template('home/shopping_cart.html',cart=cart)
    else:
        return render_template("home/empty_cart.html")

    


#-------------------------实现保存订单功能-------------------------------------

@home.route("/cart_order/",methods=["GET,POST"])
@user_login
def cart_order():
    if request.method == "POST":
        #获取用户ID
        user_id = session.get("user_id",0)
        orders = Orders(
            user_id = user_id,
            recevie_name = request.form.get("recevie_name"),
            recevie_tel = request.form.get("recevie_tel"),
            recevie_address = request.form.get("recevie_address"),
            remark = request.form.get("remark")
        )
        #添加数据
        db.session.add(orders)
        #提交数据
        db.session.add(orders)
        #添加订单详情
        cart = Cart.query.filter_by(user_id=user_id).all()
        object = []
        for item in cart:
            object.append(
                OrdersDetail(
                    order_id = orders.id,
                    goods_id = item.goods_id,
                    number = item.number,
                )
            )
        db.session.add_all(object)
        #更改购物车状态
        Cart.query.filter_by(user_id=user_id).update({'user_id':0})
        #提交
        db.session.commit()
        #重定向首页
    return redirect(url_for('home.index'))


#-----------------------------------查看订单功能--------------------------------

@home.route("/order_list/",methods = ["GET","POST"])

@user_login
def order_list():
    """
    我的订单
    """
    user_id = session.get("user_id",0)

    orders = OrdersDetail.query.join(Orders).filter(Orders.user_id == user_id).order_by(Orders.addtime.desc()).all()
    
    return render_template("home/order_list.html",orders=orders)

# ------------------------------清空购物车-------------------------
@home.route("/cart_clear/")
@user_login
def cart_clear():

    user_id = session.get('user_id', 0)  # 获取用户ID,判断用户是否登录
    Cart.query.filter_by(user_id=user_id).update({'user_id': 0})
    #提交
    db.session.commit()
    return redirect(url_for('home.shopping_cart'))