from flask import Blueprint, render_template, request, jsonify
# import pandas as pd
import time

from buscador_gasolineras import GasolinerasManager


gasolineras_router=Blueprint('gasolineras', __name__)


# INICIALIZACION

try:
	print(__file__,"Inicializando gasolineras")
	G=GasolinerasManager()
except Exception as e:
	print(e)

ERROR=""



# ROUTES

@gasolineras_router.route('/')  # What happens when the user visits the site
def base_page():
	try:
		return render_template('gasolineras_app.html')
	except Exception as e:
		global ERROR
		ERROR=str(e)
		return ERROR

@gasolineras_router.route('/buscar_gasolinera', methods=['GET'])
def buscar_gasolinera():
	try:
		request_params=request.args.to_dict()
		print(request_params)
		response = jsonify({'some': 'data'})
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	except Exception as e:
		global ERROR
		ERROR=str(e)
		print("buscar_gasolinera():",ERROR)
		return ERROR

@gasolineras_router.route('/error')
def error():
	return 'ULTIMO ERROR: '+ERROR




if __name__ == "__main__":
	# app.run(host='0.0.0.0', port=random.randint(2000, 9000))
	app.run(host='0.0.0.0', port=8080, debug=True)
