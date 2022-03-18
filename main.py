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
fr.FILE = 'test/cog_01.stp'
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
np.savetxt("data/01_cetner_of_gravity.pts", [centroid1, centroid2] , delimiter=' ')

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
fr.FILE = 'test/szelet_02.stp'
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

# obj fájl debugra
np.savetxt("debug/02_cetner_of_gravity.obj", [thumb_plus_centroid], delimiter=' ')
np.savetxt("debug/02_farthest_from_centroid.obj", [fnc.find_farthest_coordinate(thumb_plus_coordinates, thumb_plus_centroid)],delimiter=' ')


####################################################################################################################
# 3. Alulról indulva Z szintek közül legkisebb kerületű szint kiválasztása.
# Ha nem egyértelmű akkor a nagyobb z értékű de hüvelyk szint alatt!

# Rendezéshez egy osztály példányokat tartalmazó lista
coordinates_class = []

# Rossz koordináták kiszűrése és minden ötödik elem
for coordinate in fr.coordinates [::NTH_ELEMENT]:
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

slices_sorted = []
for s in slices:
    sorted = []
    fnc.sort_side(s, sorted, 3)
    slices_sorted.append(sorted)
    
slices = []
slices = slices_sorted

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
       
    print(perimeter)    
    number += 1


smallest_height = slices[smallest_number][0][2]

print("PRINT")
print(smallest_perimeter)
print(smallest_height)

bottom_number = 0
half_way_number = 0
bottom_height = smallest_height - min(150, smallest_height - 0) #fnc.find_thumb_level(fr.composite_curves) #smallest_height + min(150,absolute_bottom-smallest_height),
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

print("HEIGHTS")
print("SMALLEST:")
print(smallest_height)
print("BOTTOM:")
print(bottom_height)
print("HALF-WAY:")
print(half_way_height)

# Metszéspontok hozzáadása a három szinten
fnc.add_inetersections_2(slices, smallest_height, smallest_number)
fnc.add_inetersections_2(slices, bottom_height, bottom_number)
fnc.add_inetersections_2(slices, half_way_height, half_way_number)


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
fnc.sort_side(bottom_positive_side, bottom_positive_side_sorted,0)
fnc.sort_side(bottom_negative_side, bottom_negative_side_sorted,1)

    
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

# debug obj file save 

    
np.savetxt("debug/03_smallest_center_of_gravity.obj", [smallest_centroid], delimiter=' ',fmt='%1.8f')      
np.savetxt("debug/03_smallest_positive_side.obj", smallest_positive_side_sorted, delimiter=' ',fmt='%1.8f')
np.savetxt("debug/03_smallest_negative_side.obj", smallest_negative_side_sorted, delimiter=' ',fmt='%1.8f')

np.savetxt("debug/03_half_way_positive_side.obj", half_way_positive_side_sorted, delimiter=' ',fmt='%1.8f')
np.savetxt("debug/03_half_way_negative_side.obj", half_way_negative_side_sorted, delimiter=' ',fmt='%1.8f')

np.savetxt("debug/03_bottom_positive_side.obj", bottom_positive_side_sorted, delimiter=' ',fmt='%1.8f')
np.savetxt("debug/03_bottom_negative_side.obj", bottom_negative_side_sorted, delimiter=' ',fmt='%1.8f')

np.savetxt("debug/03_farthest_and_closest_fsc.obj", 
        [
            fnc.find_farthest_coordinate(slices[smallest_number], smallest_centroid),
            fnc.find_closest_coordinate(slices[smallest_number], smallest_centroid),  
        ],fmt='%1.8f')

####################################################################################################################
# 4. Ezek az első koordináta rendszer szerint
#   * y szerint szétválasztva [ legkisebb kerület ,legkisebb kerület - 150 ]
#   * x szerint szétválasztva [ legkisebb kerület ,legkisebb kerület - 150  ]



zero_slices = []

number=0
for s in slices:
    fnc.add_inetersections_2(slices, s[0][2], number)
    number+=1

for s in slices:
    zs = []
    for c in s:
        if c[0]==0 or c[1]==0:
            zs.append(c)
    zero_slices.append(zs)


x_segment_positive = []
x_segment_negative = []
y_segment_positive = []
y_segment_negative = []

for coordinate in zero_slices[0]:
    if coordinate[0] == 0:
        if coordinate[1] >= 0:
            x_segment_positive.append(coordinate)
        else:
            x_segment_negative.append(coordinate)
    
    if coordinate[1] == 0:
        if coordinate[0] >= 0:
            y_segment_positive.append(coordinate)
        else:
            y_segment_negative.append(coordinate)

x_zeros = []
y_zeros = []


for s in range(int(smallest_height/5), int((bottom_height)/5)+1):
    for i in zero_slices[s]:
        if i[0] == 0:
            x_zeros.append(i)
        if i[1] == 0:
            y_zeros.append(i)
    x_segment_positive.append(fnc.find_closest_coordinate(x_zeros,x_segment_positive[s-int(smallest_height/5)]))
    x_segment_negative.append(fnc.find_closest_coordinate(x_zeros,x_segment_negative[s-int(smallest_height/5)]))
    y_segment_positive.append(fnc.find_closest_coordinate(y_zeros,y_segment_positive[s-int(smallest_height/5)]))
    y_segment_negative.append(fnc.find_closest_coordinate(y_zeros,y_segment_negative[s-int(smallest_height/5)]))
    x_zeros = []
    y_zeros = []


x_segment_positive.pop(0)                                   
x_segment_negative.pop(0)
y_segment_positive.pop(0)
y_segment_negative.pop(0)


np.savetxt("data/04_x_positive",x_segment_positive, delimiter=' ')
np.savetxt("data/04_x_negative",x_segment_negative, delimiter=' ')
np.savetxt("data/04_y_positive",y_segment_positive, delimiter=' ')
np.savetxt("data/04_y_negative",y_segment_negative, delimiter=' ')


# A kiolvasott tartalom kiürítése
fr.coordinates = [] 
fr.points = []
fr.lines = [] 
fr.trimmed_curves = []
fr.composite_curve_segments = [] 
fr.composite_curves = []


####################################################################################################################
# 5. Új koordinátarendszer (x',y',z') szerint
#    * Hüvelykujj meghatározása
#    * Valós max szint hülyekujj + 15 szint
#    * y' szerint szétválasztott görbék [origo - hüvelykujj]
#    * X' szerint szétválasztott görbék [origo - hüvelykujj]

# A fájl megadása és beolvasása.
fr.FILE = 'test/02_szeletelt_5mm_step_test2.stp'
fr.read_file()

# Rendezéshez egy osztály példányokat tartalmazó lista
coordinates_class = []

# Rossz koordináták kiszűrése és minden ötödik elem coordinate_class egyedkent a listahoz adasa
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

# A hüvelykujjszint megtalálása    
thumb = fnc.find_thumb_level(fr.composite_curves)
    
# Görbe a hüvelykujjszint + 15 szinten, ezen súlypont kiírása.
thumb_plus = thumb + 15
curve_thumb_plus = fnc.find_curve_by_level(thumb_plus)



thumb_number = 0
number = -2
for t in fr.composite_curves:
    if(t.get_level() == thumb):
        thumb_number = number
    
    number+=1


number=0
for s in slices:
    fnc.add_inetersections_2(slices, s[0][2], number)
    number+=1
    

new_x_segment_positive = []
new_x_segment_negative = []
new_y_segment_positive = []
new_y_segment_negative = []

# x' sikmetszet gorbeje [0,z+15], y' szerint szetvalsztva
# y' simmetszet gorbeje [0,z+15], x' szerint szetvalasztva
zero_slices = []

for s in slices:
    zs = []
    for c in s:
        if c[0]==0 or c[1]==0:
            zs.append(c)
    zero_slices.append(zs)


for coordinate in zero_slices[0]:
    if coordinate[0] == 0:
        if coordinate[1] >= 0:
            new_x_segment_positive.append(coordinate)
        else:
            new_x_segment_negative.append(coordinate)
    
    if coordinate[1] == 0:
        if coordinate[0] >= 0:
            new_y_segment_positive.append(coordinate)
        else:
            new_y_segment_negative.append(coordinate)

x_zeros = []
y_zeros = []


for s in range(1, int(thumb_plus/5)+1):
    for i in zero_slices[s]:
        if i[0] == 0:
            x_zeros.append(i)
        if i[1] == 0:
            y_zeros.append(i)
    new_x_segment_positive.append(fnc.find_closest_coordinate(x_zeros,new_x_segment_positive[s-1]))
    new_x_segment_negative.append(fnc.find_closest_coordinate(x_zeros,new_x_segment_negative[s-1]))          
    new_y_segment_positive.append(fnc.find_closest_coordinate(y_zeros,new_y_segment_positive[s-1]))
    new_y_segment_negative.append(fnc.find_closest_coordinate(y_zeros,new_y_segment_negative[s-1]))
    x_zeros = []
    y_zeros = []



np.savetxt("data/05_new_x_positive",new_x_segment_positive, delimiter=' ')
np.savetxt("data/05_new_x_negative",new_x_segment_negative, delimiter=' ')
np.savetxt("data/05_new_y_positive",new_y_segment_positive, delimiter=' ')
np.savetxt("data/05_new_y_negative",new_y_segment_negative, delimiter=' ')


# A hüvelkyujj szint szétválasztása Y szerint
thumb_positive_side = []
thumb_negative_side = []

#fnc.add_inetersections_2(slices, thumb, thumb_number)

#fnc.add_inetersections_2(slices, thumb_plus, thumb_number+3)

fnc.separate_sides(slices, thumb_number, thumb_positive_side, thumb_negative_side, 1)

thumb_plus_coordinates = []
for tpc in fnc.get_coordinates_for_curve(curve_thumb_plus)[::NTH_ELEMENT]:
    thumb_plus_coordinates.append(tpc)


thumb_positive_side_sorted = []
thumb_negative_side_sorted = []
thumb_plus_coordinates_sorted = []


fnc.sort_side(thumb_plus_coordinates, thumb_plus_coordinates_sorted,2)
fnc.sort_side(thumb_positive_side, thumb_positive_side_sorted,0)
fnc.sort_side(thumb_negative_side, thumb_negative_side_sorted,1)


np.savetxt("data/05_thumb_positive_side.pts", thumb_positive_side_sorted, delimiter=' ')
np.savetxt("data/05_thumb_negative_side.pts", thumb_negative_side_sorted, delimiter=' ')
np.savetxt("data/05_thumb_plus_15.pts", thumb_plus_coordinates_sorted, delimiter = ' ')


# A kiolvasott tartalom kiürítése
fr.coordinates = [] 
fr.points = []
fr.lines = [] 
fr.trimmed_curves = []
fr.composite_curve_segments = [] 
fr.composite_curves = []


# TODO 03_bottom_negative_side súlypontot is tartalmaz ???
# DONE metszetek z szintje elcsúszva, rossz szinteknek néztem (most mar szerintem jo)
# DONE minden ötödik legyen kiírva
# DONE y szerinti nulla pontok mindkét oldalon legyenk
# DONE sorba legyenek a pontok y=0-tól 
# DONE túl hossszú név a farthest and closest fájloknak
# DONE legkisebb kerület legtávolabbi és legközelebbi rossz z szinten


# TODO A három szint meg mindig rossz sorrendben (0 - az alja és onnan megy felfelé)
#       bottom - huvelykujj
#       halfway - középen
#       smallest - nem a legkisebb :(
# TODO nullpontok kicsit beljebb vannak csúszva (0,01)
# TODO legkisebb kerület keresés nem jó