import requests
import time
import datetime
import geo_utils
import pandas as pd

CONSUMO_MEDIO=7.5/100 # litros por cada 1km

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
        self.distancia=round(geo_utils.distance((self.latitud,self.longitud),geo_utils.COORDS),2)
        self.coste_viaje=2*self.distancia*CONSUMO_MEDIO
        self.coste_total=None

    def calcular_coste_total(self,litros_a_repostar):
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
        self.df=[]

        for gasolinera in gasolineras:
            # print(gasolinera)
            direccion=gasolinera['direccion']
            empresa=gasolinera['empresa']
            horario=gasolinera['horario']
            latitud,longitud=gasolinera['geocords'].split(",")
            hora_ultima_actualizacion=int(gasolinera['ultima_actualizacion']) # timestamp
            precio=float(gasolinera['precio'].replace(",","."))
            tipo_gasolina=gasolinera['combustible']

            j={k:gasolinera[k] for k in ['direccion','empresa','horario','geocords','ultima_actualizacion','precio','combustible']}
            j['distancia']=round(geo_utils.distance((float(latitud),float(longitud)),geo_utils.COORDS),2)
            self.df.append(j)

            self.DATA.append(Gasolinera(direccion,empresa,horario,latitud,longitud,hora_ultima_actualizacion,precio,tipo_gasolina))
        self.df=pd.DataFrame(self.df)
    
    # obsoleto
    def buscar_mejor_gasolinera_deprecated(self):
        print("Metodo obsoleto")
        return 
        df2=self.df[self.df['precio']==self.df['precio'].min()]
        self.mejor=df2[df2['distancia']==df2['distancia'].min()]

        print(self.mejor)

    def buscar_mejor_gasolinera(self,litros_a_respostar=12):
        coste_minimo=1000
        for g in self.DATA:
            g.calcular_coste_total(litros_a_respostar)
            coste_minimo=min(coste_minimo,g.coste_total)
        
        # ordenar por coste total
        self.DATA.sort()
    
    def __str__(self) -> str:
        s ="\n\nEmpresa direccion precio (€/L) distancia (km) coste toal tiempo transcurrido\n"
        s+="===========================================================\n"
        for g in self.DATA:
            s+=g.empresa.ljust(36)
            s+=g.direccion.ljust(42)
            s+=str(g.precio).ljust(6)
            s+=str(g.distancia).ljust(4)
            s+=str(round(g.coste_total,2))
            tiempo_transucrrido=int(time.time())-g.hora_ultima_actualizacion
            tiempo_transucrrido=str(datetime.timedelta(seconds=tiempo_transucrrido))
            s+=tiempo_transucrrido
            s+="\n"
        
        return s
        





if __name__=='__main__':
    G=GasolinerasManager()
    G.buscar_datos()
    G.buscar_mejor_gasolinera()
    print(G)

