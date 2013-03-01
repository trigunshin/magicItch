#!/bin/bash
HOMEDIR="/home/pcrane/"
DEVDIR=$HOMEDIR"dev/"
ITCHDIR=$DEVDIR"magicItch/"
SRCDIR=$ITCHDIR"src/"
SCG_DATA_DIR=$ITCHDIR"scg_data/"
SPRITE_DIR=$ITCHDIR"sprites/"
LOGDIR=$HOMEDIR"logs/magicItch/"
DATE=$(date -I)
YEST=$(date -I -d '1 day ago')

python $SRCDIR"sprites.py" -f $SCG_DATA_DIR -s $SPRITE_DIR -m $SRCDIR"ocr_map.csv" &> $LOGDIR"log_"$DATE".log"
python $SRCDIR"processSprites.py" -s $SPRITE_DIR &> $LOGDIR"log_"$DATE".log"
