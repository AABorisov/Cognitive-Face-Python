#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: panel_detection.py
Description: Detection Panel for Python SDK sample.
"""

import wx

import util
import model
import os
import cv2
import time
from view import base


class VideoPanel(base.MyPanel):
    """Detection Panel."""

    def __init__(self, parent):
        super(VideoPanel, self).__init__(parent)

        self.vsizer = wx.BoxSizer(wx.VERTICAL)

        self.hsizer = wx.BoxSizer()
        self.hsizer.AddStretchSpacer()

        self.hvsizer = wx.BoxSizer(wx.VERTICAL)
        self.hvsizer.SetMinSize((util.INNER_PANEL_WIDTH, -1))

        label = ("To detect faces in an image, click the 'Choose Image' "
                 "button. You will see a rectangle surrounding every face "
                 "that the Face API detects. You will also see a list of "
                 "attributes related to the faces.")
        self.static_text = wx.StaticText(self, label=label)
        self.static_text.Wrap(util.INNER_PANEL_WIDTH)
        self.hvsizer.Add(self.static_text, 0, wx.ALL, 5)

        ### SETTINGS table

        label = 'Settings table : '
        self.settings_table_label = wx.StaticText(self, label=label)
        self.hvsizer.Add(self.settings_table_label, 0, wx.ALL, 5)
        subgridsizer = wx.GridSizer(rows=2, cols=2, hgap=5, vgap=5)

        # Time sleep
        flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.FIXED_MINSIZE
        label = 'Time sleep : '
        self.settings_table_time_label = wx.StaticText(self, label=label)
        subgridsizer.Add(self.settings_table_time_label, flag=flag, border=5)

        flag = wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALL

        time_sleep = util.CF.util.TIME_SLEEP
        self.settings_table_time_text = wx.TextCtrl(self, size=(-1, -1))
        self.settings_table_time_text.SetValue(float.__str__(time_sleep))
        subgridsizer.Add(self.settings_table_time_text, 1, flag=flag, border=5)

        # Time frame
        flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.FIXED_MINSIZE
        label = 'Time frame : '
        self.settings_table_time_frame_label = wx.StaticText(self, label=label)
        subgridsizer.Add(self.settings_table_time_frame_label, flag=flag, border=5)

        flag = wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALL
        time_frame = util.CF.util.TIME_SLEEP
        self.settings_table_time_frame_text = wx.TextCtrl(self, size=(-1, -1))
        self.settings_table_time_frame_text.SetValue(float.__str__(time_frame))
        subgridsizer.Add(self.settings_table_time_frame_text, 1, flag=flag, border=5)

        flag = wx.EXPAND | wx.TOP | wx.BOTTOM
        self.hvsizer.Add(subgridsizer, flag=flag, border=5)

        self.vhsizer = wx.BoxSizer()
        self.vhsizer.SetMinSize((util.INNER_PANEL_WIDTH, -1))

        self.lsizer = wx.BoxSizer(wx.VERTICAL)
        self.lsizer.SetMinSize((util.MAX_IMAGE_SIZE, -1))

        flag = wx.EXPAND | wx.ALIGN_CENTER | wx.ALL
        self.btn = wx.Button(self, label='Choose Video')
        self.lsizer.Add(self.btn, 0, flag, 5)
        self.Bind(wx.EVT_BUTTON, self.OnChooseVideo, self.btn)

        self.vhsizer.Add(self.lsizer, 0, wx.ALIGN_LEFT)
        self.vhsizer.AddStretchSpacer()

        self.rsizer = wx.BoxSizer(wx.VERTICAL)
        self.rsizer.SetMinSize((util.MAX_IMAGE_SIZE, -1))

        style = wx.ALIGN_CENTER
        flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL
        self.result = wx.StaticText(self, style=style)
        self.rsizer.Add(self.result, 0, flag, 5)

        self.vhsizer.Add(self.rsizer, 0, wx.EXPAND)

        self.hvsizer.Add(self.vhsizer)

        flag = wx.ALIGN_CENTER | wx.EXPAND | wx.ALL
        self.plot = base.Plot(self)
        self.hvsizer.Add(self.plot, 1, flag, 5)

        self.hsizer.Add(self.hvsizer, 0)
        self.hsizer.AddStretchSpacer()

        self.vsizer.Add(self.hsizer, 3, wx.EXPAND)

        self.log = base.MyLog(self)
        self.vsizer.Add(self.log, 1, wx.EXPAND)

        self.SetSizerAndFit(self.vsizer)

    def OnChooseVideo(self, evt):
        """Choose Video."""
        dlg = wx.FileDialog(self, wildcard=util.VIDEO_WILDCARD)
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        print(path)
        cap = cv2.VideoCapture(path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        pos_frames = cap.get(cv2.CAP_PROP_POS_FRAMES)
        count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        iter_frames = fps * 3
        print('initial attributes: fps = {}, pos_msec = {}, pos_frames = {}, count = {}'
              .format(fps, pos_msec, pos_frames, count))

        cap.open(path)
        # Make images
        image_pathes = []
        while(cap.isOpened()):
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frames)

            frame_id = int(round(cap.get(1)))
            ret, frame = cap.read()

            path_img = os.path.dirname(os.path.abspath(path)) + "/images/%s_frame%d.jpg" % \
                       (os.path.basename(path), frame_id)
            cv2.imwrite(path_img, frame)
            print(path_img)
            image_pathes.append(path_img)

            pos_frames = pos_frames + iter_frames
            if pos_frames > count:
                break.

        cap.release()
        cv2.destroyAllWindows()

        # Make async_detect
        self.async_detect_pathes(image_pathes)



    @util.async
    def async_detect_pathes(self, pathes):
        """Async detections."""
        self.log.log('Request Total: Detecting')
        self.result.SetLabelText('Detecting ...')
        self.rsizer.Layout()
        self.vhsizer.Layout()
        self.max_faces = 0
        try:
            for path in pathes:
                self.async_detect(path)
                time.sleep(3.1)
        except util.CF.CognitiveFaceException as exp:
            self.log.log('Response: {}. {}'.format(exp.code, exp.msg))

        self.btn.Enable()
        self.rsizer.Layout()
        self.vhsizer.Layout()


    @util.async
    def async_detect(self, path):
        """Async detection."""
        self.log.log('Request: Detecting {}'.format(path))

        try:
            attributes = (
                'emotion')
            res = util.CF.face.detect(path, False, False, attributes)
            self.plot.SetItems(res)
            self.max_faces = max(len(res), self.max_faces)
            text = '{} face(s) has been detected.'.format(
                self.max_faces)
            self.result.SetLabelText(text)
        except util.CF.CognitiveFaceException as exp:
            self.log.log('Response: {}. {}'.format(exp.code, exp.msg))

        self.rsizer.Layout()
        self.vhsizer.Layout()
