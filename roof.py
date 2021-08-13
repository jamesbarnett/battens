import math
import svgwrite

ROOF_LENGTH = 16 * 12
ROOF_WIDTH = 8 * 12
SCALE = 925 / ROOF_LENGTH
BOARD_WIDTH = 3.5

class Roof:
    def __init__(self, position, length, width):
        self.position = position
        self.length = length
        self.width = width
        self.battens = []

    def size(self):
        return (self.length, self. width)

    def add_batten(self, batten):
        self.battens.append(batten)

def scale_points(points):
    return [(p[0] * SCALE, p[1] * SCALE) for p in points]

class RoofRenderer:
    def __init__(self, scale_factor, roof):
        self.scale_factor = scale_factor
        self.roof = roof

    def size(self):
        return (self.roof.length * self.scale_factor, self.roof.width * self.scale_factor)

    def position(self):
        return (self.roof.position[0] * self.scale_factor, self.roof.position[1] * self.scale_factor)

    def draw(self, drawing):
        drawing.add(drawing.rect(self.position(), self.size(), stroke=svgwrite.rgb(0, 0, 0, '%'), fill='none'))
        
        for batten in self.roof.battens:
            self.draw_batten(drawing, batten)

    def translate_points(self, points):
        return [(p[0] + self.position()[0], p[1] + self.position()[1]) for p in points]

    def draw_batten(self, drawing, batten):
        tl, bl, br, tr = self.translate_points(scale_points(batten.points()))
        # print(f"tl,bl,br,tr: ${tl},${bl},${br},${tr}")
        drawing.add(drawing.polygon([tl, bl, br, tr], stroke=svgwrite.rgb(0, 0, 0, '%'), fill=svgwrite.rgb(222, 184, 135)))


# TODO: Batten "types" for edges?
class Batten:
    TOP_EDGE = 0x1
    LEFT_EDGE = 0x2
    RIGHT_EDGE = 0x4
    BOTTOM_EDGE = 0x8

    def __init__(self, position, length, edges):
        self.position = position
        self.length = length
        self.edges = edges

    def points(self):
        tl, tr, bl, br = None, None, None, None
        if self.edges & self.TOP_EDGE:
            tl = self.position
            tr = (tl[0] + BOARD_WIDTH / math.sin(math.pi / 4), tl[1])
        elif self.edges & self.LEFT_EDGE:
            tr = (self.position[0], self.position[1] - BOARD_WIDTH / math.sin(math.pi / 4))
            # tl = (self.position[0], self.position[1] + BOARD_WIDTH / math.sin(math.pi / 4))
            tl = self.position
        else: # no edges on top end
            tl = self.position
            tr = (self.position[0] + BOARD_WIDTH * math.sin(math.pi / 4),
                  self.position[1] - BOARD_WIDTH * math.sin(math.pi / 4))

        if self.edges & self.BOTTOM_EDGE:
            bl = (tl[0] + self.length * math.sin(math.pi / 4), tl[1] + self.length * math.sin(math.pi / 4))
            br = (bl[0] + BOARD_WIDTH / math.sin(math.pi / 4), bl[1])
        elif self.edges & self.RIGHT_EDGE:
            bl = (tl[0] + self.length * math.sin(math.pi / 4), tl[1] + self.length * math.sin(math.pi / 4))
            br = (bl[0], bl[1] - BOARD_WIDTH / math.sin(math.pi / 4))
        else:
            bl = (self.position[0] + self.length * math.sin(math.pi / 4),
                  self.position[1] + self.length * math.sin(math.pi / 4))
            br = (bl[0] + BOARD_WIDTH * math.sin(math.pi / 4), bl[1] - BOARD_WIDTH * math.sin(math.pi / 4))

        return [tl, bl, br, tr]

AIR_GAP = 2.0

def batten_layout():
    battens = []

    # full length battens
    for i in range(9):
        batten = Batten((i * 14, 0), 96, Batten.TOP_EDGE)
        battens.append(batten)

    # corner battens
    battens.append(Batten((0, 14), 96, Batten.LEFT_EDGE))
    battens.append(Batten((9 * 14, 0), 93.4, Batten.TOP_EDGE | Batten.RIGHT_EDGE))
    battens.append(Batten((0, 28), 96.1, Batten.LEFT_EDGE | Batten.BOTTOM_EDGE))
    battens.append(Batten((0, 42), 76.4, Batten.LEFT_EDGE |Batten.BOTTOM_EDGE))
    battens.append(Batten((10 * 14, 0), 73.5, Batten.TOP_EDGE | Batten.RIGHT_EDGE))
    battens.append(Batten((0, 56), 56.6, Batten.LEFT_EDGE |Batten.BOTTOM_EDGE))
    battens.append(Batten((11 * 14, 0), 53.7, Batten.TOP_EDGE | Batten.RIGHT_EDGE))
    battens.append(Batten((0, 70), 36.8, Batten.LEFT_EDGE |Batten.BOTTOM_EDGE))
    battens.append(Batten((12 * 14, 0), 33.9, Batten.TOP_EDGE | Batten.RIGHT_EDGE))
    battens.append(Batten((0, 84), 17.0, Batten.LEFT_EDGE |Batten.BOTTOM_EDGE))
    battens.append(Batten((13 * 14, 0), 14.1, Batten.TOP_EDGE | Batten.RIGHT_EDGE))
    battens.append(supplement_batten(7, 35.0, Batten.RIGHT_EDGE))
    battens.append(supplement_batten(8, 15.2, Batten.RIGHT_EDGE))
    battens.append(Batten(((96 + AIR_GAP) * math.sin(math.pi / 4),
                          (96 + 13 + AIR_GAP) * math.sin(math.pi / 4) + BOARD_WIDTH / math.sin(math.pi /4)),
                          17.9, Batten.BOTTOM_EDGE))
    for i in range(7):
        battens.append(supplement_batten(i, 37.8, Batten.BOTTOM_EDGE))

    return battens

def supplement_batten(index, length, edges):
    return Batten((index * 14 + (96 + AIR_GAP) * math.sin(math.pi / 4), (96 + AIR_GAP) * math.sin(math.pi / 4)),
                  length, edges)

roof = Roof((2, 2), ROOF_LENGTH, ROOF_WIDTH)
for batten in batten_layout():
    roof.add_batten(batten)

renderer = RoofRenderer(SCALE, roof)

drawing = svgwrite.Drawing("roof.svg", profile='tiny')

drawing.add(drawing.rect(renderer.position(), renderer.size(), stroke=svgwrite.rgb(0, 0, 0, '%'), fill='none'))
renderer.draw(drawing)
drawing.save()

