#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6 on Sun May 25 23:31:23 2008

# Copyright 2008 Martin Manns
# Distributed under the terms of the GNU General Public License
# generated by wxGlade 0.6 on Mon Mar 17 23:22:49 2008

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
_widgets
========

Provides:
---------
  1. IndexGrid: Grid that supports indexing and __len__
  2. MainGrid: Main grid
  2. CollapsiblePane: Collapsible pane with basic toggle mechanism
  3. MacroEditPanel: Collapsible label, parameter entry area and editor
  4. SortedListCtrl: ListCtrl with items sorted in first column
  5. PenStyleComboBox: ComboBox for border pen style selection
  6. FontChoiceCombobox: ComboBox for font selection
  7. BitmapToggleButton: Button that toggles through a list of bitmaps

"""

import keyword

import wx
import wx.grid
import wx.combo
import wx.stc  as  stc
import wx.lib.mixins.listctrl  as  listmix

from _pyspread.config import faces, text_styles, fold_symbol_style

class CollapsiblePane(wx.CollapsiblePane):
    """Collapsible pane with basic toggle mechanism
    
    Parameters:
    -----------
    panename: string
    \tLabel for the collapsible pane
    
    """
    
    def __init__(self, *args, **kwds):
        self.label_show = "Show "
        self.label_hide = "Hide "
        panename = kwds.pop('panename')
        self.__dict__['label'] = panename
        wx.CollapsiblePane.__init__(self, *args, **kwds)
        self.SetLabel(self.label_show + panename)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.restore_pane, self)
        
    def OnToggle(self, event):
        """"Toggle event handler"""
        
        self.Collapse(self.IsExpanded())
        self.restore_pane()
        
    def restore_pane(self, event=None):
        """Restores the layout of the content and changes teh labels"""
        self.GetParent().Layout()
        # and also change the labels
        if self.IsExpanded():
            self.SetLabel(self.label_hide + self.__dict__['label'])
        else:
            self.SetLabel(self.label_show + self.__dict__['label'])

# end of class CollapsiblePane

class SortedListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    """ListCtrl with items sorted in first column"""
    
    def __init__(self, parent, wxid, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, wxid, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

# end of class SortedListCtrl

class PythonSTC(stc.StyledTextCtrl):
    """Editor that highlights Python source code.
    
    Stolen from the wxPython demo.py
    """
    fold_symbols = 2
    
    def __init__(self, *args, **kwargs):
        stc.StyledTextCtrl.__init__(self, *args, **kwargs)

        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, " ".join(keyword.kwlist))

        self.SetProperty("fold", "1")
        self.SetProperty("tab.timmy.whinge.level", "1")
        self.SetMargins(0, 0)

        self.SetViewWhiteSpace(False)
        self.SetUseAntiAliasing(True)
        
        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(78)

        # Setup a margin to hold fold markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)
        
        # Import symbol style from config file
        for marker in fold_symbol_style:
            self.MarkerDefine(*marker)
        
        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        
        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, \
                          "face:%(helv)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default
        
        # Import text style specs from config file
        for spec in text_styles:
            self.StyleSetSpec(*spec)
        
        self.SetCaretForeground("BLUE")
        
        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 30)


    def OnUpdateUI(self, evt):
        """Syntax highlighting while editing"""
        
        # check for matching braces
        brace_at_caret = -1
        brace_opposite = -1
        char_before = None
        caret_pos = self.GetCurrentPos()

        if caret_pos > 0:
            char_before = self.GetCharAt(caret_pos - 1)
            style_before = self.GetStyleAt(caret_pos - 1)

        # check before
        if char_before and chr(char_before) in "[]{}()" and \
           style_before == stc.STC_P_OPERATOR:
            brace_at_caret = caret_pos - 1

        # check after
        if brace_at_caret < 0:
            char_after = self.GetCharAt(caret_pos)
            style_after = self.GetStyleAt(caret_pos)

            if char_after and chr(char_after) in "[]{}()" and \
               style_after == stc.STC_P_OPERATOR:
                brace_at_caret = caret_pos

        if brace_at_caret >= 0:
            brace_opposite = self.BraceMatch(brace_at_caret)

        if brace_at_caret != -1  and brace_opposite == -1:
            self.BraceBadLight(brace_at_caret)
        else:
            self.BraceHighlight(brace_at_caret, brace_opposite)

    def OnMarginClick(self, evt):
        """When clicked, old and unfold as needed"""
        
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.fold_all()
            else:
                line_clicked = self.LineFromPosition(evt.GetPosition())

                if self.GetFoldLevel(line_clicked) & \
                   stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(line_clicked, True)
                        self.expand(line_clicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(line_clicked):
                            self.SetFoldExpanded(line_clicked, False)
                            self.expand(line_clicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(line_clicked, True)
                            self.expand(line_clicked, True, True, 100)
                    else:
                        self.ToggleFold(line_clicked)
    
    def fold_all(self):
        """Folds/unfolds all levels in the editor"""
        
        line_count = self.GetLineCount()
        expanding = True
        
        # find out if we are folding or unfolding
        for line_num in range(line_count):
            if self.GetFoldLevel(line_num) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(line_num)
                break
        
        line_num = 0
        
        while line_num < line_count:
            level = self.GetFoldLevel(line_num)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:
                
                if expanding:
                    self.SetFoldExpanded(line_num, True)
                    line_num = self.expand(line_num, True)
                    line_num = line_num - 1
                else:
                    last_child = self.GetLastChild(line_num, -1)
                    self.SetFoldExpanded(line_num, False)
                    
                    if last_child > line_num:
                        self.HideLines(line_num+1, last_child)
            
            line_num = line_num + 1
    
    def expand(self, line, do_expand, force=False, vislevels=0, level=-1):
        """Multi-purpose expand method from original STC class"""
        
        lastchild = self.GetLastChild(line, level)
        line += 1
        
        while line <= lastchild:
            if force:
                if vislevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            elif do_expand:
                self.ShowLines(line, line)
            
            if level == -1:
                level = self.GetFoldLevel(line)
            
            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    self.SetFoldExpanded(line, vislevels - 1)
                    line = self.expand(line, do_expand, force, vislevels-1)
                
                else:
                    expandsub = do_expand and self.GetFoldExpanded(line)
                    line = self.expand(line, expandsub, force, vislevels-1)
            else:
                line += 1
        
        return line
        
# end of class PythonSTC


class PenStyleComboBox(wx.combo.OwnerDrawnComboBox):
    """Combo box for choosing line styles for cell borders
    
    Stolen from demo.py
    
    """
    
    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return
        
        r = wx.Rect(*rect)  # make a copy
        r.Deflate(3, 5)
        
        penStyle = wx.SOLID
        if item == 1:
            penStyle = wx.TRANSPARENT
        elif item == 2:
            penStyle = wx.DOT
        elif item == 3:
            penStyle = wx.LONG_DASH
        elif item == 4:
            penStyle = wx.SHORT_DASH
        elif item == 5:
            penStyle = wx.DOT_DASH
        elif item == 6:
            penStyle = wx.BDIAGONAL_HATCH
        elif item == 7:
            penStyle = wx.CROSSDIAG_HATCH
        elif item == 8:
            penStyle = wx.FDIAGONAL_HATCH
        elif item == 9:
            penStyle = wx.CROSS_HATCH
        elif item == 10:
            penStyle = wx.HORIZONTAL_HATCH
        elif item == 11:
            penStyle = wx.VERTICAL_HATCH
            
        pen = wx.Pen(dc.GetTextForeground(), 3, penStyle)
        dc.SetPen(pen)
        
        if flags & wx.combo.ODCB_PAINTING_CONTROL:
            # for painting the control itself
            dc.DrawLine(r.x+5, r.y+r.height/2, 
                        r.x+r.width - 5, r.y+r.height/2)
        
        else:
            # for painting the items in the popup
            dc.DrawText(self.GetString(item),
                        r.x + 3,
                        (r.y + 0) + ((r.height/2) - dc.GetCharHeight())/2)
            dc.DrawLine(r.x+5, r.y+((r.height/4)*3)+1, 
                        r.x+r.width - 5, r.y+((r.height/4)*3)+1)
    
    def OnDrawBackground(self, dc, rect, item, flags):
        """Called for drawing the background area of each item
        
        Overridden from OwnerDrawnComboBox
        
        """
        
        # If the item is selected, or its item # iseven, or we are painting the
        # combo control itself, then use the default rendering.
        if (item & 1 == 0 or flags & (wx.combo.ODCB_PAINTING_CONTROL |
                                      wx.combo.ODCB_PAINTING_SELECTED)):
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc, 
                                                         rect, item, flags)
            return
        
        # Otherwise, draw every other background with different colour.
        bg_color = wx.Colour(240, 240, 250)
        dc.SetBrush(wx.Brush(bg_color))
        dc.SetPen(wx.Pen(bg_color))
        dc.DrawRectangleRect(rect)
    
    def OnMeasureItem(self, item):
        """should return the height needed to display an item in the popup, 
        or -1 for default
        
        Overridden from OwnerDrawnComboBox
        
        """
        
        # Simply demonstrate the ability to have variable-height items
        if item & 1:
            return 36
        else:
            return 24
    
    def OnMeasureItemWidth(self, item):
        """Callback for item width, or -1 for default/undetermined
        
        Overridden from OwnerDrawnComboBox
        
        """
        return -1 # default - will be measured from text width
    
# end of class PenStyleComboBox

class PenWidthComboBox(wx.combo.OwnerDrawnComboBox):
    """Combo box for choosing line width for cell borders"""
    
    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return
        
        r = wx.Rect(*rect)  # make a copy
        r.Deflate(3, 5)
        
        penStyle = wx.SOLID
        if item == 0:
            penStyle = wx.TRANSPARENT
        pen = wx.Pen(dc.GetTextForeground(), item, penStyle)
        pen.SetCap(wx.CAP_BUTT)
        
        dc.SetPen(pen)
        
        if flags & wx.combo.ODCB_PAINTING_CONTROL:
            # for painting the control itself
            dc.DrawLine(r.x+5, r.y+r.height/2, 
                        r.x+r.width - 5, r.y+r.height/2)
        
        else:
            # for painting the items in the popup
            dc.DrawLine(r.x + 5, r.y + r.height / 2, 
                        r.x + r.width - 5, r.y + r.height / 2)
    
    def OnDrawBackground(self, dc, rect, item, flags):
        """Called for drawing the background area of each item
        
        Overridden from OwnerDrawnComboBox
        
        """
        
        # If the item is selected, or its item # iseven, or we are painting the
        # combo control itself, then use the default rendering.
        if (item & 1 == 0 or flags & (wx.combo.ODCB_PAINTING_CONTROL |
                                      wx.combo.ODCB_PAINTING_SELECTED)):
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc, 
                                                         rect, item, flags)
            return
        
        # Otherwise, draw every other background with different colour.
        bg_color = wx.Colour(240, 240, 250)
        dc.SetBrush(wx.Brush(bg_color))
        dc.SetPen(wx.Pen(bg_color))
        dc.DrawRectangleRect(rect)
    
    def OnMeasureItem(self, item):
        """should return the height needed to display an item in the popup, 
        or -1 for default
        
        Overridden from OwnerDrawnComboBox
        
        """
        
        return -1
    
    def OnMeasureItemWidth(self, item):
        """Callback for item width, or -1 for default/undetermined
        
        Overridden from OwnerDrawnComboBox
        
        """
        return -1 # default - will be measured from text width
    
# end of class PenWidthComboBox

class FontChoiceCombobox(wx.combo.OwnerDrawnComboBox):
    """Combo box for choosing fonts"""
    
    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return
        
        __rect = wx.Rect(*rect)  # make a copy
        __rect.Deflate(3, 5)
        
        font_string = self.GetString(item)
        font = wx.Font(faces['size'], wx.DEFAULT, wx.NORMAL, wx.NORMAL, \
                       False, font_string)
        dc.SetFont(font)
        text_width, text_height = dc.GetTextExtent(font_string)
        text_x = __rect.x
        text_y = __rect.y + int((__rect.height - text_height) / 2.0)
        dc.DrawText(font_string, text_x, text_y)
    
    def OnDrawBackground(self, dc, rect, item, flags):
        """Called for drawing the background area of each item
        
        Overridden from OwnerDrawnComboBox
        
        """
        
        # If the item is selected, or its item # iseven, or we are painting the
        # combo control itself, then use the default rendering.
        if (item & 1 == 0 or flags & (wx.combo.ODCB_PAINTING_CONTROL |
                                      wx.combo.ODCB_PAINTING_SELECTED)):
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc, 
                                                         rect, item, flags)
            return
        
        # Otherwise, draw every other background with different colour.
        bg_color = wx.Colour(240, 240, 250)
        dc.SetBrush(wx.Brush(bg_color))
        dc.SetPen(wx.Pen(bg_color))
        dc.DrawRectangleRect(rect)


# end of class FontChoiceCombobox

class BitmapToggleButton(wx.BitmapButton):
    """Toggle button that goes through a list of bitmaps
    
    Parameters
    ----------
    bitmap_list: List of wx.Bitmap
    \tMust be non-empty
    
    """
    
    def __init__(self, parent, bitmap_list):

        assert len(bitmap_list) > 0
        
        self.bitmap_list = []
        for bmp in bitmap_list:
            mask = wx.Mask(bmp, wx.BLUE)
            bmp.SetMask(mask)
            self.bitmap_list.append(bmp)
        
        self.state = 0
        
        super(BitmapToggleButton, self).__init__(parent, -1, 
                    self.bitmap_list[0], style=wx.BORDER_NONE)
        
        # For compatibility with toggle buttons
        setattr(self, "GetToolState", lambda x: self.state)
        
        self.Bind(wx.EVT_BUTTON, self.toggle, self)
    
    def toggle(self, event):
        """Toggles state to next bitmap"""
        
        if self.state < len(self.bitmap_list) - 1:
            self.state += 1
        else:
            self.state = 0
        
        self.SetBitmapLabel(self.bitmap_list[self.state])
        
        try:
            event.Skip()
        except AttributeError:
            pass
        
        """For compatibility with toggle buttons"""
        setattr(self, "GetToolState", lambda x: self.state)
        
# end of class BitmapToggleButton
