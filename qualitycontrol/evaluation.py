__author__ = 'pavelk'


import logging
log = logging.getLogger(__name__)

import json
from django.conf import settings
from crowdcafe_client.sdk import Judgement
from shapes.coordinates import getRectangleCoordinates, getPolygonPoints, getCanvasSize
from shapes.polygons import Polygon


class CanvasPolygon:
    def __init__(self, judgement):
        self.data = judgement.output_data
        # self.polygon
        # self.canvas
        if self.isValid():
            shapes = json.loads(self.data['_shapes'])
            for shape in shapes['objects']:
                if shape['type'] == 'image':
                    self.canvas = getCanvasSize(shape)
                if shape['type'] == 'rect':
                    self.polygon = Polygon(getRectangleCoordinates(shape))
                if shape['type'] == 'polygon':
                    self.polygon = Polygon(getPolygonPoints(shape))
    def isValid(self):
        if '_shapes' in self.data:
            return True
        else:
            return False


class CanvasPolygonSimilarity:
    def __init__(self, canvaspolygons):
        # we expect to have 2 canvaspolygons
        self.canvaspolygons = canvaspolygons
        self.threashold = settings.MARBLE_3D_ERROR_THREASHOLD

    def areSimilar(self):
        # bring polygons to one scale:
        for canvaspolygon in self.canvaspolygons:
            width = 800
            height = 600
            canvaspolygon.polygon.scale(1.0 * width / canvaspolygon.canvas['width'], 1.0 * height / canvaspolygon.canvas['height'])

        # check if their Perimetr, Area and Center are similar
        if self.haveSimilarPerimetr() and self.haveSimilarArea() and self.haveSimilarCenter():
            return True
        else:
            return False

    def haveSimilarPerimetr(self):
        perimeters = [cp.polygon.getPerimeter() for cp in self.canvaspolygons]
        return self.getDivergence(perimeters) <= self.threashold['perimetr']

    def haveSimilarArea(self):
        areas = [cp.polygon.getArea() for cp in self.canvaspolygons]
        return self.getDivergence(areas) <= self.threashold['area']

    def haveSimilarCenter(self):
        return True

    def getDivergence(self, arr):
        return (max(arr) - min(arr)) / min(arr)

