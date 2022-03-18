# coding=utf-8
# Minden szükséges függvény itt található

import numpy as np
import file_read as fr

        
# Visszaadja egy koordinátahalmaz súlyponját
def centroid(coordinates):
    return np.mean(coordinates, axis=0)


# Megkeresi a legtávolabbi koordinátát a súlyponthoz        
def find_farthest_coordinate(coordinates, centroid):
    farthest = coordinates[0]

    for coordinate in coordinates:
        param1 = [centroid[0]-coordinate[0], centroid[1]-coordinate[1], centroid[2]-coordinate[2]]
        param2 = [centroid[0]-farthest[0], centroid[1]-farthest[1], centroid[2]-farthest[2]]
        if(np.linalg.norm(param1) > np.linalg.norm(param2)):
            farthest = coordinate

    return farthest
   
    
# Megkeresi a legközelebbi koordinátát a súlyponthoz
def find_closest_coordinate(coordinates, centroid):
    closest = coordinates[0]
    
    for coordinate in coordinates:
        param1 = [centroid[0]-coordinate[0], centroid[1]-coordinate[1], centroid[2]-coordinate[2]]
        param2 = [centroid[0]-closest[0], centroid[1]-closest[1], centroid[2]-closest[2]]
        if(np.linalg.norm(param1) < np.linalg.norm(param2)):
            closest = coordinate

    return closest

# Sorba szedi egy oldal pontjait, y=0 ponttól indulva
def sort_side(side, side_sorted, type):
    # 0 pozitiv side
    # 1 negative side
    # both sides
    for p in side:
        if type == 0:
            if p[1] == 0 and p[0] >= 0:
                start = p
                side.remove(p)
                side_sorted.append(start)
        elif type == 1:
            if p[1] == 0 and p[0] < 0:
                start = p
                side.remove(p)
                side_sorted.append(start)
        else:
            start = p
            side.remove(p)
            side_sorted.append(start)
                
    if side_sorted.__len__() == 0:
        previous_point = [0.0, 0.0, p[2]]
    else:
        previous_point = side_sorted[0]
        
        
    while side.__len__() != 0:
        next_point = find_closest_coordinate(side,previous_point)
        side_sorted.append(next_point)
        side.remove(next_point)
        previous_point = next_point
        
    return side_sorted

# Kiirja a koordinátákat    
def print_coordinates(coordinates):
    
    for coordinate in coordinates:
        print(coordinate[0], coordinate[1], coordinate[2])
      
        
# Beállítja a görbék szintjeit a z koordináta értékek alapján
def level_of_curves(composite_curves, composite_curve_segments, trimmed_curves, lines, points):
    
    for cc in composite_curves:
        for c in composite_curve_segments:
                if c.get_id() == cc.get_list()[0]:
                    for t in trimmed_curves:
                        if c.get_trimmed_curve_id() == t.get_id():
                            for l in lines:
                                if t.get_line_id() == l.get_id():
                                    for p in points:
                                        if l.get_point_id() == p.get_id():
                                            if(p.coordinate.get_z()%5==0):
                                                cc.set_level(p.coordinate.get_z())
    
    
                            
# A kapott összetett görbékből visszaadja az a szintet ahol a hüvelykujj található                                    
def find_thumb_level(composite_curves):
    prev_level = -1               
    for cc in composite_curves:
        level = cc.get_level()
        if(prev_level == level):
            return level
        prev_level = level
 
# Visszadja a kapott szinten lévő görbéket
def find_curve_by_level(curve_level):
    curve = fr.composite_curves[0]
    for cc in fr.composite_curves:
        if cc.level == curve_level and len(cc.get_list()) > len(curve.get_list()) :
            curve = cc
            
    return curve

def get_coordinates_for_curve(curve):
    coordinates = []
    
    for c in curve.get_list():
        for ccs in fr.composite_curve_segments:
            if(c == ccs.get_id()):
                for t in fr.trimmed_curves:
                    if ccs.get_trimmed_curve_id() == t.get_id():
                        for l in fr.lines:
                            if t.get_line_id() == l.get_id():
                                for p in fr.points:
                                    if l.get_point_id() == p.get_id():
                                        coordinates.append([
                                                            p.get_coordinate().get_x(),
                                                            p.get_coordinate().get_y(),
                                                            p.get_coordinate().get_z()
                                                            ])
                

    return coordinates

# Vonal két poont között
# Visssatér az x=0 vagy y=0 szerint vonalra illeszkedő ponttal
def line_from_points(P, Q, which):
    # which = 1: y=0
    # which = 0: x=0
    a = float(Q[1]) - float(P[1])  
    b = float(P[0]) - float(Q[0])   
    c = a*(float(P[0])) + b*(float(P[1]))
    
    if(c < 0 ):
        # a * x - b * y =  c
        if(which == 1):
            return [c/a, 0]
        else:
            return [0 ,c/b*(-1.0)]
            
             
    else:
        # a * x + b * y =  c
        if(which == 1):
            return [c/a, 0]
        else:
            return [0 ,c/b]
            
            
def add_inetersections_2(slices, height, number):
    # Metszetek
    intersection_A_1 = None
    intersection_A_2 = None
    intersection_B_1 = None
    intersection_B_2 = None
    intersection_C_1 = None
    intersection_C_2 = None
    intersection_D_1 = None
    intersection_D_2 = None

    # Szintenkénti metszéspontok listája
    intersection_list = []
    # A metszéspontok megkeresése a két 0-hoz közeli kordináta alpján
    # A két közeli pont egyenesének egyenletét felállítva az x=0/y=0 pontok megtalálása
    # Ezek lesznek a metszéspontok
    #         A1|A2
    #           |
    #  D2       |       B1
    #  ---------+---------
    #  D1       |       B2
    #           |
    #         C2|C1
        
    # A szeletekben ha épp valamelyik számunkra fontos szinten vagyunk akkor a belső loop hajtódik végre
    # Szinteket kaphatná paraméterként és akkor rövidebb!
    for layer in slices:
        if layer[0][2] == height:
            previous = layer[0]
            for point in layer:
                # X negatívból pozitívba vált 
                # A1, A2
                if previous[0] <= 0 and point[0] >= 0:
                    intersection_A_1 = previous
                    intersection_A_2 = point
                
                # X pozitívból negatívba vált 
                # C1, C2
                if previous[0] >= 0 and point[0] <= 0:
                    intersection_C_1 = previous
                    intersection_C_2 = point
                
                # Y negatívból pozitívba vált 
                # D1, D2
                if previous[1] <= 0 and point[1] >= 0:
                    intersection_D_1 = previous
                    intersection_D_2 = point
                    
                # Y pozitívból negatívba vált 
                # B1, B2
                if previous[1] >= 0 and point[1] <= 0:
                    intersection_B_1 = previous
                    intersection_B_2 = point
                
                previous = point

                # Ha C1, C2 vagy A1, A2 lenne NoneType, akkor az x koordinatak olyan sorrendben vannak, hogy csak egyszer valt elojelet, 
                # ekkor az elso es utolso tagok kozti valtas kell megadni a NoneType valtozoknak
                if  intersection_C_1 is None and intersection_C_2 is None:
                    intersection_C_1 = layer[layer.__len__()-1]
                    intersection_C_2 = layer[0]

                if intersection_A_1 is None and intersection_A_2 is None:
                    intersection_A_1 = layer[layer.__len__()-1]
                    intersection_A_2 = layer[0]

                if intersection_B_1 is None and intersection_B_2 is None:
                    intersection_B_1 = layer[layer.__len__()-1]
                    intersection_B_2 = layer[0]

                if intersection_D_1 is None and intersection_D_2 is None:
                    intersection_D_1 = layer[layer.__len__()-1]
                    intersection_D_2 = layer[0]

            if layer[0][2] == height:
                intersection_list.append(intersection_A_1)
                intersection_list.append(intersection_A_2)
                intersection_list.append(intersection_B_1)
                intersection_list.append(intersection_B_2)
                intersection_list.append(intersection_C_1)
                intersection_list.append(intersection_C_2)
                intersection_list.append(intersection_D_1)
                intersection_list.append(intersection_D_2)

    
    
    
    intersections = []

     # A nulla pontok megkeresése
    #----------------------------------------------------------------------------------------------
    # A1, A2       
    p = line_from_points([intersection_list[0][0],intersection_list[0][1]],
                     [intersection_list[1][0],intersection_list[1][1]],0)
    p.append(height)
    #print(p)
    intersections.append(p)

    # B1, B2
    p = line_from_points([intersection_list[2][0],intersection_list[2][1]],
                    [intersection_list[3][0],intersection_list[3][1]],1)
    p.append(height)
    #print(p)
    intersections.append(p)
    
    # C1, C2     
    p = line_from_points([intersection_list[4][0],intersection_list[4][1]],
                     [intersection_list[5][0],intersection_list[5][1]],0)
    p.append(height)
    #print(p)
    intersections.append(p)

    # D1, D2
    p = line_from_points([intersection_list[6][0],intersection_list[6][1]],
                    [intersection_list[7][0],intersection_list[7][1]],1)
    p.append(height)
    #print(p)
    intersections.append(p)

    slices[number] += intersections
    
    #print(intersections)



# Metszéspontok hozzáadása a három fontos szinthez
def add_intersections(slices, smallest_height, bottom_height, half_way_height, smallest_number, bottom_number, half_way_number):
    # Metszetek
    intersection_A_1 = None
    intersection_A_2 = None
    intersection_B_1 = None
    intersection_B_2 = None
    intersection_C_1 = None
    intersection_C_2 = None
    intersection_D_1 = None
    intersection_D_2 = None
    # Szintenkénti metszéspontok listája
    intersection_list_smallest = []
    intersection_list_half_way = []
    intersection_list_bottom = []
    # A metszéspontok megkeresése a két 0-hoz közeli kordináta alpján
    # A két közeli pont egyenesének egyenletét felállítva az x=0/y=0 pontok megtalálása
    # Ezek lesznek a metszéspontok
    #         A1|A2
    #           |
    #  D2       |       B1
    #  ---------+---------
    #  D1       |       B2
    #           |
    #         C2|C1
        
    # A szeletekben ha épp valamelyik számunkra fontos szinten vagyunk akkor a belső loop hajtódik végre
    # Szinteket kaphatná paraméterként és akkor rövidebb!
    for layer in slices:
        if layer[0][2] == smallest_height or layer[0][2] == bottom_height or layer[0][2] == half_way_height:
            previous = layer[0]
            for point in layer:
                # X negatívból pozitívba vált 
                # A1, A2
                if previous[0] < 0 and point[0] > 0:
                    intersection_A_1 = previous
                    intersection_A_2 = point
                
                # X pozitívból negatívba vált 
                # C1, C2
                if previous[0] > 0 and point[0] < 0:
                    intersection_C_1 = previous
                    intersection_C_2 = point
                
                # Y negatívból pozitívba vált 
                # D1, D2
                if previous[1] < 0 and point[1] > 0:
                    intersection_D_1 = previous
                    intersection_D_2 = point
                    
                # Y pozitívból negatívba vált 
                # B1, B2
                if previous[1] > 0 and point[1] < 0:
                    intersection_B_1 = previous
                    intersection_B_2 = point
                
                previous = point
                
            if layer[0][2] == smallest_height:
                intersection_list_smallest.append(intersection_A_1)
                intersection_list_smallest.append(intersection_A_2)
                intersection_list_smallest.append(intersection_B_1)
                intersection_list_smallest.append(intersection_B_2)
                intersection_list_smallest.append(intersection_C_1)
                intersection_list_smallest.append(intersection_C_2)
                intersection_list_smallest.append(intersection_D_1)
                intersection_list_smallest.append(intersection_D_2)
                
            if layer[0][2] == half_way_height:
                intersection_list_half_way.append(intersection_A_1)
                intersection_list_half_way.append(intersection_A_2)
                intersection_list_half_way.append(intersection_B_1)
                intersection_list_half_way.append(intersection_B_2)
                intersection_list_half_way.append(intersection_C_1)
                intersection_list_half_way.append(intersection_C_2)
                intersection_list_half_way.append(intersection_D_1)
                intersection_list_half_way.append(intersection_D_2)    
                
            if layer[0][2] == bottom_height:
                intersection_list_bottom.append(intersection_A_1)
                intersection_list_bottom.append(intersection_A_2)
                intersection_list_bottom.append(intersection_B_1)
                intersection_list_bottom.append(intersection_B_2)
                intersection_list_bottom.append(intersection_C_1)
                intersection_list_bottom.append(intersection_C_2)
                intersection_list_bottom.append(intersection_D_1)
                intersection_list_bottom.append(intersection_D_2)    
                
     
    intersections_smallest = []
    intersections_half_way = []
    intersections_bottom = []
  
    
                    
    # A nulla pontok megkeresése
    #----------------------------------------------------------------------------------------------
    # A1, A2
    #print(intersection_list_bottom[0],intersection_list_bottom[1])
    # x=0        
    p = line_from_points([intersection_list_bottom[0][0],intersection_list_bottom[0][1]],
                     [intersection_list_bottom[1][0],intersection_list_bottom[1][1]],0)
    p.append(bottom_height)
    #print(p)
    intersections_bottom.append(p)

    # B1, B2
    #print(intersection_list_bottom[2],intersection_list_bottom[3])
    # y=0
    p = line_from_points([intersection_list_bottom[2][0],intersection_list_bottom[2][1]],
                    [intersection_list_bottom[3][0],intersection_list_bottom[3][1]],1)
    p.append(bottom_height)
    #print(p)
    intersections_bottom.append(p)
    
    # C1, C2
    #print(intersection_list_bottom[4],intersection_list_bottom[5])
    # x=0        
    p = line_from_points([intersection_list_bottom[4][0],intersection_list_bottom[4][1]],
                     [intersection_list_bottom[5][0],intersection_list_bottom[5][1]],0)
    p.append(bottom_height)
    #print(p)
    intersections_bottom.append(p)

    # D1, D2
    #print(intersection_list_bottom[6],intersection_list_bottom[7])
    # y=0
    p = line_from_points([intersection_list_bottom[6][0],intersection_list_bottom[6][1]],
                    [intersection_list_bottom[7][0],intersection_list_bottom[7][1]],1)
    p.append(bottom_height)
    #print(p)
    intersections_bottom.append(p)
    #----------------------------------------------------------------------------------------------      
    # A1, A2
    #print(intersection_list_half_way[0],intersection_list_half_way[1])
    # x=0        
    p = line_from_points([intersection_list_half_way[0][0],intersection_list_half_way[0][1]],
                     [intersection_list_half_way[1][0],intersection_list_half_way[1][1]],0)
    p.append(half_way_height)
    #print(p)
    intersections_half_way.append(p)

    # B1, B2
    #print(intersection_list_half_way[2],intersection_list_half_way[3])
    # y=0
    p = line_from_points([intersection_list_half_way[2][0],intersection_list_half_way[2][1]],
                    [intersection_list_half_way[3][0],intersection_list_half_way[3][1]],1)
    p.append(half_way_height)
    #print(p)
    intersections_half_way.append(p)
    
    # C1, C2
    #print(intersection_list_half_way[4],intersection_list_half_way[5])
    # x=0        
    p = line_from_points([intersection_list_half_way[4][0],intersection_list_half_way[4][1]],
                     [intersection_list_half_way[5][0],intersection_list_half_way[5][1]],0)
    p.append(half_way_height)
    #print(p)
    intersections_half_way.append(p)
    # D1, D2
    #print(intersection_list_half_way[6],intersection_list_half_way[7])
    # y=0
    p = line_from_points([intersection_list_half_way[6][0],intersection_list_half_way[6][1]],
                    [intersection_list_half_way[7][0],intersection_list_half_way[7][1]],1)
    p.append(half_way_height)
    #print(p)
    intersections_half_way.append(p)
    #----------------------------------------------------------------------------------------------
    # A1, A2
    #print(intersection_list_smallest[0],intersection_list_smallest[1])
    # x=0        
    p = line_from_points([intersection_list_smallest[0][0],intersection_list_smallest[0][1]],
                     [intersection_list_smallest[1][0],intersection_list_smallest[1][1]],0)
    p.append(smallest_height)
    #print(p)
    intersections_smallest.append(p)
    # B1, B2
    #print(intersection_list_smallest[2],intersection_list_smallest[3])
    # y=0
    p = line_from_points([intersection_list_smallest[2][0],intersection_list_smallest[2][1]],
                    [intersection_list_smallest[3][0],intersection_list_smallest[3][1]],1)
    p.append(smallest_height)
    #print(p)
    intersections_smallest.append(p)
    
    # C1, C2
    #print(intersection_list_smallest[4],intersection_list_smallest[5])
    # x=0        
    p = line_from_points([intersection_list_smallest[4][0],intersection_list_smallest[4][1]],
                     [intersection_list_smallest[5][0],intersection_list_smallest[5][1]],0)
    p.append(smallest_height)
    #print(p)
    intersections_smallest.append(p)

    # D1, D2
    #print(intersection_list_smallest[6],intersection_list_smallest[7])
    # y=0
    p = line_from_points([intersection_list_smallest[6][0],intersection_list_smallest[6][1]],
                    [intersection_list_smallest[7][0],intersection_list_smallest[7][1]],1)
    p.append(smallest_height)
    #print(p)
    intersections_smallest.append(p)
    #----------------------------------------------------------------------------------------------
    
    #print(intersections_bottom)
    #print(intersections_half_way)
    #print(intersections_smallest)
    
    

    slices[smallest_number] += intersections_smallest
    slices[half_way_number] += intersections_half_way
    slices[bottom_number] += intersections_bottom


    
# A koordináta halmazból szétválasztja a szeleteket        
def separate_slices(coordinates, slices):
    z = coordinates[0][2]
    slice = []
    for coordinate in coordinates:
        if(coordinate[2] != z):
            slices.append(slice)
            slice = []
            z = coordinate[2]
        slice.append(coordinate)
        
        

def separate_sides(slices, number, positive_side, negative_side, separate_by):
    # x szerinti szétválasztás 0
    # y szerinti szétválasztás 1

    for point in slices[number]:
        if point[separate_by] > 0:
            positive_side.append(point)
        elif point[separate_by] == 0:
            positive_side.append(point)
            negative_side.append(point)
        else:
            negative_side.append(point)