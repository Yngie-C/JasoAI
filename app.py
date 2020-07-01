"""
필요한 모듈 import
"""
from flask import Flask, render_template, request, redirect, session, url_for
import os
import datetime
import re
from flaskext.mysql import MySQL
from flask_restful import Resource, Api, reqparse
from oauth2client.contrib.flask_util import UserOAuth2
from oauth2client.client import OAuth2Credentials
import simplejson as json
from jupyter_generator import main


"""
플라스크 호출
"""
app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'


"""
구글 로그인 OAuth2.0 을 위한 아이디와 비밀번호 설정
"""
app.config['GOOGLE_OAUTH2_CLIENT_ID'] = 'YOUR_GOOGLE_OAUTH2_CLIENT_ID'
app.config['GOOGLE_OAUTH2_CLIENT_SECRET'] = 'YOUR_GOOGLE_OAUTH2_CLIENT_SECRET'
oauth2 = UserOAuth2(app)


"""
DB 정보 입력하기
"""
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'USER_NAME'
app.config['MYSQL_DATABASE_PASSWORD'] = 'DB_PASSWORD'
app.config['MYSQL_DATABASE_DB'] = 'DB_NAME'
app.config['MYSQL_DATABASE_HOST'] = 'HOST_NAME'
mysql.init_app(app)
app.secret_key = 'your_secret_key'


"""
랜딩 페이지
"""
@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('user_id'):
        return render_template('landing.html')
    else:
        return render_template('landing.html')


"""
로그인 페이지 :
구글 로그인을 사용하며 로그인이 완료된 후에는 자소서 작성 페이지로 이동
회원가입이 되어있지 않은 회원의 경우 회원가입 페이지로 이동
"""
@app.route('/login', methods=['GET', 'POST'])
@oauth2.required
def login():
    email = oauth2.email
    user_id = oauth2.user_id
    session['user_id'] = user_id
    session['user_email'] = email
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute('select user_id from user_tb')
    chk_user_id_tuple = cur.fetchall()
    chk_user_id = sum([list(i) for i in chk_user_id_tuple],[])
    if user_id in chk_user_id:
        cur.execute(f'select major from user_tb where user_id="{user_id}"')
        chk_empty = cur.fetchone()[0]
        if chk_empty is None:
            return redirect('/signup')
        return redirect('/writeResume')
    else:
        cur.execute(f'insert into user_tb (email, user_id) values ("{email}","{user_id}")')
        conn.commit()
        return redirect('/signup')


"""
로그아웃
"""
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


"""
회원가입 페이지 :
DB에 저장할 성별, 생년월일, 전공계열 GET
"""
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    user_id = session['user_id']
    conn = mysql.connect()
    cur = conn.cursor()

    if request.method == 'GET':
        return render_template('signup.html')
    else:
        birthdate = request.form.get('birthdate')
        birthdate = birthdate[6:] +'-'+ birthdate[3:5] +'-'+ birthdate[:2]
        gender = request.form.get('gender')
        classes = request.form.get('classes')
        cur.execute(f'''update user_tb set birthdate="{birthdate}", gender="{gender}",
            major="{classes}" where user_id="{user_id}"''')
        conn.commit()
        return render_template('writeResume.html')


"""
자소서 작성 페이지 :
키워드를 입력한 후 문장 생성을 눌러 자소서 생성 페이지를 불러올 수 있도록 함
"""
@app.route('/writeResume', methods=['GET', 'POST'])
def writeResume():
    if not session.get('user_id'):
        return render_template('error.html', msg="로그인 후 이용해 주세요.")
    if request.method == 'GET':
        try:
            sentences = session['texts']
            return render_template('writeResume.html', sentences=sentences)
        except Exception as ex:
            print(ex)
            return render_template('writeResume.html', sentences="")
    else:
        texts = request.form.get('DOC_TEXT')
        session['texts'] = texts
        return redirect(url_for('resumeGen'))


"""
자소서 생성 페이지 :
GET에서 모델이 실제로 작동하며 총 5개의 문장이 생성되도록 함
"""
@app.route('/resumeGen', methods=['GET', 'POST'])
def resumeGen():
    if not session.get('user_id'):
        return render_template('error.html', msg="로그인 후 이용해 주세요.")
    if request.method == 'GET':
        texts = session['texts']
        if len(texts) > 200:
            return render_template('error.html', msg='입력 문장을 조금 더 짧게 조정해주세요.')
        ctx= 'cpu'
        cachedir='~/kogpt2/'
        load_path = './checkpoint/KoGPT2_checkpoint_277500.tar'
        loops = 6
        sent_dict = main(temperature=1.1, tmp_sent = texts, text_size = len(texts)//2+40, loops = loops, load_path = load_path)
        # 하이퍼파라미터(temperature, top_p, top_k) 조정 가능하며 키워드가 길어짐에 따라 더 많은 문장을 생성할 수 있도록 text_size 설정 
        for key, value in sent_dict.items():
            lst = value.split('.')
            lst_delete_last = lst[:-1]
            lst_to_str = ".".join(lst_delete_last) + "."
            sent_dict[key] = lst_to_str
        
        return render_template('resumeGen.html', msg=sent_dict)
    else:
        sentences = request.form.get('sentences')
        session['texts'] = sentences        
        return redirect(url_for('writeResume'))


"""
자소서 관리 페이지 :
저장한 자소서를 보여줌
"""
@app.route('/myresume', methods=['GET'])
def myresume():
    if not session.get('user_id'):
        return render_template('error.html', msg="로그인 후 이용해 주세요.")
    conn = mysql.connect()
    cur = conn.cursor()
    email = session['user_email']
    if request.method == 'GET':
        cur.execute(f'select email from resume_tb')
        db_email_tuple = cur.fetchall()
        chk_email = sum([list(i) for i in db_email_tuple],[])
        if email in chk_email:
            cur.execute(f'select title, texts from resume_tb where email="{email}" and actDeact="1"')
            user_data = cur.fetchall()
            return render_template('myresume.html', user_data=user_data, length=len(user_data))
        else:
            return render_template('error.html', msg="자소서 작성 후 이용해 주세요.")


"""
자소서 관리 페이지 (추가) :
자소서 생성 페이지에서 '저장하기'를 눌러 새로운 자소서를 저장할 수 있음 (최대 6개)
"""
@app.route('/insert', methods=['POST'])
def insert():
    conn = mysql.connect()
    cur = conn.cursor()
    email = session['user_email']
    user_title = request.form.get('user_title')
    user_text = request.form.get('user_text')
    
    cur.execute(f'select title from resume_tb where email="{email}" and actDeact="1"')
    title_tuple = cur.fetchall()
    chk_title = sum([list(i) for i in title_tuple],[])
    if user_title in chk_title:
        return render_template('error.html', msg="동일한 이름의 자소서 제목이 있습니다. 다른 이름으로 작성해주세요.")

    cur.execute(f'select idx from resume_tb where email="{email}" and actDeact="1"')
    resume_count_tuple = cur.fetchall()
    chk_resume_count = sum([list(i) for i in resume_count_tuple],[])
    if len(chk_resume_count) >= 6:
        return render_template('error.html', msg="저장 가능한 자소서 수를 넘었습니다.(최대6개)")

    cur.execute(f'insert into resume_tb (email, title, texts) values ("{email}", "{user_title}", "{user_text}")')
    conn.commit()
    return redirect(url_for('myresume'))


"""
자소서 관리 페이지 (수정) :
자소서 관리 페이지에서 수정을 원하는 자소서의 제목을 눌러
해당 자소서를 수정할 수 있음
"""
@app.route('/update', methods=['POST'])
def update():
    if not session.get('user_id'):
        return render_template('error.html', msg="로그인 후 이용해 주세요.")
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        email = session['user_email']
        user_title = request.form.get('user_title')
        user_text = request.form.get('user_text')

        cur.execute(f'update resume_tb set texts="{user_text}" where email="{email}" and actDeact = "1" and title="{user_title}"')
        conn.commit()
        return redirect(url_for('myresume'))


"""
자소서 관리 페이지 (삭제) :
자소서 관리 페이지에서 수정을 원하는 자소서의 아래에 있는 삭제하기 버튼을 눌러
해당 자소서를 삭제할 수 있음
"""
@app.route('/delete', methods=['POST'])
def delete():
    if not session.get('user_id'):
        return render_template('error.html', msg="로그인 후 이용해 주세요.")
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        email = session['user_email']
        user_title = request.form.get('deact').split(' 삭제')[0]

        cur.execute(f'update resume_tb set actDeact="0" where title="{user_title}" and email="{email}"')
        conn.commit()
        return redirect(url_for('myresume'))





# 실행을 위한 함수 
if __name__ == '__main__':
    app.run()