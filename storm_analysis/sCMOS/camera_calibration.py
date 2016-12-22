#!/usr/bin/python
#
# Calculates offset, variance and gain for each pixel of
# a sCMOS camera. The input files are in the form that
# is generated by calibrate.py program in the folder
# hal4000/hamamatsu/ of the STORM-Control project which
# is available here:
#
# http://zhuang.harvard.edu/software.html
#
# Hazen 10/13
#

import matplotlib
import matplotlib.pyplot as pyplot
import numpy
import os
import sys

if (len(sys.argv) < 3):
    print("usage: <result file> <dark> <light1> ..")
    exit()

if os.path.exists(sys.argv[1]):
    print("calibration file already exists, please delete before proceeding.")
    exit()

n_points = len(sys.argv) - 2
all_means = False
all_vars = False

for i, file in enumerate(sys.argv[2:]):
    print(i, "loading", file)
    [frames, x, xx] = numpy.load(file)
    x = x.astype(numpy.float64)
    xx = xx.astype(numpy.float64)
    file_mean = x/float(frames)
    file_var = xx/float(frames) - file_mean * file_mean

    if not isinstance(all_means, numpy.ndarray):
        all_means = numpy.zeros((x.shape[0], x.shape[1], n_points))
        all_vars = numpy.zeros((x.shape[0], x.shape[1], n_points))

    if (i > 0):
        all_means[:,:,i] = file_mean - all_means[:,:,0]
        all_vars[:,:,i] = file_var - all_vars[:,:,0]
    else:
        all_means[:,:,i] = file_mean
        all_vars[:,:,i] = file_var

gain = numpy.zeros((all_means.shape[0], all_means.shape[1]))
if (len(sys.argv) > 3):
    for i in range(all_means.shape[0]):
        for j in range(all_means.shape[1]):
            gain[i,j] = numpy.polyfit(all_vars[i,j,:], all_means[i,j,:], 1)[0]
            if ((((i+1)*(j+1)) % 1000) == 0):
                print("pixel", i, j, "gain", gain[i,j])

if True:
    print("")
    for i in range(5):
        fig = pyplot.figure()
        ax = fig.add_subplot(111)

        data_x = all_vars[i,0,:]
        data_y = all_means[i,0,:]
        fit = numpy.polyfit(data_x, data_y, 1)

        print(i, "gain:", fit[0])
        ax.scatter(data_x,
                   data_y,
                   marker = 'o',
                   s = 2)

        xf = numpy.array([0, data_x[-1]])
        yf = xf * fit[0] + fit[1]

        ax.plot(xf, yf, color = 'blue')
        
        pyplot.show()

offset = all_means[:,:,0]
variance = all_vars[:,:,0]

#
# Transpose the calibration data as storm-analysis uses the
# transpose of the image for historical reasons.
#
offset = numpy.transpose(offset)
variance = numpy.transpose(variance)
gain = numpy.transpose(gain)    

numpy.save(sys.argv[1], [offset, variance, gain])

#
# The MIT License
#
# Copyright (c) 2013 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
