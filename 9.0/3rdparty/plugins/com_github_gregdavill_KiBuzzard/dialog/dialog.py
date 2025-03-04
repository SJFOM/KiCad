"""Subclass of dialog_base, which is generated by wxFormBuilder."""
from logging import exception
import os
import re
import copy

import wx
import base64
import json

from . import dialog_text_base

def ParseFloat(InputString, DefaultValue=0.001):
    value = DefaultValue
    if InputString != "":
        try:
            value = float(InputString)
        except ValueError:
            print("Value not valid")
    return value

def ParseInt(InputString, DefaultValue=0):
    value = DefaultValue
    if InputString != "":
        try:
            value = int(InputString)
        except ValueError:
            print("Value not valid")
    return value

class Dialog(dialog_text_base.DIALOG_TEXT_BASE):

    config_defaults = {
        'MultiLineText': 'KiBuzzard',
        'HeightCtrl': '2',
        'FontComboBox': 'UbuntuMono-B',
        'LayerComboBox': 'F.Cu',
        'CapLeftChoice': '[',
        'CapRightChoice': ']',
        'PaddingTopCtrl': '3.75',
        'PaddingLeftCtrl': '3.75',
        'PaddingRightCtrl': '3.75',
        'PaddingBottomCtrl': '3.75',
        'LineSpacingCtrl': '1.5',
        'WidthCtrl': None,
        'AlignmentChoice': 'Center',
        'advancedCheckbox': False,
        'inlineFormatTextbox': False,
        'lineoverStyleChoice': 'rounded',
        'lineoverThicknessCtrl': '1'
    }

    def __init__(self, parent, config, buzzard, func):
        dialog_text_base.DIALOG_TEXT_BASE.__init__(self, parent)
        
        typeface_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'buzzard', 'typeface')
        for entry in os.listdir(typeface_path):
            entry_path = os.path.join(typeface_path, entry)
            
            if not (entry_path.endswith('.ttf') or entry_path.endswith('.otf')):
                continue
            
            self.m_FontComboBox.Append(os.path.splitext(entry)[0])
        
        self.m_FontComboBox.SetSelection(0)

        #for fnt in buzzard.SystemFonts:
        #    self.m_FontComboBox.Append(fnt)

        self._layer_choices = layer_choices = ["F.Cu", "F.Paste", "F.SilkS", "F.Mask", "F.Cu/F.Mask"]
        self.m_LayerComboBox.AppendItems(layer_choices)
        self.m_LayerComboBox.SetSelection(0)
        self.m_HeightUnits.SetLabel("mm")
        self.m_WidthUnits.SetLabel("mm")
        self.m_lineoverThicknessUnits.SetLabel("")        

        best_size = self.BestSize
        # hack for some gtk themes that incorrectly calculate best size
        best_size.IncBy(dx=0, dy=30)
        self.SetClientSize(best_size)
        self.config_file = config
        self.func = func

        self.error = None
        
        self.label_params = {}
        self.updateFootprint = None

        self.loadConfig()

        if self.m_advancedCheckbox.IsChecked():
            self.m_lineoverPanel.Show()
            self.m_spCharPanel.Show()
            self.m_AdvancedDivider.Show()
        else:
            self.m_lineoverPanel.Hide()
            self.m_spCharPanel.Hide()
            self.m_AdvancedDivider.Hide()

        self.buzzard = buzzard

        self.polys = []
        
        self.m_PreviewPanel.Bind(wx.EVT_PAINT, self.OnPaint)

        self.Bind(wx.EVT_TIMER, self.labelEditOnText)
        self.m_sdbSizerCancel.Bind(wx.EVT_BUTTON, self.Cancel)

        self.timer = wx.Timer(self, 0)
        self.timer.Start(milliseconds=250, oneShot=True)

        self.m_MultiLineText.SelectAll()

    def Cancel(self, e):
        self.timer.Stop()

        self.saveConfig()
        e.Skip()


    def loadConfig(self):
        # check if we have a footprint we can load value from first
        try:
            import pcbnew
            b = pcbnew.GetBoard()
            selected_footprints = [f for f in b.Footprints() if f.IsSelected()]
            if len(selected_footprints) == 1:
                f = selected_footprints[0]
                if 'kibuzzard' in f.GetReference():
                    param_str = f.GetKeywords()
                    if param_str.startswith("kb_params="):
                        encoded_str = param_str[10:]
                        json_str = base64.b64decode(encoded_str).decode('utf-8')
                        params = json.loads(json_str)
                        self.LoadSettings(params)
                        self.updateFootprint = f

                        return
                
        except:
            import traceback
            wx.LogError(traceback.format_exc())
            return

        # else load up last sessions config
        params = self.config_defaults
        try:
            with open(self.config_file, 'r') as cf:
                json_params = json.load(cf)
            params.update(json_params)

            # Clear text between uses
            params['MultiLineText'] = '' 
        except Exception as e:
            # Don't throw exception if we can't load previous config
            pass

        self.LoadSettings(params)
        
    def saveConfig(self):
        try:
            with open(self.config_file, 'w') as cf:
                json.dump(self.CurrentSettings(), cf, indent=2)
        except Exception as e:
            # Don't throw exception if we can't save previous config
            pass
            
    def LoadSettings(self, params):
        for key,value in params.items():
            if key not in self.config_defaults.keys():
                continue
            if value is None:
                continue

            try:
                obj = getattr(self, "m_{}".format(key))
                if hasattr(obj, "SetValue"):
                    obj.SetValue(value)
                elif hasattr(obj, "SetStringSelection"):
                    obj.SetStringSelection(value)
                else:
                    raise Exception("Invalid item")  

            except Exception as e:
                pass
        return params

    def CurrentSettings(self):
        params = {}

        for item in self.config_defaults.keys():
            obj = getattr(self, "m_{}".format(item))
            if hasattr(obj, "GetValue"):
                params.update({item: obj.GetValue()})
            elif hasattr(obj, "GetStringSelection"):
                params.update({item: obj.GetStringSelection()})
            else:
                raise Exception("Invalid item")    
        return params


    def labelEditOnText( self, event ):
        while self.label_params != self.CurrentSettings():
            self.label_params.update(self.CurrentSettings())
            self.ReGeneratePreview()
        self.timer.Start(milliseconds=250, oneShot=True)
        event.Skip()
    
    def OnCharHook( self, event ):
        if (event.GetKeyCode() == wx.WXK_RETURN) & (event.ShiftDown() | event.ControlDown()):
            self.OnOkClick(event)
            wx.PostEvent(self, wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_OK))
            return
        event.Skip()

    def ReGenerateFlag(self, e):
        self.label_params = {}

    def ReGeneratePreview(self, e=None):
        self.polys = []
        
        self.buzzard.fontName = self.m_FontComboBox.GetValue()
        self.buzzard.lineSpacing = ParseFloat(self.m_LineSpacingCtrl.GetValue()) * 10

        requestedHeight = ParseFloat(self.m_HeightCtrl.GetValue())
        requestedWidth = ParseFloat(self.m_WidthCtrl.GetValue())

        # When editing the text height field. If the value is null, avoid a divide by 0 exception
        if requestedHeight == 0:
            return
        
        self.buzzard.padding.top = ParseFloat(self.m_PaddingTopCtrl.GetValue())
        self.buzzard.padding.left = ParseFloat(self.m_PaddingLeftCtrl.GetValue())
        self.buzzard.padding.right = ParseFloat(self.m_PaddingRightCtrl.GetValue())
        self.buzzard.padding.bottom = ParseFloat(self.m_PaddingBottomCtrl.GetValue())
        
        #this was originally in buzzard.py but have moved it here in order to accomodate
        #realtime updates of padding
        for attr in ['left', 'right', 'top', 'bottom']:
            if getattr(self.buzzard.padding,attr) <= 0: setattr(self.buzzard.padding, attr, 0.001) 
 
        self.buzzard.layer = self.m_LayerComboBox.GetValue()

        self.buzzard.alignment = self.m_AlignmentChoice.GetStringSelection()
        # KiBuzzard aims to size uppercase letters at the height requested.
        # Font size include space below the baseline and above the "caps height" for larger glyphs like `[]`
        # All fonts are slightly different. So we render a 'H' to determine the scale of the selected font.
        text_height = self.buzzard.text_height()

        # Scale font and apply DPI
        self.buzzard.scaleFactor = (requestedHeight/text_height) * (96/25.4)
        self.buzzard.width = ParseFloat(self.m_WidthCtrl.GetValue(), 0.0) * (96/25.4) * 1/self.buzzard.scaleFactor

        styles = {'':'', '(':'round', '[':'square', '<':'pointer', '/':'fslash', '\\':'bslash', '>':'flagtail'}
        self.buzzard.leftCap = styles[self.m_CapLeftChoice.GetStringSelection()]

        styles = {'':'', ')':'round', ']':'square', '>':'pointer', '/':'fslash', '\\':'bslash', '<':'flagtail'}
        self.buzzard.rightCap = styles[self.m_CapRightChoice.GetStringSelection()]

        if self.m_inlineFormatTextbox.IsChecked():
            self.buzzard.inlineFormat = True
        else:
            self.buzzard.inlineFormat = False

        self.buzzard.lineOverThickness = ParseInt(self.m_lineoverThicknessCtrl.GetValue(), DefaultValue=1) 

        self.buzzard.lineOverStyle = self.m_lineoverStyleChoice.GetString(self.m_lineoverStyleChoice.GetSelection())

        
        if len(self.m_MultiLineText.GetValue()) == 0:
            self.RePaint()
            return
        if len(self.m_MultiLineText.GetValue()) > 128:
            self.error = "Text input loo long"
            return
        
        try:
            self.polys = self.buzzard.generate(self.m_MultiLineText.GetValue())
        except:
            import traceback
            traceback.print_exc()

        self.RePaint()        

    def RePaint(self, e=None):
        self.Layout()
        self.Refresh()
        self.Update()


    def OnPaint(self, e):
        dc = wx.PaintDC(self.m_PreviewPanel)

        if self.error is not None:
            font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL)
            dc.SetFont(font)
            dc.SetTextForeground('#FF0000')

            rect = wx.Rect(0,0, self.m_PreviewPanel.GetSize().GetWidth(),self.m_PreviewPanel.GetSize().GetHeight())
            dc.DrawLabel(self.error, rect, wx.ALIGN_LEFT)
        else:
            dc.SetPen(wx.Pen('#000000', width=1))

            size_x, size_y = self.m_PreviewPanel.GetSize()

            dc.SetDeviceOrigin(int(size_x/2), int(size_y/2))
            dc.SetBrush(wx.Brush('#000000'))

            if len(self.polys):
                # Create copy of poly list for scaling preview
                polys = copy.deepcopy(self.polys)


                # TODO use matrix for scaling
                # TODO use bbox to determine scaling
                min_x = 0
                max_x = 0
                for i in range(len(self.polys)):
                    for j in range(len(self.polys[i])):
                        min_x = min(self.polys[i][j].x, min_x)
                        max_x = max(self.polys[i][j].x, max_x)

                min_y = 0
                max_y = 0
                for i in range(len(self.polys)):
                    for j in range(len(self.polys[i])):
                        min_y = min(self.polys[i][j].y, min_y)
                        max_y = max(self.polys[i][j].y, max_y)

                scale = (size_x * 0.95) / (max_x - min_x)

                scale = min(scale, (size_y * 0.95) / (max_y - min_y))

                #scale = min(15.0, scale)
                for i in range(len(polys)):
                    for j in range(len(polys[i])):
                        polys[i][j] = (scale*polys[i][j].x,scale*polys[i][j].y)

                dc.DrawPolygonList(polys)


    def OnOkClick(self, event):
        self.timer.Stop()
        self.saveConfig()
        
        self.func(self, self.buzzard)

    def advancedModeChange(self, event):
        if self.m_advancedCheckbox.IsChecked():
            self.m_lineoverPanel.Show()
            self.m_spCharPanel.Show()
            self.m_AdvancedDivider.Show()
        else:
            self.m_lineoverPanel.Hide()
            self.m_spCharPanel.Hide()
            self.m_AdvancedDivider.Hide()
            self.m_inlineFormatTextbox.SetValue(False)
            self.buzzard.inlineFormat = False
            self.ReGeneratePreview()

        self.RePaint()

    def inlineFormatChange(self, event):
        self.ReGeneratePreview()

    def thicknessCtrlChange(self, event):
        self.ReGeneratePreview()

    def lineoverStyleChange(self, event):
        self.ReGeneratePreview()

    def addCharOhm(self, event):
        self.m_MultiLineText.SetValue(self.m_MultiLineText.GetValue()+"Ω")

    def addCharMu(self, event):
        self.m_MultiLineText.SetValue(self.m_MultiLineText.GetValue()+"µ")

    def addCharSup2(self, event):
        self.m_MultiLineText.SetValue(self.m_MultiLineText.GetValue()+"²")

    def addCharDegree(self, event):
        self.m_MultiLineText.SetValue(self.m_MultiLineText.GetValue()+"°")

    def addCharNumero(self, event):
        self.m_MultiLineText.SetValue(self.m_MultiLineText.GetValue()+"№")