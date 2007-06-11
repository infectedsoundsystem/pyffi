# --------------------------------------------------------------------------
# PyTriStrip.PyTriStrip
# A wrapper for TriangleStripifier and NvTriStrip.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, NIF File Format Library and Tools.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the NIF File Format Library and Tools
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

USE_NVTRISTRIP = False

if USE_NVTRISTRIP:
    import NvTriStrip
else:
    from TriangleStripifier import TriangleStripifier
    from TriangleMesh import FaceEdgeMesh

def triangulate(strips):
    """A generator for iterating over the faces in a set of
    strips. Degenerate triangles in strips are discarded.

    >>> triangulate([[1, 0, 1, 2, 3, 4, 5, 6]])
    [[0, 2, 1], [1, 2, 3], [2, 4, 3], [3, 4, 5], [4, 6, 5]]
    """

    triangles = []

    for strip in strips:
        if len(strip) < 3: continue # skip empty strips
        i = strip.__iter__()
        j = False
        t1, t2 = i.next(), i.next()
        for k in xrange(2, len(strip)):
            j = not j
            t0, t1, t2 = t1, t2, i.next()
            if t0 == t1 or t1 == t2 or t2 == t0: continue
            triangles.append([t0, t1, t2] if j else [t0, t2, t1])

    return triangles

def _generateFacesFromTriangles(triangles):
    i = triangles.__iter__()
    while True:
        yield [i.next(), i.next(), i.next()]

def _checkStrips(triangles, strips):
    strips_triangles = triangulate(strips)
    for t0,t1,t2 in triangles:
        if t0 == t1 or t1 == t2 or t2 == t0: continue
        if [t0,t1,t2] not in strips_triangles and [t1,t2,t0] not in strips_triangles and [t2,t0,t1] not in strips_triangles:
            raise ValueError('triangle %s in triangles but not in strips\ntriangles = %s\nstrips = %s'%([t0,t1,t2],triangles,strips))
    for t0,t1,t2 in strips_triangles:
        if t0 == t1 or t1 == t2 or t2 == t0: continue
        if [t0,t1,t2] not in triangles and [t1,t2,t0] not in triangles and [t2,t0,t1] not in triangles:
            raise ValueError('triangle %s in strips but not in triangles\ntriangles = %s\nstrips = %s'%([t0,t1,t2],triangles,strips))

def stripify(triangles, stitchstrips = False):
    """Converts triangles into a list of strips.

    >>> triangles = [[0,1,4],[1,2,4],[2,3,4],[3,0,4]]
    >>> strips = stripify(triangles)
    >>> _checkStrips(triangles, strips)
    >>> triangles = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23]]
    >>> strips = stripify(triangles)
    >>> _checkStrips(triangles, strips)
    >>> triangles = [[0, 1, 2], [0, 1, 2]]
    >>> strips = stripify(triangles)
    >>> _checkStrips(triangles, strips)
    >>> triangles = [[0, 1, 2], [2, 1, 0]]
    >>> strips = stripify(triangles)
    >>> _checkStrips(triangles, strips)
    >>> triangles = [[0, 1, 2], [2, 1, 0], [1, 2, 3]]
    >>> strips = stripify(triangles)
    >>> _checkStrips(triangles, strips) # NvTriStrip gives wrong result
    >>> triangles = [[0, 1, 2], [0, 1, 3]]
    >>> strips = stripify(triangles)
    >>> _checkStrips(triangles, strips) # NvTriStrip gives wrong result
    >>> triangles = [[1, 5, 2], [5, 2, 6], [5, 9, 6], [9, 6, 10], [9, 13, 10], [13, 10, 14], [0, 4, 1], [4, 1, 5], [4, 8, 5], [8, 5, 9], [8, 12, 9], [12, 9, 13], [2, 6, 3], [6, 3, 7], [6, 10, 7], [10, 7, 11], [10, 14, 11], [14, 11, 15]]
    >>> strips = stripify(triangles)
    >>> _checkStrips(triangles, strips) # NvTriStrip gives wrong result
    >>> triangles = [[1, 2, 3], [4, 5, 6], [6, 5, 7], [8, 5, 9], [4, 10, 9], [8, 3, 11], [8, 10, 3], [12, 13, 6], [14, 2, 15], [16, 13, 15], [16, 2, 3], [3, 2, 1]]
    >>> strips = stripify(triangles)
    >>> _checkStrips(triangles, strips) # NvTriStrip gives wrong result
"""

    if USE_NVTRISTRIP:
        SetStitchStrips(stitchstrips)
        lst = []
        for face in triangles:
            lst.extend(face)
        pgroups = NvTriStrip.GenerateStrips(lst, validateEnabled = False)
        strips = []
        for ptype, indices in pgroups:
            if ptype == NvTriStrip.PT_STRIP:
                strips.append(indices)
            else:
                raise RuntimeError("unexpected primitive group type %i (bug!)"%ptype)
        return strips
    else:
        # build a mesh from triangles
        mesh = FaceEdgeMesh()
        for face in triangles:
            mesh.AddFace(*face)

        # calculate the strip
        stripifier = TriangleStripifier()
        stripifier.GLSelector.MinStripLength = 0
        stripifier.GLSelector.Samples = 10
        stripifier(mesh)

        # add the triangles to it
        i = stripifier.TriangleList.__iter__()
        strips = [face for face in _generateFacesFromTriangles(stripifier.TriangleList)] + stripifier.TriangleStrips

        if stitchstrips: return [stitchStrips(strips)]
        else: return strips

def stitchStrips(strips):
    """Stitch strips keeping stitch size minimal."""
    result = []
    realstrips = [strip for strip in strips if len(strip) >= 3]
    forward  = [strip for strip in realstrips if strip[0] != strip[1]]
    backward = [strip for strip in realstrips if strip[0] == strip[1]]
    while forward or backward:
        # create stitch
        if result:
            result.append(result[-1]) # first stitch
            winding = len(result) & 1
            # stitch length 2
            if winding == 1 and forward:
                strip = forward.pop()
                result.append(strip[0]) # second stitch
            elif winding == 0 and backward:
                strip = backward.pop()  # (second stitch is already in the strip)
            # stitch length 3
            elif winding == 0 and forward:
                strip = forward.pop()
                result.append(strip[0]) # second stitch
                result.append(strip[0]) # third stitch
            elif winding == 1 and backward:
                strip = backward.pop()
                result.append(strip[0]) # second stitch (third stitch is already in strip)
        else:
            if forward:
                strip = forward.pop()
            else:
                strip = backward.pop()
        # append strip
        result.extend(strip)
    return result

def unstitchStrip(strip):
    """Revert stitched strip back to a set of strips without stitches.

    >>> strip = [0,1,2,2,3,3,4,5,6,7,8]
    >>> triangles = triangulate([strip])
    >>> strips = unstitchStrip(strip)
    >>> _checkStrips(triangles, strips)
    >>> print strips
    [[0, 1, 2], [3, 3, 4, 5, 6, 7, 8]]
    >>> strip = [0,1,2,3,3,4,4,4,5,6,7,8]
    >>> triangles = triangulate([strip])
    >>> strips = unstitchStrip(strip)
    >>> _checkStrips(triangles, strips)
    >>> print strips
    [[0, 1, 2, 3], [4, 4, 5, 6, 7, 8]]
    >>> strip = [0,1,2,3,4,4,4,4,5,6,7,8]
    >>> triangles = triangulate([strip])
    >>> strips = unstitchStrip(strip)
    >>> _checkStrips(triangles, strips)
    >>> print strips
    [[0, 1, 2, 3, 4], [4, 4, 5, 6, 7, 8]]
    >>> strip = [0,1,2,3,4,4,4,4,4,5,6,7,8]
    >>> triangles = triangulate([strip])
    >>> strips = unstitchStrip(strip)
    >>> _checkStrips(triangles, strips)
    >>> print strips
    [[0, 1, 2, 3, 4], [4, 5, 6, 7, 8]]
    >>> strip = [0,0,1,1,2,2,3,3,4,4,4,4,4,5,5,6,6,7,7,8,8]
    >>> triangles = triangulate([strip])
    >>> strips = unstitchStrip(strip)
    >>> _checkStrips(triangles, strips)
    >>> print strips
    []"""
    strips = []
    currentstrip = []
    i = 0
    while i < len(strip)-3:
        # get potential stitch
        stitch = strip[i:i+4]
        if stitch[0] == stitch[1] == stitch[2] != stitch[3]:
            # skip degenerate
            i += 2
        elif stitch[0] == stitch[1] and stitch[2] == stitch[3]:
            # unstitch
            currentstrip.append(strip[i])
            if len(currentstrip) >= 3:
                strips.append(currentstrip)
            currentstrip = []
            # set up right winding for next strip
            if i & 1:
                i += 3
            else:
                i += 2
        else:
            # nothing special
            currentstrip.append(strip[i])
            i += 1
    currentstrip.extend(strip[i:])
    if len(currentstrip) >= 3:
        strips.append(currentstrip)
    return strips

if __name__=='__main__':
    import doctest
    doctest.testmod()
