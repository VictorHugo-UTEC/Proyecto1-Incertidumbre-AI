#Librerias que se utilizan
from IPython.display import HTML, display
import numpy as np

class proy1_ia:

    # Constructor
    def __init__(self, nodoFin, tasa_dsct, premio, valFin, filas,cols):
        self.nodoFin = nodoFin
        self.tasa_dsct = tasa_dsct
        self.premio = premio
        self.valFin = valFin
        self.initVal = np.empty([filas,cols]) # Tabla con los valores iniciales para iterar la func valor
        self.TablaCaminos = np.empty([filas,cols]) # Tabla para guardar las politicas
        self.directEstados = dict() # Diccionario con los vecinos de cada estado

    ## Funciones propias
    # --------------------------------------------------------------------------- #
    # Funcion 1: Graficar la tabla en html
    def tableHtml(self, data):
        ## Diccionario de las flechas
        # 0:vacio, 1: derecha, 2: abajo, 3: izquierda, 4: arriba , 5: inicio, 6: fin    
        dictFlecha = {0: '&#10068',
            1: '&#8594',
            2: '&#8595',
            3: '&#8592',
            4: '&#8593',
            5: '&#9989',
            6: '&#128205',
            -1: '&#9820'}
        
        
        # Prototipos para la tabla que se enseña
        estrucTable = '<table>{}</table>'   
        estrucRows = '<tr>{}</tr>'    
        estructCelda = '<td>{}</td>'

        # Se construyen la tabla
        allRows = ""
        for ix in data:
            format1 = "".join([estructCelda.format( dictFlecha[i] ) for i in ix])
            allRows += estrucRows.format(format1)

        # Se muestra la tabla
        tabla = estrucTable.format(allRows)
        style = """
        <style>
            td {
                font-size: 10px;
                white-space: wrap;
            }
        </style>
        """
        display(HTML(style + tabla))
        global h
        h = HTML(style + tabla).data
        
    
    def guardarTabla(self,nom):
        with open(nom.replace("/", "-" ) + '.html', 'w') as f:
            f.write(h)
            f.close
        return 0
    
    # --------------------------------------------------------------------------- #
    # Funcion 2: Encontrar vecinos    
    # Se busca estados a los cuales me puedo mover por cada estado
    def buscarVecinos(self, data):
        vecinosEstados = dict()  # Diccionario de lugares a los que se puede mover
        for ix in range(data.shape[0]):
            for jx in range(data.shape[0]):
                if (data[ix][jx] != -1):    #"No se visitan las paredes"
                    # ---------------------------------------------------------- #
                    ## Se buscan todos los vecinos posibles 
                    temp1 = {}
                    # Se comprueba vecino derecha
                    if (data[ix][jx+1]!=-1):
                        temp1[str(ix)+"_"+str(jx+1)]=1
                    else:
                        temp1[str(ix)+"_"+str(jx+1)]=0

                    # Se comprueba vecino abajo
                    if (data[ix+1][jx]!=-1):
                        temp1[str(ix+1)+"_"+str(jx)]=1
                    else:
                        temp1[str(ix+1)+"_"+str(jx)]=0  

                    # Se comprueba vecino izquierda
                    if (data[ix][jx-1]!=-1):
                        temp1[str(ix)+"_"+str(jx-1)]=1
                    else:
                        temp1[str(ix)+"_"+str(jx-1)]=0

                    # Se comprueba vecino arriba
                    if (data[ix-1][jx]!=-1):
                        temp1[str(ix-1)+"_"+str(jx)]=1
                    else:
                        temp1[str(ix-1)+"_"+str(jx)]=0                

                    # Se guarda en el diccionario de vecinos
                    vecinosEstados[str(ix)+"_"+str(jx)] = temp1    
        
        # Se devuelvan los vecinos
        return vecinosEstados


    # --------------------------------------------------------------------------- #
    # Funcion 4: Extraer Funcion Valor de los vecinos de un nodo (i,j)
    def buscarValFunc(self, fila, columna, valFunc, tasa_dsct, nodo, premio):
        derec = valFunc[fila, columna+1] * tasa_dsct
        abajo = valFunc[fila+1, columna] * tasa_dsct
        izqui = valFunc[fila, columna-1] * tasa_dsct
        arrib = valFunc[fila-1, columna] * tasa_dsct
        
        # En caso se alcance el nodo final
        if (str(fila) +"_" +str(columna+1)) == nodo:
            derec += premio
        if (str(fila+1) +"_"+str(columna)) == nodo:
            abajo += premio
        if (str(fila) +"_"+str(columna-1)) == nodo:
            izqui += premio
        if (str(fila-1) +"_"+str(columna)) == nodo:
            arrib += premio
            
        return np.array([derec,abajo,izqui,arrib])

    # --------------------------------------------------------------------------- #
    # Funcion 5: Extraer la lista de lados a los cuales puede moverse el estado
    def buscarDirec(self, fila, columna, dictDirect):
        localDir = dictDirect[str(fila) + "_" + str(columna)]
            
        derec = localDir[str(fila) + "_" + str(columna+1)]
        abajo = localDir[str(fila+1) + "_" + str(columna)]
        izqui = localDir[str(fila) + "_" + str(columna-1)]
        arrib = localDir[str(fila-1) + "_" + str(columna)]

        return np.array([derec,abajo,izqui,arrib])

    # --------------------------------------------------------------------------- #
    # Funcion 6: Vector con proporcion que se multiplica a Funciones valor de vecinos
    # Ejemp movi derecha: V(i,j) = 0.7(0+ 0.9v[i,j+1]) + 0.1 (0+0.9v[i+1,j]) + 0.1 (0+0.9v[i,j-1]) + 0.1 (0+0.9v[i-1,j]) 
    def peso_accion(self, listVal, movimiento):
        ## Inputs
        # listVal: arreglo con pagos asociados a cada movimiento
        # movimiento: (1: derecha, 2: abajo, 3: izquierda, 4: arriba)

        # Lista con proporciones
        prop_accion = np.array([0.1,0.1,0.1,0.1])
        prop_accion[movimiento-1] = 0.7  # Solo se reemplaza la accion elegida

        # Se multiplica componete a componete para extraer vector que multiplica a las funciones valor
        result = np.multiply(listVal, prop_accion)    

        # Se extrae el porcentaje asociado a volver al mismo nodo
        propFalt = round(1 - result.sum(),2)

        return result, propFalt


    # --------------------------------------------------------------------------- #
    # Funcion 7: Extraer vecinos a los cuales puede acceder cada estados
    def extraerVecinos(self):
        return self.directEstados

    # --------------------------------------------------------------------------- #
    # Funcion 8: Extraer regla de politica
    def extraerPI(self):
        return self.TablaCaminos.copy()

    # --------------------------------------------------------------------------- #
    # Funcion 9: Extraer resultados de la ultima iteracion de politica
    def resultPI(self):
        self.tableHtml(self.TablaCaminos)



# ---------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------- #
    # Se carga el problema inicial
    def infoProblema(self, Tabla_inicial, nodoFinal):
        self.TablaCaminos = Tabla_inicial.copy()
        self.initVal = (np.random.randint(10, size=Tabla_inicial.shape) + 1) * 1.0
        self.initVal[nodoFinal[0]+1,nodoFinal[1]+1] = self.valFin # Se agrega 1 por las paredes
        
        # Vecinos a los que puedo visitar (i,j) -> i= fila, j= columna
        self.directEstados = self.buscarVecinos(self.TablaCaminos)      

    # Paso 1: calcular la funcion valor asociada a las acciones actuales
    # Se itera hasta encontrar la funcion valor estacionacionaria
    def aproxValueFun(self, epsilon):
        # Se copia la politica inicial para iterar
        prevVal = self.initVal.copy()
        actualVal = self.initVal.copy()
        converDiff = 10

        # Se itera hasta que la distancias entre las funciones valor en n y n-1 sea menor que epsilon
        while (converDiff>epsilon):   
            # Calculo del funcion valor de manera iterativa
            for i in range (self.TablaCaminos.shape[0]): # filas
                for j in range (self.TablaCaminos.shape[1]): # columnas
                    # No se utilizan estados bloqueados o paredes, asi como estado final
                    #if (self.TablaCaminos[i,j] != -1 and (str(i)+"_"+str(j) != self.nodoFin) ):
                    if (self.TablaCaminos[i,j] != -1 and self.TablaCaminos[i,j] != 6 ):                        
                        # Vecinos que puede visitar el nodo (i,j)
                        vecinosDisp = self.buscarDirec(i, j, self.directEstados)

                        # Pesos bajo accion actual del nodo (i,j)
                        accionActual = self.TablaCaminos[i,j]
                        pesosMulti, propFalt = self.peso_accion(vecinosDisp, accionActual)

                        # FuncionValor asociado a cada estado vecino (considerando tasa de dsct)
                        valActualVecino = self.buscarValFunc(i, j, prevVal, self.tasa_dsct, self.nodoFin, self.premio)   # Funcion Valor de vecinos del nodo (i,j)
                        
                        # Se actualiza la funcion valor actual en n, con informacion de n-1
                        actualVal[i,j] = round(np.dot(pesosMulti, valActualVecino) + (propFalt * prevVal[i,j]), 10)  
            
            # Se analiza la convergencia del metodo iterativo
            converDiff = np.abs(actualVal - prevVal).max() 
            
            # Una vez que se recorre toda la matriz, se actualiza los valores de las funciones valor
            prevVal = actualVal.copy()
        
        return actualVal
    
    # Paso 2: Se evaluan las Funciones Valor bajo otras acciones disponibles
    def evalOtrasAcciones(self, actualVal):
        # Nodo final
        nodfinalstr = str(self.nodoFin[0])+"_"+str(self.nodoFin[1])

        for i in range (self.TablaCaminos.shape[0]): # filas
            for j in range (self.TablaCaminos.shape[1]): # columnas
                # Se extraen la acciones complementarias a la actual                
                if (self.TablaCaminos[i,j] != -1 and (str(i)+"_"+str(j) != nodfinalstr) ):
                    accionComp = [1,2,3,4]
                    #accionComp.remove(self.TablaCaminos[i,j]) # Se remueve la accion ya evaluada
                    
                    # Se evaluan los resultados con las acciones complementaria y se ve si hay mejora
                    listIdVal = [actualVal[i,j], self.TablaCaminos[i,j]] # Valor de Func Valor y accion inicial
                    for accNueva in accionComp:
                        # Vecinos que puede visitar el nodo (i,j)
                        vecinosDisp = self.buscarDirec(i, j, self.directEstados)
                        
                        # Busqueda bajo nueva accion
                        pesosMulti, propFalt = self.peso_accion(vecinosDisp, accNueva)
                    
                        # FuncionValor asociado a cada estado vecino (considerando tasa de dsct)
                        valActualVecino = self.buscarValFunc(i, j, actualVal, self.tasa_dsct, self.nodoFin, self.premio)
                    
                        # Se evalua si hay mejora de cambiar
                        evalActual = round(np.dot(pesosMulti, valActualVecino) + (propFalt * actualVal[i,j]), 10) 
                        
                        if (evalActual>listIdVal[0]):
                            listIdVal[0] = evalActual
                            listIdVal[1] = accNueva 
                            
                    # En caso se tenga mejora de cambiar de accion se actualizan las acciones
                    self.TablaCaminos[i,j] = listIdVal[1]


class importInfo():

    def __init__(self, problema):
        self.problema = problema

    # funcion de apoyo para extrae el tamanho y nodo final
    def szProblema(self, problem):
        # Variables iniciales
        fila = 0
        columna = 0
        for i in problem.keys():    
            coord = i.split("-")[-1].replace("x","").split("y")
            # Tamanho de la matriz
            if (int(coord[1])>fila):
                fila = int(coord[1])
            if (int(coord[0])>columna):
                columna = int(coord[0])

            # Nodo final
            if (problem[i] == "-"):
                nodoFin = [coord[1],coord[0]] 

        # Se actualiza el nodo fin con formato para python
        nodoFin[1] = int(nodoFin[1])-1
        nodoFin[0] = np.abs(int(nodoFin[0])-fila)

        return fila, columna, nodoFin


    def convertInfo(self, problem):
        maxfila, maxColumn, nodoFin = self.szProblema(problem)
        Tabla_poli = np.ones((maxfila, maxColumn)) * - 1
            
        # Obs: # 0:vacio, 1: derecha, 2: abajo, 3: izquierda, 4: arriba , 5: inicio, 6: fin    
        dictCardinal = {"east":1, "south":2, "west":3, "north":4}
        
        # Se recorren todos los nodos
        for i in problem.keys():
            # Se cambian las coordenadas para que tengan concordancia con python
            coord = i.split("-")[-1].replace("x","").split("y")
            coord = [int(i) for i in coord]
            new_coord = [np.abs(coord[1]-maxfila), coord[0]-1]

            if (problem[i] != "-"): # Caso diferente al nodo final 
                Tabla_poli[new_coord[0],new_coord[1]] = dictCardinal[problem[i]]
            
            else: # Caso del nodo final
                Tabla_poli[new_coord[0],new_coord[1]] = 6 # Nodo final
                
        # Se agrega el borde o paredes
        Tabla_poli = np.pad(Tabla_poli, pad_width=1, mode='constant', constant_values=-1)
        Tabla_poli = Tabla_poli.astype(int)
        
        return Tabla_poli, nodoFin
    
    def extraerInfo(self):
        return self.convertInfo(self.problema)


class proy1_ia_otro():

    # Constructor
    def __init__(self, nodoFin, tasa_dsct, premio, valFin, filas,cols):
        self.nodoFin = nodoFin
        self.tasa_dsct = tasa_dsct
        self.premio = premio
        self.valFin = valFin
        self.initVal = np.empty([filas,cols]) # Tabla con los valores iniciales para iterar la func valor
        self.TablaCaminos = np.empty([filas,cols]) # Tabla para guardar las politicas
        self.directEstados = dict() # Diccionario con los vecinos de cada estado

    ## Funciones propias
    # --------------------------------------------------------------------------- #
    # Funcion 1: Graficar la tabla en html
    def tableHtml(self, data):
        ## Diccionario de las flechas
        # 0:vacio, 1: derecha, 2: abajo, 3: izquierda, 4: arriba , 5: inicio, 6: fin    
        dictFlecha = {0: '&#10068',
            1: '&#8594',
            2: '&#8595',
            3: '&#8592',
            4: '&#8593',
            5: '&#9989',
            6: '&#128205',
            -1: '&#9820'}
        
        
        # Prototipos para la tabla que se enseña
        estrucTable = '<table>{}</table>'   
        estrucRows = '<tr>{}</tr>'    
        estructCelda = '<td>{}</td>'

        # Se construyen la tabla
        allRows = ""
        for ix in data:
            format1 = "".join([estructCelda.format( dictFlecha[i] ) for i in ix])
            allRows += estrucRows.format(format1)

        # Se muestra la tabla
        tabla = estrucTable.format(allRows)
        style = """
        <style>
            td {
                font-size: 10px;
                white-space: wrap;
            }
        </style>
        """
        display(HTML(style + tabla))
        global g
        g = HTML(style + tabla).data
        
    
    def guardarTabla(self,nom):
        with open(nom.replace("/", "-" ) + '.html', 'w') as f:
            f.write(g)
            f.close
        return 0
    
    # --------------------------------------------------------------------------- #
    # Funcion 2: Encontrar vecinos    
    # Se busca estados a los cuales me puedo mover por cada estado
    def buscarVecinos(self, data):
        vecinosEstados = dict()  # Diccionario de lugares a los que se puede mover
        for ix in range(data.shape[0]):
            for jx in range(data.shape[0]):
                if (data[ix][jx] != -1):    #"No se visitan las paredes"
                    # ---------------------------------------------------------- #
                    ## Se buscan todos los vecinos posibles 
                    temp1 = {}
                    # Se comprueba vecino derecha
                    if (data[ix][jx+1]!=-1):
                        temp1[str(ix)+"_"+str(jx+1)]=1
                    else:
                        temp1[str(ix)+"_"+str(jx+1)]=0

                    # Se comprueba vecino abajo
                    if (data[ix+1][jx]!=-1):
                        temp1[str(ix+1)+"_"+str(jx)]=1
                    else:
                        temp1[str(ix+1)+"_"+str(jx)]=0  

                    # Se comprueba vecino izquierda
                    if (data[ix][jx-1]!=-1):
                        temp1[str(ix)+"_"+str(jx-1)]=1
                    else:
                        temp1[str(ix)+"_"+str(jx-1)]=0

                    # Se comprueba vecino arriba
                    if (data[ix-1][jx]!=-1):
                        temp1[str(ix-1)+"_"+str(jx)]=1
                    else:
                        temp1[str(ix-1)+"_"+str(jx)]=0                

                    # Se guarda en el diccionario de vecinos
                    vecinosEstados[str(ix)+"_"+str(jx)] = temp1    
        
        # Se devuelvan los vecinos
        return vecinosEstados
        
    # --------------------------------------------------------------------------- #
    # Funcion 3: Extraer Funcion Valor de los vecinos de un nodo (i,j)
    def buscarValFunc(self, fila, columna, valFunc, tasa_dsct, nodo, premio):
        derec = valFunc[fila, columna+1] * tasa_dsct
        abajo = valFunc[fila+1, columna] * tasa_dsct
        izqui = valFunc[fila, columna-1] * tasa_dsct
        arrib = valFunc[fila-1, columna] * tasa_dsct
        
        # En caso se alcance el nodo final
        if (str(fila) +"_" +str(columna+1)) == nodo:
            derec += premio
        if (str(fila+1) +"_"+str(columna)) == nodo:
            abajo += premio
        if (str(fila) +"_"+str(columna-1)) == nodo:
            izqui += premio
        if (str(fila-1) +"_"+str(columna)) == nodo:
            arrib += premio
            
        return np.array([derec,abajo,izqui,arrib])

    # --------------------------------------------------------------------------- #
    # Funcion 4: Extraer la lista de lados a los cuales puede moverse el estado
    def buscarDirec(self, fila, columna, dictDirect):
        localDir = dictDirect[str(fila) + "_" + str(columna)]
            
        derec = localDir[str(fila) + "_" + str(columna+1)]
        abajo = localDir[str(fila+1) + "_" + str(columna)]
        izqui = localDir[str(fila) + "_" + str(columna-1)]
        arrib = localDir[str(fila-1) + "_" + str(columna)]

        return np.array([derec,abajo,izqui,arrib])     

    # --------------------------------------------------------------------------- #
    # Funcion 5: Iteracion de Funcion valor    
    # Iteracion de la funcion valor con todos los estados disponibles
    def aproxValueFun(self, epsilon):
        # Se copia la politica inicial para iterar
        prevVal = self.initVal.copy()
        actualVal = self.initVal.copy()
        converDiff = 10        
        
        # Se itera hasta que la distancias entre las funciones valor en n y n-1 sea menor que epsilon
        while (converDiff>epsilon):   
            # Calculo del funcion valor de manera iterativa
            for i in range (self.TablaCaminos.shape[0]): # filas
                for j in range (self.TablaCaminos.shape[1]): # columnas
                    # No se utilizan estados bloqueados o paredes, asi como estado final
                    #if (self.TablaCaminos[i,j] != -1 and (str(i)+"_"+str(j) != self.nodoFin) ):
                    if (self.TablaCaminos[i,j] != -1 and self.TablaCaminos[i,j] != 6 ):                        
                        # Vecinos que puede visitar el nodo (i,j)
                        vecinosDisp = self.buscarDirec(i, j, self.directEstados)

                        # FuncionValor asociado a cada estado vecino (considerando tasa de dsct)
                        valActualVecino = self.buscarValFunc(i, j, prevVal, self.tasa_dsct, self.nodoFin, self.premio)   # Funcion Valor de vecinos del nodo (i,j)

                        # Se evaluan las 4 acciones disponibles
                        resAccion = list()
                        for accionActual in range(1,5):
                            pesosMulti, propFalt = self.peso_accion(vecinosDisp, accionActual)
                        
                            # Se actualiza la funcion valor actual en n, con informacion de n-1
                            resAccion.append(round(np.dot(pesosMulti, valActualVecino) + (propFalt * prevVal[i,j]), 10))
                            
                        # Backup de bellman
                        actualVal[i,j] = max(resAccion)
                        
                        # Se toma la accion de mayor valor
                        self.TablaCaminos[i,j] = resAccion.index(actualVal[i,j])+1 
                            
            # Se analiza la convergencia del metodo iterativo
            converDiff = np.abs(actualVal - prevVal).max() 
            
            # Una vez que se recorre toda la matriz, se actualiza los valores de las funciones valor
            prevVal = actualVal.copy()
        
        #return actualVal                

    # --------------------------------------------------------------------------- #
    # Funcion 6: Vector con proporcion que se multiplica a Funciones valor de vecinos
    # Ejemp movi derecha: V(i,j) = 0.7(0+ 0.9v[i,j+1]) + 0.1 (0+0.9v[i+1,j]) + 0.1 (0+0.9v[i,j-1]) + 0.1 (0+0.9v[i-1,j]) 
    def peso_accion(self, listVal, movimiento):
        ## Inputs
        # listVal: arreglo con pagos asociados a cada movimiento
        # movimiento: (1: derecha, 2: abajo, 3: izquierda, 4: arriba)

        # Lista con proporciones
        prop_accion = np.array([0.1,0.1,0.1,0.1])
        prop_accion[movimiento-1] = 0.7  # Solo se reemplaza la accion elegida

        # Se multiplica componete a componete para extraer vector que multiplica a las funciones valor
        result = np.multiply(listVal, prop_accion)    

        # Se extrae el porcentaje asociado a volver al mismo nodo
        propFalt = round(1 - result.sum(),2)

        return result, propFalt
    
    # --------------------------------------------------------------------------- #       
    # Funcion 7: Extraer resultados de la ultima iteracion de politica    
    def resultPI(self):
        self.tableHtml(self.TablaCaminos)        

        
    # ---------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------- #
    # Se carga el problema inicial
    def infoProblema(self, Tabla_inicial, nodoFinal):
        self.TablaCaminos = Tabla_inicial.copy()
        self.initVal = (np.random.randint(10, size=Tabla_inicial.shape) + 1) * 1.0
        self.initVal[nodoFinal[0]+1,nodoFinal[1]+1] = self.valFin # Esto no cambia Ojo
        
        # Vecinos a los que puedo visitar (i,j) -> i= fila, j= columna
        self.directEstados = self.buscarVecinos(self.TablaCaminos)        