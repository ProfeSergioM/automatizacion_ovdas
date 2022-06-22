# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 11:51:04 2022

@author: sergio.morales
"""


def crearDB():
    # A simple comment preceding a simple print statement
    import argparse
    import os, sys
    sys.path.insert(0, os.path.abspath('..'))
            
    parser = argparse.ArgumentParser(
        description="Generador de base de datos: Procesamiento de altura de columa, para procesamiento automático"
        ,add_help=False)
    
    #Ayuda
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Muestra esta ayuda y termina el programa.')
    #Archivo de entrada
    parser.add_argument('-f',dest='f',help="Archivo .txt con parámetros de entrada",
                        metavar='INPUTFILENAME'
                        )
    parser.add_argument('-v',action='store', nargs=3, 
                        help="Volcan en nombre_db, fechas inicio y final de datos en formato  YYYY-MM-DD",
                        metavar=('volcan','ini','fin')
                        )
    args = parser.parse_args()
    if args.f:
        inputFile='inputs/'+args.f+'.txt'
        print('Cargando parámetros de entrada desde '+inputFile)
    elif args.v:
        volcan=args.v[0]
        fechai=args.v[1]
        fechaf=args.v[2]
        print('Cargando datos de volcán '+volcan+' entre las fechas '+fechai+' y '+fechaf)
    else:
        inputFile='inputs/crearDb_input.txt'
        print('Cargando parámetros de entrada desde archivo por defecto inputs/crearDb_input.txt')
    filename=inputFile
    import sys
    with open(filename) as file:
        #try:
        for line in file:
            pname =line.split(' ')[0]
            if pname=='VOLCAN':
                volcan=line.split(' ')[1].rstrip()
            if pname=='FECHAI':
                fechai=line.split(' ')[1].rstrip()
            if pname=='FECHAF':
                fechaf=line.split(' ')[1].rstrip()
            if pname=='ROOTCI':
                rootci=line.split(' ')[1].rstrip()
            if pname=='PYOVLI':
                pyovli=line.split(' ')[1].rstrip()
            if pname=='PREFIX':
                prefix=line.split(' ')[1].rstrip()
            if pname=='SITIOC':
                sitioc=line.split(' ')[1].rstrip()
                
    outer_locals = locals()
    if all(var in outer_locals for var in ('volcan','fechai','fechaf','rootci','pyovli')):
        print("Parámetros de entrada cargados, procediendo...")
    else:
        sys.exit('\nFalta configurar archivo de parámetros de entrada, saliendo...')
    import sys
    import pandas as pd
    sys.path.append(pyovli)
    import ovdas_getfromdb_lib as gdb
    import cv2 as cv
    vistacam = gdb.get_metadata_camIP(volcan)
    vistacam=vistacam[vistacam.sitio==sitioc]
    #%%
    fullpaths=[]
    df=[]
    for index1,row1 in vistacam.iterrows():
        dfAlt = gdb.get_datos_x_vista_camIP(row1.idvista, fechai, fechaf)
        dfAlt = dfAlt[(dfAlt.archivo!='null') & (dfAlt.archivo.isnull()==False)]
        dfAlt['cam']=row1.directorioac
        df.append(dfAlt)
    dfAlt = pd.concat(df)
    
    for index2,row2 in dfAlt.iterrows():
        fullpaths.append(rootci+'/'+prefix+volcan+'/'+row2.cam+'/'+str(row2.fecha.year)+
              '/'+str(row2.fecha.month).zfill(2)+
              '/'+str(row2.fecha.day).zfill(2)+
              '/'+row2.archivo
              )
    dfAlt['fullpath']=fullpaths
    #%%
    import os
    directory='/data/imdata/'+volcan+'/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    datadir=os.path.abspath('.')+directory
    for wf in ('incan','quiet','ashes','cloud','degas'):
        if not os.path.exists('data/imdata/'+volcan+'/'+wf):
            os.makedirs('data/imdata/'+volcan+'/'+wf)
    i=0
    for index,row in dfAlt.iterrows():
        try:
            img = cv.imread(row.fullpath)
            if row.incandescencia==1:
                label='incan'   
            elif row.ceniza==1:
                label='ashes'   
            elif row.altura>0:
                label='degas'
            elif row.altura==0:
                label='quiet' 
            elif row.altura==-1:
                label='cloud' 
            cv.imwrite(datadir+label+'/'+row.archivo,img)
            i=i+1
        except:
            print('Archivo '+row.fullpath+' no encontrado')
    
crearDB()