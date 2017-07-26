#!/usr/bin/env python
#
#    This is renaconf, a graphical configuration editor for LinuxCNC
#    Copyright 2007 Jeff Epler <jepler@unpythonic.net>
#    renaconf 1.1 revamped by Chris Morley 2014
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    This builds the INI file from the collected data.
#

import os
import time

class INI:
    def __init__(self,app):
        # access to:
        self.d = app.d  # collected data
        global SIG
        SIG = app._p    # private data (signals names)
        self.a = app    # The parent, renaconf

    def write_inifile(self, base):
        if self.d.axes == 2:
            maxvel = max(self.d.xmaxvel, self.d.zmaxvel)        
        else:
            maxvel = max(self.d.xmaxvel, self.d.ymaxvel, self.d.zmaxvel)        
        hypotvel = (self.d.xmaxvel**2 + self.d.ymaxvel**2 + self.d.zmaxvel**2) **.5
        defvel = min(maxvel, max(.1, maxvel/10.))

        filename = os.path.join(base, self.d.machinename + ".ini")
        file = open(filename, "w")
        print >>file, _("# Generated by renaconf 1.1 at %s") % time.asctime()
        print >>file, _("# If you make changes to this file, they will be")
        print >>file, _("# overwritten when you run renaconf again")

        print >>file
        print >>file, "[EMC]"
        print >>file, "MACHINE = %s" % self.d.machinename
        print >>file, "DEBUG = 0"

        print >>file
        print >>file, "[DISPLAY]"
        print >>file, "DISPLAY = axis"
        print >>file, "EDITOR = gedit"
        print >>file, "POSITION_OFFSET = RELATIVE"
        print >>file, "POSITION_FEEDBACK = ACTUAL"
        print >>file, "ARCDIVISION = 64"
        print >>file, "GRIDS = 10mm 20mm 50mm 100mm 1in 2in 5in 10in"
        print >>file, "MAX_FEED_OVERRIDE = 1.2"
        print >>file, "MIN_SPINDLE_OVERRIDE = 0.5"
        print >>file, "MAX_SPINDLE_OVERRIDE = 1.2"
        print >>file, "DEFAULT_LINEAR_VELOCITY = %.2f" % defvel
        print >>file, "MIN_LINEAR_VELOCITY = 0"
        print >>file, "MAX_LINEAR_VELOCITY = %.2f" % maxvel
        if self.d.axes == 1:
            defvel = min(60, self.d.amaxvel/10.)
            print >>file, "DEFAULT_ANGULAR_VELOCITY = %.2f" % defvel
            print >>file, "MIN_ANGULAR_VELOCITY = 0"
            print >>file, "MAX_ANGULAR_VELOCITY = %.2f" % self.d.amaxvel

        print >>file, "INTRO_GRAPHIC = linuxcnc.gif"
        print >>file, "INTRO_TIME = 5"
        print >>file, "PROGRAM_PREFIX = %s" % os.path.expanduser("~/linuxcnc/nc_files")
        if self.d.units:
            print >>file, "INCREMENTS = 5mm 1mm .5mm .1mm .05mm .01mm .005mm"
        else:
            print >>file, "INCREMENTS = .1in .05in .01in .005in .001in .0005in .0001in"
        if self.d.pyvcp:
            print >>file, "PYVCP = custompanel.xml"
        if self.d.axes == 2:
            print >>file, "LATHE = 1"

        print >>file
        print >>file, "[FILTER]"
        print >>file, "PROGRAM_EXTENSION = .png,.gif,.jpg Greyscale Depth Image"
        print >>file, "PROGRAM_EXTENSION = .py Python Script"
        print >>file, "png = image-to-gcode"
        print >>file, "gif = image-to-gcode"
        print >>file, "jpg = image-to-gcode"
        print >>file, "py = python"        

        print >>file
        print >>file, "[TASK]"
        print >>file, "TASK = milltask"
        print >>file, "CYCLE_TIME = 0.010"

        print >>file
        print >>file, "[RS274NGC]"
        print >>file, "PARAMETER_FILE = linuxcnc.var"

        base_period = self.ideal_period()

        print >>file
        print >>file, "[EMCMOT]"
        print >>file, "EMCMOT = motmod"
        print >>file, "COMM_TIMEOUT = 1.0"
        print >>file, "COMM_WAIT = 0.010"
        print >>file, "BASE_PERIOD = %d" % base_period
        print >>file, "SERVO_PERIOD = 1000000"

        print >>file
        print >>file, "[HAL]"
        if self.d.halui:
            print >>file,"HALUI = halui"          
        print >>file, "HALFILE = %s.hal" % self.d.machinename
        if self.d.customhal:
            print >>file, "HALFILE = custom.hal"
            print >>file, "POSTGUI_HALFILE = custom_postgui.hal"

        if self.d.halui:
           print >>file
           print >>file, "[HALUI]"
           print >>file, _("# add halui MDI commands here (max 64) ")

        print >>file
        print >>file, "[TRAJ]"
        if self.d.axes == 1:
            print >>file, "AXES = 4"
            print >>file, "COORDINATES = X Y Z A"
        elif self.d.axes == 0:
            print >>file, "AXES = 3"
            print >>file, "COORDINATES = X Y Z"
        else:
            print >>file, "AXES = 3"
            print >>file, "COORDINATES = X Z"
        if self.d.units:
            print >>file, "LINEAR_UNITS = mm"
        else:
            print >>file, "LINEAR_UNITS = inch"
        print >>file, "ANGULAR_UNITS = degree"
        print >>file, "CYCLE_TIME = 0.010"
        print >>file, "DEFAULT_VELOCITY = %.2f" % defvel
        print >>file, "MAX_VELOCITY = %.2f" % maxvel
        print >>file
        print >>file, "[EMCIO]"
        print >>file, "EMCIO = io"
        print >>file, "CYCLE_TIME = 0.100"
        print >>file, "TOOL_TABLE = tool.tbl"

        all_homes = self.a.home_sig("x") and self.a.home_sig("z")
        if self.d.axes != 2: all_homes = all_homes and self.a.home_sig("y")
        if self.d.axes == 4: all_homes = all_homes and self.a.home_sig("a")

        self.write_one_axis(file, 0, "x", "LINEAR", all_homes)
        if self.d.axes != 2:
            self.write_one_axis(file, 1, "y", "LINEAR", all_homes)
        self.write_one_axis(file, 2, "z", "LINEAR", all_homes)
        if self.d.axes == 1:
            self.write_one_axis(file, 3, "a", "ANGULAR", all_homes)

        file.close()
        self.d.add_md5sum(filename)

#******************
# HELPER FUNCTIONS
#******************
    def write_one_axis(self, file, num, letter, type, all_homes):
        order = "1203"
        def get(s): return self.d[letter + s]
        scale = get("scale")
        vel = min(get("maxvel"), self.ideal_maxvel(scale))
        print >>file
        print >>file, "[AXIS_%d]" % num
        print >>file, "TYPE = %s" % type
        print >>file, "HOME = %s" % get("homepos")
        print >>file, "MAX_VELOCITY = %s" % vel
        print >>file, "MAX_ACCELERATION = %s" % get("maxacc")
        print >>file, "STEPGEN_MAXACCEL = %s" % (1.25 * get("maxacc"))
        print >>file, "SCALE = %s" % scale
        if num == 3:
            print >>file, "FERROR = 1"
            print >>file, "MIN_FERROR = .25"
        elif self.d.units:
            print >>file, "FERROR = 1"
            print >>file, "MIN_FERROR = .25"
        else:
            print >>file, "FERROR = 0.05"
            print >>file, "MIN_FERROR = 0.01"

        # linuxcnc doesn't like having home right on an end of travel,
        # so extend the travel limit by up to .01in or .1mm
        minlim = get("minlim")
        maxlim = get("maxlim")
        home = get("homepos")
        if self.d.units: extend = .001
        else: extend = .01
        minlim = min(minlim, home - extend)
        maxlim = max(maxlim, home + extend)
        print >>file, "MIN_LIMIT = %s" % minlim
        print >>file, "MAX_LIMIT = %s" % maxlim

        inputs = self.a.build_input_set()
        thisaxishome = set((SIG.ALL_HOME, SIG.ALL_LIMIT_HOME, "home-" + letter, "min-home-" + letter,
                            "max-home-" + letter, "both-home-" + letter))
        # no need to set HOME_IGNORE_LIMITS when ALL_LIMIT_HOME, HAL logic will do the trick
        ignore = set(("min-home-" + letter, "max-home-" + letter,
                            "both-home-" + letter))
        homes = bool(inputs & thisaxishome)
    
        if homes:
            print >>file, "HOME_OFFSET = %f" % get("homesw")
            print >>file, "HOME_SEARCH_VEL = %f" % get("homevel")
            latchvel = get("homevel") / abs(get("homevel"))
            if get("latchdir"): latchvel = -latchvel
            # set latch velocity to one step every two servo periods
            # to ensure that we can capture the position to within one step
            latchvel = latchvel * 500 / get("scale")
            # don't do the latch move faster than the search move
            if abs(latchvel) > abs(get("homevel")):
                latchvel = latchvel * (abs(get("homevel"))/abs(latchvel))
            print >>file, "HOME_LATCH_VEL = %f" % latchvel
            if inputs & ignore:
                print >>file, "HOME_IGNORE_LIMITS = YES"
            if all_homes:
                print >>file, "HOME_SEQUENCE = %s" % order[num]
        else:
            print >>file, "HOME_OFFSET = %s" % get("homepos")

    def hz(self, axname):
        steprev = self.d[axname+"steprev"]
        microstep = self.d[axname+"microstep"]
        pulleynum = self.d[axname+"pulleynum"]
        pulleyden = self.d[axname+"pulleyden"]
        leadscrew = self.d[axname+"leadscrew"]
        maxvel = self.d[axname+"maxvel"]
        if self.d.units or axname == 'a': leadscrew = 1./leadscrew
        pps = leadscrew * steprev * microstep * (pulleynum/pulleyden) * maxvel
        return abs(pps)

    def minperiod(self, steptime=None, stepspace=None, latency=None):
        if steptime is None: steptime = self.d.steptime
        if stepspace is None: stepspace = self.d.stepspace
        if latency is None: latency = self.d.latency
        if self.a.doublestep(steptime):
            return max(latency + steptime + stepspace + 5000, 4*steptime)
        else:
            return latency + max(steptime, stepspace)

    def maxhz(self):
        return 1e9 / self.minperiod()

    def ideal_period(self):
        xhz = self.hz('x')
        yhz = self.hz('y')
        zhz = self.hz('z')
        ahz = self.hz('a')
        if self.d.axes == 1:
            pps = max(xhz, yhz, zhz, ahz)
        elif self.d.axes == 0:
            pps = max(xhz, yhz, zhz)
        else:
            pps = max(xhz, zhz)
        if self.a.doublestep():
            base_period = 1e9 / pps
        else:
            base_period = .5e9 / pps
        if base_period > 100000: base_period = 100000
        if base_period < self.minperiod(): base_period = self.minperiod()
        return int(base_period)

    def ideal_maxvel(self, scale):
        if self.a.doublestep():
            return abs(.95 * 1e9 / self.ideal_period() / scale)
        else:
            return abs(.95 * .5 * 1e9 / self.ideal_period() / scale)

    # Boiler code
    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, item, value):
        return setattr(self, item, value)
