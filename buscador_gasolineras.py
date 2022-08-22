import requests
import time
import datetime
import geo_utils
import pandas as pd


def guardar_en_archivo(t):
    f=open("respuesta.txt","w")
    f.write(t)
    f.close()

class Gasolinera():
    def __init__(self,direccion,empresa,horario,latitud,longitud,hora_ultima_actualizacion,precio,tipo_gasolina) -> None:
        self.direccion=direccion
        self.empresa=empresa
        self.horario=horario
        self.latitud=float(latitud)
        self.longitud=float(longitud)
        self.hora_ultima_actualizacion=hora_ultima_actualizacion
        self.precio=precio
        self.tipo_gasolina=tipo_gasolina

        # Valores calculados por mi
        self.distancia=None
        self.coste_viaje=None
        self.coste_total=None

    def calcular_coste_total(self,coordenadas_actuales,litros_a_repostar,consumo_en_l_por_km):
        self.distancia=round(geo_utils.distance((self.latitud,self.longitud),coordenadas_actuales),2)
        self.coste_viaje=2*self.distancia*consumo_en_l_por_km
        self.coste_total=litros_a_repostar*self.precio+self.coste_viaje
    
    def __lt__(self,other):
        if self.coste_total is None: return True
        if other.coste_total is None: return False
        return self.coste_total<other.coste_total
    
    def __str__(self) -> str:
        tiempo_transucrrido=int(time.time())-self.hora_ultima_actualizacion
        tiempo_transucrrido=str(datetime.timedelta(seconds=tiempo_transucrrido))

        return self.empresa+" - "+self.direccion+" - €/L: "+str(self.precio)+" - distancia: "+str(self.distancia)+" km - coste total: "+str(round(self.coste_total,2))+" hace: "+tiempo_transucrrido

    def __repr__(self) -> str:
        return "Gasolinera(direccion="+self.direccion+",empresa="+self.empresa+",horario="+self.horario+",latitud="+str(self.latitud)+",longitud="+str(self.longitud)+",hora_ultima_actualizacion="+str(self.hora_ultima_actualizacion)+",precio="+str(self.precio)+",tipo_gasolina="+self.tipo_gasolina+")"

class GasolinerasManager():
    def __init__(self) -> None:
        self.DATA=[]
        self.df=pd.DataFrame()
    
    def buscar_datos(self):
        print("Buscando gasolineras...")
        data = {
            'provincia': '8',
            'localidad': '42',
            'tipo_combustible': '1',
            'empresa': '',
            'brapido': '1',
        }
        self.respuesta = requests.post('https://www.dieselogasolina.com/Buscador/Busqueda', data=data)

        # guardar_en_archivo(respuesta.text)
        gasolineras=self.respuesta.json()

        for gasolinera in gasolineras:
            direccion=gasolinera['direccion']
            empresa=gasolinera['empresa']
            horario=gasolinera['horario']
            latitud,longitud=gasolinera['geocords'].split(",")
            hora_ultima_actualizacion=int(gasolinera['ultima_actualizacion']) # timestamp
            precio=float(gasolinera['precio'].replace(",","."))
            tipo_gasolina=gasolinera['combustible']

            self.DATA.append(Gasolinera(direccion,empresa,horario,latitud,longitud,hora_ultima_actualizacion,precio,tipo_gasolina))
        
        print("Datos correctamente parseados")

    def buscar_mejor_gasolinera(self,coordenadas_actuales,litros_a_repostar,consumo):
        info=f"""Calculando mejor gasolinera para repostar en las siguientes condiciones:

        Coordenadas: {coordenadas_actuales},
        Litros a repostar: {litros_a_repostar},
        Consumo medio esperado (l/km): {consumo}
        """
        print(info)
        coste_minimo=1000
        for g in self.DATA:
            g.calcular_coste_total(coordenadas_actuales,litros_a_repostar,consumo_en_l_por_km=consumo)
            coste_minimo=min(coste_minimo,g.coste_total)
        
        # ordenar por coste total
        self.DATA.sort()
    
    def __str__(self) -> str:
        s ="\n\nEmpresa direccion precio (€/L) distancia (km) coste total tiempo transcurrido\n"
        s="\n\n"
        s+="Empresa".ljust(36)+'| '
        s+="Direccion".ljust(44)+'| '
        s+="Precio (€/L)".ljust(12)+'| '
        s+="Distancia (km)".ljust(14)+'| '
        s+="Coste total".ljust(11)+'| '
        s+="Ultima actualizacion"

        s+="\n"+"="*175+"\n\n"
        for g in self.DATA:
            s+=g.empresa.ljust(36)+'| '
            s+=g.direccion.ljust(44)+'| '
            s+=str(g.precio).ljust(12)+'| '
            s+=str(g.distancia).ljust(14)+'| '
            s+=str(round(g.coste_total,2)).ljust(11)+'| '
            tiempo_transucrrido=int(time.time())-g.hora_ultima_actualizacion
            tiempo_transucrrido=str(datetime.timedelta(seconds=tiempo_transucrrido))
            s+=tiempo_transucrrido
            s+="\n"
        
        return s
        





if __name__=='__main__':
    # Coordenadas de del hospital de SantPau
    LATITUD, LONGITUD = 41.411470, 2.174364
    COORDS=(LATITUD, LONGITUD)

    # Posible consumo medio de un coche por ciudad (l/km)
    CONSUMO_MEDIO=7.5/100

    # Posibles litros a repostar
    LISTROS_A_REPOSTAR=50

    # Ejemplo de ejecucion
    G=GasolinerasManager()
    G.buscar_datos()
    G.buscar_mejor_gasolinera(
        coordenadas_actuales=COORDS,
        litros_a_repostar=LISTROS_A_REPOSTAR,
        consumo=CONSUMO_MEDIO
        )
    print(G)

