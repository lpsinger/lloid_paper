#!/usr/bin/env python
"""Convert legacy SVD bank files"""

# Command line interface
import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    'filename', metavar='FILENAME.xml[.gz]', nargs=1,
    help='Name of file to modify in-place')
args = parser.parse_args()

# Late imports
import os
import glue.ligolw.utils
import glue.ligolw.table
import glue.ligolw.param
import glue.ligolw.array
import glue.ligolw.types
import glue.ligolw.lsctables
import numpy as np

# Determine input filename
filename, = args.filename
_, ext = os.path.splitext(filename)
gz = (ext == '.gz')

# Read file, get root element
xmldoc = glue.ligolw.utils.load_filename(filename, gz=gz)
root, = xmldoc.childNodes

# Add name to root element
root.setAttribute(u'Name', u'gstlal_svd_bank_Bank')

# Add empty sngl_inspiral table
root.appendChild(glue.ligolw.lsctables.New(
    glue.ligolw.lsctables.SnglInspiralTable))

# Add empty bank_id param
root.appendChild(glue.ligolw.param.new_param(
    'bank_id', glue.ligolw.types.FromPyType[str], ' '))

# Doesn't like empty logname
logname = glue.ligolw.param.get_param(root, 'logname')
logname.pcdata = ' '

# Add empty autocorrelation_mask array
root.appendChild(glue.ligolw.array.from_array(
    'autocorrelation_mask', np.empty(0)))

glue.ligolw.utils.write_filename(xmldoc, filename, gz=gz)
