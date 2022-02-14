# coding=utf-8


# STEP fájl elérési útvonala a projekt mappán belül + a fájl neve  
FILE = 'sample/02_szeletelt_5mm_step_test2.stp'

class CompositeCurve():
    def __init__(self, id, composite_curve_segment_ids, level=0):
        self.id = id
        self.composite_curve_segment_ids = composite_curve_segment_ids
        self.level = level
    
    def __str__(self):
        print(self.id + " COMPOSITE_CURVE" )
        for ccsi in self.composite_curve_segment_ids:
            print(ccsi)
            
    def get_id(self):
        return self.id

    def get_list(self):
        return self.composite_curve_segment_ids
    
    def get_level(self):
        return self.level
    
    def set_level(self, level):
        self.level = level
           
    
class CompositeCurveSegment():
    def __init__(self, id, trimmed_curve_id):
        self.id = id
        self.trimmed_curve_id = trimmed_curve_id
    
    def __str__(self):
        print(self.id + " COMPOSTIE_CURVE_SEGMENT " + self.trimmed_curve_id)
       
        
    def get_id(self):
        return self.id
    
    def get_trimmed_curve_id(self):
        return self.trimmed_curve_id

    
class TrimmedCurve():
    def __init__(self, id, line_id):
        self.id = id
        self.line_id = line_id
    
    def __str__(self):
        print(self.id + " TRIMMED_CURVE " + self.line_id)
        
        
    def get_id(self):
        return self.id
    
    def get_line_id(self):
        return self.line_id
 
        
class Line():
    def __init__(self, id, point_id):
        self.id = id
        self.point_id = point_id
      
    def __str__(self):
        print(self.id + " LINE " + self.point_id)
         
        
    def get_id(self):
        return self.id
    
    def get_point_id(self):
        return self.point_id
 
        
class CartesianPoint():
    def __init__(self, id, coordinate):
        self.id = id
        self.coordinate = coordinate
        
    def __str__(self):
        print(self.id + " CARTESIAN POINT " + "(" + 
              str(self.coordinate.get_x())  + ", " + 
              str(self.coordinate.get_y())  + ", " + 
              str(self.coordinate.get_z())  + ")"
              )
        
    def get_id(self):
        return self.id

    def get_coordinate(self):
        return self.coordinate
        
        
class Coordinate(): 
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        print(self.x, self.y, self.z)
        
    def __lt__(self, other):
        return self.z < other.z
    
    def __gt__(self, other):
        if self.y == other.y:
            return self.x > other.x
        else:
            return self.y > other.y
    
        
    def get_id(self):
        return self.id
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_z(self):
        return self.z
    

    
def read_file():
    file = open(FILE,'r+')
    file_lines = file.readlines()
    file.close()


    for row in file_lines:
        if("CARTESIAN_POINT" in row):
            id = row[ : row.find('=')]
            row = row[row.rfind('(')+1 : row.find(')')]
            row = row.split(',')
            x = float(row[0])
            y = float(row[1])
            try:
                z = float(row[2])
            except:
                continue
                row = row[:row.find('(')]
                print(row)
                z = float(row)
            coordinates.append([x,y,z])
            points.append(CartesianPoint(id, Coordinate(x, y, z)))
            
        if("LINE" in row):
            id = row[ : row.find('=')]
            point_id = row[ row.find(',')+1 : row.rfind(',') ]
            lines.append(Line(id, point_id))
        
        if("TRIMMED_CURVE" in row):
            id = row[ : row.find('=')]
            line_id = row[ row.find(',')+1 : row.find(',', row.find(',')+1) ]
            trimmed_curves.append(TrimmedCurve(id, line_id))
            
        if("COMPOSITE_CURVE_SEGMENT" in row):
            id = row[ : row.find('=')]
            trimmed_curve_id = row[ row.rfind(',')+1 : row.find(')') ]
            composite_curve_segments.append(CompositeCurveSegment(id, trimmed_curve_id))
        
        if("COMPOSITE_CURVE(" in row):
            id = row[ : row.find('=')]
            text = '\n'.join(file_lines)
            
            curve_string = text[text.find(row)-len(row) : text.find('.F.',text.find(row)) ]
            curve_string = curve_string[curve_string.find("('',(")+5 : curve_string.rfind(')')]
            curve_string = curve_string.rstrip('\r\n').replace('\n', '')
            curve_segments = curve_string.splitlines()
            curve_segments = curve_segments[0].__str__().split(',')
        
            composite_curves.append(CompositeCurve(id,curve_segments))

    
    
coordinates = []     
points = []
lines = []
trimmed_curves = []
composite_curve_segments = []
composite_curves = []
