#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: view.py
Description: Base components for Python SDK sample.
"""
import time

import wx

import util
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar



class MyPanel(wx.Panel):
    """Base Panel."""

    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        colour_window = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        self.SetBackgroundColour(colour_window)


class MyStaticBitmap(MyPanel):
    """Base StaticBitmap."""

    def __init__(self, parent, bitmap=wx.NullBitmap, size=util.MAX_IMAGE_SIZE):
        super(MyStaticBitmap, self).__init__(parent)
        self.bmp = bitmap
        self.scale = 1.0
        self.bitmap = wx.StaticBitmap(self, bitmap=bitmap)
        self.size = size
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddStretchSpacer()
        self.sizer.Add(self.bitmap, 0, wx.EXPAND)
        self.sizer.AddStretchSpacer()
        self.SetMinSize((size, size))
        self.SetSizer(self.sizer)
        self.sizer.Layout()

    def set_path(self, path):
        """Set the image path."""
        img = util.rotate_image(path)
        width = img.GetWidth()
        img = util.scale_image(img, size=self.size)
        new_width = img.GetWidth()
        self.scale = 1.0 * new_width / width
        self.bmp = img.ConvertToBitmap()
        self.bitmap.SetBitmap(self.bmp)
        self.sizer.Layout()


class MyGridStaticBitmap(wx.Panel):
    """Base Grid StaticBitmap."""

    def __init__(self,
                 parent,
                 rows=1,
                 cols=0,
                 vgap=0,
                 hgap=0,
                 size=util.MAX_THUMBNAIL_SIZE):
        super(MyGridStaticBitmap, self).__init__(parent)
        self.sizer = wx.GridSizer(rows, cols, vgap, hgap)
        self.SetSizer(self.sizer)
        self.size = size

    def set_paths(self, paths):
        """Set the paths for the images."""
        self.sizer.Clear(True)
        for path in paths:
            bitmap = MyStaticBitmap(self, size=self.size)
            bitmap.set_path(path)
            self.sizer.Add(bitmap)
        self.SetSizerAndFit(self.sizer)
        self.sizer.Layout()

    def set_faces(self, faces):
        """Set the faces."""
        self.sizer.Clear(True)
        for face in faces:
            bitmap = MyStaticBitmap(self, bitmap=face.bmp, size=self.size)
            self.sizer.Add(bitmap)
        self.SetSizerAndFit(self.sizer)
        self.sizer.Layout()


class WrapCaptionFaceList(wx.WrapSizer):
    """Wrap face list with caption under the face."""

    def __init__(self, parent, confidence_faces, size=util.MAX_THUMBNAIL_SIZE):
        super(WrapCaptionFaceList, self).__init__()
        for face, confidence in confidence_faces:
            vsizer = wx.BoxSizer(wx.VERTICAL)
            bitmap = MyStaticBitmap(parent, face.bmp, size=size)
            vsizer.Add(bitmap)
            static_text = wx.StaticText(parent, label='%.2f' % confidence)
            vsizer.Add(static_text)
            self.Add(vsizer, 0, wx.ALIGN_LEFT | wx.EXPAND)
            vsizer.Layout()
        if len(confidence_faces) == 0:
            static_text = wx.StaticText(parent, label='no one')
            self.Add(static_text, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.Layout()


class FindSimilarsResult(wx.Panel):
    """The view for Find Similar result."""

    def __init__(self, parent):
        super(FindSimilarsResult, self).__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

    def set_data(self, faces, res_tot, size=util.MAX_THUMBNAIL_SIZE):
        """Set the data."""
        self.sizer.Clear(True)
        static_text_title = wx.StaticText(
            self,
            label='Find {} Similar Candidate Faces Results:'.format(
                len(faces)))
        self.sizer.Add(static_text_title, 0, wx.EXPAND)

        for mode in ('matchPerson', 'matchFace'):
            static_text_caption = wx.StaticText(
                self, label='{} Mode:'.format(mode))
            self.sizer.Add(static_text_caption, 0, wx.EXPAND)

            for face_id, face in faces.items():

                static_line = wx.StaticLine(self)
                self.sizer.Add(static_line, 0, wx.EXPAND)

                bitmap = MyStaticBitmap(self, face.bmp, size=size)
                self.sizer.Add(bitmap, 0, wx.ALIGN_LEFT)

                static_text = wx.StaticText(
                    self, label='Similar Faces Ranked by Similarity')
                self.sizer.Add(static_text, 0, wx.ALIGN_LEFT)

                confidence_face_list = WrapCaptionFaceList(
                    self, res_tot[mode][face_id])
                self.sizer.Add(confidence_face_list, 0, wx.EXPAND)
        self.SetSizerAndFit(self.sizer)


class WrapFaceList(wx.Panel):
    """Base wrap face list."""

    def __init__(self, parent, faces, size=util.MAX_THUMBNAIL_SIZE):
        super(WrapFaceList, self).__init__(parent)
        self.sizer = wx.WrapSizer()
        self.sizer.SetMinSize((util.MAX_IMAGE_SIZE, -1))
        for face in faces:
            bitmap = MyStaticBitmap(self, face.bmp, size=size)
            self.sizer.Add(bitmap, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()


class CaptionWrapFaceList(wx.Panel):
    """Wrap face list with a caption."""

    def __init__(self, parent):
        super(CaptionWrapFaceList, self).__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

    def set_data(self, caption_faces_list, size=util.MAX_THUMBNAIL_SIZE):
        """Set the data."""
        self.sizer.Clear(True)

        for caption, faces in caption_faces_list.items():
            static_text = wx.StaticText(self, label=caption)
            self.sizer.Add(static_text, 0, wx.ALIGN_LEFT)
            wrap_face_list = WrapFaceList(self, faces, size)
            self.sizer.Add(wrap_face_list, 0, wx.EXPAND)

        self.SetSizerAndFit(self.sizer)


class GroupResult(wx.Panel):
    """The view for Group result."""

    def __init__(self, parent):
        super(GroupResult, self).__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

    def set_data(self, faces, res, size=util.MAX_THUMBNAIL_SIZE):
        """Set the data."""
        self.sizer.Clear(True)

        for group in res['groups']:
            static_text = wx.StaticText(self, label='Group:')
            self.sizer.Add(static_text, 0, wx.EXPAND)

            group_faces = [faces[face_id] for face_id in group]
            wrap_face_list = WrapFaceList(self, group_faces, size)
            self.sizer.Add(wrap_face_list, 0, wx.EXPAND)

        if res.get('messyGroup'):
            static_text = wx.StaticText(self, label='Group (Messy):')
            self.sizer.Add(static_text, 0, wx.EXPAND)

            group_faces = [faces[face_id] for face_id in res['messyGroup']]
            wrap_face_list = WrapFaceList(self, group_faces, size)
            self.sizer.Add(wrap_face_list, 0, wx.EXPAND)

        self.SetSizerAndFit(self.sizer)
        self.sizer.Layout()


class MyLog(wx.TextCtrl):
    """The window for each scenario."""

    def __init__(self, parent):
        style = wx.TE_MULTILINE | wx.TE_READONLY
        super(MyLog, self).__init__(parent, style=style)
        colour_menu = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU)
        self.SetBackgroundColour(colour_menu)

    def log(self, msg):
        """Add log."""
        log_time = time.strftime("%H:%M:%S", time.localtime())
        msg = '[{}]: {}\n'.format(log_time, msg)
        self.WriteText(msg)


class MyFaceList(wx.VListBox):
    """Face List."""

    def __init__(self, parent, faces=[], **kwargs):
        super(MyFaceList, self).__init__(parent, **kwargs)
        self.SetItems(faces)

    def OnMeasureItem(self, index):
        """OnMeasureItem for Layout."""
        face = self.faces[index]
        bmp_height = face.bmp.GetHeight() + 4
        label_height = self.GetTextExtent(face.attr.gender)[1] * 6
        return max(bmp_height, label_height)

    def OnDrawItem(self, dc, rect, index):
        """OnDrawItem for Layout."""
        face = self.faces[index]
        dc.DrawBitmap(face.bmp, rect.x + 2,
                      ((rect.height - face.bmp.GetHeight()) / 2) + rect.y)

        textx = rect.x + 2 + face.bmp.GetWidth() + 2
        label_rect = wx.Rect(textx, rect.y, rect.width - textx, rect.height)
        label = util.LABEL_FACE.format(
            face.attr.gender, face.attr.age, face.attr.hair,
            face.attr.facial_hair, face.attr.makeup, face.attr.emotion,
            face.attr.occlusion, face.attr.exposure, face.attr.head_pose,
            face.attr.accessories)
        dc.DrawLabel(label, label_rect, wx.ALIGN_LEFT | wx.ALIGN_TOP)

    def SetItems(self, faces):
        """Set the items for the list."""
        self.faces = faces
        self.SetItemCount(len(self.faces))
        self.Refresh()


class MyPlotChart(wx.Panel):
    """Plot histogram chart."""

    def __init__(self, parent):
        super(MyPlotChart, self).__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddStretchSpacer()
        self.sizer.SetMinSize((util.MAX_IMAGE_SIZE, -1))
        self.SetSizer(self.sizer)
        self.Layout()
    pass


class Plot(wx.Panel):
    def __init__(self, parent, id=-1, dpi=None, **kwargs):
        wx.Panel.__init__(self, parent, id=id, **kwargs)
        self.figure = Figure(dpi=dpi, figsize=(2, 2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlim(0, 200)
        self.axes.set_ylim(0, 1)
        self.axes.grid(True)
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'gray']
        labels = ['anger', 'contempt', 'disgust', 'fear', 'happiness', 'sadness', 'surprise', 'neutral']

        self.n_bins = 1
        self.x = [[],[],[],[],[],[],[],[]]
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.SetMinSize((util.MAX_IMAGE_SIZE, -1))
        self.SetSizer(sizer)
        self.Fit()


    def SetItems(self, faces):
        """Set the items for the list."""
        anger, contempt, disgust, fear, happiness, neutral, sadness, surprise = \
            [], [], [], [], [], [], [], []
        anger       = list(map(lambda face: face['faceAttributes']['emotion']['anger'], faces))
        contempt    = list(map(lambda face: face['faceAttributes']['emotion']['contempt'], faces))
        disgust     = list(map(lambda face: face['faceAttributes']['emotion']['disgust'], faces))
        fear        = list(map(lambda face: face['faceAttributes']['emotion']['fear'], faces))
        happiness   = list(map(lambda face: face['faceAttributes']['emotion']['happiness'], faces))
        sadness     = list(map(lambda face: face['faceAttributes']['emotion']['sadness'], faces))
        surprise    = list(map(lambda face: face['faceAttributes']['emotion']['surprise'], faces))
        neutral     = list(map(lambda face: face['faceAttributes']['emotion']['neutral'], faces))
        self.x[0].append(self.mean(anger))
        self.x[1].append(self.mean(contempt))
        self.x[2].append(self.mean(disgust))
        self.x[3].append(self.mean(fear))
        self.x[4].append(self.mean(happiness))
        self.x[5].append(self.mean(sadness))
        self.x[6].append(self.mean(surprise))
        self.x[7].append(self.mean(neutral))

        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'gray']
        labels = ['anger', 'contempt', 'disgust', 'fear', 'happiness', 'sadness', 'surprise', 'neutral']
        self.axes.cla()
        self.axes.set_xlim(0, 200)
        self.axes.set_ylim(0, 1)
        self.axes.grid(True)
        self.axes.hist(self.x, density=True, histtype='bar', stacked=True, color=colors, label=labels)
        print(self.x)
        self.axes.plot()
        self.canvas.draw()
        plt.show()

        import json
        with open('data.txt', 'w') as outfile:
            json.dump(self.x, outfile)


    def mean(self, numbers):
        return float(sum(numbers)) / max(len(numbers), 1)
