from flask import Flask, render_template, url_for, request, session, redirect
import bcrypt
import pymongo
import re

app = Flask(__name__)

connection = pymongo.MongoClient("mongodb://localhost")

db = connection.patika
registered = db.felhasznalok
gyogyszerek=db.gyogyszerek
betegsegek=db.betegsegek

posts = [
    {
        'author': 'HáziPatika',
        'title': 'Miért ennyire gyakori az ízületi kopás?',
        'content': 'Az ízületi kopás - más néven arthrosis - világszerte a legelterjedtebb ízületi megbetegedés, és az egyik leggyakoribb probléma az időseknél. Bár tipikusan az 50 feletti korosztályban nő meg az előfordulása (75 éves kor felett pedig már szinte mindenkit érint), a probléma egyre gyakrabban jelentkezik már a 20-as és 30-as éveikben lévőknél. Összességében Magyarországon minden negyedik-ötödik ember szenved miatta valamilyen mértékben. Miért ilyen gyakori ez a betegség, és mit tehetünk a megelőzésért?',
        'date_posted': '2018. november 13.'
    },
    {
        'author': '24.hu',
        'title': 'Életet is menthetnek a drónok',
        'content': 'A hagyományos szállítási módszerek nem a legmegfelelőbbek a szervre várók számára: ha valakinek sürgősen lenne rá szüksége, nem mindig áll a közelben készenlétben megfelelő. Ezen a helyzeten segíthetne az, ha nem autóval, hanem drónokkal szállítanák a donorok szerveit a helyszínekre, legalább is egy friss kutatás szerint. ',
        'date_posted': '2018. november 12.'
    }
]

@app.route('/')
@app.route('/home')
def home():
    if (request.args.get('kijelentkezes')==""):
        session.clear()
    return render_template('home.html', posts = posts)


@app.route('/gyogyszer', methods = ['GET', 'POST'])
def gyogyszer():
    post = request.form
    if 'uj_gyogyszer' in post:
        return redirect(url_for('gyogyszer_felvetele'))
    gyogyszer_neve = post.get('gyogyszer_neve', '').strip()
    print(gyogyszer_neve)
    talalati_lista_darab=gyogyszerek.find({'nev': {'$regex': '.*'+re.escape(gyogyszer_neve)+'.*','$options': 'i'}}).count()
    gyogyszerek_listaja=gyogyszerek.find({'nev': {'$regex': '.*'+re.escape(gyogyszer_neve)+'.*','$options': 'i'}})
    context = {
        'title': 'Gyógyszerek',
        'gyogyszer_neve': gyogyszer_neve,
        'gyogyszerek_listaja': gyogyszerek_listaja,
        'lista_darabszam' : talalati_lista_darab
    }
    
    return render_template('gyogyszer.html',**context)

    return render_template('login_required.html', title = "Bejelentkezés szükséges")


@app.route('/gyogyszer_felvetele', methods=['GET','POST'] )
def gyogyszer_felvetele():
    betegsegek_listaja=betegsegek.find()
    context = {
        'title': 'Gyógyszerek felvétele',
        'betegsegek': betegsegek_listaja
    }
    if 'username' in session:
        post = request.form
        nev=post.get('nev')
        ar=post.get('ar')
        kiszereles=post.get('kiszereles')
        if 'mentes' in post and len(nev)>0 and len(ar)>0 and len(kiszereles)>0:
            betegseg=post.getlist('betegseg')
            betegseg=list(map(int, betegseg))
            print("ez: ",betegseg)
            gyogyszerek.insert_one({'nev':nev,'ar':int(ar),'kiszereles':int(kiszereles),'betegsegre_jo':betegseg})
        return render_template('gyogyszer_felvetele.html', **context)
            

    return render_template('login_required.html', title = "Bejelentkezés szükséges")

@app.route('/betegseg',methods = ['GET', 'POST'])
def betegseg():
    post = request.form

    if 'uj_betegseg' in post:
        return redirect(url_for('betegseg_felvetele'))
    betegseg_neve=post.get('betegseg_neve','').strip()
    betegsegek_listaja=betegsegek.find({'betegseg_neve': {'$regex': '.*'+re.escape(betegseg_neve)+'.*','$options': 'i'}})
    betegsegek_szama=betegsegek_listaja.count()
    context = {
        'title': 'Betegség felvétele',
        'betegseg_neve':betegseg_neve,
        'betegsegek': betegsegek_listaja,
        'betegsegek_szama': betegsegek_szama
    }
    return render_template('betegseg.html', **context)

@app.route('/betegseg_felvetele', methods=['GET','POST'] )
def betegseg_felvetele():
    id=betegsegek.find().count()+1
    context = {
        'title': 'Betegség felvétele',
    }
    if 'username' in session:
        post = request.form
        nev=post.get('nev')
        leiras=post.get('leiras')
        if 'mentes' in post and len(nev)>0 and len(leiras)>0:
            betegsegek.insert_one({'_id': id,'betegseg_neve':nev,'leiras':leiras})
        return render_template('betegseg_felvetele.html', **context)
            

    return render_template('login_required.html', title = "Bejelentkezés szükséges")




@app.route('/login', methods = ['GET', 'POST'])
def login():
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('login.html')


@app.route('/loginproc', methods = ['POST'])
def handle_login():
    login_user = registered.find_one({'nev': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['jelszo']) == login_user['jelszo']:
            session['username'] = request.form['username']
            return redirect(url_for('home'))

    return redirect(url_for('login', hiba="igaz"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.secret_key = 'secretkey'
    app.run(debug=True)