# NOTE: This is inspired by an earlier version which used the media server.
# Date and time is now in ISO 8601-1:2019 basic format.
# Observed no significant test time difference with -v (verbose) option with gst-launch-1.0
#DEVICES="0 3 5 6 7 4 1 2"
#ENCODE="nvjpegenc"                                      # JPG: "nvjpegenc" | "queue leaky=2 max-size-buffers=1 ! nvjpegenc"
#ENCODE="queue leaky=2 max-size-buffers=1 ! nvjpegenc"   # JPG: "nvjpegenc" | "queue leaky=2 max-size-buffers=1 ! nvjpegenc"
#ENCODE="queue ! pngenc"                                 # PNG: "queue ! pngenc" | "queue leaky=2 max-size-buffers=1 ! pngenc"
ENCODE="queue leaky=2 max-size-buffers=1 ! pngenc"      # PNG: "queue ! pngenc" | "queue leaky=2 max-size-buffers=1 ! pngenc"
#FILE_EXT=".jpg"         # JPG: ".jpg" | PNG: ".png"
FILE_EXT=".png"         # JPG: ".jpg" | PNG: ".png"
HEIGHT=720
#FORMAT=""               # JPG: "" | PNG: "RGBA"
FORMAT="RGBA"               # JPG: "" | PNG: "RGBA"
NUM_BUFFERS=25          # Still playing with this. Caution: Must be, for example, <=99 with %02d in filename. Image was muted when using 1 and PNG. Seems to only be useful with multifilesink not filesink.
#NUM_CAMERAS=8
#RAW_FORMAT_STRING=""    # JPG: "" | PNG: "format=$FORMAT,"
RAW_FORMAT_STRING="format=$FORMAT,"    # JPG: "" | PNG: "format=$FORMAT,"
WIDTH=1280

# Test time noticeably reduced by 3 to 5 seconds when FILE_EXT is explicitly pre-assigned.
#if [ "$ENCODE" = "queue ! pngenc" ]
#then
#        FILE_EXT=".png"
#elif [ "$ENCODE" = "nvjpegenc" ]
#then
#        FILE_EXT=".jpg"
#else
#        FILE_EXT=".png"  # default to PNG
#fi

# Just in case, 'videos' directory creation is leftover from original media server method.
mkdir -pv ~/camera-capture/images ~/camera-capture/videos

# Reference commands...
#gst-inspect-1.0 nvarguscamerasrc
#gst-launch-1.0 \
#       -v \
#       nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=0 \
#       ! nvvidconv \
#       ! nvjpegenc \
#       ! multifilesink location=/home/botuser/camera-capture/images/device0_%Y%m%dT%H%M%S$FILE_EXT
#
#        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=3 \
#        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
#        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
#        ! $ENCODE \
#        ! queue \    <- removed
#        ! multifilesink location=/home/botuser/camera-capture/images/device3_%02d_`date +'%Y%m%dT%H%M%S'`$FILE_EXT    <- removed %02d

gst-launch-1.0 \
        -v \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=0 \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
        ! $ENCODE \
        ! multifilesink location=/home/botuser/camera-capture/images/device0_`date +'%Y%m%dT%H%M%S'`$FILE_EXT \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=1 \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
        ! $ENCODE \
        ! multifilesink location=/home/botuser/camera-capture/images/device1_`date +'%Y%m%dT%H%M%S'`$FILE_EXT \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=2 \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
        ! $ENCODE \
        ! multifilesink location=/home/botuser/camera-capture/images/device2_`date +'%Y%m%dT%H%M%S'`$FILE_EXT \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=3 \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
        ! $ENCODE \
        ! multifilesink location=/home/botuser/camera-capture/images/device3_`date +'%Y%m%dT%H%M%S'`$FILE_EXT \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=4 \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
        ! $ENCODE \
        ! multifilesink location=/home/botuser/camera-capture/images/device4_`date +'%Y%m%dT%H%M%S'`$FILE_EXT \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=5 \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
        ! $ENCODE \
        ! multifilesink location=/home/botuser/camera-capture/images/device5_`date +'%Y%m%dT%H%M%S'`$FILE_EXT \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=6 \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
        ! $ENCODE \
        ! multifilesink location=/home/botuser/camera-capture/images/device6_`date +'%Y%m%dT%H%M%S'`$FILE_EXT \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=7 \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw, $RAW_FORMAT_STRING width=$WIDTH,height=$HEIGHT" \
        ! $ENCODE \
        ! multifilesink location=/home/botuser/camera-capture/images/device7_`date +'%Y%m%dT%H%M%S'`$FILE_EXT

#for (( i=0; i<$NUM_CAMERAS; i++ ))
#for i in $DEVICES;
#do
: '    gst-launch-1.0 \
        -v \
        nvarguscamerasrc \
        num-buffers=$NUM_BUFFERS \
        sensor-id=$i \
        ! nvvidconv ! queue ! pngenc ! multifilesink \
        location=/home/botuser/camera-capture/images/device"$i"_`date +'%Y%m%dT%H%M%S'`$FILE_EXT
'
: '    gst-launch-1.0 \
        -v \
        nvarguscamerasrc num-buffers=$NUM_BUFFERS sensor-id=$i \
        ! "video/x-raw(memory:NVMM),width=$WIDTH,height=$HEIGHT" \
        ! nvvidconv ! "video/x-raw,format=$FORMAT,width=$WIDTH,height=$HEIGHT" \
        ! queue \
        ! pngenc \
        ! queue \
        ! filesink location=/home/botuser/camera-capture/images/device"$i"_`date +'%Y%m%dT%H%M%S'`$FILE_EXT
'
#done

# Playing with this as a temporary measure when $NUM_BUFFERS is > 1 to delete all other snapshots but the last one taken.
#if [ "$NUM_BUFFERS" -gt "1" ]
#then
#        find ~/camera-capture/images -type f \! -name "device?_`expr $NUM_BUFFERS - 1`_????????T??????$FILE_EXT" -delete
#fi

ls -al ~/camera-capture/images
