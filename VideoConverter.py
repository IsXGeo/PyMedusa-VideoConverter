#!/usr/bin/env python
# coding=utf-8

import os
import sys
import subprocess
import datetime

DEFAULT_VIDEO_CODEC = "h264"
DEFAULT_AUDIO_CODEC = "aac"
MAX_WIDTH = 854
MAX_HEIGHT = 480

OUT_VLIB = "libx264"
OUT_ALIB = "aac"
OUT_EXTENSION = ".mp4"
MKV_EXTENSION = ".mkv"
TEMP_EXTENSION = ".tmp.mp4"


def main(args):
    # log file	====================================================================================
    logfilename = os.path.splitext(args[0])[0] + ".log"

    # ensure file exists
    subprocess.call('/usr/bin/touch "' + logfilename + '"', shell=True)

    # open for append
    logfile = open(logfilename, "a")

    # new header
    logfile.write("****************************************************************************\n")
    logfile.write(str(datetime.datetime.now()) + "\n")
    logfile.write("\n")

    # process input file	========================================================================
    infilename = args[1]

    logfile.write("input file: " + infilename + "\n")

    # ensure input file exists
    if not os.path.isfile(infilename):
        logfile.write("<-- input file does not exist; aborting\n")

        return 1

    inExtension = os.path.splitext(infilename)[-1].lower()
    commandoutput = os.path.splitext(args[0])[0] + ".output"

    if os.path.isfile(commandoutput):
        os.remove(commandoutput)

    # command to extract video stream details
    command = '/usr/local/bin/ffprobe -v error -select_streams v:0 -show_entries stream=width,height,codec_name -of ' \
              'default=noprint_wrappers=1 "' + infilename + '" >"' + commandoutput + '" '

    logfile.write("  command: " + command + "\n")

    rv = subprocess.call(command, shell=True)

    if not os.path.isfile(commandoutput):
        logfile.write("<-- no ffprobe(v) output generated; aborting\n")

        return 1

    # fetch command output
    with open(commandoutput) as commandfile:
        lines = commandfile.readlines()

    # log command output if it failed
    if rv != 0:
        logfile.writelines(lines)

    # delete command output
    os.remove(commandoutput)

    # initialise the video properties we need
    invideocodec = ""
    inHeight = 0
    inWidth = 0

    # extract video properties from command output
    for line in lines:
        if line[:11] == "codec_name=":
            invideocodec = line[11:].lower().rstrip()

        elif line[:6] == "width=":
            inWidth = int(line[6:].rstrip())

        elif line[:7] == "height=":
            inHeight = int(line[7:].rstrip())

    #  command to extract audio stream details
    command = '/usr/local/bin/ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of ' \
              'default=noprint_wrappers=1 "' + infilename + '" >"' + commandoutput + '" '

    # logfile.write("  command: " + command + "\n")

    rv = subprocess.call(command, shell=True)

    if not os.path.isfile(commandoutput):
        logfile.write("<-- no ffprobe(a) output generated; aborting\n")

        return 1

    # fetch command output
    with open(commandoutput) as commandfile:
        lines = commandfile.readlines()

    # log command output if it failed
    if rv != 0:
        logfile.writelines(lines)

    # delete command output
    os.remove(commandoutput)

    # initialise audio properties
    inAudioCodec = ""

    # extract audio properties from the command output
    for line in lines:
        if line[:11] == "codec_name=":
            inAudioCodec = line[11:].lower().rstrip()

    # log input file properties
    logfile.write("  > video codec = " + invideocodec + "; audio codec = " + inAudioCodec + "; dimensions = " + str(
        inWidth) + "x" + str(inHeight) + "\n")

    # check what processing is needed	===============================================================
    doTranscode = False

    # initialise output format
    outVideoCodec = "copy"
    outAudioCodec = "copy"
    outExtension = OUT_EXTENSION

    if inExtension == OUT_EXTENSION:
        logfile.write("  MP4:\n")

        if invideocodec != DEFAULT_VIDEO_CODEC:
            logfile.write("    wrong video codec; transcode required\n")
            outVideoCodec = OUT_VLIB
            doTranscode = True

        if inAudioCodec != DEFAULT_AUDIO_CODEC:
            logfile.write("    wrong audio codec")

            if not doTranscode:
                logfile.write("; transcode required")

            logfile.write("\n")

            outAudioCodec = OUT_ALIB
            doTranscode = True

        # MP4 output will need to go into a temporary file, as input file is the name we want to ultimately end up with
        outExtension = TEMP_EXTENSION

    elif inExtension == MKV_EXTENSION:
        logfile.write("  MKV: transcode required\n")
        doTranscode = True

        if invideocodec != DEFAULT_VIDEO_CODEC:
            logfile.write("    wrong video codec\n")
            outVideoCodec = OUT_VLIB

        if inAudioCodec != DEFAULT_AUDIO_CODEC:
            logfile.write("    wrong audio codec\n")
            outAudioCodec = OUT_ALIB

    else:
        logfile.write("  " + inExtension[1:].upper() + ": full transcode required\n")
        doTranscode = True
        outVideoCodec = OUT_VLIB
        outAudioCodec = OUT_ALIB

    # initialise output dimensions (omit if no change)
    outDimensions = ""

    if (inWidth > MAX_WIDTH) or (inHeight > MAX_HEIGHT):
        logfile.write("  wrong dimensions")

        if not doTranscode:
            logfile.write("; transcode required")

        logfile.write("\n")

        # start by using max allowable height and calculating width in original ratio
        outHeight = MAX_HEIGHT
        outWidth = int(int(inWidth * MAX_HEIGHT / inHeight) / 2) * 2  # ensure even number

        # if width still too big, set max allowable width and calculate height in original ratio
        if outWidth > MAX_WIDTH:
            outWidth = MAX_WIDTH
            outHeight = int(int(inHeight * MAX_WIDTH / inWidth) / 2) * 2  # ensure even number

        outVideoCodec = OUT_VLIB
        outDimensions = " -s " + str(outWidth) + "x" + str(outHeight)
        doTranscode = True

        logfile.write("    old dimensions: " + str(inWidth) + "x" + str(inHeight) + "; new dimensions: " + str(
            outWidth) + "x" + str(outHeight) + "\n")

    # exit if no transcoding required	=====================================================================
    if not doTranscode:
        logfile.write("<-- transcode is not required; exiting\n")

        return 0

    # perform transcode	=====================================================================================
    outFilename = os.path.splitext(infilename)[0] + outExtension

    logfile.write("  Output file: " + outFilename + "\n")

    if os.path.isfile(outFilename):
        logfile.write("  Output file exists; deleting")
        os.remove(outFilename)

    # command to transcode the file
    command = '/usr/local/bin/ffmpeg -i "' + infilename + '" -map 0 -codec:v ' + outVideoCodec + \
              ' -preset fast -crf 22' + outDimensions + ' -codec:a ' + outAudioCodec + ' -sn "' + outFilename + \
              '" -hide_banner -loglevel warning >"' + commandoutput + '"'

    logfile.write("  command: " + command + "\n")

    rv = subprocess.call(command, shell=True)

    if (rv == 0) and os.path.isfile(outFilename):
        # success status and outfile exists
        logfile.write("  successful conversion; deleting input file\n")

        # delete input file
        os.remove(infilename)

        # if output file needs to become the input file, rename it
        if inExtension == OUT_EXTENSION:
            logfile.write("  renaming " + outFilename + " to " + infilename + "\n")
            os.rename(outFilename, infilename)

        logfile.write("<-- done\n")
    else:
        # error of some kind, write command output to log file
        if os.path.isfile(commandoutput):
            with open(commandoutput) as commandfile:
                logfile.writelines(commandfile.readlines())

        logfile.write("<-- conversion failed\n")

    if os.path.isfile(commandoutput):
        os.remove(commandoutput)

    logfile.close()

    return rv


if __name__ == '__main__':
    exit(main(sys.argv))
