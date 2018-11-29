from flask import Flask, render_template, url_for, request, session, redirect
import bcrypt
import pymongo

app = Flask(__name__)

connection = pymongo.MongoClient("mongodb://localhost")

db = connection.users
registered = db.registered

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
    return render_template('home.html', posts = posts)


@app.route('/gyogyszer')
def gyogyszer():
    if 'username' in session:
        return render_template('gyogyszer.html', title = "Gyógyszerek")

    return render_template('login_required.html', title = "Bejelentkezés szükséges")


@app.route('/betegseg')
def betegsek():
    return render_template('betegseg.html', title = "Betegségek")


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('login.html')


@app.route('/loginproc', methods = ['POST'])
def handle_login():
    login_user = registered.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('home'))

    return 'Invalid username/password combination'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.secret_key = 'secretkey'
    app.run(debug=True)