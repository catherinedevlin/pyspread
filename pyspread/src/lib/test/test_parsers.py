#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for parsers.py"""

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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

from sys import path, modules
path.insert(0, "..") 
path.insert(0, "../..") 

import types

import gmpy
import numpy

import wx

app= wx.App()

from pyspread.src.lib.testlib import params, pytest_generate_tests

from pyspread.src.lib.parsers import get_font_from_data, get_pen_from_data

param_font = [ \
    {"fontdata": "Sans 13", "face": "Sans", "size": 13},
    {"fontdata": "Serif 43", "face": "Serif", "size": 43},
]

@params(param_font)
def test_get_font_from_data(fontdata, face, size):
    """Unit test for get_font_from_data"""
    
    font = get_font_from_data(fontdata)
    
    assert font.GetFaceName() == face
    assert font.GetPointSize() == size

param_pen = [ \
    {"pendata": [wx.RED.GetRGB(), 4], "width": 4, "color": wx.Colour(255, 0, 0, 255)},
    {"pendata": [wx.BLUE.GetRGB(), 1], "width": 1, "color": wx.Colour(0, 0, 255, 255)},
    {"pendata": [wx.GREEN.GetRGB(), 0], "width": 0, "color": wx.Colour(0, 255, 0, 255)},
]

@params(param_pen)
def test_get_pen_from_data(pendata, width, color):
    """Unit test for get_pen_from_data"""
    
    pen = get_pen_from_data(pendata)
    
    assert pen.GetColour() == color
    assert pen.GetWidth() == width

