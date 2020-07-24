from flask import render_template, redirect, url_for, flash, session, request,jsonify
from app.admin.forms import LoginForm,GoodsForm
from app.models import Admin,Goods,SuperCat,SubCat,User,Orders,OrdersDetail
from sqlalchemy import or_
from functools import wraps
from decimal import *


def admin_login(f):
    """
    登录装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function
