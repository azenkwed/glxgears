#!/usr/bin/env python
##########################################################################
# 
# Copyright 2008 Tungsten Graphics, Inc., Cedar Park, Texas.
# All Rights Reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sub license, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice (including the
# next paragraph) shall be included in all copies or substantial portions
# of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.
# IN NO EVENT SHALL TUNGSTEN GRAPHICS AND/OR ITS SUPPLIERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
##########################################################################


import os.path
import sys
import struct
import Image # http://www.pythonware.com/products/pil/

PIPE_FORMAT_LAYOUT_RGBAZS   = 0
PIPE_FORMAT_LAYOUT_YCBCR    = 1
PIPE_FORMAT_LAYOUT_DXT      = 2
PIPE_FORMAT_LAYOUT_MIXED    = 3

PIPE_FORMAT_COMP_R    = 0
PIPE_FORMAT_COMP_G    = 1
PIPE_FORMAT_COMP_B    = 2
PIPE_FORMAT_COMP_A    = 3
PIPE_FORMAT_COMP_0    = 4
PIPE_FORMAT_COMP_1    = 5
PIPE_FORMAT_COMP_Z    = 6
PIPE_FORMAT_COMP_S    = 7

PIPE_FORMAT_TYPE_UNKNOWN = 0
PIPE_FORMAT_TYPE_FLOAT   = 1
PIPE_FORMAT_TYPE_UNORM   = 2
PIPE_FORMAT_TYPE_SNORM   = 3
PIPE_FORMAT_TYPE_USCALED = 4
PIPE_FORMAT_TYPE_SSCALED = 5
PIPE_FORMAT_TYPE_SRGB    = 6
PIPE_FORMAT_TYPE_FIXED   = 7

def _PIPE_FORMAT_RGBAZS( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, EXP2, TYPE ):
   return ((PIPE_FORMAT_LAYOUT_RGBAZS << 0) |\
   ((SWZ) << 2) |\
   ((SIZEX) << 14) |\
   ((SIZEY) << 17) |\
   ((SIZEZ) << 20) |\
   ((SIZEW) << 23) |\
   ((EXP2) << 26) |\
   ((TYPE) << 29) )

def _PIPE_FORMAT_SWZ( SWZX, SWZY, SWZZ, SWZW ):
	return (((SWZX) << 0) | ((SWZY) << 3) | ((SWZZ) << 6) | ((SWZW) << 9))

def _PIPE_FORMAT_RGBAZS_1( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, TYPE ):
	return _PIPE_FORMAT_RGBAZS( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, 0, TYPE )

def _PIPE_FORMAT_RGBAZS_2( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, TYPE ):
    _PIPE_FORMAT_RGBAZS( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, 1, TYPE )

def _PIPE_FORMAT_RGBAZS_8( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, TYPE ):
	return _PIPE_FORMAT_RGBAZS( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, 3, TYPE )

def _PIPE_FORMAT_RGBAZS_64( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, TYPE ):
	return _PIPE_FORMAT_RGBAZS( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, 6, TYPE )

def _PIPE_FORMAT_MIXED( SWZ, SIZEX, SIZEY, SIZEZ, SIZEW, SIGNX, SIGNY, SIGNZ, SIGNW, NORMALIZED, SCALE8 ):
    return ((PIPE_FORMAT_LAYOUT_MIXED << 0) |\
    ((SWZ) << 2) |\
    ((SIZEX) << 14) |\
    ((SIZEY) << 17) |\
    ((SIZEZ) << 20) |\
    ((SIZEW) << 23) |\
    ((SIGNX) << 26) |\
    ((SIGNY) << 27) |\
    ((SIGNZ) << 28) |\
    ((SIGNW) << 29) |\
    ((NORMALIZED) << 30) |\
    ((SCALE8) << 31) )


_PIPE_FORMAT_R001 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_1 )
_PIPE_FORMAT_RG01 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_1 )
_PIPE_FORMAT_RGB1 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_B, PIPE_FORMAT_COMP_1 )
_PIPE_FORMAT_RGBA = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_B, PIPE_FORMAT_COMP_A )
_PIPE_FORMAT_ARGB = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_A, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_B )
_PIPE_FORMAT_ABGR = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_A, PIPE_FORMAT_COMP_B, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_R )
_PIPE_FORMAT_BGRA = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_B, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_A )
_PIPE_FORMAT_1RGB = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_1, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_B )
_PIPE_FORMAT_1BGR = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_1, PIPE_FORMAT_COMP_B, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_R )
_PIPE_FORMAT_BGR1 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_B, PIPE_FORMAT_COMP_G, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_1 )
_PIPE_FORMAT_0000 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0 )
_PIPE_FORMAT_000R = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_R )
_PIPE_FORMAT_RRR1 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_1 )
_PIPE_FORMAT_RRRR = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_R )
_PIPE_FORMAT_RRRG = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_R, PIPE_FORMAT_COMP_G )
_PIPE_FORMAT_Z000 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_Z, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0 )
_PIPE_FORMAT_0Z00 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_Z, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0 )
_PIPE_FORMAT_SZ00 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_S, PIPE_FORMAT_COMP_Z, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0 )
_PIPE_FORMAT_ZS00 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_Z, PIPE_FORMAT_COMP_S, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0 )
_PIPE_FORMAT_S000 = _PIPE_FORMAT_SWZ( PIPE_FORMAT_COMP_S, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0, PIPE_FORMAT_COMP_0 )

def _PIPE_FORMAT_YCBCR( REV ):
   return ((PIPE_FORMAT_LAYOUT_YCBCR << 0) |\
   ((REV) << 2) )

def _PIPE_FORMAT_DXT( LEVEL, RSIZE, GSIZE, BSIZE, ASIZE ):
    return ((PIPE_FORMAT_LAYOUT_DXT << 0) | \
    ((LEVEL) << 2) | \
    ((RSIZE) << 5) | \
    ((GSIZE) << 8) | \
    ((BSIZE) << 11) | \
    ((ASIZE) << 14) )

PIPE_FORMAT_NONE                  = _PIPE_FORMAT_RGBAZS_1 ( _PIPE_FORMAT_0000, 0, 0, 0, 0, PIPE_FORMAT_TYPE_UNKNOWN )
PIPE_FORMAT_A8R8G8B8_UNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_ARGB, 1, 1, 1, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_X8R8G8B8_UNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_1RGB, 1, 1, 1, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_B8G8R8A8_UNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_BGRA, 1, 1, 1, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_B8G8R8X8_UNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_BGR1, 1, 1, 1, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_A1R5G5B5_UNORM        = _PIPE_FORMAT_RGBAZS_1 ( _PIPE_FORMAT_ARGB, 1, 5, 5, 5, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_A4R4G4B4_UNORM        = _PIPE_FORMAT_RGBAZS_1 ( _PIPE_FORMAT_ARGB, 4, 4, 4, 4, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R5G6B5_UNORM          = _PIPE_FORMAT_RGBAZS_1 ( _PIPE_FORMAT_RGB1, 5, 6, 5, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_A2B10G10R10_UNORM     = _PIPE_FORMAT_RGBAZS_2 ( _PIPE_FORMAT_ABGR, 1, 5, 5, 5, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_L8_UNORM              = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RRR1, 1, 1, 1, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_A8_UNORM              = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_000R, 0, 0, 0, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_I8_UNORM              = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RRRR, 1, 1, 1, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_A8L8_UNORM            = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RRRG, 1, 1, 1, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_L16_UNORM             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RRR1, 2, 2, 2, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_YCBCR                 = _PIPE_FORMAT_YCBCR( 0 )
PIPE_FORMAT_YCBCR_REV             = _PIPE_FORMAT_YCBCR( 1 )
PIPE_FORMAT_Z16_UNORM             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_Z000, 2, 0, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_Z32_UNORM             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_Z000, 4, 0, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_Z32_FLOAT             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_Z000, 4, 0, 0, 0, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_S8Z24_UNORM           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_SZ00, 1, 3, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_Z24S8_UNORM           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_ZS00, 3, 1, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_X8Z24_UNORM           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_0Z00, 1, 3, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_Z24X8_UNORM           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_Z000, 3, 1, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_S8_UNORM              = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_S000, 1, 0, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R64_FLOAT             = _PIPE_FORMAT_RGBAZS_64( _PIPE_FORMAT_R001, 1, 0, 0, 0, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_R64G64_FLOAT          = _PIPE_FORMAT_RGBAZS_64( _PIPE_FORMAT_RG01, 1, 1, 0, 0, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_R64G64B64_FLOAT       = _PIPE_FORMAT_RGBAZS_64( _PIPE_FORMAT_RGB1, 1, 1, 1, 0, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_R64G64B64A64_FLOAT    = _PIPE_FORMAT_RGBAZS_64( _PIPE_FORMAT_RGBA, 1, 1, 1, 1, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_R32_FLOAT             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 4, 0, 0, 0, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_R32G32_FLOAT          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 4, 4, 0, 0, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_R32G32B32_FLOAT       = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 4, 4, 4, 0, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_R32G32B32A32_FLOAT    = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 4, 4, 4, 4, PIPE_FORMAT_TYPE_FLOAT )
PIPE_FORMAT_R32_UNORM             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 4, 0, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R32G32_UNORM          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 4, 4, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R32G32B32_UNORM       = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 4, 4, 4, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R32G32B32A32_UNORM    = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 4, 4, 4, 4, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R32_USCALED           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 4, 0, 0, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R32G32_USCALED        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 4, 4, 0, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R32G32B32_USCALED     = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 4, 4, 4, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R32G32B32A32_USCALED  = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 4, 4, 4, 4, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R32_SNORM             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 4, 0, 0, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R32G32_SNORM          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 4, 4, 0, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R32G32B32_SNORM       = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 4, 4, 4, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R32G32B32A32_SNORM    = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 4, 4, 4, 4, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R32_SSCALED           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 4, 0, 0, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R32G32_SSCALED        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 4, 4, 0, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R32G32B32_SSCALED     = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 4, 4, 4, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R32G32B32A32_SSCALED  = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 4, 4, 4, 4, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R16_UNORM             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 2, 0, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R16G16_UNORM          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 2, 2, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R16G16B16_UNORM       = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 2, 2, 2, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R16G16B16A16_UNORM    = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 2, 2, 2, 2, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R16_USCALED           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 2, 0, 0, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R16G16_USCALED        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 2, 2, 0, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R16G16B16_USCALED     = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 2, 2, 2, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R16G16B16A16_USCALED  = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 2, 2, 2, 2, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R16_SNORM             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 2, 0, 0, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R16G16_SNORM          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 2, 2, 0, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R16G16B16_SNORM       = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 2, 2, 2, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R16G16B16A16_SNORM    = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 2, 2, 2, 2, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R16_SSCALED           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 2, 0, 0, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R16G16_SSCALED        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 2, 2, 0, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R16G16B16_SSCALED     = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 2, 2, 2, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R16G16B16A16_SSCALED  = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 2, 2, 2, 2, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R8_UNORM              = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 1, 0, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R8G8_UNORM            = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 1, 1, 0, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R8G8B8_UNORM          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 0, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R8G8B8A8_UNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 1, 1, 1, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R8G8B8X8_UNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 1, PIPE_FORMAT_TYPE_UNORM )
PIPE_FORMAT_R8_USCALED            = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 1, 0, 0, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R8G8_USCALED          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 1, 1, 0, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R8G8B8_USCALED        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 0, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R8G8B8A8_USCALED      = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 1, 1, 1, 1, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R8G8B8X8_USCALED      = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 1, PIPE_FORMAT_TYPE_USCALED )
PIPE_FORMAT_R8_SNORM              = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 1, 0, 0, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R8G8_SNORM            = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 1, 1, 0, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R8G8B8_SNORM          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R8G8B8A8_SNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R8G8B8X8_SNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_B6G5R5_SNORM          = _PIPE_FORMAT_RGBAZS_1 ( _PIPE_FORMAT_BGR1, 6, 5, 5, 0, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_A8B8G8R8_SNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_BGRA, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_X8B8G8R8_SNORM        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SNORM )
PIPE_FORMAT_R8_SSCALED            = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 1, 0, 0, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R8G8_SSCALED          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 1, 1, 0, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R8G8B8_SSCALED        = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 0, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R8G8B8A8_SSCALED      = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R8G8B8X8_SSCALED      = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SSCALED )
PIPE_FORMAT_R32_FIXED             = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_R001, 4, 0, 0, 0, PIPE_FORMAT_TYPE_FIXED )
PIPE_FORMAT_R32G32_FIXED          = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RG01, 4, 4, 0, 0, PIPE_FORMAT_TYPE_FIXED )
PIPE_FORMAT_R32G32B32_FIXED       = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 4, 4, 4, 0, PIPE_FORMAT_TYPE_FIXED )
PIPE_FORMAT_R32G32B32A32_FIXED    = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 4, 4, 4, 4, PIPE_FORMAT_TYPE_FIXED )
PIPE_FORMAT_L8_SRGB               = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RRR1, 1, 1, 1, 0, PIPE_FORMAT_TYPE_SRGB )
PIPE_FORMAT_A8_L8_SRGB            = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RRRG, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SRGB )
PIPE_FORMAT_R8G8B8_SRGB           = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 0, PIPE_FORMAT_TYPE_SRGB )
PIPE_FORMAT_R8G8B8A8_SRGB         = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGBA, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SRGB )
PIPE_FORMAT_R8G8B8X8_SRGB         = _PIPE_FORMAT_RGBAZS_8 ( _PIPE_FORMAT_RGB1, 1, 1, 1, 1, PIPE_FORMAT_TYPE_SRGB )
PIPE_FORMAT_X8UB8UG8SR8S_NORM     = _PIPE_FORMAT_MIXED( _PIPE_FORMAT_1BGR, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1 )
PIPE_FORMAT_B6UG5SR5S_NORM        = _PIPE_FORMAT_MIXED( _PIPE_FORMAT_BGR1, 6, 5, 5, 0, 0, 1, 1, 0, 1, 0 )
PIPE_FORMAT_DXT1_RGB              = _PIPE_FORMAT_DXT( 1, 8, 8, 8, 0 )
PIPE_FORMAT_DXT1_RGBA             = _PIPE_FORMAT_DXT( 1, 8, 8, 8, 8 )
PIPE_FORMAT_DXT3_RGBA             = _PIPE_FORMAT_DXT( 3, 8, 8, 8, 8 )
PIPE_FORMAT_DXT5_RGBA             = _PIPE_FORMAT_DXT( 5, 8, 8, 8, 8 )


formats = {}
for name, value in globals().items():
    if name.startswith("PIPE_FORMAT_") and isinstance(value, int):
        formats[value] = name


def clip(g):
	return min(max(g, 0), 255)


def yuv2rgb(y, u, v):
	C = y - 16
	D = u - 128
	E = v - 128

	r = clip(( 298 * C           + 409 * E + 128) >> 8)
	g = clip(( 298 * C - 100 * D - 208 * E + 128) >> 8)
	b = clip(( 298 * C + 516 * D           + 128) >> 8)
	
	return r, g, b

	
def translate_r5g6b5(data):
	value, = struct.unpack_from("H", data)
	r = ((value >> 11) & 0x1f)*0xff/0x1f
	g = ((value >>  5) & 0x3f)*0xff/0x3f
	b = ((value >>  0) & 0x1f)*0xff/0x1f
	a = 255
	return [[(r, g, b, a)]]


def translate_r8g8b8a8(data):
	r, g, b, a = struct.unpack_from("BBBB", data)
	return [[(r, g, b, a)]]


def translate_ycbcr(data):
	y1, u, y2, v = struct.unpack_from("BBBB", data)
	r1, g1, b1 = yuv2rgb(y1, u, v)
	r2, g2, b2 = yuv2rgb(y1, u, v)
	return [[(r1, g1, b1, 255), (r2, g2, b2, 255)]]

def translate_ycbcr_rev(data):
    v, y2, u, y1 = struct.unpack_from("BBBB", data)
    r1, g1, b1 = yuv2rgb(y1, u, v)
    r2, g2, b2 = yuv2rgb(y1, u, v)
    return [[(r1, g1, b1, 255), (r2, g2, b2, 255)]]


translate = {
	PIPE_FORMAT_A8R8G8B8_UNORM: (4, 1, 1, translate_r8g8b8a8),
	PIPE_FORMAT_X8R8G8B8_UNORM: (4, 1, 1, translate_r8g8b8a8),
	PIPE_FORMAT_B8G8R8A8_UNORM: (4, 1, 1, translate_r8g8b8a8),
	PIPE_FORMAT_B8G8R8X8_UNORM: (4, 1, 1, translate_r8g8b8a8),
	PIPE_FORMAT_A8B8G8R8_SNORM: (4, 1, 1, translate_r8g8b8a8),
	PIPE_FORMAT_R5G6B5_UNORM: (2, 1, 1, translate_r5g6b5),
	PIPE_FORMAT_YCBCR: (4, 2, 1, translate_ycbcr),
	PIPE_FORMAT_YCBCR_REV: (4, 2, 1, translate_ycbcr_rev),
}

def read_header(infile):
	header_fmt = "IIII"
	header = infile.read(struct.calcsize(header_fmt))
	return struct.unpack_from(header_fmt, header)

def process(infilename, outfilename):
	sys.stderr.write("%s -> %s\n" % (infilename, outfilename))
	infile = open(infilename, "rb")
	format, cpp, width, height = read_header(infile)
	sys.stderr.write("  %ux%ux%ubpp %s\n" % (width, height, cpp*8, formats[format]))
	outimage = Image.new(
	mode='RGB',
	size=(width, height),
	color=(0,0,0))
	outpixels = outimage.load()
	try:
		bsize, bwidth, bheight, translate_func = translate[format]
	except KeyError:
		sys.stderr.write('error: unsupported format %s\n' % formats[format])
		return
	for y in range(0, height, bheight):
		for x in range(0, width, bwidth):
			indata = infile.read(bsize)
			outdata = translate_func(indata)
			for j in range(bheight):
				for i in range(bwidth):
					r, g, b, a = outdata[j][i]
					outpixels[x+i, y+j] = r, g, b
	outimage.save(outfilename, "PNG")


def main():
	if sys.platform == 'win32':
		# wildcard expansion
		from glob import glob
		args = []
		for arg in sys.argv[1:]:
			args.extend(glob(arg))
	else:
		args = sys.argv[1:]
	for infilename in args:
		root, ext = os.path.splitext(infilename)
		outfilename = root + ".png"
		process(infilename, outfilename)


if __name__ == '__main__':
	main()
