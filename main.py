# coding=utf-8
# A fő program, ahol a megfelelő műveleteket a helyes sorrendben hajtjuk végre


import numpy as np
import functions as fnc
import file_read as fr

# Minden valahanyadik elem paraméter
NTH_ELEMENT = 5
####################################################################################################################
# 1. A legalsó sík és legfelső sík súlypontjának kiírása és
#    a súlyponthoz legközelebbi és legtávolabbi pontok kiírása.

# A fájl megadása és beolvasása.
fr.FILE = 'test/01_2sulypontg_step_test2.stp'
fr.read_file()

# A legalsó sík és a legfelső sík halmazok létrehozása
coordinates_1 = []
coordinates_2 = []

z_changed = False
z_first = fr.coordinates[0][2]

# A két sík szétválogatása    
for coordinate in fr.coordinates[::NTH_ELEMENT]:
    if(coordinate[2] != z_first):
        z_changed = True
        
    if z_changed:
        coordinates_2.append(coordinate)    
    else:
        coordinates_1.append(coordinate)

# A koordináták kiírása
# fnc.print_coordinates(coordinates_1)
# fnc.print_coordinates(coordinates_2)

# Súlypontok kiszámítása
centroid1 = fnc.centroid(coordinates_1)
centroid2 = fnc.centroid(coordinates_2)

# A súlyponthoz legközelebbi és legtávolabbi pontok kiírása fájlba
# Csak a felsőnek a legközelebbi pontját írjuk ki
if centroid1[2] > centroid2[2]:
    centroid = centroid1
else:
    centroid = centroid2
    
     
np.savetxt("data/01_closest_fc.pts", 
        [
            fnc.find_closest_coordinate(coordinates_1, centroid), 
        ])

# A súlypontok kiírása fájlba
np.savetxt("data/01_cetner_of_gravity.pts", [centroid1], delimiter=' ')

# A kiolvasott tartalom kiürítése
fr.coordinates = [] 
fr.points = []
fr.lines = [] 
fr.trimmed_curves = []
fr.composite_curve_segments = [] 
fr.composite_curves = []


####################################################################################################################
# 2. A hüvelykujj szintjének meghatározása.
#    Adott z szintről alulról haladva csak egy vagy két composite curve van?

# A fájl megadása és beolvasása.
fr.FILE = 'test/02_szeletelt_5mm_step_test2.stp'
fr.read_file()


# A görbék szintjének meghatározása a z koordinátákalapján
fnc.level_of_curves(fr.composite_curves, fr.composite_curve_segments, fr.trimmed_curves, fr.lines, fr.points)

# A hüvelykujjszintt megtalálása    
thumb = fnc.find_thumb_level(fr.composite_curves)

# Görbe a hüvelykujjszint + 15 szinten, ezen súlypont kiírása.
thumb_plus = thumb + 15
curve_thumb_plus = fnc.find_curve_by_level(thumb_plus)

thumb_plus_coordinates = []
thumb_plus_coordinates = fnc.get_coordinates_for_curve(curve_thumb_plus)
thumb_plus_centroid = fnc.centroid(thumb_plus_coordinates)

# A súlypont és a legtávolabbi pont kiírása fájlba
np.savetxt("data/02_cetner_of_gravity.pts", [thumb_plus_centroid], delimiter=' ')
np.savetxt("data/02_farthest_from_centroid.pts", [fnc.find_farthest_coordinate(thumb_plus_coordinates, thumb_plus_centroid)],delimiter=' ')


####################################################################################################################
# 3. Alulról indulva Z szintek közül legkisebb kerületű szint kiválasztása.
# Ha nem egyértelmű akkor a nagyobb z értékű de hüvelyk szint alatt!

# Rendezéshez egy osztály példányokat tartalmazó lista
coordinates_class = []

# Rossz koordináták kiszűrése és minden ötödik elem
for coordinate in fr.coordinates [::NTH_ELEMENT]:
    # mm-enként
    if (coordinate[2] % 5) == 0.0:
        coordinates_class.append(fr.Coordinate(coordinate[0],coordinate[1],coordinate[2]))

# A koordináták rendezése z értékek szerint
coordinates_class.sort()

# Visszaírás sima koordinátákat tartalmazó listába
coordinates = []
for coordinate in coordinates_class:
    coordinates.append([coordinate.get_x(), coordinate.get_y(), coordinate.get_z()])

# Szeletek lista és az egyes szeletek szétválasztása z érték alapján   
slices = []
fnc.separate_slices(coordinates, slices)

number = 0
absolute_bottom = float('-inf')
smallest_perimeter =float('inf')
smallest_number = 0
smallest_height = 0

for slice in reversed(slices):
    perimeter = 0.0
    previous_point = slice[0]
    
    for i in range(1,len(slice)):
        
        p1 = np.array([previous_point[0],previous_point[1],previous_point[2]])
        p2 = np.array([slice[i][0],slice[i][1],slice[i][2]])
        
        perimeter = perimeter + np.linalg.norm(p2 - p1)
        previous_point = slice[i]
        
    if(previous_point[2] > absolute_bottom):
        absolute_bottom = previous_point[2]
        
        
    if(perimeter <= smallest_perimeter):
        smallest_perimeter = perimeter
        smallest_number = number
    #print(perimeter, previous_point[2]) 
    number += 1

smallest_height = slices[smallest_number][0][2]
#print(smallest_number, smallest_perimeter)
#for pr in slices[smallest_number]:
#    print(pr)


bottom_number = 0
half_way_number = 0
bottom_height = fnc.find_thumb_level(fr.composite_curves) #smallest_height + min(150,absolute_bottom-smallest_height),
half_way_height = np.round(bottom_height - (bottom_height - smallest_height)/2//5*5)

# A magasságok szintjének megkeresése
number = 0
for slice in reversed(slices):
    for i in range(1,len(slice)):
        if(slice[i][2] == bottom_height):
            bottom_number = slices.__len__() - number - 1
            
        if(slice[i][2] == half_way_height):
            half_way_number = slices.__len__() - number - 1
    number+=1



# Metszéspontok hozzáadása a három szinten
fnc.add_intersections(slices, smallest_height, bottom_height, half_way_height,
                      smallest_number, bottom_number, half_way_number)
#DEBUG PRINT
#for s in slices:
#    for i in s:
#        print(i)


# A pozitív és negatív oldalak listája
smallest_positive_side = []
smallest_negative_side = []

half_way_positive_side = []
half_way_negative_side = []

bottom_positive_side = []
bottom_negative_side = []

# Y szerinti szátválasztás
fnc.separate_sides(slices, bottom_number, bottom_positive_side, bottom_negative_side, 1)
fnc.separate_sides(slices, half_way_number, half_way_positive_side, half_way_negative_side, 1)        
fnc.separate_sides(slices, smallest_number, smallest_positive_side, smallest_negative_side, 1) 
smallest_centroid = np.mean(slices[smallest_number], axis=0)


#print(smallest_height)
#print(half_way_height)
#print(bottom_height)
#print(absolute_bottom)

# A pontok sorrendbe szedése
smallest_positive_side_sorted = []
smallest_negative_side_sorted = []
half_way_positive_side_sorted = []
half_way_negative_side_sorted = []
bottom_positive_side_sorted = []
bottom_negative_side_sorted = []


#Oldalak rendbeszedése
fnc.sort_side(smallest_positive_side, smallest_positive_side_sorted,0)
fnc.sort_side(smallest_negative_side, smallest_negative_side_sorted,1)

    
fnc.sort_side(half_way_positive_side, half_way_positive_side_sorted,0)
fnc.sort_side(half_way_negative_side, half_way_negative_side_sorted,1)
  
  
#for i in bottom_positive_side:
#    print(i)    
#print(".............................")
#for i in bottom_negative_side:
#    print(i)

#print("###########################£")
fnc.sort_side(bottom_positive_side, bottom_positive_side_sorted,0)
fnc.sort_side(bottom_negative_side, bottom_negative_side_sorted,1)

#for i in bottom_positive_side_sorted:
#    print(i)    
#print(".............................")
#for i in bottom_negative_side_sorted:
#    print(i)
    
np.savetxt("data/03_smallest_center_of_gravity.pts", [smallest_centroid], delimiter=' ')      
np.savetxt("data/03_smallest_positive_side.pts", smallest_positive_side_sorted, delimiter=' ')
np.savetxt("data/03_smallest_negative_side.pts", smallest_negative_side_sorted, delimiter=' ')

np.savetxt("data/03_half_way_positive_side.pts", half_way_positive_side_sorted, delimiter=' ')
np.savetxt("data/03_half_way_negative_side.pts", half_way_negative_side_sorted, delimiter=' ')

np.savetxt("data/03_bottom_positive_side.pts", bottom_positive_side_sorted, delimiter=' ')
np.savetxt("data/03_bottom_negative_side.pts", bottom_negative_side_sorted, delimiter=' ')

np.savetxt("data/03_farthest_and_closest_fsc.pts", 
        [
            fnc.find_farthest_coordinate(slices[smallest_number], smallest_centroid),
            fnc.find_closest_coordinate(slices[smallest_number], smallest_centroid),  
        ])


# A kiolvasott tartalom kiürítése
fr.coordinates = [] 
fr.points = []
fr.lines = [] 
fr.trimmed_curves = []
fr.composite_curve_segments = [] 
fr.composite_curves = []


####################################################################################################################
# 4. Új koordinátarendszer szerint
#    * Hüvelykujj meghatározása
#    * Valós max szint hülyekujj + 15 szint
#    * y' szerint szétválasztott görbék [origo - hüvelykujj]
#    * X' szerint szétválasztott görbék [origo - hüvelykujj]

# A fájl megadása és beolvasása.
fr.FILE = 'test/02_szeletelt_5mm_step_test2.stp'
fr.read_file()

# Rendezéshez egy osztály példányokat tartalmazó lista
coordinates_class = []

# Rossz koordináták kiszűrése és minden ötödik elem
for coordinate in fr.coordinates [::NTH_ELEMENT]:
    # mm-enként
    if (coordinate[2] % 5) == 0.0:
        coordinates_class.append(fr.Coordinate(coordinate[0],coordinate[1],coordinate[2]))

# A koordináták rendezése z értékek szerint
coordinates_class.sort()

# Visszaírás sima koordinátákat tartalmazó listába
coordinates = []
for coordinate in coordinates_class:
    coordinates.append([coordinate.get_x(), coordinate.get_y(), coordinate.get_z()])
    
# Szeletek lista és az egyes szeletek szétválasztása z érték alapján   
slices = []
fnc.separate_slices(coordinates, slices)

# A görbék szintjének meghatározása a z koordinátákalapján
fnc.level_of_curves(fr.composite_curves, fr.composite_curve_segments, fr.trimmed_curves, fr.lines, fr.points)

# A hüvelykujjszintt megtalálása    
thumb = fnc.find_thumb_level(fr.composite_curves)
print(thumb)
    
# Görbe a hüvelykujjszint + 15 szinten, ezen súlypont kiírása.
thumb_plus = thumb + 15
curve_thumb_plus = fnc.find_curve_by_level(thumb_plus)



thumb_number = 0
number = -2
for t in fr.composite_curves:
    if(t.get_level() == thumb):
        thumb_number = number
    
    number+=1


# A hüvelkyujj szint szétválasztása Y szerint
thumb_positive_side = []
thumb_negative_side = []
fnc.separate_sides(slices, thumb_number, thumb_positive_side, thumb_negative_side, 1)

thumb_plus_coordinates = []
for tpc in fnc.get_coordinates_for_curve(curve_thumb_plus)[::NTH_ELEMENT]:
    thumb_plus_coordinates.append(tpc)




np.savetxt("data/04_thumb_positive_side.pts", thumb_positive_side, delimiter=' ')
np.savetxt("data/04_thumb_negative_side.pts", thumb_negative_side, delimiter=' ')
np.savetxt("data/04_thumb_plus_15.pts", thumb_plus_coordinates, delimiter = ' ')

# A kiolvasott tartalom kiürítése
fr.coordinates = [] 
fr.points = []
fr.lines = [] 
fr.trimmed_curves = []
fr.composite_curve_segments = [] 
fr.composite_curves = []

####################################################################################################################
# 5. 
#   Ezek az első koordináta rendszer szerint
#   * y szerint szétválasztva [ legkisebb kerület - legkisebb kerület - 150 ]
#   * x szerint szétválasztva [ legkisebb kerület - legkisebb kerület - 150  ]


# TODO 03_bottom_negative_side súlypontot is tartalmaz ???
# DONE metszetek z szintje elcsúszva, rossz szinteknek néztem (most mar szerintem jo)
# DONE minden ötödik legyen kiírva
# DONE y szerinti nulla pontok mindkét oldalon legyenk
# DONE sorba legyenek a pontok y=0-tól 
# DONE túl hossszú név a farthest and closest fájloknak
# DONE legkisebb kerület legtávolabbi és legközelebbi rossz z szinten