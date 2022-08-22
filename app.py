from flask import Flask
from gasolineras import gasolineras_router

app=Flask(__name__)
app.register_blueprint(gasolineras_router, url_prefix="/gasolineras")

@app.route("/")
def home():
    html=""
    html+="<a href='/numberrecognition'> Number recognition </a>"+"<br>"
    html+="<a href='/apuestasseguras'> Sure bets </a>"+"<br>"
    html+="<a href='/gasolineras'> Gasolineras baratas Barcleona </a>"
    return html


# ruta para hacer ping y mantenerlo vivo
@app.route('/check')
def check():
	telegram_bot.enviar_mensaje('MyWeb check')
	return 'check done'


if __name__=='__main__':
    app.run(debug=True)
    # app.run()