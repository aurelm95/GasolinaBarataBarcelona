from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import time
import datetime

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

MAX_ROWS=5

@gasolineras_router.route('/buscar_gasolinera', methods=['GET'])
def buscar_gasolinera():
	try:
		request_params=request.args.to_dict()
		print(request_params)
		
		G.buscar_datos()
		G.buscar_mejor_gasolinera(
			coordenadas_actuales=(float(request_params['latitude']), float(request_params['longitude'])),
			litros_a_repostar=int(request_params['litros']),
			consumo=float(request_params['consumo'])
			)

		response_data=[]
		now=int(time.time())
		for gasolinera in G.DATA[:MAX_ROWS]:
			response_data.append({
				'Empresa':gasolinera.empresa,
				'Dirección':gasolinera.direccion,
				'Precio (€/L)':gasolinera.precio,
				'Distancia (km)':gasolinera.distancia,
				'Coste total (€)':round(gasolinera.coste_total,2),
				'Tiempo transcurrido desde la última actualización':str(datetime.timedelta(seconds=now-gasolinera.hora_ultima_actualizacion))
			})
		# print(response_data)

		df=pd.DataFrame.from_dict(response_data)

		response=jsonify({'table':df.to_html(index=False)})
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
