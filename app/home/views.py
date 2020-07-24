# _*_ coding: utf-8 _*_
from . import home
from app import db
from app.home.forms import LoginForm,PasswordForm
from app.models import User ,Goods,Orders,Cart,OrdersDetail
from flask import render_template, url_for, redirect, flash, session, request,make_response
from werkzeug.security import generate_password_hash
from functools import wraps
import random
import string
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

def rndColor():
    '''随机颜色'''
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

def gene_text():
    '''生成4位验证码'''
    return ''.join(random.sample(string.ascii_letters+string.digits, 4))

def draw_lines(draw, num, width, height):
    '''划线'''
    for num in range(num):
        x1 = random.randint(0, width / 2)
        y1 = random.randint(0, height / 2)
        x2 = random.randint(0, width)
        y2 = random.randint(height / 2, height)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

def get_verify_code():
    '''生成验证码图形'''
    code = gene_text()
    # 图片大小120×50
    width, height = 120, 50
    # 新图片对象
    im = Image.new('RGB',(width, height),'white')
    # 字体
    font = ImageFont.truetype('app/static/fonts/arial.ttf', 40)
    # draw对象
    draw = ImageDraw.Draw(im)
    # 绘制字符串
    for item in range(4):
        draw.text((5+random.randint(-3,3)+23*item, 5+random.randint(-3,3)),
                  text=code[item], fill=rndColor(),font=font )
    return im, code


@home.route('/code')
def get_code():
    image, code = get_verify_code()
    # 图片以二进制形式写入
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把buf_str作为response返回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = code
    return response

def user_login(f):
    """
    登录装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("home.login"))
        return f(*args, **kwargs)

    return decorated_function

@home.route("/login/", methods=["GET", "POST"])
def login():
    """
    登录
    """
    if "user_id" in session:        # 如果已经登录，则直接跳转到首页
        return redirect(url_for("home.index"))
    form = LoginForm()              # 实例化LoginForm类
    if form.validate_on_submit():   # 如果提交
        data = form.data            # 接收表单数据
        # 判断验证码
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('验证码错误',"err")
            return render_template("home/login.html", form=form)  # 返回登录页
        # 判断用户名是否存在
        user = User.query.filter_by(username=data["username"]).first()    # 获取用户信息
        if not user :
            flash("用户名不存在！", "err")           # 输出错误信息
            return render_template("home/login.html", form=form)  # 返回登录页
        # 判断用户名和密码是否匹配
        if not user.check_password(data["password"]):     # 调用check_password()方法，检测用户名密码是否匹配
            flash("密码错误！", "err")           # 输出错误信息
            return render_template("home/login.html", form=form)  # 返回登录页

        session["user_id"] = user.id                # 将user_id写入session, 后面用户判断用户是否登录
        session["username"] = user.username                # 将user_id写入session, 后面用户判断用户是否登录
        return redirect(url_for("home.index")) # 登录成功，跳转到首页

    return render_template("home/login.html",form=form) # 渲染登录页面模板

@home.route("/register/", methods=["GET", "POST"])
def register():
    """
    注册功能
    """
    if "user_id" in session:
        return redirect(url_for("home.index"))
    form = RegisterForm()           # 导入注册表单
    if form.validate_on_submit():   # 提交注册表单
        data = form.data            # 接收表单数据
        # 为User类属性赋值
        user = User(
            username = data["username"],            # 用户名
            email = data["email"],                  # 邮箱
            password = generate_password_hash(data["password"]),# 对密码加密
            phone = data['phone']
        )
        db.session.add(user) # 添加数据
        db.session.commit()  # 提交数据
        return redirect(url_for("home.login"))  # 登录成功，跳转到首页
    return render_template("home/register.html", form=form) # 渲染模板

@home.route("/logout/")
def logout():
    """
    退出登录
    """
    # 重定向到home模块下的登录。
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for('home.login'))

@home.route("/modify_password/",methods=["GET","POST"])
@user_login
def modify_password():
    """
    修改密码
    """
    form = PasswordForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(username=session["username"]).first()
        from werkzeug.security import generate_password_hash
        user.password = generate_password_hash(data["password"])
        db.session.add(user)
        db.session.commit()
        return "<script>alert('密码修改成功');location.href='/';</script>"
    return render_template("home/modify_password.html", form=form)
